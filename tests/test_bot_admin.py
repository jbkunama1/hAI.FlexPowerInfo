import unittest,struct
from copy import deepcopy
from core import DEFAULT
from bot_visuals import chart_png
from telegram_service import is_admin,edited,text_for

class BotAdminTests(unittest.TestCase):
    def test_private_admin(self):
        self.assertTrue(is_admin({'from':{'id':42},'chat':{'type':'private'}},{'42'}))
        self.assertFalse(is_admin({'from':{'id':42},'chat':{'type':'group'}},{'42'}))
        self.assertFalse(is_admin({'from':{'id':43},'chat':{'type':'private'}},{'42'}))
    def test_edit_validation(self):
        s=deepcopy(DEFAULT);self.assertEqual(edited(s,'vat','7,5')['vat'],'7.5');self.assertEqual(s['vat'],'19')
        for field,value in [('vat','-1'),('vat','NaN'),('refresh_minutes','1'),('name','foo')]:
            with self.assertRaises(ValueError):edited(s,field,value)
    def test_png(self):
        rows=[{'start':0,'end':900000,'price':{'gross_ct':'-5'}},{'start':900000,'end':1800000,'price':{'gross_ct':'25'}}]
        data=chart_png(rows);self.assertEqual(data[:8],b'\x89PNG\r\n\x1a\n');self.assertEqual(struct.unpack('!II',data[16:24]),(800,300))
        with self.assertRaises(ValueError):chart_png([])
    def test_welcome(self):
        state=lambda:{'current':None,'tariff_price':None,'configured':False}
        self.assertIn('Willkommen',text_for('/start',state))
        self.assertIn('highfishAI',text_for('/start',state))
