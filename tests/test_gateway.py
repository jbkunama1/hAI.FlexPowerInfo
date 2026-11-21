import os,subprocess,sys,unittest,tempfile

class GatewayTests(unittest.TestCase):
    def test_root_login_and_protected_data(self):
        code='''
import os
from fastapi.testclient import TestClient
from gateway import app
with TestClient(app) as c:
    r=c.get('/',follow_redirects=False)
    assert r.status_code==200 and 'location' not in r.headers
    assert 'id="login"' in r.text
    for path in ('/admin','/admin/','/login','/login/'):
        r=c.get(path,follow_redirects=False)
        assert r.status_code==303,(path,r.status_code)
        assert r.headers['location']=='/'
    for path in ('/api/public','/api/public/','/public.js','/public.html'):
        assert c.get(path).status_code==404,path
    assert c.get('/api/status').status_code==401
    assert c.post('/api/tariff',json={}).status_code==401
    for path in ('/mcp','/mcp/'):
        for method in ('GET','POST','DELETE','OPTIONS'):
            for headers in ({},{'Authorization':'Bearer invalid'}):
                r=c.request(method,path,headers=headers)
                assert r.status_code==401,(method,path,r.status_code)
    assert c.get('/',headers={'Origin':'https://untrusted.example'}).status_code==403
    r=c.post('/api/login',json={'username':'admin','password':os.environ['ADMIN_PASSWORD']})
    assert r.status_code==200,r.text
    csrf=r.json()['csrf']
    assert c.get('/',follow_redirects=False).status_code==200
    assert c.get('/api/status').status_code==200
    assert c.get('/api/public').status_code==404
    assert c.post('/api/logout',json={},headers={'X-CSRF-Token':csrf}).status_code==200
    assert c.get('/api/status').status_code==401
    assert c.get('/',follow_redirects=False).status_code==200
'''
        with tempfile.TemporaryDirectory() as directory:
            env=dict(os.environ,DATA_DIR=directory,ADMIN_USER='admin',ADMIN_PASSWORD='test-password-only-12345',MCP_TOKEN='',MCP_PUBLIC='true',PUBLIC_DASHBOARD='true',PUBLIC_URL='',ALLOWED_HOSTS='testserver,localhost,127.0.0.1',ALLOWED_ORIGINS='',COOKIE_SECURE='false',TELEGRAM_BOT_TOKEN='')
            r=subprocess.run([sys.executable,'-c',code],env=env,capture_output=True,text=True,timeout=45)
            self.assertEqual(r.returncode,0,r.stdout+r.stderr)
