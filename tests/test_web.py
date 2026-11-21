import os,subprocess,sys,tempfile,unittest

class WebTests(unittest.TestCase):
    def isolated(self,code):
        with tempfile.TemporaryDirectory() as directory:
            env=dict(os.environ,DATA_DIR=directory,ADMIN_USER='admin',ADMIN_PASSWORD='test-password-only-12345',MCP_TOKEN='test-mcp-token-only-12345678901234567890',PUBLIC_URL='',COOKIE_SECURE='false',ALLOWED_HOSTS='testserver,localhost,127.0.0.1',ALLOWED_ORIGINS='',TELEGRAM_BOT_TOKEN='')
            r=subprocess.run([sys.executable,'-c',code],env=env,capture_output=True,text=True,timeout=45)
            self.assertEqual(r.returncode,0,r.stdout+r.stderr)
    def test_auth_and_csrf(self):
        self.isolated('''
import os
from fastapi.testclient import TestClient
from gateway import app
with TestClient(app) as c:
    assert c.get('/health').status_code==200
    assert c.get('/admin',follow_redirects=False).status_code==303
    assert c.get('/api/public').status_code==404
    assert c.get('/api/status').status_code==401
    assert c.post('/mcp',json={}).status_code==401
    r=c.post('/api/login',json={'username':'admin','password':os.environ['ADMIN_PASSWORD']})
    assert r.status_code==200,r.text
    csrf=r.json()['csrf']
    assert c.get('/admin').status_code==200
    assert c.get('/api/status').status_code==200
    assert c.post('/api/logout',json={}).status_code==403
    assert c.post('/api/logout',json={},headers={'X-CSRF-Token':csrf}).status_code==200
    assert c.get('/api/status').status_code==401
''')
    def test_mcp_initialize_and_tools(self):
        self.isolated('''
import os
from fastapi.testclient import TestClient
from gateway import app
h={'Authorization':'Bearer '+os.environ['MCP_TOKEN'],'Accept':'application/json, text/event-stream'}
with TestClient(app) as c:
    for path in ('/mcp','/mcp/'):
        assert c.post(path,json={}).status_code==401
        r=c.post(path,headers=h,json={'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2025-03-26','capabilities':{},'clientInfo':{'name':'test','version':'1'}}},follow_redirects=False)
        assert r.status_code==200,r.text
        r=c.post(path,headers=h,json={'jsonrpc':'2.0','id':2,'method':'tools/list','params':{}})
        assert r.status_code==200,r.text
        assert 'get_current_price' in {x['name'] for x in r.json()['result']['tools']}
        r=c.post(path,headers=h,json={'jsonrpc':'2.0','id':3,'method':'tools/call','params':{'name':'get_status','arguments':{}}})
        assert r.status_code==200,r.text
        assert not r.json()['result'].get('isError',False),r.text
''')
