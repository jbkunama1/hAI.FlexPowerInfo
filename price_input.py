from copy import deepcopy
from decimal import Decimal, InvalidOperation

def normalize_tariff_input(value):
    if not isinstance(value, dict):
        raise ValueError('Tarifobjekt erwartet')
    result = deepcopy(value)
    bases = value.get('price_basis')
    if not isinstance(bases, dict):
        raise ValueError('Bitte für jeden Tarifbetrag netto oder brutto angeben (price_basis).')
    try:
        vat = Decimal(str(value.get('vat')))
    except (InvalidOperation, ValueError):
        raise ValueError('Ungültiger Umsatzsteuersatz')
    if not vat.is_finite() or not 0 <= vat <= 100:
        raise ValueError('Umsatzsteuer muss zwischen 0 und 100 liegen')
    factor = 1 + vat / 100

    def net(amount, basis, label):
        if basis not in ('net', 'gross'):
            raise ValueError(f'{label}: Bitte netto oder brutto angeben.')
        try:
            number = Decimal(str(amount))
        except (InvalidOperation, ValueError):
            raise ValueError(f'{label}: Ungültige Zahl')
        if not number.is_finite() or abs(number) > 100000:
            raise ValueError(f'{label}: Zahl außerhalb des Bereichs')
        return str(number if basis == 'net' else number / factor)

    for key in ('energy_ct', 'base_net'):
        result[key] = net(value.get(key), bases.get(key), key)
    if value.get('floor_ct') not in (None, ''):
        result['floor_ct'] = net(value['floor_ct'], bases.get('floor_ct'), 'Energie-Untergrenze')
    parts = value.get('components', [])
    if not isinstance(parts, list) or len(parts) > 50:
        raise ValueError('Maximal 50 Bestandteile')
    result['components'] = []
    for part in parts:
        if not isinstance(part, dict):
            raise ValueError('Ungültiger Tarifbestandteil')
        result['components'].append(dict(part, ct=net(part.get('ct'), part.get('price_basis'), str(part.get('name', 'Bestandteil'))), price_basis='net'))
    result['price_basis'] = {'energy_ct': 'net', 'base_net': 'net', 'floor_ct': 'net'}
    return result
