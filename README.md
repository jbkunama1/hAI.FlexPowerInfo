# hAI.FlexPowerInfo

Self-hosted Strompreis-Dashboard mit frei konfigurierbarem Tarif und Admin-Oberfläche. Ziel: Web-App, Telegram-Bot und MCP-Server gemeinsam in einem Docker-Container.

## Projektstatus

Dieses Repository startet mit Dokumentation und einer statischen Projektseite. Der im Projektchat erstellte Python-Prototyp ist noch nicht in dieses Repository übertragen. Deshalb enthält dieser Stand noch keine startbare Anwendung und kein veröffentlichtes Docker-Image. Telegram-Bot und MCP-Server sind geplant, nicht implementiert.

## Funktionsumfang des bisherigen Prototyps

- Mobilfreundliches Dashboard mit geschätztem Brutto-Arbeitspreis, Börsenpreis und separatem Grundpreis.
- Passwortgeschützte Tarifverwaltung mit frei benennbaren Netto-Preisbestandteilen in ct/kWh.
- Änderbare Umsatzsteuer, monatlicher Grundpreis und prozentuale Servicegebühr.
- Dynamischer Energiepreis, fester Energieanteil oder manuell eingetragener Monats-/Referenzwert.
- Manueller oder optional automatischer Abruf, frühestens alle 15 Minuten.
- SQLite-Persistenz und vorbereitete Docker-/Compose-Konfiguration im Chat-Prototyp.

Diese Aufzählung beschreibt den Chat-Prototyp, nicht bereits vorhandenen Anwendungscode dieses Repositorys.

## Geplante gemeinsame Architektur

```text
Ein Docker-Container
|-- Web-App und Admin-Oberfläche
|-- Telegram-Bot mit Nutzerfreigabe
|-- MCP-Server mit lesenden Agent-Tools
`-- Gemeinsamer Tarifdienst und SQLite-Volume
```

### Geplante MCP-Tools

| Tool | Zweck |
| --- | --- |
| get_current_price | Aktueller geschätzter Preis inklusive aller Bestandteile |
| get_price_schedule | Verfügbare Preisintervalle für einen Zeitraum |
| get_tariff | Konfigurierte Tarifbestandteile und Berechnungsmodell |
| get_status | Datenalter, Abrufstatus und Konfigurationsstatus |

MCP ist als Streamable-HTTP-Endpunkt unter /mcp mit eigenem Zugang vorgesehen. Agenten sollen zunächst keine Tarifänderungen vornehmen können. Die konkrete Client-Authentifizierung wird bei der Implementierung abgeglichen.

## Preisberechnung

Alle Tarif-Eingaben sind netto. Grundschema:

```text
Energieanteil + zusätzliche ct/kWh-Bestandteile + Servicegebühr
= Netto-Arbeitspreis
Netto-Arbeitspreis × (1 + Umsatzsteuer / 100)
= Brutto-Arbeitspreis
```

Der monatliche Grundpreis wird separat ausgewiesen. Gebührenbasis und Rundung müssen mit dem tatsächlichen Vertrag abgeglichen werden. Ein Abruf alle 15 Minuten bedeutet nicht automatisch eine viertelstündliche Abrechnung. Die App soll die tatsächlichen Intervalle der Datenquelle übernehmen.

Es sind keine geprüften Immergrün-Vertragswerte hinterlegt. Das genaue Preisblatt steht noch aus. Monatsdurchschnitt, zeitabhängige Abrechnung und fester Arbeitspreis dürfen nicht verwechselt werden. Eine monatliche Referenz ist im bisherigen Prototyp nur manuell eintragbar. Gebühren auf den gesamten Rechnungsbetrag inklusive Grundpreis sind dort noch nicht abgebildet.

## Datenquelle

Im Prototyp vorgesehen: aWATTar Deutschland, https://api.awattar.de/v1/marketdata . Dokumentation: https://www.awattar.at/services/api/ . EUR/MWh wird durch 10 geteilt, um ct/kWh zu erhalten. Liveabruf und Nutzungsbedingungen sind vor produktivem Einsatz zu prüfen. Keine direkte Verbindung zum Immergrün-Kundenkonto.

## Installation

Noch nicht aus diesem Repository möglich. Nächster Schritt ist die Übertragung und Prüfung des Anwendungscodes samt Dockerfile, Compose-Datei, Beispieldatei für Umgebungsvariablen und Tests. Keine produktiven Zugangsdaten oder persönlichen Tarifunterlagen committen.

## Sicherheit

- Externer Zugriff nur über HTTPS-Reverse-Proxy oder VPN.
- Separate Zugangsdaten für Admin, MCP und Telegram vorsehen.
- Telegram auf freigegebene Nutzer/Chats beschränken.
- Tokens und Passwörter ausschließlich über Umgebungsvariablen oder Secrets.
- Fehlende/veraltete Marktdaten und ungeprüfte Tarifwerte sichtbar kennzeichnen.
- Tarifschätzungen ersetzen keine Abrechnung des Energieversorgers.

## GitHub Pages

Die statische Projektseite liegt unter docs/index.html. Sie ist keine laufende Strompreis-App und enthält keine privaten Tarifdaten.

Nach dem Commit unter Settings → Pages → Build and deployment die Quelle GitHub Actions auswählen. Der enthaltene Workflow veröffentlicht nur den Ordner docs. Die erwartete Projektadresse nach erfolgreicher Einrichtung ist https://jbkunama1.github.io/hAI.FlexPowerInfo/ . Ein erfolgreicher Pages-Deploy muss separat überprüft werden.

## Roadmap

- [ ] Anwendungscode des Chat-Prototyps übernehmen und testen.
- [ ] Immergrün-Preisblatt und genaue Gebührenformel integrieren.
- [ ] Telegram-Bot ergänzen.
- [ ] Authentifizierten MCP-Server ergänzen.
- [ ] Alle Dienste in einem Container integrieren und Start/Stop testen.
- [ ] Docker-Build, API-Liveabruf und Integrationsprüfungen automatisieren.

## Lizenz

MIT, siehe LICENSE. Unabhängiges Projekt; keine offizielle Anwendung von Immergrün oder aWATTar.
