import unittest,tempfile
from pathlib import Path
from copy import deepcopy
from core import DEFAULT,validate,calculate,parse_market,Store,snapshot
class CoreTests(unittest.TestCase):
    def tariff(self,**kw):return dict(deepcopy(DEFAULT),**kw)
    def test_price(self):self.assertEqual(calculate(5,self.tariff(components=[{'name':'Z','ct':'10'}],fee_percent='10'))['gross_ct'],'18.445')
    def test_negative(self):self.assertEqual(calculate(-10,DEFAULT)['gross_ct'],'-11.9')
    def test_floor(self):self.assertEqual(calculate(-10,self.tariff(floor_ct='0'))['gross_ct'],'0')
    def test_fixed(self):self.assertEqual(calculate(1,self.tariff(mode='fixed',energy_ct='20')),calculate(100,self.tariff(mode='fixed',energy_ct='20')))
    def test_reference(self):self.assertEqual(calculate(1,self.tariff(mode='reference',energy_ct='10'))['gross_ct'],'11.9')
    def test_subtotal(self):self.assertEqual(calculate(5,self.tariff(components=[{'name':'Z','ct':'10'}],fee_percent='10',fee_basis='subtotal'))['fee_net_ct'],'1.5')
    def test_base(self):self.assertEqual(calculate(0,self.tariff(base_net='10'))['base_gross_eur'],'11.90')
    def test_validation(self):
        for kw in ({'vat':'NaN'},{'vat':'-1'},{'mode':'foo'},{'refresh_minutes':1},{'refresh_minutes':15.5},{'confirmed':'yes'}):
            with self.assertRaises(ValueError):validate(self.tariff(**kw))
    def test_conversion(self):self.assertEqual(parse_market({'data':[{'start_timestamp':0,'end_timestamp':900000,'marketprice':100,'unit':'EUR/MWh'}]})[0]['market_net_ct'],'10')
    def test_overlap(self):
        x={'start_timestamp':0,'end_timestamp':900000,'marketprice':100,'unit':'EUR/MWh'}
        with self.assertRaises(ValueError):parse_market({'data':[x,x]})
    def test_store(self):
        with tempfile.TemporaryDirectory() as d:
            s=Store(Path(d)/'test.db');s.save_tariff(self.tariff(name='Test'));self.assertEqual(s.get('tariff')['name'],'Test')
    def test_expired(self):
        with tempfile.TemporaryDirectory() as d:
            s=Store(Path(d)/'test.db');s.put('market',{'fetched':1,'rows':[{'start':0,'end':900000,'market_net_ct':'5'}]})
            self.assertIsNone(snapshot(s,now=1000)['current']);self.assertIsNotNone(snapshot(s,now=500)['current']);self.assertTrue(snapshot(s,now=5000)['stale'])
if __name__=='__main__':unittest.main()
