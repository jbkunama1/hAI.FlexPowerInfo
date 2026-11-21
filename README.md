<p align="center"><img src="docs/assets/hero.svg" alt="hAI.FlexPowerInfo – Dein Strompreis. Dein Tarif. Deine Kontrolle." width="100%"></p>
<h1 align="center">⚡ hAI.FlexPowerInfo · highfishAI</h1>
<p align="center">Dein Strompreis. Dein Tarif. Dein geschützter Zugriff.</p>
<p align="center"><a href="LICENSE"><img src="https://img.shields.io/badge/Lizenz-MIT-22c55e?style=for-the-badge" alt="MIT"></a> <img src="https://img.shields.io/badge/Web-Login%20Required-06b6d4?style=for-the-badge" alt="Web Login erforderlich"> <img src="https://img.shields.io/badge/MCP-Token%20Required-a855f7?style=for-the-badge" alt="MCP Token erforderlich"> <img src="https://img.shields.io/badge/Docker-Port%208911-2496ed?style=for-the-badge" alt="Docker Port 8911"></p>

## 🌈 Eine Preisbasis. Drei geschützte Zugänge.

hAI.FlexPowerInfo verbindet Börsenpreise mit deinem persönlichen Tarif. Eine gemeinsame Berechnung für Browser, Telegram und KI-Agenten, selbst gehostet auf deiner Infrastruktur. Das Zielbild ist nachvollziehbare Tariftransparenz ohne anonymen Zugriff auf deine Daten.

| Zugang | Schutz |
| --- | --- |
| 🌐 Web-Dashboard und Tarifverwaltung | Anmeldung mit ADMIN_USER und ADMIN_PASSWORD |
| 🤖 MCP /mcp | Bearer-Token für jede Anfrage, Lesen und Schreiben |
| 💬 Telegram | Nutzerfreigabe, separate Admin-IDs für Änderungen |

Ohne Web-Anmeldung ist nur die Login-Oberfläche samt benötigtem JavaScript/CSS erreichbar. /health meldet ausschließlich den Prozessstatus für Docker, keine Preise oder Einstellungen. Dashboard, Preise, Tarif und Status benötigen eine Sitzung. Die frühere /api/public ist abgeschaltet. PUBLIC_DASHBOARD und MCP_PUBLIC können keine anonyme Freigabe mehr aktivieren.

## 🎛️ Dein Tarif

Dynamischer Energiepreis, fester Wert oder manuelle Monatsreferenz. Frei benannte Preisbestandteile, Steuern, Grundpreis, Servicegebühr und optionale Energie-Untergrenze. Alle Eingaben netto, Grundpreis separat. Ausgangspunkt Immergrün, ohne feste Anbieterbindung.

```text
⚡ Energie + 🧩 Zuschläge + 🧮 Servicegebühr
= Netto-Arbeitspreis + Umsatzsteuer
= Geschätzter Brutto-Arbeitspreis in ct/kWh
```

## 🔐 Agenten mit Token

Tools: get_current_price, get_price_schedule, get_tariff, get_status, update_tariff. Tokenpflicht auch für initialize und tools/list. Leerer MCP_TOKEN sperrt MCP; keine OAuth-Discovery. Der Token erlaubt Lesen und Schreiben. update_tariff ersetzt den vollständigen validierten Tarif und setzt confirmed=false. Änderungen vorher mit dem Nutzer abstimmen. Keine Secret- oder Serverbefehlsverwaltung.

## 💬 Telegram mit Admin-Menü

Private Chats benötigen Bot-Token und Nutzer-ID. TELEGRAM_ADMIN_IDS erlaubt zusätzlich bestätigte Änderungen ausgewählter Tarifwerte. Startnachricht, Inline-Menüs, farbige Preisgrafik und Statusauskunft. Details in TELEGRAM.md.

## 🐳 Deine Infrastruktur

Ein Container, SQLite-Volume, docker-compose.yml, Port 8911 → 8080, externes Netzwerk highfishNetwork. PUBLIC_URL bezeichnet lediglich deine Zugriffsadresse, nicht eine öffentliche Datenfreigabe. Für Internetbetrieb HTTPS/VPN und Proxy-Limits. ADMIN_PASSWORD mindestens 4 Zeichen, MCP_TOKEN mindestens 32 Zeichen.

## ⏱️ Nachvollziehbar statt scheinbar exakt

Optionaler Abruf alle 15 Minuten; Quelle und Vertrag bestimmen Preisintervalle. Keine erfundenen Viertelstunden, Monatsreferenzen manuell. Veraltete Daten und ungeprüfte Tarife sichtbar machen. Kein Abrechnungsnachweis, keine Verbrauchsmessung und keine Servicegebühr auf den Grundpreis. Weitere Automatisierung bleibt Teil des Zielbilds. Funktionsbeschreibung ist kein Build- oder Live-Testnachweis.

[Installation](INSTALL.md) · [MCP](MCP.md) · [Telegram](TELEGRAM.md) · [MIT](LICENSE)

Die statische GitHub-Pages-Seite ist ausschließlich Projektbeschreibung, keine laufende Preisinstanz. Ein Projekt von highfishAI. Keine offizielle Anwendung von Immergrün oder aWATTar.

## 🧭 Tarif einrichten: Was brauchst du und was trägst du wo ein?

Diese Anleitung ist unabhängig vom Stromanbieter. Öffne deine Instanz direkt unter `/`, melde dich an und klappe „Tarifverwaltung“ auf. Tarifwerte gehören in die App, nicht in die Docker-ENV oder ins öffentliche Repository.

### 📄 1. Unterlagen zusammenstellen

Halte Vertragsbestätigung, aktuell gültiges Preisblatt und die Bedingungen zur Preisberechnung bereit. Eine aktuelle Rechnung kann beim Abgleich helfen. Benötigt werden:

- Vollständiger Tarifname und Gültigkeitsdatum der Preise; mögliche Sonderregel im ersten Monat beachten.
- Abrechnungsmodell: fester Arbeitspreis, zeitabhängiger Börsenpreis oder Monats-/Referenzwert. Bei Referenzen auch Bezugszeitraum und Berechnungsart prüfen.
- Energiepreis und alle zusätzlich berechneten ct/kWh-Bestandteile.
- Grundpreis pro Monat oder Jahr, jeweils mit Netto-/Brutto-Kennzeichnung.
- Servicegebühr samt genauer Basis: Energie, Energie plus Zuschläge oder gesamter Rechnungsbetrag.
- Umsatzsteuer und gegebenenfalls vertragliche Regeln für negative Preise beziehungsweise Preisuntergrenzen.

### 🎛️ 2. Werte den Feldern zuordnen

| Feld in der Tarifverwaltung | Hier eintragen |
| --- | --- |
| Tarifname | Die vollständige Bezeichnung deines Tarifs. |
| Preismodell | Das vertragliche Modell anhand der Auswahlhilfe unten. |
| Energie-/Referenzwert netto ct/kWh | Festen Energieanteil oder manuell ermittelten Referenzwert. Im Börsenmodell kommt der Energieanteil aus der Marktdatenquelle; dieses Feld wird dafür nicht verwendet. |
| Umsatzsteuer % | Den für deine Rechnung geltenden Umsatzsteuersatz. |
| Grundpreis netto EUR/Monat | Monatlichen Grundpreis ohne Umsatzsteuer; Jahresbetrag vorher durch zwölf teilen. |
| Servicegebühr % | Den vertraglichen Prozentsatz; ohne prozentuale Gebühr 0. Einen festen ct/kWh-Aufschlag stattdessen als zusätzlichen Bestandteil erfassen. |
| Gebührenbasis | „Energieanteil“ oder „Energie + ct/kWh-Bestandteile“ – nur wählen, wenn die Vertragsformel dazu passt. |
| Optionale Energie-Untergrenze netto ct/kWh | Nur eine tatsächlich geltende Untergrenze des Energieanteils; sonst leer lassen. Sie wirkt vor Zuschlägen und ist keine Untergrenze des gesamten Endkundenpreises. |
| Abrufintervall Minuten | Beispielsweise 15 für den Marktdatenabruf; keine Änderung des Abrechnungsintervalls. |
| Zusätzliche Bestandteile netto ct/kWh | Pro zusätzlicher verbrauchsabhängiger Position eine Zeile, z. B. Stromsteuer, Netzentgelt, Konzessionsabgabe, Umlage oder Lieferantenaufschlag. |
| Automatischer Abruf | Aktivieren, wenn der Server Marktdaten im Hintergrund aktualisieren soll. |
| Tarifdaten anhand meines Vertrags geprüft | Erst nach Abgleich von Modell, Bestandteilen und Gebührenformel aktivieren. |

### ⚡ 3. Das richtige Preismodell wählen

- „Börsenpreis je Quellintervall“: Nur wenn dein Vertrag den jeweiligen Energiepreis passend zu den gelieferten Intervallen und zur verwendeten Marktreferenz abrechnet. Ein Abruf alle 15 Minuten beweist das nicht.
- „Fester Energieanteil“: Für einen festen Netto-Energieanteil plus zusätzlich erfasste Bestandteile. Ein vollständiger fester Netto-Arbeitspreis kann ebenfalls als Wert dienen, dann keine enthaltenen Bestandteile oder Gebühren nochmals addieren.
- „Manueller Monats-/Referenzwert“: Für einen vertraglichen Referenzwert, der manuell eingetragen wird. Einen reinen Energie-Referenzwert von einem vollständigen Arbeitspreis unterscheiden. Die App berechnet derzeit keinen automatischen oder verbrauchsgewichteten Monatsdurchschnitt.

### 🧮 4. Netto, brutto und Einheiten prüfen

Alle Preisbeträge in der Verwaltung sind netto. Falls die Unterlagen nur Bruttopreise enthalten:

```text
Netto = Brutto / (1 + Umsatzsteuersatz / 100)
Monatlicher Grundpreis = jährlicher Grundpreis / 12
```

Reine Rechenbeispiele, keine Tarifempfehlung: Bei 19 % Umsatzsteuer entsprechen 11,90 EUR brutto einem Nettobetrag von 10,00 EUR; 29,75 ct/kWh brutto entsprechen 25,00 ct/kWh netto. Ein jährlicher Brutto-Grundpreis von 142,80 EUR entspricht dann 10,00 EUR netto pro Monat. Prozentangaben sind keine ct/kWh-Werte. EUR/kWh vor dem Eintragen mit 100 in ct/kWh umrechnen.

### 🧩 5. Nichts doppelt berechnen

Prüfe für jede Position, ob sie bereits im eingetragenen Energie-/Arbeitspreis oder Grundpreis enthalten ist. Ein vollständiger Arbeitspreis darf nicht zusätzlich um dieselben Steuern, Netzentgelte oder Gebühren erhöht werden. Jährliche oder monatliche feste Kosten nicht als ct/kWh-Zuschlag eintragen. Ein Gesamt-Grundpreis muss in den monatlichen Grundpreis, nicht zusätzlich in die Verbrauchsbestandteile.

### ⚠️ 6. Grenzen der Berechnung beachten

Die aktuelle Servicegebühr wirkt entweder auf den Energieanteil oder auf Energie plus zusätzliche ct/kWh-Bestandteile. Eine prozentuale Gebühr auf den gesamten Rechnungsbetrag inklusive Grundpreis ist damit nicht vollständig abgebildet. Ebenso sind individuelle Preisdeckel, abweichende Rundungsregeln, zeitvariable Zusatzentgelte oder andere Vertragsformeln nicht automatisch unterstützt. Eine Untergrenze nur setzen, wenn sie exakt zur Vertragsregel passt.

Passt die Formel nicht, keine vermeintlich passende Einstellung erzwingen und den Tarif noch nicht als geprüft markieren. Die Berechnungslogik muss dann ergänzt werden. Das monatliche Preismodell darf nicht als persönlicher Viertelstundenpreis dargestellt werden.

### ✅ 7. Speichern und gegenprüfen

1. Werte eintragen und „Tarif speichern“ wählen.
2. Marktdaten abrufen beziehungsweise den passenden festen/manuellen Referenzwert verwenden.
3. Energieanteil, zusätzliche Bestandteile, Servicegebühr, Umsatzsteuer und separaten Grundpreis mit den Vertragsunterlagen vergleichen.
4. Erst bei passender Formel und korrekten Werten die Prüfbestätigung setzen und erneut speichern.

Die Anzeige bleibt eine Tarifschätzung. Für Hilfe reichen geschwärzte Ausschnitte mit Preisbestandteilen und Berechnungsformel; Name, Anschrift, Vertrags-/Kunden- und Zählernummer sowie Zugangsdaten werden nicht benötigt und gehören nicht ins öffentliche Repository.
