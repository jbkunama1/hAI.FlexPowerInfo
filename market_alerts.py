from copy import deepcopy
from core import calculate, dec

DEFAULT_ALERTS = {'enabled': False, 'lower': '30', 'upper': '42'}

def validate_alerts(value):
    if not isinstance(value, dict) or not isinstance(value.get('enabled'), bool):
        raise ValueError('Alarmobjekt mit enabled-Schalter erwartet')
    lower, upper = dec(value.get('lower')), dec(value.get('upper'))
    if lower >= upper:
        raise ValueError('Untergrenze muss kleiner als Obergrenze sein')
    return {'enabled': value['enabled'], 'lower': str(lower), 'upper': str(upper)}

def evaluate(market, tariff, config, now):
    fetched = market.get('fetched')
    if not config['enabled'] or not fetched or not 0 <= now-fetched <= 3600:
        return None
    row = next((r for r in market.get('rows', []) if r['start'] <= now*1000 < r['end']), None)
    if row is None:
        return None
    spot = deepcopy(tariff)
    spot['mode'] = 'spot'
    price = calculate(row['market_net_ct'], spot)
    gross = dec(price['gross_ct'])
    band = 'low' if gross < dec(config['lower']) else 'high' if gross > dec(config['upper']) else 'normal'
    return {'band': band, 'gross_ct': str(gross), 'start': row['start'], 'end': row['end']}
