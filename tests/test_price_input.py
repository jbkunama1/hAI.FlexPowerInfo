import unittest
from copy import deepcopy
from decimal import Decimal
from core import DEFAULT, validate, calculate

class PriceBasisTests(unittest.TestCase):
    def tariff(self):
        s=deepcopy(DEFAULT)
        s.update(mode='fixed', energy_ct='11.9', base_net='11.9', floor_ct='-11.9', price_basis={'energy_ct':'gross','base_net':'gross','floor_ct':'gross'}, components=[{'name':'Zuschlag','ct':'1.19','price_basis':'gross'}])
        return s

    def test_gross_normalized_once(self):
        s=validate(self.tariff())
        self.assertEqual(Decimal(s['energy_ct']),Decimal('10'))
        self.assertEqual(Decimal(s['base_net']),Decimal('10'))
        self.assertEqual(Decimal(s['floor_ct']),Decimal('-10'))
        self.assertEqual(Decimal(s['components'][0]['ct']),Decimal('1'))
        self.assertEqual(validate(s),s)
        self.assertEqual(Decimal(calculate(0,s)['gross_ct']),Decimal('13.09'))

    def test_missing_basis_rejected(self):
        with self.assertRaises(ValueError): validate(deepcopy(DEFAULT))
        s=self.tariff();s['components'][0].pop('price_basis')
        with self.assertRaises(ValueError): validate(s)

    def test_zero_tax_and_negative_energy(self):
        s=self.tariff();s.update(vat='0',energy_ct='-5',floor_ct=None,components=[])
        self.assertEqual(Decimal(calculate(0,validate(s))['gross_ct']),Decimal('-5'))

    def test_legacy_calculation_unchanged(self):
        s=deepcopy(DEFAULT);s.update(mode='fixed',energy_ct='10')
        self.assertEqual(Decimal(calculate(0,s)['gross_ct']),Decimal('11.9'))

if __name__=='__main__': unittest.main()
