const $=s=>document.querySelector(s);let current,csrf='';const form=$('#tariff');
const fmt=n=>Number(n).toLocaleString('de-DE',{maximumFractionDigits:3,minimumFractionDigits:2});const dt=n=>new Date(n).toLocaleString('de-DE',{timeZone:'Europe/Berlin',timeZoneName:'short'});
function msg(x){$('#message').textContent=x}
async function api(path,data){let r=await fetch(path,data===undefined?{}:{method:'POST',headers:{'Content-Type':'application/json','X-CSRF-Token':csrf},body:JSON.stringify(data)});let x=await r.json();if(!r.ok){if(r.status===401)show(false);throw Error(typeof x.detail==='string'?x.detail:x.error||'Anfrage fehlgeschlagen')}return x}
function show(ok){$('#login').hidden=ok;$('#dashboard').hidden=!ok}
function part(x={name:'Neuer Bestandteil',ct:'0'}){let d=document.createElement('div');d.className='component';let a=document.createElement('input'),b=document.createElement('input'),c=document.createElement('button');a.value=x.name;a.required=true;a.setAttribute('aria-label','Bezeichnung');b.type='number';b.step='any';b.required=true;b.value=x.ct;b.setAttribute('aria-label','Netto ct pro kWh');c.type='button';c.textContent='Entfernen';c.onclick=()=>d.remove();d.append(a,b,c);$('#components').append(d)}
function populate(s){for(let k in s){let e=form.elements.namedItem(k);if(e){if(e.type==='checkbox')e.checked=s[k];else e.value=s[k]??''}}$('#components').replaceChildren();s.components.forEach(part)}
function render(x){current=x;let p=x.current?.price||x.tariff_price;$('#price').textContent=p?fmt(p.gross_ct)+' ct/kWh':'Kein gültiger Preis';$('#market').textContent=x.current?fmt(x.current.market_net_ct)+' ct/kWh':'Keine gültigen Marktdaten';$('#period').textContent=x.tariff.mode==='spot'?(x.current?dt(x.current.start)+' – '+dt(x.current.end):'Aktuelles Intervall fehlt'):x.tariff.mode==='fixed'?'Fester Tarifwert':'Manueller Referenzwert';$('#base').textContent=fmt(Number(x.tariff.base_net)*(1+Number(x.tariff.vat)/100))+' €';$('#fetched').textContent='Letzter Abruf: '+(x.fetched?dt(x.fetched*1000):'noch keiner');msg([!x.configured?'Tarif ungeprüft: keine belastbaren Vertragspreise.':'Tarif durch dich als geprüft markiert.',x.stale?'Marktdaten fehlen oder sind veraltet.':'',x.error||''].join(' '));$('#breakdown').textContent=p?`Energie ${fmt(p.energy_net_ct)} + Bestandteile ${fmt(p.components_net_ct)} + Service ${fmt(p.fee_net_ct)} = ${fmt(p.net_ct)} netto; MwSt. ${fmt(p.vat_ct)}; brutto ${fmt(p.gross_ct)} ct/kWh.`:'';$('#rows').replaceChildren();$('#chart').replaceChildren();for(let a of x.rows){let tr=document.createElement('tr');for(let t of [dt(a.start)+' – '+dt(a.end),fmt(a.market_net_ct),fmt(a.price.gross_ct)]){let td=document.createElement('td');td.textContent=t;tr.append(td)}$('#rows').append(tr);let item=document.createElement('span');item.className='bar '+(Number(a.price.gross_ct)<0?'negative':'positive');item.textContent=fmt(a.price.gross_ct);item.title=dt(a.start)+' – '+dt(a.end)+'; '+fmt(a.price.gross_ct)+' ct/kWh brutto';item.setAttribute('role','listitem');$('#chart').append(item)}}
async function load(first=false){let x=await api('/api/status');csrf=x.csrf;show(true);render(x);if(first){populate(x.tariff);await loadAlerts()}}
$('#login').onsubmit=async e=>{e.preventDefault();try{let x=await api('/api/login',{username:$('#username').value,password:$('#password').value});csrf=x.csrf;$('#password').value='';await load(true)}catch(e){msg(e.message)}};
$('#add').onclick=()=>part();$('#refresh').onclick=async()=>{let b=$('#refresh');b.disabled=true;try{render(await api('/api/refresh',{}))}catch(e){msg(e.message)}finally{b.disabled=false}};
form.onsubmit=async e=>{e.preventDefault();let s={...current.tariff};for(let k in s){let a=form.elements.namedItem(k);if(a)s[k]=a.type==='checkbox'?a.checked:a.value}s.components=[...document.querySelectorAll('.component')].map(d=>({name:d.children[0].value,ct:d.children[1].value}));try{await api('/api/tariff',s);await load();msg('Tarif gespeichert. '+(!s.confirmed?'Weiterhin ungeprüft.':''))}catch(e){msg(e.message)}};
$('#logout').onclick=async()=>{try{await api('/api/logout',{});show(false);csrf='';$('#alerts-fields').disabled=true;$('#alerts-form').reset();$('#alerts-status').textContent=''}catch(e){msg(e.message)}};
$('#export').onclick=()=>{let blob=new Blob([JSON.stringify(current.tariff,null,2)],{type:'application/json'}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='flexpower-tarif.json';a.click();URL.revokeObjectURL(url)};
$('#import').onchange=async e=>{try{let file=e.target.files[0];if(!file||file.size>65536)throw Error('Datei fehlt oder ist zu groß');let x=JSON.parse(await file.text());if(!Array.isArray(x.components))throw Error('Ungültiger Tarif');populate(x);msg('Import zur Prüfung im Formular geladen. Zum Übernehmen speichern.')}catch(e){msg(e.message)}};

const alertsPanel=document.createElement('section');
alertsPanel.setAttribute('aria-labelledby','alerts-title');
alertsPanel.innerHTML=`<h2 id="alerts-title">Marktpreisalarme per Telegram</h2>
<p>Die Grenzen sind frei einstellbar, auch mit Nachkommastellen und negativen Werten. Verglichen wird der aktuelle Börsenintervallpreis mit deinen gespeicherten Zuschlägen, Gebühren und Umsatzsteuer, ohne monatlichen Grundpreis. Das ist eine Modellrechnung, nicht dein EnerFlex-Blue-Monatsabrechnungspreis.</p>
<form id="alerts-form"><fieldset id="alerts-fields" disabled><legend>Alarm-Einstellungen</legend>
<label><input id="alerts-enabled" type="checkbox"> Telegram-Preisalarme aktivieren</label>
<div class="grid"><label>Nachricht bei Preis unter (ct/kWh brutto)<input id="alerts-lower" type="number" step="any" min="-100000" max="100000" required></label>
<label>Nachricht bei Preis über (ct/kWh brutto)<input id="alerts-upper" type="number" step="any" min="-100000" max="100000" required></label></div>
<button id="alerts-save" type="submit">Alarm-Einstellungen speichern</button></fieldset></form>
<button id="alerts-reload" type="button">Gespeicherte Einstellungen neu laden</button>
<p id="alerts-status" role="status" aria-live="polite"></p>
<p>Untergrenze muss kleiner als Obergrenze sein. Bei genau gleichem Preis erfolgt kein Alarm. Eine Nachricht beim Eintritt in einen Alarmbereich, nicht bei jedem Abruf. Geänderte Grenzen oder Aktivierung können sofort eine Nachricht auslösen. Versand an die privaten Chats aller freigegebenen TELEGRAM_USER_IDS; der Bot muss dort bereits gestartet sein. Änderungen werden erst mit Speichern wirksam und bleiben nach Containerneustart erhalten.</p>`;
$('#dashboard').append(alertsPanel);
function populateAlerts(config){$('#alerts-enabled').checked=config.enabled;$('#alerts-lower').value=config.lower;$('#alerts-upper').value=config.upper}
async function loadAlerts(){
    $('#alerts-fields').disabled=true;$('#alerts-status').textContent='Alarm-Einstellungen werden geladen …';
    try{let x=await api('/api/market-alerts');if($('#dashboard').hidden)return;populateAlerts(x.config);$('#alerts-fields').disabled=false;$('#alerts-status').textContent='Gespeichert: '+(x.config.enabled?'aktiv':'ausgeschaltet')+' · unter '+x.config.lower+' / über '+x.config.upper+' ct/kWh brutto.'}
    catch(e){$('#alerts-status').textContent='Alarm-Einstellungen nicht verfügbar: '+e.message+'. Prüfe, ob das aktualisierte Image mit alert_gateway läuft.'}
}
$('#alerts-reload').onclick=()=>loadAlerts();
$('#alerts-form').onsubmit=async e=>{
    e.preventDefault();
    const lower=$('#alerts-lower').value,upper=$('#alerts-upper').value;
    if(!lower.trim()||!upper.trim()||!Number.isFinite(Number(lower))||!Number.isFinite(Number(upper))||Number(lower)>=Number(upper)){
        $('#alerts-status').textContent='Bitte gültige Zahlen eingeben: Untergrenze muss kleiner als Obergrenze sein.';return;
    }
    const config={enabled:$('#alerts-enabled').checked,lower,upper};
    $('#alerts-fields').disabled=true;$('#alerts-reload').disabled=true;$('#alerts-status').textContent='Wird gespeichert …';
    try{const saved=await api('/api/market-alerts',config);if($('#dashboard').hidden)return;populateAlerts(saved);$('#alerts-status').textContent='Alarm-Einstellungen gespeichert: '+(saved.enabled?'aktiv':'ausgeschaltet')+' · unter '+saved.lower+' / über '+saved.upper+' ct/kWh brutto.'}
    catch(e){$('#alerts-status').textContent='Speichern nicht bestätigt: '+e.message+'. Gespeicherte Einstellungen neu laden, bevor du es erneut versuchst.'}
    finally{if(!$('#dashboard').hidden)$('#alerts-fields').disabled=false;$('#alerts-reload').disabled=false}
};
load(true).catch(()=>msg('Bitte anmelden.'));setInterval(()=>{if(!$('#dashboard').hidden)load().catch(e=>msg(e.message))},60000);
