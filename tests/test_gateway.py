import os,subprocess,sys,unittest,tempfile

class GatewayTests(unittest.TestCase):
    def test_public_access_and_private_admin(self):
        code='''
from fastapi.testclient import TestClient
from gateway import app
with TestClient(app) as c:
    s=c.get('/api/public');assert s.status_code==200
    assert 'tariff' not in s.json() and 'error' not in s.json()
    assert c.get('/api/status').status_code==401
    assert c.post('/api/tariff',json={}).status_code==401
    for path in ('/mcp','/mcp/'):
        for method in ('GET','POST','DELETE','OPTIONS'):
            for headers in ({},{'Authorization':'Bearer invalid'}):
                r=c.request(method,path,headers=headers)
                assert r.status_code==401,(method,path,r.status_code)
    assert c.get('/api/public',headers={'Origin':'https://untrusted.example'}).status_code==403
'''
        with tempfile.TemporaryDirectory() as directory:
            env=dict(os.environ,DATA_DIR=directory,ADMIN_USER='admin',ADMIN_PASSWORD='test-password-only-12345',MCP_TOKEN='',MCP_PUBLIC='true',PUBLIC_DASHBOARD='true',PUBLIC_URL='',ALLOWED_HOSTS='testserver,localhost,127.0.0.1',ALLOWED_ORIGINS='',TELEGRAM_BOT_TOKEN='')
            r=subprocess.run([sys.executable,'-c',code],env=env,capture_output=True,text=True,timeout=45)
            self.assertEqual(r.returncode,0,r.stdout+r.stderr)
