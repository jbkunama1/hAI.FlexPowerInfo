<p align="center"><img src="docs/assets/hero.svg" alt="hAI.FlexPowerInfo – Dein Strompreis. Dein Tarif. Deine Kontrolle." width="100%"></p>
<h1 align="center">⚡ hAI.FlexPowerInfo · highfishAI</h1>
<p align="center">Dein Strompreis. Dein Tarif. Dein geschützter Zugriff.</p>
<p align="center"><a href="LICENSE"><img src="https://img.shields.io/badge/Lizenz-MIT-22c55e?style=for-the-badge" alt="MIT"></a> <img src="https://img.shields.io/badge/Web-Login%20Required-06b6d4?style=for-the-badge" alt="Web Login erforderlich"> <img src="https://img.shields.io/badge/MCP-Token%20Required-a855f7?style=for-the-badge" alt="MCP Token erforderlich"> <img src="https://img.shields.io/badge/Docker-Port%208911-2496ed?style=for-the-badge" alt="Docker Port 8911"></p>

## 🌈 Geschützte Zugänge, nachvollziehbare Preise

hAI.FlexPowerInfo verbindet Börsenpreise mit deinem konfigurierbaren Tarif: selbst gehostet, mit Web-Dashboard, Telegram, MCP und einem optionalen Nur-Lese-Preislink für FHEM oder Home Assistant.

| Zugang | Schutz |
| --- | --- |
| Web-Dashboard und Tarifverwaltung unter `/` | Anmeldung mit ADMIN_USER und ADMIN_PASSWORD |
| MCP `/mcp` | Bearer-Token für jede Anfrage, auch initialize und tools/list |
| Telegram | Freigegebene Nutzer; separate Admin-IDs für Tarifänderungen |
| Zahlenexport `/price.txt?token=DEIN_LESETOKEN` | Separater PRICE_READ_TOKEN, nur lesend |

Login-Oberfläche und benötigtes JavaScript/CSS sind öffentlich erreichbar, nicht deine Tarifdaten. `/health` liefert nur Prozessstatus. Web-APIs benötigen eine Sitzung, schreibende Web-Aufrufe zusätzlich CSRF-Schutz. Der Preislink ist die gezielte Ausnahme von der Web-Sitzung: nur mit eigenem Lesetoken, niemals anonym. `/api/public` ist abgeschaltet; PUBLIC_DASHBOARD und MCP_PUBLIC aktivieren keine anonyme Freigabe.

## 🎛️ Dein Tarif

Börsenpreis je Quellintervall, fester Energieanteil oder manuelle Monatsreferenz. Frei benannte Preisbestandteile, Umsatzsteuer, Grundpreis, Servicegebühr und optionale Energie-Untergrenze. Tarif-Preisbeträge netto eingeben, Grundpreis separat. Anbieterunabhängig; Ausgangspunkt war Immergrün.

```text
Energie + zusätzliche Bestandteile + Servicegebühr
= Netto-Arbeitspreis + Umsatzsteuer
= geschätzter Brutto-Arbeitspreis in ct/kWh
```

## 🔔 Einstellbare Marktpreisalarme

Nach Anmeldung am Ende des Dashboards: „Marktpreisalarme per Telegram“. Alarm aktivieren, Untergrenze und Obergrenze in ct/kWh brutto eintragen und „Alarm-Einstellungen speichern“ wählen. 30 und 42 sind nur Startwerte. Negative Zahlen und Nachkommastellen sind erlaubt; Untergrenze muss kleiner als Obergrenze sein. Beide Grenzen gelten gemeinsam; genau auf der Grenze kein Alarm. Einstellungen bleiben im Datenvolume erhalten. Neu laden verwirft ungespeicherte Alarmeingaben.

Die Alarmbasis ist immer das aktuelle Börsenintervall plus gespeicherte Bestandteile, Servicegebühr und Umsatzsteuer, gegebenenfalls mit Energie-Untergrenze, ohne Grundpreis. Der feste/manuelle Energiepreis wird ignoriert. Dies ist eine Marktpreis-Modellrechnung und bei monatlich abgerechneten Verträgen kein persönlicher Intervall-Abrechnungspreis.

Versand über den vorhandenen Bot an private Chats aller TELEGRAM_USER_IDS; Bot vorher starten. Standardmäßig ausgeschaltet. Aktivierung oder geänderte Grenzen können beim nächsten gültigen Prüfzyklus eine Nachricht auslösen. Prüfung etwa alle zehn Sekunden; keine Meldung bei fehlendem aktuellen Intervall oder ungültiger Datenfrische. Gespeicherter Bereichsstatus je Empfänger vermeidet wiederholte Meldungen im selben Bereich auch nach Neustart. Nach beobachteter Rückkehr oder direktem Wechsel zum anderen Alarmbereich ist eine neue Meldung möglich. Keine historischen oder zukünftigen Vorabalarme. Bei unklarem Versandfehler sind Duplikate nicht vollständig auszuschließen.

MCP: `get_market_alerts`, `update_market_alerts`. Web-API: GET/POST `/api/market-alerts` mit Sitzung, POST zusätzlich mit CSRF-Token. Details: [Alarmverhalten](MARKET-ALERTS.md), [Dashboard-Anleitung](DASHBOARD-ALERTS.md).

## 🔗 Nur die Zahl: FHEM und Home Assistant

```text
http://DEIN-SERVER:8911/price.txt?token=DEIN_LESETOKEN
```

Nach Einrichtung kommt bei HTTP 200 ausschließlich eine Dezimalzahl mit Punkt zurück, beispielsweise `29.437`. Einheit: ct/kWh brutto. Kein JSON, keine Einheit im Body, keine weiteren Tarifdaten. Negative Werte sind möglich; keine feste Rundung auf drei Nachkommastellen. Die Berechnung nutzt dieselbe Marktpreisfunktion wie die Alarme, unabhängig vom Monatsmodell und davon, ob Telegram-Alarme aktiviert sind.

In der privaten Container-Umgebung `PRICE_READ_TOKEN` setzen: 32 bis 256 Zeichen aus Buchstaben, Ziffern, Bindestrich und Unterstrich. Eigenen zufälligen Token verwenden, niemals MCP_TOKEN oder ADMIN_PASSWORD; identische Werte werden abgelehnt. `DEIN_LESETOKEN` ist nur ein Platzhalter. Leerer/ungültiger Token sperrt den Endpunkt. Token niemals ins Repository schreiben; Link wie ein Passwort behandeln.

HTTP 401: Zugriff nicht autorisiert. HTTP 503: keine aktuellen/verwendbaren Preisdaten oder Berechnungsfehler. Keine Ersatz-Null, kein Preis außerhalb seines Intervalls. FHEM/HA müssen HTTP-Fehler und Aktualität berücksichtigen und dürfen einen alten Preis nicht unbegrenzt weiterverwenden. Antworten verwenden no-store; Token können dennoch in Browserhistorie und Proxy-/Client-Logs stehen. Nur vertrauenswürdiges LAN, VPN oder HTTPS; Proxy-Logs ohne Tokens konfigurieren. Keine neue anonyme Dashboard- oder MCP-Freigabe.

Ein konfigurierter Lesetoken aktiviert einen eigenen Aktualisierungsbedarf auch bei ausgeschaltetem Tarif-Autoabruf. Der Hintergrundprozess prüft alle 30 Sekunden, der gemeinsame Marktdatenabruf bleibt mindestens 15 Minuten auseinander. HTTP-GET selbst stößt keinen externen Abruf an. Vollständige Einrichtung und Integrationshinweise: [PRICE-EXPORT.md](PRICE-EXPORT.md). FHEM/HA werden nicht automatisch konfiguriert; der Link wird nicht automatisch im Dashboard angezeigt.

## 🔐 Agenten und Telegram

MCP-Tools: get_current_price, get_price_schedule, get_tariff, get_status, update_tariff, get_market_alerts, update_market_alerts. MCP_TOKEN mindestens 32 Zeichen; leer sperrt MCP. Keine OAuth-Discovery. Der MCP-Token erlaubt Lesen und Schreiben. update_tariff ersetzt den vollständigen validierten Tarif und setzt confirmed=false. Schreibzugriffe vorher abstimmen. Keine Secret- oder Serverbefehlsverwaltung.

Telegram bietet Startnachricht, Inline-Menü, Preisgrafik, Tarif- und Statusabfragen. TELEGRAM_ADMIN_IDS erlaubt zusätzlich bestätigte Änderungen ausgewählter Tarifwerte im privaten Chat; Admin muss auch freigegebener Nutzer sein. Alarmgrenzen im Dashboard oder per MCP/API einstellen, nicht über das bisherige Telegram-Tarifmenü. [Telegram-Dokumentation](TELEGRAM.md).

## 🐳 Betrieb und Versionsstatus

Ein Container, SQLite-Volume, `docker-compose.yml`, Port 8911 → 8080 und externes `highfishNetwork`. Docker-Einstiegspunkt: `price_gateway:app`, der Alarm- und geschützten Gateway umschließt. PUBLIC_URL ist nur die Zugriffsadresse. ADMIN_PASSWORD mindestens vier Zeichen. HTTPS/VPN und Proxy-Limits für externen Betrieb.

Nach erfolgreichem Image-Build aktualisierte Compose-Datei übernehmen, private Umgebungswerte setzen, Image ziehen und Container neu erstellen; Browser für den neuen Editor neu laden. Ein Commit ist kein Deployment. Alarmgrenzen bleiben zunächst ausgeschaltet, Preisexport ohne Lesetoken gesperrt. Tests sind im Repository ergänzt; ein vollständig grüner aktueller CI-/GHCR-Lauf sowie Container-, Browser-, Alarm-, Preisexport- und FHEM-/HA-Live-Tests sind hier nicht bestätigt.

Quelle und Vertrag bestimmen die Preisintervalle; ein Abruf alle 15 Minuten macht keinen Viertelstundenvertrag. Manuelle Monatsreferenzen werden nicht automatisch oder verbrauchsgewichtet gemittelt. Kein Abrechnungsnachweis, keine Verbrauchsmessung, keine Servicegebühr auf den Grundpreis. Die statische GitHub-Pages-Seite enthält keine Live-Preise und keine persönlichen Tarifwerte. highfishAI ist unabhängig von Immergrün und aWATTar.

[Installation](INSTALL.md) · [MCP](MCP.md) · [Telegram](TELEGRAM.md) · [Marktpreisalarme](MARKET-ALERTS.md) · [Dashboard](DASHBOARD-ALERTS.md) · [Preisexport](PRICE-EXPORT.md) · [MIT](LICENSE)

## 🧭 Tarif einrichten: Was brauchst du und was trägst du wo ein?

### 1. Unterlagen vorbereiten

Vertragsbestätigung, gültiges Preisblatt und Preisberechnungsbedingungen, optional Rechnung zum Vergleich. Ermitteln: vollständiger Tarifname, Preisgültigkeit und mögliche Erstmonatsregel, festes/zeitvariables/monatliches Modell samt Referenzzeitraum, Energiepreis und zusätzliche Bestandteile, monatlicher/jährlicher Grundpreis, Netto-/Brutto-Kennzeichnung, Umsatzsteuer, Gebührenformel und Regeln für negative Preise. Persönliche Werte in der App pflegen, nicht im öffentlichen Repository oder in Docker-ENV.

### 2. App-Felder zuordnen

| Feld | Eintrag |
| --- | --- |
| Tarifname | Vollständige Vertragsbezeichnung |
| Preismodell | Nach Vertragsformel, siehe unten |
| Energie-/Referenzwert netto ct/kWh | Fester Energieanteil oder manueller Referenzwert; im Börsenmodell nicht verwendet |
| Umsatzsteuer % | Für die Rechnung geltender Satz |
| Grundpreis netto EUR/Monat | Monatlicher Nettobetrag; Jahresbetrag durch zwölf teilen |
| Servicegebühr % | Vertraglicher Prozentsatz, ohne Gebühr 0; festen ct/kWh-Aufschlag als Bestandteil erfassen |
| Gebührenbasis | Energie oder Energie plus ct/kWh-Bestandteile, passend zur Vertragsformel |
| Energie-Untergrenze netto ct/kWh | Nur bei passender Vertragsregel, sonst leer; wirkt vor Zuschlägen, nicht als Gesamtpreisdeckel |
| Abrufintervall Minuten | Zum Beispiel 15; ändert nicht das Vertrags-Abrechnungsintervall |
| Zusätzliche Bestandteile netto ct/kWh | Zusätzliche Positionen einzeln, etwa Netzentgelt, Stromsteuer, Konzessionsabgabe, Umlagen und Aufschläge |
| Automatischer Abruf | Tarifbezogene Hintergrundaktualisierung; aktive Alarme/Preisexport fordern zusätzlich Marktdaten an |
| Tarif anhand meines Vertrags geprüft | Erst nach Abgleich von Modell, Preisen und Formel aktivieren |

### 3. Preismodell wählen

- Börsenpreis je Quellintervall: nur bei passender Vertragsreferenz und Zeitauflösung.
- Fester Energieanteil: fester Nettowert plus zusätzliche Bestandteile. Bei vollständigem Netto-Arbeitspreis enthaltene Kosten nicht nochmals addieren.
- Manueller Monats-/Referenzwert: vertraglichen Referenzwert selbst eintragen. Energie-Referenz und vollständigen Arbeitspreis unterscheiden; keine automatische oder verbrauchsgewichtete Monatsmittelung.

### 4. Netto, brutto und Einheiten

```text
Netto = Brutto / (1 + Umsatzsteuersatz / 100)
Monatsgrundpreis = Jahresgrundpreis / 12
EUR/kWh × 100 = ct/kWh
```

Reine Rechenbeispiele bei 19 % Umsatzsteuer: 11,90 EUR brutto = 10,00 EUR netto; 29,75 ct/kWh brutto = 25,00 ct/kWh netto; 142,80 EUR jährlicher Brutto-Grundpreis = 10,00 EUR netto pro Monat. Keine Tarifempfehlung. Prozent ist keine Preiseinheit. Alarmgrenzen sind im Unterschied zu Tarif-Preiseingaben brutto.

### 5. Doppelzählungen und Grenzen vermeiden

Bereits im Arbeitspreis oder Grundpreis enthaltene Positionen nicht erneut addieren. Monatliche/jährliche Fixkosten nicht als ct/kWh erfassen. Gebühren auf die gesamte Rechnung inklusive Grundpreis, individuelle Preisdeckel, abweichende Rundung und zeitvariable Zusatzentgelte sind nicht pauschal abgebildet. Bei unpassender Formel keine Einstellung erzwingen oder Prüfbestätigung setzen; dann muss die Berechnungslogik erweitert werden. Ein Monatswert ist kein persönlicher Intervallpreis, auch wenn Alarme und Export ein separates Marktpreismodell verwenden.

### 6. Speichern und prüfen

Werte eintragen, „Tarif speichern“, Marktdaten abrufen beziehungsweise richtigen Referenzwert verwenden. Energie, Bestandteile, Gebühr, Umsatzsteuer und separaten Grundpreis mit den Unterlagen abgleichen. Erst danach Prüfbestätigung setzen und erneut speichern. Die Anzeige bleibt eine Schätzung. Für Hilfe nur geschwärzte Preis-/Formelausschnitte teilen, keine Namen, Anschriften, Kunden-/Vertrags-/Zählernummern oder Zugangsdaten.
