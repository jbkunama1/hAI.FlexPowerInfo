# hAI.FlexPowerInfo

Dein Strompreis. Dein Tarif. Transparent aufgeschlüsselt.

hAI.FlexPowerInfo ist als selbst gehostete Strompreis-Zentrale konzipiert: Börsenpreise mit den eigenen Tarifbestandteilen verbinden und den persönlichen Preis pro Kilowattstunde nachvollziehbar machen – im Browser, über Telegram und für KI-Agenten per MCP.

Diese README beschreibt das Zielbild und den vorgesehenen Funktionsumfang des Projekts, keine Zusicherung eines vollständigen Implementierungsstands.

## Eine Preisbasis, drei Zugänge

| Zugang | Aufgabe im Zielbild |
| --- | --- |
| Web-App | Mobilfreundliches Dashboard mit aktuellem Preis, Preisverlauf und Tarifaufschlüsselung |
| Telegram-Bot | Preise und Bestandteile direkt im Chat abfragen |
| MCP-Server | Strukturierte Tarif- und Preisdaten für Agenten bereitstellen |

Alle Zugänge nutzen dieselbe Berechnungslogik und denselben Datenbestand. Web-App, Bot und MCP laufen gemeinsam in einem Docker-Container.

## Den eigenen Tarif vollständig abbilden

Die Admin-Oberfläche dient als zentrale Tarifverwaltung. Preisbestandteile lassen sich benennen, hinzufügen, ändern und entfernen:

- Energieanteil: dynamischer Börsenpreis, fester Wert oder Monats-/Referenzwert.
- Verbrauchsabhängige Bestandteile in ct/kWh, etwa Stromsteuer, Netzentgelte, Konzessionsabgabe und weitere Umlagen oder Zuschläge.
- Servicegebühren mit einer zum Vertrag passenden Berechnungsbasis.
- Umsatzsteuer und separater monatlicher Grundpreis.

Ausgangspunkt ist die Abbildung eines Immergrün-Tarifs. Die Konfiguration soll nicht an einen einzelnen Anbieter gebunden sein. Maßgeblich bleiben das persönliche Preisblatt und die darin festgelegten Berechnungsregeln.

## Preise verstehen statt nur Zahlen sehen

Das Dashboard soll den persönlichen Brutto-Arbeitspreis zusammen mit seiner Zusammensetzung zeigen:

```text
Energieanteil
+ verbrauchsabhängige Tarifbestandteile
+ tarifliche Servicegebühr
= Netto-Arbeitspreis
+ Umsatzsteuer
= Brutto-Arbeitspreis in ct/kWh
```

Der Grundpreis bleibt separat sichtbar. Prozentuale Gebühren müssen entsprechend ihrer vertraglichen Basis berechnet werden; die Darstellung ist kein pauschales Berechnungsschema für jeden Tarif.

## Aktualisierung und Zeitauflösung

Vorgesehen sind manuelle Abfragen und ein optionaler automatischer Abruf, beispielsweise alle 15 Minuten. Die gelieferten Preisintervalle bleiben unverändert. Ein häufigerer Abruf erzeugt keine feineren Börsenpreise und ändert nicht das Abrechnungsmodell des Vertrags.

Stündliche oder viertelstündliche Preise, Monatsreferenzen und feste Arbeitspreise müssen eindeutig voneinander unterschieden werden. Datenquelle, Gültigkeitsintervall, letzter erfolgreicher Abruf und Konfigurationsstatus gehören zu jeder aussagekräftigen Preisauskunft.

## MCP für Agenten

Als Schnittstelle ist ein authentifizierter Streamable-HTTP-Endpunkt unter `/mcp` vorgesehen. Der lesende Werkzeugumfang:

| Tool | Ziel der Abfrage |
| --- | --- |
| `get_current_price` | Aktueller geschätzter Arbeitspreis mit Börsen-/Energieanteil, einzelnen Zuschlägen, Servicegebühr und Umsatzsteuer |
| `get_price_schedule` | Verfügbare Preisintervalle für einen gewählten Zeitraum |
| `get_tariff` | Tarifmodell, Preisbestandteile und Berechnungsregeln |
| `get_status` | Datenalter, Abruffehler und Konfigurationsstatus |

Agenten erhalten strukturierte Werte mit Einheiten und Zeitbezug. Der Grundpreis wird getrennt zurückgegeben. Tarifänderungen bleiben der Admin-Oberfläche vorbehalten.

## Telegram

Der Bot soll dieselben Preise und Aufschlüsselungen wie die Web-App liefern. Zugriff erhalten ausschließlich freigegebene Nutzer beziehungsweise Chats. Bot-Zugang und Agent-Zugang bleiben von der Admin-Anmeldung getrennt.

## Self-hosted mit Docker und Portainer

```text
Ein Docker-Container
├── Web-App und Admin-Oberfläche
├── Telegram-Bot
├── MCP-Server
└── Gemeinsamer Tarif- und Preisdienst
    ├── Marktdatenabruf und Cache
    ├── Tarifberechnung
    └── SQLite im persistenten Volume
```

Ziel des Betriebsmodells sind eine schlanke Bereitstellung über Docker Compose oder Portainer, persistente Einstellungen und zentrale Konfiguration über Umgebungsvariablen beziehungsweise Secrets. Es werden keine persönlichen Vertragsdaten im öffentlichen Repository benötigt.

## Daten und Verlässlichkeit

Als erster Marktdatenadapter ist aWATTar Deutschland vorgesehen. Die Tariflogik bleibt von der Quelle getrennt. Eine automatische Anmeldung im Immergrün-Kundenportal ist nicht Bestandteil des Zielbilds.

- Ungeprüfte Tarifkonfigurationen und veraltete Daten klar kennzeichnen.
- Fehlende Preisintervalle nicht durch erfundene Werte ersetzen.
- Negative Börsenpreise entsprechend den tatsächlichen Vertragsregeln behandeln.
- Börsenpreis und persönlichen Endkundenpreis getrennt ausweisen.
- Ergebnisse als Tarifschätzung, nicht als Abrechnungsnachweis verstehen.

## Sicherheit

Externer Zugriff ausschließlich über HTTPS oder VPN. Separate Zugangsdaten für Administration, MCP und Telegram; keine Tokens oder Passwörter im Repository. Agent-Tools sind lesend, Telegram-Zugriffe auf freigegebene Identitäten beschränkt.

## Projektseite und Lizenz

Die statische GitHub-Pages-Projektseite liegt in `docs/index.html`. Sie stellt das Projekt vor; die persönliche Strompreis-App wird auf der eigenen Infrastruktur betrieben.

MIT-Lizenz, siehe [LICENSE](LICENSE). Ein Projekt von Daniel Lienhard. Keine offizielle Anwendung von Immergrün oder aWATTar.
