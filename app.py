import os, asyncio, secrets, time, hashlib, json, logging
from contextlib import asynccontextmanager, suppress
from pathlib import Path
import httpx
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from mcp.server.fastmcp import FastMCP
from starlette.middleware.trustedhost import TrustedHostMiddleware
from core import Store, DEFAULT, snapshot, parse_market, dec

store=Store(Path(os.getenv('DATA_DIR','/data'))/'flexpower.db')
password=os.getenv('ADMIN_PASSWORD','')
mcp_token=os.getenv('MCP_TOKEN','')
user=os.getenv('ADMIN_USER','admin')
allowed_hosts=[x.strip() for x in os.getenv('ALLOWED_HOSTS','localhost,127.0.0.1').split(',') if x.strip()]
origins={x.strip().rstrip('/') for x in os.getenv('ALLOWED_ORIGINS','http://localhost:8098,http://127.0.0.1:8098').split(',') if x.strip()}
sessions={};attempts={};refresh_lock=asyncio.Lock()
log=logging.getLogger('flexpower')
salt=secrets.token_bytes(16)
expected=hashlib.scrypt(password.encode(),salt=salt,n=16384,r=8,p=1)

def state():return snapshot(store)
async def refresh():
    async with refresh_lock:
        if time.time()-store.get('last_attempt',0)<900:return
        store.put('last_attempt',time.time())
        try:
            async with httpx.AsyncClient(timeout=20) as c:
                response=await c.get('https://api.awattar.de/v1/marketdata');response.raise_for_status()
                rows=parse_market(response.json())
            store.put('market',{'fetched':time.time(),'rows':rows});store.put('error',None)
        except Exception:
            store.put('error','Marktdatenabruf fehlgeschlagen; letzte erfolgreiche Daten bleiben erhalten.')
            log.warning('Marktdatenabruf fehlgeschlagen')

def price_text():
    x=state();p=x['current']['price'] if x['current'] else x['tariff_price']
    if not p:return 'Kein aktuelles Preisintervall verfügbar.'
    parts='\n'.join(f"{a['name']}: {a['ct']} ct/kWh netto" for a in x['tariff']['components'])
    return f"{x['tariff']['name']}\nGeschätzt: {dec(p['gross_ct']):.3f} ct/kWh brutto\nEnergie: {p['energy_net_ct']} ct/kWh netto\n{parts}\nService: {p['fee_net_ct']} ct/kWh netto\nMwSt.: {p['vat_ct']} ct/kWh\nGrundpreis: {p['base_gross_eur']} EUR/Monat brutto\nTarif geprüft: {x['configured']} · Marktdaten veraltet: {x['stale']}"

async def telegram():
    token=os.getenv('TELEGRAM_BOT_TOKEN','')
    users={x.strip() for x in os.getenv('TELEGRAM_USER_IDS','').split(',') if x.strip()}
    chats={x.strip() for x in os.getenv('TELEGRAM_CHAT_IDS','').split(',') if x.strip()}
    if not(token and users and chats):return
    offset=store.get('telegram_offset',0)
    async with httpx.AsyncClient(timeout=40) as c:
        while True:
            try:
                r=await c.post(f'https://api.telegram.org/bot{token}/getUpdates',json={'offset':offset,'timeout':25,'allowed_updates':['message']})
                r.raise_for_status();payload=r.json()
                if not payload.get('ok'):raise ValueError('Telegram refusal')
                for update in payload['result']:
                    msg=update.get('message',{});sender=str(msg.get('from',{}).get('id',''));chat=str(msg.get('chat',{}).get('id',''))
                    offset=update['update_id']+1
                    if sender in users and chat in chats:
                        cmd=msg.get('text','').split(' ')[0].split('@')[0]
                        if cmd=='/preis':text=price_text()
                        elif cmd=='/tarif':text=json.dumps(state()['tariff'],ensure_ascii=False,indent=2)
                        elif cmd=='/status':
                            x=state();text=json.dumps({k:x[k] for k in ('fetched','stale','error','configured')},ensure_ascii=False)
                        elif cmd=='/verlauf':
                            from datetime import datetime
                            from zoneinfo import ZoneInfo
                            x=state();rows=[a for a in x['rows'] if a['end']>time.time()*1000][:24]
                            text='Nächste verfügbare Intervalle (Europe/Berlin):\n'+'\n'.join(datetime.fromtimestamp(a['start']/1000,ZoneInfo('Europe/Berlin')).isoformat()+f" → {dec(a['price']['gross_ct']):.3f} ct/kWh brutto" for a in rows)
                        else:text='/preis · /verlauf · /tarif · /status · /hilfe'
                        out=await c.post(f'https://api.telegram.org/bot{token}/sendMessage',json={'chat_id':chat,'text':text[:4000]});out.raise_for_status()
                    store.put('telegram_offset',offset)
            except asyncio.CancelledError:raise
            except Exception:
                log.warning('Telegram-Kommunikation fehlgeschlagen');await asyncio.sleep(10)

async def scheduler():
    while True:
        try:
            s=store.get('tariff',DEFAULT)
            if s['auto_refresh'] and time.time()-store.get('last_attempt',0)>=s['refresh_minutes']*60:await refresh()
        except Exception:log.warning('Scheduler-Zyklus fehlgeschlagen')
        await asyncio.sleep(10)

mcp=FastMCP('hAI.FlexPowerInfo',stateless_http=True,json_response=True)
@mcp.tool()
def get_current_price()->dict:
    x=state();return {k:x[k] for k in ('current','tariff_price','tariff','source','fetched','stale','configured','units','notice')}
@mcp.tool()
def get_price_schedule(start_ms:int=0,end_ms:int=0)->dict:
    x=state();x['rows']=[a for a in x['rows'] if (not start_ms or a['end']>start_ms) and (not end_ms or a['start']<end_ms)]
    return {k:x[k] for k in ('rows','source','fetched','stale','configured','units','notice')}
@mcp.tool()
def get_tariff()->dict:return store.get('tariff',DEFAULT)
@mcp.tool()
def get_status()->dict:
    x=state();return {k:x[k] for k in ('source','fetched','stale','error','configured')}
mcp_app=mcp.streamable_http_app()

@asynccontextmanager
async def lifespan(app):
    if len(password)<4:raise RuntimeError('ADMIN_PASSWORD muss mindestens 4 Zeichen haben')
    if mcp_token and len(mcp_token)<32:raise RuntimeError('MCP_TOKEN muss mindestens 32 Zeichen haben')
    async with mcp.session_manager.run():
        tasks=[asyncio.create_task(scheduler()),asyncio.create_task(telegram())]
        try:yield
        finally:
            for t in tasks:t.cancel()
            for t in tasks:
                with suppress(asyncio.CancelledError):await t

app=FastAPI(lifespan=lifespan,docs_url=None,redoc_url=None,openapi_url=None)
app.add_middleware(TrustedHostMiddleware,allowed_hosts=allowed_hosts)

@app.middleware('http')
async def security(req,call_next):
    path=req.url.path
    if req.method not in ('GET','HEAD') and path!='/health':
        origin=req.headers.get('origin')
        if origin and origin.rstrip('/') not in origins:return JSONResponse({'error':'Origin nicht freigegeben'},403)
    if path=='/mcp' or path.startswith('/mcp/'):
        auth=req.headers.get('authorization','')
        if not mcp_token or not secrets.compare_digest(auth.encode(),('Bearer '+mcp_token).encode()):return JSONResponse({'error':'MCP-Zugang erforderlich'},401,headers={'WWW-Authenticate':'Bearer'})
    elif path.startswith('/api/') and path!='/api/login':
        sid=req.cookies.get('session','');session=sessions.get(sid)
        if not session or session['expires']<time.time():
            sessions.pop(sid,None);return JSONResponse({'error':'Anmeldung erforderlich'},401)
        if req.method not in ('GET','HEAD') and not secrets.compare_digest(req.headers.get('x-csrf-token','').encode(),session['csrf'].encode()):return JSONResponse({'error':'CSRF-Prüfung fehlgeschlagen'},403)
    length=req.headers.get('content-length')
    if length and (not length.isdigit() or int(length)>65536):return JSONResponse({'error':'Anfrage zu groß'},413)
    response=await call_next(req)
    response.headers['Cache-Control']='no-store'
    response.headers['X-Content-Type-Options']='nosniff'
    response.headers['Content-Security-Policy']="default-src 'self'; script-src 'self'; style-src 'self'; frame-ancestors 'none'; base-uri 'none'"
    return response

@app.get('/health')
def health():return {'ok':True}
@app.get('/')
def index():return FileResponse('static/index.html')
@app.get('/app.js')
def js():return FileResponse('static/app.js',media_type='text/javascript')
@app.get('/style.css')
def css():return FileResponse('static/style.css',media_type='text/css')
@app.post('/api/login')
async def login(req:Request):
    key=req.client.host if req.client else 'unknown';now=time.time()
    for k in list(attempts):
        attempts[k]=[t for t in attempts[k] if now-t<300]
        if not attempts[k]:attempts.pop(k,None)
    times=attempts.setdefault(key,[])
    if len(times)>=5:raise HTTPException(429,'Zu viele Versuche. Fünf Minuten warten.')
    times.append(now)
    if len(attempts)>10000:raise HTTPException(503,'Anmeldungen vorübergehend begrenzt')
    data=await req.json()
    submitted=str(data.get('password',''))
    if len(submitted)>1024:raise HTTPException(401,'Ungültige Anmeldung')
    digest=await asyncio.to_thread(hashlib.scrypt,submitted.encode(),salt=salt,n=16384,r=8,p=1)
    if not secrets.compare_digest(str(data.get('username','')).encode(),user.encode()) or not secrets.compare_digest(digest,expected):raise HTTPException(401,'Ungültige Anmeldung')
    for sid in list(sessions):
        if sessions[sid]['expires']<now:sessions.pop(sid,None)
    if len(sessions)>=1000:raise HTTPException(503,'Zu viele Sitzungen')
    sid=secrets.token_urlsafe(32);csrf=secrets.token_urlsafe(32)
    sessions[sid]={'csrf':csrf,'expires':now+28800}
    response=JSONResponse({'csrf':csrf});response.set_cookie('session',sid,httponly=True,secure=os.getenv('COOKIE_SECURE','true').lower()=='true',samesite='strict',max_age=28800)
    return response
@app.post('/api/logout')
def logout(req:Request):
    sessions.pop(req.cookies.get('session',''),None);res=JSONResponse({'ok':True});res.delete_cookie('session');return res
@app.get('/api/status')
def status(req:Request):
    return dict(state(),csrf=sessions[req.cookies['session']]['csrf'])
@app.post('/api/tariff')
async def tariff(req:Request):
    try:return store.save_tariff(await req.json())
    except (ValueError,KeyError,TypeError) as e:raise HTTPException(400,str(e))
@app.post('/api/refresh')
async def fetch():await refresh();return state()
app.mount('/',mcp_app)
