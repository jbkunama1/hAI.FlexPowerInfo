import asyncio,os,logging,time,json,secrets
from copy import deepcopy
from datetime import datetime
from zoneinfo import ZoneInfo
from html import escape
import httpx
from core import dec,validate,DEFAULT
from bot_visuals import chart_png

def authorized(message,users,chats):
    sender=str(message.get('from',{}).get('id',''));chat=message.get('chat',{})
    if sender not in users:return False
    if not chats:return chat.get('type')=='private' and str(chat.get('id',''))==sender
    return str(chat.get('id','')) in chats

def is_admin(message,admins):
    return message.get('chat',{}).get('type')=='private' and str(message.get('from',{}).get('id','')) in admins

def menu(admin=False):
    rows=[[{'text':'⚡ Preis','callback_data':'/preis'},{'text':'📋 Verlauf','callback_data':'/verlauf'}],[{'text':'📊 Preisgrafik','callback_data':'/grafik'},{'text':'🧩 Tarif','callback_data':'/tarif'}],[{'text':'🩺 Status','callback_data':'/status'},{'text':'🏠 Start','callback_data':'/start'}]]
    if admin:rows.append([{'text':'🛠 Administration','callback_data':'/admin'}])
    return {'inline_keyboard':rows}

def stamp(ms):return datetime.fromtimestamp(ms/1000,ZoneInfo('Europe/Berlin')).strftime('%d.%m. %H:%M %Z')

def text_for(command,state):
    s=state();p=s['current']['price'] if s['current'] else s['tariff_price']
    warning='🧾 Tarifschätzung · '+('✅ Tarif geprüft' if s['configured'] else '⚠️ Tarif ungeprüft')
    if command in ('/start','/hilfe'):
        return '<b>⚡ Willkommen bei hAI.FlexPowerInfo!</b>\n<i>Dein Strompreis. Dein Tarif. Deine Kontrolle.</i>\n\n🌐 Ein Tarifdienst für Web, Telegram und MCP.\n⚡ Preis mit allen Bestandteilen\n📊 Farbige Preisgrafik\n🧩 Tarif und Status\n\nNutze die Buttons unten. Admin-Funktionen erscheinen nur nach separater Freigabe.\n\n'+warning+'\n🐟 highfishAI'
    if command=='/status':
        return '<b>🩺 Systemstatus</b>\n'+warning+'\n📡 Marktdaten: '+('⚠️ veraltet/fehlend' if s['stale'] else '✅ vorhanden')+'\nAbruf: '+(stamp(s['fetched']*1000) if s['fetched'] else 'noch keiner')
    if command=='/verlauf':
        rows=[x for x in s['rows'] if x['end']>time.time()*1000][:24]
        return '<b>📋 Nächste Preisintervalle</b>\n'+warning+'\n'+'\n'.join(stamp(x['start'])+f" → {dec(x['price']['gross_ct']):.3f} ct/kWh brutto" for x in rows)
    if command in ('/preis','/tarif'):
        if not p:return warning+'\n⏳ Kein gültiger aktueller Preis verfügbar.'
        parts='\n'.join('🧩 '+escape(str(x['name']))+': '+escape(str(x['ct']))+' ct/kWh netto' for x in s['tariff']['components'])
        interval=stamp(s['current']['start'])+' – '+stamp(s['current']['end']) if s['current'] else 'Fester/manueller Referenzwert'
        return '<b>⚡ Dein geschätzter Strompreis</b>'+f"\n<b>{dec(p['gross_ct']):.3f} ct/kWh brutto</b>\n"+interval+'\n\n'+warning+f"\nEnergie: {escape(p['energy_net_ct'])} ct/kWh netto\n"+parts+f"\nService: {escape(p['fee_net_ct'])} ct/kWh netto\nMwSt.: {escape(p['vat_ct'])} ct/kWh\nGrundpreis: {escape(p['base_gross_eur'])} EUR/Monat brutto\n"+('⚠️ Marktdaten veraltet/fehlend' if s['stale'] else '📡 Marktdaten vorhanden')
    return '❓ Unbekannter Befehl. Nutze /start oder /hilfe.'

FIELDS={'vat':'Umsatzsteuer (%)','base_net':'Grundpreis netto (EUR/Monat)','energy_ct':'Fester/manueller Energieanteil netto (ct/kWh)','fee_percent':'Servicegebühr (%)','refresh_minutes':'Abrufintervall (Minuten)'}
def edited(tariff,field,value):
    if field not in FIELDS:raise ValueError('Unbekanntes Feld')
    candidate=deepcopy(tariff);candidate[field]=value.replace(',','.')
    return validate(candidate)

def admin_menu():
    return {'inline_keyboard':[[{'text':'📡 Preise abrufen','callback_data':'admin:refresh'},{'text':'⏱ Auto-Abruf umschalten','callback_data':'admin:auto'}],[{'text':'🧾 MwSt. ändern','callback_data':'edit:vat'},{'text':'🏠 Grundpreis ändern','callback_data':'edit:base_net'}],[{'text':'⚡ Energieanteil ändern','callback_data':'edit:energy_ct'},{'text':'🧮 Service ändern','callback_data':'edit:fee_percent'}],[{'text':'🕒 Abrufintervall','callback_data':'edit:refresh_minutes'},{'text':'🏠 Hauptmenü','callback_data':'/start'}]]}

async def run(store,state):
    token=os.getenv('TELEGRAM_BOT_TOKEN','')
    users={x.strip() for x in os.getenv('TELEGRAM_USER_IDS','').split(',') if x.strip()}
    chats={x.strip() for x in os.getenv('TELEGRAM_CHAT_IDS','').split(',') if x.strip()}
    admins={x.strip() for x in os.getenv('TELEGRAM_ADMIN_IDS','').split(',') if x.strip()}
    if not token or not users:return
    pending={}
    async with httpx.AsyncClient(timeout=40) as client:
        async def call(method,body=None,photo=None):
            url=f'https://api.telegram.org/bot{token}/{method}'
            if photo is None:r=await client.post(url,json=body)
            else:r=await client.post(url,data={k:str(v) for k,v in body.items()},files={'photo':('preise.png',photo,'image/png')})
            r.raise_for_status();value=r.json()
            if not value.get('ok'):raise ValueError('Telegram request failed')
            return value.get('result')
        async def send(chat,text,keyboard):
            await call('sendMessage',{'chat_id':chat,'text':text[:4000],'parse_mode':'HTML','reply_markup':keyboard})
        async def propose(chat,key,base,candidate):
            nonce=secrets.token_hex(6)
            pending[key]={'base':base,'candidate':candidate,'nonce':nonce,'expires':time.time()+300}
            changes='\n'.join(escape(k)+': '+escape(str(base.get(k)))+' → '+escape(str(v)) for k,v in candidate.items() if base.get(k)!=v)
            await send(chat,'<b>🔎 Änderung prüfen</b>\n'+changes+'\n\nSpeichern hebt die Tarif-Prüfbestätigung auf. Vorschlag gilt fünf Minuten.',{'inline_keyboard':[[{'text':'✅ Speichern','callback_data':'apply:'+nonce},{'text':'❌ Abbrechen','callback_data':'cancel'}]]})
        while True:
            try:
                for key in list(pending):
                    if pending[key]['expires']<time.time():pending.pop(key,None)
                updates=await call('getUpdates',{'offset':store.get('telegram_offset',0),'timeout':25,'allowed_updates':['message','callback_query']})
                for update in updates:
                    cb=update.get('callback_query');message=update.get('message',{})
                    if cb:
                        message=dict(cb.get('message',{}));message['from']=cb.get('from',{})
                    if not authorized(message,users,chats):
                        store.put('telegram_offset',update['update_id']+1);continue
                    chat=message['chat']['id'];key=(str(message['from']['id']),str(chat));admin=is_admin(message,admins)
                    raw=cb.get('data','') if cb else message.get('text','')
                    command=raw.split(' ')[0].split('@')[0]
                    if cb:await call('answerCallbackQuery',{'callback_query_id':cb['id']})
                    if command in ('cancel','/cancel'):
                        pending.pop(key,None);await send(chat,'❎ Abgebrochen.',menu(admin))
                    elif command=='/admin' or command.startswith(('admin:','edit:','apply:')) or command=='/set':
                        if not admin:await send(chat,'🔒 Nur freigegebene Admins im privaten Chat dürfen ändern.',menu(False))
                        else:
                            base=store.get('tariff',DEFAULT)
                            if command=='/admin':
                                await send(chat,'<b>🛠 Administration</b>\n⏱ Auto-Abruf: '+('an' if base['auto_refresh'] else 'aus')+'\nTarifwerte netto. Änderungen erst nach Bestätigung.\nWeitere Bestandteile und Tarifmodell über die Web-Administration.',admin_menu())
                            elif command=='admin:refresh':
                                from app import refresh
                                await refresh();await send(chat,'📡 Abruf angefordert. Die 15-Minuten-Sperre bleibt gültig.\n'+text_for('/status',state),admin_menu())
                            elif command=='admin:auto':
                                candidate=deepcopy(base);candidate['auto_refresh']=not base['auto_refresh'];await propose(chat,key,base,candidate)
                            elif command.startswith('edit:'):
                                field=command.split(':',1)[1]
                                if field in FIELDS:
                                    pending[key]={'field':field,'expires':time.time()+300}
                                    await send(chat,'✏️ '+escape(FIELDS[field])+'\nAntworte mit einer Zahl. /cancel bricht ab.',{'inline_keyboard':[[{'text':'❌ Abbrechen','callback_data':'cancel'}]]})
                            elif command=='/set':
                                try:
                                    _,field,value=raw.split(maxsplit=2);await propose(chat,key,base,edited(base,field,value))
                                except (ValueError,TypeError):await send(chat,'⚠️ Beispiel: <code>/set vat 19</code>. Erlaubt: '+', '.join(FIELDS),admin_menu())
                            elif command.startswith('apply:'):
                                draft=pending.pop(key,None)
                                if not draft or draft.get('nonce')!=command.split(':',1)[1] or draft['expires']<time.time():await send(chat,'⌛ Vorschlag ungültig oder abgelaufen.',admin_menu())
                                elif draft['base']!=base:await send(chat,'⚠️ Tarif wurde zwischenzeitlich geändert. Bitte neu beginnen.',admin_menu())
                                else:
                                    candidate=draft['candidate'];candidate['confirmed']=False;store.save_tariff(candidate)
                                    await send(chat,'✅ Gespeichert. Bitte Tarif in der Web-Administration erneut prüfen.',admin_menu())
                    elif not cb and key in pending and 'field' in pending[key] and not raw.startswith('/'):
                        draft=pending.pop(key)
                        if admin and draft['expires']>=time.time():
                            base=store.get('tariff',DEFAULT)
                            try:await propose(chat,key,base,edited(base,draft['field'],raw.strip()))
                            except (ValueError,TypeError):await send(chat,'⚠️ Ungültige Eingabe. Änderung nicht gespeichert.',admin_menu())
                    elif command=='/grafik':
                        s=state();rows=[x for x in s['rows'] if x['end']>time.time()*1000][:96]
                        if not rows:await send(chat,'⏳ Keine Preisintervalle für eine Grafik verfügbar.',menu(admin))
                        else:
                            values=[dec(x['price']['gross_ct']) for x in rows]
                            caption='📊 Geschätzte Arbeitspreise brutto\n'+stamp(rows[0]['start'])+' – '+stamp(rows[-1]['end'])+f'\nMin: {min(values):.3f} · Max: {max(values):.3f} ct/kWh\nGrün: ≥ 0 · Violett: < 0 · Weiße Linie: 0\nZeit proportional, bis zu 96 Quellintervalle.\n'+('⚠️ Tarif ungeprüft. ' if not s['configured'] else '')+('⚠️ Marktdaten veraltet.' if s['stale'] else '')
                            await call('sendPhoto',{'chat_id':chat,'caption':caption,'reply_markup':json.dumps(menu(admin),ensure_ascii=False)},await asyncio.to_thread(chart_png,rows))
                    else:await send(chat,text_for(command,state),menu(admin))
                    store.put('telegram_offset',update['update_id']+1)
            except asyncio.CancelledError:raise
            except Exception:
                logging.getLogger('flexpower').warning('Telegram-Anfrage fehlgeschlagen; Details ausgeblendet')
                await asyncio.sleep(10)
