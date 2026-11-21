import os,subprocess,sys,tempfile,unittest

class MCPWriteTests(unittest.TestCase):
    def test_token_required_for_read_and_write(self):
        code='''
import os,json
from fastapi.testclient import TestClient
from gateway import app
from core import DEFAULT
h={'Authorization':'Bearer '+os.environ['MCP_TOKEN'],'Accept':'application/json, text/event-stream'}
with TestClient(app) as c:
    for path in ('/mcp','/mcp/'):
        for headers in ({},{'Authorization':'Bearer wrong'}):
            r=c.post(path,headers=headers,json={'jsonrpc':'2.0','id':1,'method':'tools/call','params':{'name':'update_tariff','arguments':{'tariff':dict(DEFAULT,name='UNAUTHORIZED')}}})
            assert r.status_code==401,r.text
        r=c.post(path,headers=h,json={'jsonrpc':'2.0','id':2,'method':'initialize','params':{'protocolVersion':'2025-03-26','capabilities':{},'clientInfo':{'name':'test','version':'1'}}})
        assert r.status_code==200,r.text
        def tool(name,args):
            r=c.post(path,headers=h,json={'jsonrpc':'2.0','id':3,'method':'tools/call','params':{'name':name,'arguments':args}})
            assert r.status_code==200,r.text
            return r.json()['result']
        original=tool('get_tariff',{});assert not original.get('isError',False),original
        assert json.loads(original['content'][0]['text'])['name']!='UNAUTHORIZED'
        invalid=tool('update_tariff',{'tariff':dict(DEFAULT,vat='NaN')})
        assert invalid.get('isError',False),invalid
        changed=tool('update_tariff',{'tariff':dict(DEFAULT,name='MCP test',confirmed=True)})
        assert not changed.get('isError',False),changed
        data=json.loads(tool('get_tariff',{})['content'][0]['text'])
        assert data['name']=='MCP test' and data['confirmed'] is False,data
'''
        with tempfile.TemporaryDirectory() as directory:
            env=dict(os.environ,DATA_DIR=directory,ADMIN_PASSWORD='test-password-only-12345',MCP_TOKEN='test-mcp-token-only-12345678901234567890',MCP_PUBLIC='true',PUBLIC_URL='',ALLOWED_HOSTS='testserver,localhost,127.0.0.1',ALLOWED_ORIGINS='',TELEGRAM_BOT_TOKEN='')
            r=subprocess.run([sys.executable,'-c',code],env=env,capture_output=True,text=True,timeout=45)
            self.assertEqual(r.returncode,0,r.stdout+r.stderr)
