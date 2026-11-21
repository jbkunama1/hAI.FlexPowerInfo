import asyncio, json, logging, os, secrets, time
from contextlib import asynccontextmanager, suppress
from datetime import datetime
from zoneinfo import ZoneInfo
import httpx
from fastapi import Request, HTTPException
from fastapi.routing import APIRoute
from gateway import app, mcp, legacy, session_valid
from market_alerts import DEFAULT_ALERTS, validate_alerts, evaluate

def get_config():
    return legacy.store.get('market_alerts', DEFAULT_ALERTS)

def save_config(config):
    value = validate_alerts(config)
    legacy.store.put('market_alerts', value)
    return value

@mcp.tool()
def get_market_alerts() -> dict:
    return {'config': get_config(), 'basis': 'Aktuelles Boersenintervall plus gespeicherte Tarifbestandteile und Umsatzsteuer; ohne Grundpreis. Modellrechnung, kein Monatsabrechnungspreis.'}

@mcp.tool()
def update_market_alerts(config: dict) -> dict:
    '''WRITE: configure Telegram market alerts. Review with user first. enabled bool, lower and upper in gross ct/kWh. All TELEGRAM_USER_IDS receive private alerts. Independent of tariff mode.'''
    return save_config(config)

async def api_get(request: Request):
    if not session_valid(request):
        raise HTTPException(401, 'Anmeldung erforderlich')
    return get_market_alerts()

async def api_save(request: Request):
    if not session_valid(request):
        raise HTTPException(401, 'Anmeldung erforderlich')
    session = legacy.sessions[request.cookies['session']]
    if not secrets.compare_digest(request.headers.get('x-csrf-token', '').encode(), session['csrf'].encode()):
        raise HTTPException(403, 'CSRF-Pruefung fehlgeschlagen')
    if len(await request.body()) > 4096:
        raise HTTPException(413, 'Anfrage zu gross')
    try:
        return save_config(await request.json())
    except (ValueError, TypeError, KeyError):
        raise HTTPException(400, 'Ungueltige Alarmkonfiguration')

app.router.routes.insert(-1, APIRoute('/api/market-alerts', api_get, methods=['GET']))
app.router.routes.insert(-1, APIRoute('/api/market-alerts', api_save, methods=['POST']))

def stamp(ms):
    return datetime.fromtimestamp(ms/1000, ZoneInfo('Europe/Berlin')).strftime('%d.%m.%Y %H:%M %Z')

async def monitor():
    token = os.getenv('TELEGRAM_BOT_TOKEN', '')
    users = sorted({x.strip() for x in os.getenv('TELEGRAM_USER_IDS', '').split(',') if x.strip()})
    if not token or not users:
        return
    retry_after = {}
    async with httpx.AsyncClient(timeout=20) as client:
        while True:
            try:
                config = get_config()
                if config['enabled']:
                    await legacy.refresh()
                    now = time.time()
                    tariff = legacy.store.get('tariff', legacy.DEFAULT)
                    result = evaluate(legacy.store.get('market', {}), tariff, config, now)
                    if result:
                        fingerprint = json.dumps(config, sort_keys=True)
                        for user in users:
                            key = 'market_alert_state:' + user
                            old = legacy.store.get(key, {})
                            if old.get('config') == fingerprint and old.get('band') == result['band']:
                                continue
                            saved = {'config': fingerprint, 'band': result['band'], 'interval': result['start']}
                            if result['band'] == 'normal':
                                legacy.store.put(key, saved)
                                continue
                            if retry_after.get(user, 0) > now:
                                continue
                            bound = config['lower'] if result['band'] == 'low' else config['upper']
                            relation = 'unter' if result['band'] == 'low' else 'ueber'
                            text = ('Marktpreisalarm: ' + relation + ' ' + bound + ' ct/kWh\n'
                                    + 'Modellpreis: ' + result['gross_ct'] + ' ct/kWh brutto\n'
                                    + stamp(result['start']) + ' bis ' + stamp(result['end']) + '\n'
                                    + 'Boersenpreis plus gespeicherte Zuschlaege, Gebuehren und Umsatzsteuer; ohne Grundpreis.\n'
                                    + 'Vorlaeufige Modellrechnung, kein bestaetigter EnerFlex-Blue-Abrechnungspreis.\n'
                                    + ('Tarif ungeprueft.' if not tariff['confirmed'] else 'Tarifwerte als geprueft markiert.'))
                            retry_after[user] = now + 60
                            try:
                                response = await client.post('https://api.telegram.org/bot' + token + '/sendMessage', json={'chat_id': user, 'text': text[:4000]})
                                response.raise_for_status()
                                if not response.json().get('ok'):
                                    raise ValueError('Telegram refusal')
                                legacy.store.put(key, saved)
                            except Exception:
                                logging.getLogger('flexpower').warning('Marktpreisalarm konnte nicht zugestellt werden; Details ausgeblendet')
                else:
                    for user in users:
                        if legacy.store.get('market_alert_state:' + user):
                            legacy.store.put('market_alert_state:' + user, {})
            except asyncio.CancelledError:
                raise
            except Exception:
                logging.getLogger('flexpower').warning('Marktpreisalarm-Pruefung fehlgeschlagen; Details ausgeblendet')
            await asyncio.sleep(10)

original_lifespan = app.router.lifespan_context
@asynccontextmanager
async def lifespan(application):
    async with original_lifespan(application):
        task = asyncio.create_task(monitor())
        try:
            yield
        finally:
            task.cancel()
            with suppress(asyncio.CancelledError):
                await task
app.router.lifespan_context = lifespan
