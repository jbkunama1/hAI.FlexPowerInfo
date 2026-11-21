import os,tempfile,unittest
os.environ['DATA_DIR']=tempfile.mkdtemp()
os.environ['ADMIN_PASSWORD']='test-password-only-12345'
os.environ['MCP_TOKEN']='test-mcp-token-only-12345678901234567890'
os.environ['COOKIE_SECURE']='false'
os.environ['ALLOWED_HOSTS']='testserver,localhost,127.0.0.1'
os.environ['TELEGRAM_BOT_TOKEN']=''
from fastapi.testclient import TestClient
from app import app
class WebTests(unittest.TestCase):
    def test_auth_and_csrf(self):
        with TestClient(app) as c:
            self.assertEqual(c.get('/health').status_code,200)
            self.assertEqual(c.get('/').status_code,200)
            self.assertEqual(c.get('/api/status').status_code,401)
            self.assertEqual(c.post('/mcp',json={}).status_code,401)
            r=c.post('/api/login',json={'username':'admin','password':os.environ['ADMIN_PASSWORD']})
            self.assertEqual(r.status_code,200);csrf=r.json()['csrf']
            self.assertEqual(c.get('/api/status').status_code,200)
            self.assertEqual(c.post('/api/logout',json={}).status_code,403)
            self.assertEqual(c.post('/api/logout',json={},headers={'X-CSRF-Token':csrf}).status_code,200)
            self.assertEqual(c.get('/api/status').status_code,401)
    def test_mcp_initialize_and_tools(self):
        headers={'Authorization':'Bearer '+os.environ['MCP_TOKEN'],'Accept':'application/json, text/event-stream'}
        with TestClient(app) as c:
            r=c.post('/mcp',headers=headers,json={'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2025-03-26','capabilities':{},'clientInfo':{'name':'test','version':'1'}}})
            self.assertEqual(r.status_code,200);self.assertIn('result',r.json())
            r=c.post('/mcp',headers=headers,json={'jsonrpc':'2.0','id':2,'method':'tools/list','params':{}})
            self.assertEqual(r.status_code,200)
            self.assertIn('get_current_price',{x['name'] for x in r.json()['result']['tools']})
            r=c.post('/mcp',headers=headers,json={'jsonrpc':'2.0','id':3,'method':'tools/call','params':{'name':'get_status','arguments':{}}})
            self.assertEqual(r.status_code,200);self.assertFalse(r.json()['result'].get('isError',False))
if __name__=='__main__':unittest.main()
