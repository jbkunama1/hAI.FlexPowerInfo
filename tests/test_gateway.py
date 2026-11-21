import os,tempfile,unittest
os.environ['DATA_DIR']=tempfile.mkdtemp()
os.environ['ADMIN_PASSWORD']='test-password-only-12345'
os.environ['MCP_TOKEN']=''
os.environ['MCP_PUBLIC']='true'
os.environ['PUBLIC_DASHBOARD']='true'
os.environ['PUBLIC_URL']=''
os.environ['ALLOWED_HOSTS']='testserver,localhost,127.0.0.1'
os.environ['TELEGRAM_BOT_TOKEN']=''
from fastapi.testclient import TestClient
from gateway import app
class GatewayTests(unittest.TestCase):
    def test_public_access_and_private_admin(self):
        with TestClient(app) as c:
            self.assertEqual(c.get('/').status_code,200)
            s=c.get('/api/public');self.assertEqual(s.status_code,200)
            self.assertNotIn('tariff',s.json());self.assertNotIn('error',s.json())
            self.assertEqual(c.get('/api/status').status_code,401)
            self.assertEqual(c.post('/api/tariff',json={}).status_code,401)
            self.assertEqual(c.get('/api/public',headers={'Origin':'https://untrusted.example'}).status_code,403)
            h={'Accept':'application/json, text/event-stream'}
            result=c.post('/mcp',headers=h,json={'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2025-03-26','capabilities':{},'clientInfo':{'name':'test','version':'1'}}})
            self.assertEqual(result.status_code,200)
            result=c.post('/mcp',headers=h,json={'jsonrpc':'2.0','id':2,'method':'tools/call','params':{'name':'get_tariff','arguments':{}}})
            self.assertEqual(result.status_code,200);self.assertFalse(result.json()['result'].get('isError',False))
