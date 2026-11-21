import json,os,subprocess,sys,unittest

class GatewayTests(unittest.TestCase):
    def test_public_access_and_private_admin(self):
        code='''
import json
from fastapi.testclient import TestClient
from gateway import app
with TestClient(app) as c:
    assert c.get('/').status_code==200
    s=c.get('/api/public');assert s.status_code==200
    assert 'tariff' not in s.json() and 'error' not in s.json()
    assert c.get('/api/status').status_code==401
    assert c.post('/api/tariff',json={}).status_code==401
    assert c.get('/api/public',headers={'Origin':'https://untrusted.example'}).status_code==403
    h={'Accept':'application/json, text/event-stream'}
    for path in ('/mcp','/mcp/'):
        r=c.post(path,headers=h,json={'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2025-03-26','capabilities':{},'clientInfo':{'name':'test','version':'1'}}},follow_redirects=False)
        assert r.status_code==200,(path,r.status_code,r.text)
        assert 'result' in r.json(),r.text
        r=c.post(path,headers=h,json={'jsonrpc':'2.0','id':2,'method':'tools/list','params':{}})
        assert r.status_code==200,r.text
        assert {x['name'] for x in r.json()['result']['tools']}=={'get_current_price','get_price_schedule','get_tariff','get_status'}
        r=c.post(path,headers=h,json={'jsonrpc':'2.0','id':3,'method':'tools/call','params':{'name':'get_tariff','arguments':{}}})
        assert r.status_code==200,r.text
        result=r.json()['result'];assert not result.get('isError',False),result
        data=json.loads(result['content'][0]['text'])
        assert 'name' not in data and 'error' not in data
'''
        import tempfile
        with tempfile.TemporaryDirectory() as directory:
            env=dict(os.environ,DATA_DIR=directory,ADMIN_USER='admin',ADMIN_PASSWORD='test-password-only-12345',MCP_TOKEN='',MCP_PUBLIC='true',PUBLIC_DASHBOARD='true',PUBLIC_URL='',ALLOWED_HOSTS='testserver,localhost,127.0.0.1',ALLOWED_ORIGINS='',TELEGRAM_BOT_TOKEN='')
            result=subprocess.run([sys.executable,'-c',code],env=env,capture_output=True,text=True,timeout=45)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
