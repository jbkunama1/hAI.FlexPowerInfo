import os,time,secrets,asyncio
from collections import defaultdict,deque
from urllib.parse import urlsplit
from contextlib import asynccontextmanager,suppress
from fastapi import FastAPI,Request
from fastapi.responses import FileResponse,JSONResponse,RedirectResponse
from mcp.server.fastmcp import FastMCP
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.routing import Route
from core import validate

public_url=os.getenv('PUBLIC_URL','').rstrip('/')
if public_url:
    parsed=urlsplit(public_url)
    if parsed.scheme not in ('http','https') or not parsed.hostname or parsed.path or parsed.query or parsed.fragment or parsed.username:raise RuntimeError('PUBLIC_URL muss eine reine HTTP(S)-Origin sein')
    os.environ.setdefault('ALLOWED_HOSTS',parsed.hostname+',localhost,127.0.0.1')
else:os.environ.setdefault('ALLOWED_HOSTS','*')
import app as legacy
from telegram_service import run

def price_state():
    s=legacy.state()
    return {k:s[k] for k in ('current','tariff_price','rows','source','fetched','stale','configured','units','notice')}

def session_valid(req):
    session=legacy.sessions.get(req.cookies.get('session',''))
    return bool(session and session['expires']>time.time())

mcp=FastMCP('hAI.FlexPowerInfo Authenticated',stateless_http=True,json_response=True)
@mcp.tool()
def get_current_price()->dict:
    """Authenticated estimated electricity price with explicit units."""
    s=price_state();s.pop('rows');s['components']=legacy.state()['tariff']['components'];return s
@mcp.tool()
def get_price_schedule(start_ms:int=0,end_ms:int=0)->dict:
    """Authenticated available source intervals."""
    if start_ms<0 or end_ms<0 or (end_ms and end_ms<=start_ms):raise ValueError('Ungültiger Zeitraum')
    s=price_state();s['rows']=[x for x in s['rows'] if (not start_ms or x['end']>start_ms) and (not end_ms or x['start']<end_ms)]
    return s
@mcp.tool()
def get_tariff()->dict:
    """Read the full editable tariff after bearer authentication. No credentials.

    Stored monetary amounts are normalized NET: energy_ct, floor_ct and
    components[].ct in ct/kWh; base_net in EUR/month. New saved tariffs
    explicitly mark these values with price_basis='net'. Legacy tariffs
    may lack price_basis metadata but their stored amounts are also NET.
    Before submitting user-entered amounts to update_tariff, explicitly
    ask the person entering each amount whether it is net or gross.
    Never infer the basis, including for customer prices.
    """
    return legacy.store.get('tariff',legacy.DEFAULT)
@mcp.tool()
def get_status()->dict:
    """Authenticated freshness, excluding internal errors."""
    s=price_state();return {k:s[k] for k in ('source','fetched','stale','configured')}
@mcp.tool()
def update_tariff(tariff:dict)->dict:
    """WRITE: replace the complete tariff. Read get_tariff first and review
    the exact changes with the user before writing. Clears the tariff's
    checked flag (confirmed=False). Does not alter credentials.

    For EVERY user-entered monetary amount, explicitly ask the person
    entering it: net or gross? No default or inferred basis is allowed,
    including for customer prices. Submit a price_basis object containing
    energy_ct and base_net, plus floor_ct when that amount is not empty.
    Each entry must be exactly 'net' or 'gross'. Every components[] item
    must also include its own price_basis: 'net' or 'gross'. Missing or
    invalid required basis values are rejected by the server.

    Units: energy_ct, floor_ct and components[].ct are ct/kWh; base_net
    is EUR/month, despite the legacy field name accepting either input
    basis. vat and fee_percent are percentages, not monetary amounts.
    Example basis metadata: price_basis={'energy_ct':'gross',
    'base_net':'net','floor_ct':'gross'}; a component can be
    {'name':'Surcharge','ct':'1.19','price_basis':'gross'}.

    Gross input is converted to NET on save using the supplied tariff vat
    percentage. Saved and returned monetary amounts are NET with explicit
    'net' basis metadata. The price calculation then applies VAT once for
    gross output; do not add VAT again to an already gross customer price.
    Existing stored legacy amounts remain NET and must not be silently
    reinterpreted as gross. Unchanged known stored amounts can be submitted
    with explicit 'net' metadata; never use that as a default for new input.
    Separate market-alert thresholds are not changed by this tool and
    remain gross ct/kWh.
    """
    candidate=validate(tariff);candidate['confirmed']=False
    saved=legacy.store.save_tariff(candidate)
    return {'saved':True,'tariff':saved,'notice':'Tarif gespeichert. Vor Verwendung erneut anhand des Vertrags prüfen.'}

mcp_app=mcp.streamable_http_app()
@asynccontextmanager
async def lifespan(app):
    if len(legacy.password)<4:raise RuntimeError('ADMIN_PASSWORD muss mindestens 4 Zeichen haben')
    if legacy.mcp_token and len(legacy.mcp_token)<32:raise RuntimeError('MCP_TOKEN muss mindestens 32 Zeichen haben')
    async with mcp.session_manager.run():
        tasks=[asyncio.create_task(legacy.scheduler()),asyncio.create_task(run(legacy.store,legacy.state))]
        try:yield
        finally:
            for task in tasks:task.cancel()
            for task in tasks:
                with suppress(asyncio.CancelledError):await task
app=FastAPI(lifespan=lifespan,docs_url=None,redoc_url=None,openapi_url=None)
app.add_middleware(TrustedHostMiddleware,allowed_hosts=legacy.allowed_hosts)
hits=defaultdict(deque)
@app.middleware('http')
async def access(req:Request,next):
    path=req.url.path
    is_mcp=path=='/mcp' or path.startswith('/mcp/')
    if is_mcp:
        supplied=req.headers.get('authorization','').encode()
        if not legacy.mcp_token or not secrets.compare_digest(supplied,('Bearer '+legacy.mcp_token).encode()):
            return JSONResponse({'error':'MCP-Token erforderlich'},401,headers={'WWW-Authenticate':'Bearer','Cache-Control':'no-store'})
    origin=req.headers.get('origin')
    configured={x.strip().rstrip('/') for x in os.getenv('ALLOWED_ORIGINS','').split(',') if x.strip()}
    expected=public_url or str(req.base_url).rstrip('/')
    if origin and origin.rstrip('/') not in configured|{expected}:return JSONResponse({'error':'Origin nicht freigegeben'},403)
    if origin:legacy.origins.add(origin.rstrip('/'))
    if path.rstrip('/') in ('/api/public','/public.js','/public.html'):
        return JSONResponse({'error':'Nicht gefunden'},404,headers={'Cache-Control':'no-store'})
    if path.rstrip('/') in ('/admin','/login'):
        return RedirectResponse('/',status_code=303,headers={'Cache-Control':'no-store'})
    if is_mcp:
        now=time.monotonic()
        for key in list(hits):
            while hits[key] and now-hits[key][0]>=60:hits[key].popleft()
            if not hits[key]:hits.pop(key,None)
        key=req.client.host if req.client else 'unknown'
        if key not in hits and len(hits)>=10000:return JSONResponse({'error':'Überlastet'},503)
        if len(hits[key])>=60:return JSONResponse({'error':'Zu viele Anfragen'},429,headers={'Retry-After':'60'})
        hits[key].append(now)
    # Root serves only the UI shell. Every data endpoint still requires a session.
    elif path not in ('/','/api/login','/app.js','/style.css','/health') and not session_valid(req):
        if path.startswith('/api/'):
            return JSONResponse({'error':'Anmeldung erforderlich'},401,headers={'Cache-Control':'no-store'})
        return RedirectResponse('/',status_code=303,headers={'Cache-Control':'no-store'})
    response=await next(req)
    response.headers['Cache-Control']='no-store'
    response.headers['X-Content-Type-Options']='nosniff'
    response.headers['Content-Security-Policy']="default-src 'self'; script-src 'self'; style-src 'self'; frame-ancestors 'none'; base-uri 'none'"
    return response
@app.get('/')
def home():return FileResponse('static/index.html')
class MCPTransport:
    async def __call__(self,scope,receive,send):await mcp.session_manager.handle_request(scope,receive,send)
for path in ('/mcp','/mcp/'):
    app.router.routes.append(Route(path,endpoint=MCPTransport(),methods=['GET','POST','DELETE']))
app.mount('/',legacy.app)
