import asyncio, os, logging, time
from datetime import datetime
from zoneinfo import ZoneInfo
import httpx
from core import dec

def authorized(message, users, chats):
    sender=str(message.get('from',{}).get('id',''))
    chat=message.get('chat',{})
    if sender not in users:return False
    if not chats:return chat.get('type')=='private' and str(chat.get('id',''))==sender
    return str(chat.get('id','')) in chats

def menu():
    return {'inline_keyboard':[[{'text':'Aktueller Preis','callback_data':'/preis'},{'text':'Verlauf','callback_data':'/verlauf'}],[{'text':'Tarif','callback_data':'/tarif'},{'text':'Status','callback_data':'/status'}]]}

def text_for(command, state):
    s=state();p=s['current']['price'] if s['current'] else s['tariff_price']
    warning='Tarifschätzung · '+('Tarif geprüft' if s['configured'] else 'Tarif ungeprüft')
    if command=='/status':return warning+'\nMarktdaten: '+('veraltet/fehlend' if s['stale'] else 'vorhanden')
    if command=='/verlauf':
        rows=[x for x in s['rows'] if x['end']>time.time()*1000][:24]
        return warning+'\nEurope/Berlin:\n'+'\n'.join(datetime.fromtimestamp(x['start']/1000,ZoneInfo('Europe/Berlin')).isoformat()+f" → {dec(x['price']['gross_ct']):.3f} ct/kWh brutto" for x in rows)
    if command in ('/preis','/tarif'):
        if not p:return warning+'\nKein gültiger aktueller Preis verfügbar.'
        parts='\n'.join(f"{x['name']}: {x['ct']} ct/kWh netto" for x in s['tariff']['components'])
        return warning+f"\nArbeitspreis: {dec(p['gross_ct']):.3f} ct/kWh brutto\nEnergie: {p['energy_net_ct']} ct/kWh netto\n{parts}\nService: {p['fee_net_ct']} ct/kWh netto\nMwSt.: {p['vat_ct']} ct/kWh\nGrundpreis: {p['base_gross_eur']} EUR/Monat brutto\nMarktdaten veraltet: {s['stale']}"
    return '/preis · /verlauf · /tarif · /status · /hilfe'

async def run(store,state):
    token=os.getenv('TELEGRAM_BOT_TOKEN','')
    users={x.strip() for x in os.getenv('TELEGRAM_USER_IDS','').split(',') if x.strip()}
    chats={x.strip() for x in os.getenv('TELEGRAM_CHAT_IDS','').split(',') if x.strip()}
    if not token or not users:return
    async with httpx.AsyncClient(timeout=40) as client:
        async def call(method,body):
            r=await client.post(f'https://api.telegram.org/bot{token}/{method}',json=body)
            r.raise_for_status();value=r.json()
            if not value.get('ok'):raise ValueError('Telegram request failed')
            return value.get('result')
        while True:
            try:
                updates=await call('getUpdates',{'offset':store.get('telegram_offset',0),'timeout':25,'allowed_updates':['message','callback_query']})
                for update in updates:
                    cb=update.get('callback_query');message=update.get('message',{})
                    if cb:
                        message=dict(cb.get('message',{}));message['from']=cb.get('from',{})
                    if authorized(message,users,chats):
                        command=(cb.get('data','') if cb else message.get('text','')).split(' ')[0].split('@')[0]
                        if cb:await call('answerCallbackQuery',{'callback_query_id':cb['id']})
                        await call('sendMessage',{'chat_id':message['chat']['id'],'text':text_for(command,state)[:4000],'reply_markup':menu()})
                    store.put('telegram_offset',update['update_id']+1)
            except asyncio.CancelledError:raise
            except Exception:
                logging.getLogger('flexpower').warning('Telegram-Anfrage fehlgeschlagen; Details ausgeblendet')
                await asyncio.sleep(10)
