import os,subprocess,sys,tempfile,unittest

class PasswordPolicyTests(unittest.TestCase):
    def check_start(self,module,password,expected):
        code='''
import importlib,os
from fastapi.testclient import TestClient
module=importlib.import_module(os.environ['TEST_APP_MODULE'])
try:
    with TestClient(module.app) as client:
        assert client.get('/health').status_code==200
        if os.environ['EXPECT_START']=='no':raise AssertionError('Short password accepted')
        r=client.post('/api/login',json={'username':'admin','password':os.environ['ADMIN_PASSWORD']})
        assert r.status_code==200,r.text
except RuntimeError as error:
    if os.environ['EXPECT_START']!='no':raise
    assert str(error)=='ADMIN_PASSWORD muss mindestens 4 Zeichen haben',str(error)
'''
        with tempfile.TemporaryDirectory() as directory:
            env=dict(os.environ,DATA_DIR=directory,TEST_APP_MODULE=module,EXPECT_START=expected,ADMIN_USER='admin',ADMIN_PASSWORD=password,MCP_TOKEN='',MCP_PUBLIC='true',PUBLIC_URL='',ALLOWED_HOSTS='testserver,localhost,127.0.0.1',COOKIE_SECURE='false',TELEGRAM_BOT_TOKEN='')
            r=subprocess.run([sys.executable,'-c',code],env=env,capture_output=True,text=True,timeout=45)
            self.assertEqual(r.returncode,0,r.stdout+r.stderr)
    def test_four_characters_start_and_login(self):
        for module in ('app','gateway'):
            with self.subTest(module=module):self.check_start(module,'abcd','yes')
    def test_short_password_rejected(self):
        for module in ('app','gateway'):
            for password in ('','abc'):
                with self.subTest(module=module,length=len(password)):self.check_start(module,password,'no')
