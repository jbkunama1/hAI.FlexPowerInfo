import json, sqlite3, time
from pathlib import Path
from decimal import Decimal, InvalidOperation
from copy import deepcopy
from price_input import normalize_tariff_input

DEFAULT={'name':'Mein Tarif','confirmed':False,'mode':'spot','energy_ct':'0','vat':'19','base_net':'0','fee_percent':'0','fee_basis':'energy','floor_ct':None,'auto_refresh':False,'refresh_minutes':15,'components':[]}
def dec(x):
    if isinstance(x,bool): raise ValueError('Zahl erwartet')
    try: d=Decimal(str(x))
    except InvalidOperation: raise ValueError('Ungültige Zahl')
    if not d.is_finite() or abs(d)>100000: raise ValueError('Zahl außerhalb des Bereichs')
    return d

def validate(s):
    s=normalize_tariff_input(s)
    v=deepcopy(DEFAULT)
    if s.get('mode') not in ('spot','fixed','reference'): raise ValueError('Unbekanntes Preismodell')
    if s.get('fee_basis') not in ('energy','subtotal'): raise ValueError('Unbekannte Gebührenbasis')
    v['name']=str(s.get('name',''))[:150]
    v['mode']=s['mode'];v['fee_basis']=s['fee_basis']
    for k in ('confirmed','auto_refresh'):
        if not isinstance(s.get(k),bool): raise ValueError('Ungültiger Schalter')
        v[k]=s[k]
    for k in ('energy_ct','vat','base_net','fee_percent'):
        d=dec(s.get(k))
        if k!='energy_ct' and d<0: raise ValueError('Negativer Wert nicht erlaubt')
        if k in ('vat','fee_percent') and d>100: raise ValueError('Prozentsatz maximal 100')
        v[k]=str(d)
    v['floor_ct']=None if s.get('floor_ct') in (None,'') else str(dec(s['floor_ct']))
    interval=dec(s.get('refresh_minutes',15))
    if interval!=int(interval) or not 15<=interval<=1440: raise ValueError('Abrufintervall 15–1440 ganze Minuten')
    v['refresh_minutes']=int(interval)
    v['components']=[{'name':str(p['name'])[:100],'ct':str(dec(p['ct'])),'price_basis':'net'} for p in s['components']]
    v['price_basis']=s['price_basis']
    return v

def calculate(market,s):
    e=dec(market if s['mode']=='spot' else s['energy_ct'])
    if s['floor_ct'] is not None:e=max(e,dec(s['floor_ct']))
    z=sum((dec(x['ct']) for x in s['components']),Decimal(0))
    fee=(e if s['fee_basis']=='energy' else e+z)*dec(s['fee_percent'])/100
    net=e+z+fee;tax=net*dec(s['vat'])/100
    return {k:str(v) for k,v in dict(energy_net_ct=e,components_net_ct=z,fee_net_ct=fee,net_ct=net,vat_ct=tax,gross_ct=net+tax,base_gross_eur=dec(s['base_net'])*(1+dec(s['vat'])/100)).items()}

class Store:
    def __init__(self,path):
        self.path=str(path);Path(path).parent.mkdir(parents=True,exist_ok=True)
        with self.conn() as c:
            c.execute('CREATE TABLE IF NOT EXISTS kv(k TEXT PRIMARY KEY,v TEXT)')
            c.execute('CREATE TABLE IF NOT EXISTS tariffs(id INTEGER PRIMARY KEY,created REAL,body TEXT)')
    def conn(self): return sqlite3.connect(self.path,timeout=20)
    def get(self,k,default=None):
        with self.conn() as c: row=c.execute('SELECT v FROM kv WHERE k=?',(k,)).fetchone()
        return json.loads(row[0]) if row else deepcopy(default)
    def put(self,k,v):
        with self.conn() as c:c.execute('INSERT OR REPLACE INTO kv VALUES(?,?)',(k,json.dumps(v)))
    def save_tariff(self,s):
        s=validate(s)
        with self.conn() as c:
            c.execute('INSERT INTO tariffs(created,body) VALUES(?,?)',(time.time(),json.dumps(s)))
            c.execute('INSERT OR REPLACE INTO kv VALUES(?,?)',('tariff',json.dumps(s)))
        return s

def parse_market(raw):
    rows=[]
    for x in raw['data']:
        if x['unit'].lower()!='eur/mwh':raise ValueError('Unbekannte Einheit')
        a,b=int(x['start_timestamp']),int(x['end_timestamp'])
        if b<=a:raise ValueError('Ungültiges Intervall')
        rows.append({'start':a,'end':b,'market_net_ct':str(dec(x['marketprice'])/10)})
    rows.sort(key=lambda x:x['start'])
    if not rows or any(b['start']<a['end'] for a,b in zip(rows,rows[1:])):raise ValueError('Leere oder überlappende Daten')
    return rows

def snapshot(store,now=None):
    now=time.time() if now is None else now
    s=store.get('tariff',DEFAULT);m=store.get('market',{'fetched':None,'rows':[]})
    rows=[dict(x,price=calculate(x['market_net_ct'],s)) for x in m['rows']]
    current=next((x for x in rows if x['start']<=now*1000<x['end']),None)
    return {'tariff':s,'current':current,'tariff_price':calculate(0,s) if s['mode']!='spot' else None,'rows':rows,'source':'aWATTar DE Day-Ahead','fetched':m['fetched'],'stale':not m['fetched'] or now-m['fetched']>3600,'error':store.get('error'),'configured':s['confirmed'],'units':{'work_price':'ct/kWh','base':'EUR/month'},'notice':'Tarifschätzung; Tabellenwerte verwenden die aktuell gespeicherte Tarifversion.'}
