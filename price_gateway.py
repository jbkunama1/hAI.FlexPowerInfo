import asyncio, logging, os, secrets, time
from contextlib import asynccontextmanager, suppress
from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from starlette.middleware.trustedhost import TrustedHostMiddleware
from alert_gateway import app as protected_app, legacy
from market_alerts import evaluate
from core import dec

def read_token():
    token = os.getenv('PRICE_READ_TOKEN', '')
    if not 32 <= len(token) <= 256 or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_' for c in token):
        return ''
    if token in (legacy.mcp_token, legacy.password):
        return ''
    return token

def response(text, status=200):
    return PlainTextResponse(text, status_code=status, headers={'Cache-Control': 'no-store', 'Referrer-Policy': 'no-referrer', 'X-Content-Type-Options': 'nosniff', 'Content-Security-Policy': "default-src 'none'; frame-ancestors 'none'"})

async def refresh_prices():
    while True:
        try:
            if read_token():
                await legacy.refresh()
        except asyncio.CancelledError:
            raise
        except Exception:
            logging.getLogger('flexpower').warning('Preisexport-Aktualisierung fehlgeschlagen; Details ausgeblendet')
        await asyncio.sleep(30)

@asynccontextmanager
async def lifespan(application):
    async with protected_app.router.lifespan_context(protected_app):
        task = asyncio.create_task(refresh_prices())
        try:
            yield
        finally:
            task.cancel()
            with suppress(asyncio.CancelledError):
                await task

app = FastAPI(lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=legacy.allowed_hosts)

@app.get('/price.txt')
async def price(request: Request):
    expected = read_token()
    supplied = request.query_params.getlist('token')
    if not expected or len(supplied) != 1 or len(supplied[0]) > 256 or not secrets.compare_digest(supplied[0].encode(), expected.encode()):
        return response('Unauthorized', 401)
    try:
        result = evaluate(legacy.store.get('market', {}), legacy.store.get('tariff', legacy.DEFAULT), {'enabled': True, 'lower': '30', 'upper': '42'}, time.time())
        if result is None:
            return response('Unavailable', 503)
        return response(format(dec(result['gross_ct']), 'f'))
    except Exception:
        logging.getLogger('flexpower').warning('Preisexport nicht verfuegbar; Details ausgeblendet')
        return response('Unavailable', 503)

app.mount('/', protected_app)
