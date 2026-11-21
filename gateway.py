import os,time,secrets,asyncio
from collections import defaultdict,deque
from urllib.parse import urlsplit
from contextlib import asynccontextmanager,suppress
from fastapi import FastAPI,Request
from fastapi.responses import FileResponse,JSONResponse
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
public_web=os.getenv('PUBLIC_DASHBOARD','true').lower()=='true'

def public_state():
    s=legacy.state()
    return {k:s[k] for k in ('current','tariff_price','rows','source','fetched','stale','configured','units','notice')}
def public_tariff():
    s=legacy.state()['tariff']
    return {k:s[k] for k in ('mode','vat','components','base_net')}

mcp=FastMCP('hAI.FlexPowerInfo Authenticated',stateless_http=True,json_response=True)
@mcp.tool()
def get_current_price()->dict:
    """Authenticated estimated electricity price with explicit units."""
    s=public_state();s.pop('rows');s['components']=public_tariff()['components'];return s
@mcp.tool()
def get_price_schedule(start_ms:int=0,end_ms:int=0)->dict:
    """Authenticated available source intervals."""
    if start_ms<0 or end_ms<0 or (end_ms and end_ms<=start_ms):raise ValueError('Ungültiger Zeitraum')
    s=public_state();s['rows']=[x for x in s['rows'] if (not start_ms or x['end']>start_ms) and (not end_ms or x['start']<end_ms)]
    return s
@mcp.tool()
def get_tariff()->dict:
    """Read the full editable tariff after bearer authentication. No credentials."""
    return legacy.store.get('tariff',legacy.DEFAULT)
@mcp.tool()
def get_status()->dict:
    """Authenticated freshness, excluding internal errors."""
    s=public_state();return {k:s[k] for k in ('source','fetched','stale','configured')}
@mcp.tool()
def update_tariff(tariff:dict)->dict:
    """WRITE: replace the complete tariff. Read get_tariff first; review changes with the user. All numeric tariff inputs are NET. Clears the tariff's checked flag. Does not alter credentials."""
    candidate=validate(tariff)
    candidate['confirmed']=False
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
    # Authenticate EVERY MCP method before routing or exposing protocol information.
    # MCP_PUBLIC is intentionally ignored, including existing deployments that set it true.
    if is_mcp:
        supplied=req.headers.get('authorization','').encode()
        if not legacy.mcp_token or not secrets.compare_digest(supplied,('Bearer '+legacy.mcp_token).encode()):
            return JSONResponse({'error':'MCP-Token erforderlich'},401,headers={'WWW-Authenticate':'Bearer','Cache-Control':'no-store'})
    origin=req.headers.get('origin')
    configured={x.strip().rstrip('/') for x in os.getenv('ALLOWED_ORIGINS','').split(',') if x.strip()}
    expected=public_url or str(req.base_url).rstrip('/')
    if origin and origin.rstrip('/') not in configured|{expected}:return JSONResponse({'error':'Origin nicht freigegeben'},403)
    if origin:legacy.origins.add(origin.rstrip('/'))
    if is_mcp or path=='/api/public':
        now=time.monotonic()
        for key in list(hits):
            while hits[key] and now-hits[key][0]>=60:hits[key].popleft()
            if not hits[key]:hits.pop(key,None)
        key=req.client.host if req.client else 'unknown'
        if key not in hits and len(hits)>=10000:return JSONResponse({'error':'Überlastet'},503)
        if len(hits[key])>=60:return JSONResponse({'error':'Zu viele Anfragen'},429,headers={'Retry-After':'60'})
        hits[key].append(now)
    response=await next(req)
    response.headers['Cache-Control']='no-store'
    response.headers['X-Content-Type-Options']='nosniff'
    response.headers['Content-Security-Policy']="default-src 'self'; script-src 'self'; style-src 'self'; frame-ancestors 'none'; base-uri 'none'"
    return response
@app.get('/')
def home():return FileResponse('static/public.html' if public_web else 'static/index.html')
@app.get('/admin')
def admin():return FileResponse('static/index.html')
@app.get('/public.js')
def javascript():return FileResponse('static/public.js',media_type='text/javascript')
@app.get('/api/public')
def prices():
    if not public_web:return JSONResponse({'error':'Öffentliche Ansicht deaktiviert'},404)
    return dict(public_state(),components=public_tariff()['components'])
class MCPTransport:
    async def __call__(self,scope,receive,send):await mcp.session_manager.handle_request(scope,receive,send)
for path in ('/mcp','/mcp/'):
    app.router.routes.append(Route(path,endpoint=MCPTransport(),methods=['GET','POST','DELETE']))
app.mount('/',legacy.app)
