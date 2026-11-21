import unittest
from copy import deepcopy
from core import DEFAULT
from market_alerts import evaluate, validate_alerts

class MarketAlertTests(unittest.TestCase):
    def setUp(self):
        self.tariff = deepcopy(DEFAULT)
        self.tariff.update(mode='reference', energy_ct='999', vat='0', base_net='999')
        self.config = {'enabled': True, 'lower': '30', 'upper': '42'}

    def run_price(self, price, now=1000, fetched=1000):
        market = {'fetched': fetched, 'rows': [{'start': 999000, 'end': 1001000, 'market_net_ct': str(price)}]}
        return evaluate(market, self.tariff, self.config, now)

    def test_strict_thresholds_and_reference_independence(self):
        for price, band in [('29.99', 'low'), ('30', 'normal'), ('42', 'normal'), ('42.01', 'high'), ('-1', 'low')]:
            with self.subTest(price=price):
                self.assertEqual(self.run_price(price)['band'], band)
        self.assertEqual(self.tariff['mode'], 'reference')

    def test_missing_stale_expired_disabled(self):
        self.assertIsNone(self.run_price(20, now=1001))
        self.assertIsNone(self.run_price(20, now=4000, fetched=1))
        self.assertIsNone(evaluate({}, self.tariff, self.config, 1000))
        self.config['enabled'] = False
        self.assertIsNone(self.run_price(20))

    def test_components_vat_and_no_base(self):
        self.tariff.update(vat='19', components=[{'name': 'Test', 'ct': '10'}])
        self.assertEqual(self.run_price(10)['gross_ct'], '23.80')

    def test_invalid_config(self):
        for value in [{'enabled': True, 'lower': '42', 'upper': '30'}, {'enabled': True, 'lower': 'NaN', 'upper': '42'}, {'enabled': 'yes', 'lower': '30', 'upper': '42'}]:
            with self.assertRaises(ValueError):
                validate_alerts(value)
