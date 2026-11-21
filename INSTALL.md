# Installation und Betrieb

## GHCR und Portainer

Image: `ghcr.io/jbkunama1/hai.flexpowerinfo:latest`. Der Workflow `.github/workflows/docker-ghcr.yml` testet vor dem Build, baut linux/amd64 und linux/arm64 und veröffentlicht bei Push auf main latest und den vollständigen Commit-SHA als Tags. v-Tags werden zusätzlich als Image-Tags übernommen. Pull Requests bauen ohne Veröffentlichung. Ein Workflow im Repository bedeutet noch keinen erfolgreichen Build. GHCR-Pakete können anfangs privat sein: Für anonymes Pull gegebenenfalls Package Settings auf Public stellen. Ein öffentliches Repository garantiert kein öffentliches Package.

Die Compose-Datei verwendet das GHCR-Image ohne lokalen Build. In Portainer als Stack einfügen und Umgebungsvariablen explizit setzen. Lokale .env-Dateien werden vom Portainer-Webeditor nicht automatisch geladen. Vorher erfolgreichen GHCR-Build prüfen. Nicht für Swarm konzipiert.

```sh
cp .env.example .env
joe .env
# ADMIN_PASSWORD mindestens 16 Zeichen
# MCP_TOKEN optional, mindestens 32 Zeichen; leer deaktiviert MCP
docker compose pull
docker compose up -d
docker compose logs -f
```

Für lokalen Build: `docker build -t hai-flexpowerinfo:local .` und in Compose die Image-Referenz entsprechend ändern.

Standardzugriff am Docker-Host: http://127.0.0.1:8098 . Bei rein lokalem HTTP-Test COOKIE_SECURE=false setzen, bei HTTPS true. Für LAN-Zugriff BIND_IP auf Server-LAN-IP setzen; ALLOWED_HOSTS enthält erlaubte Hostnamen/IPs ohne Port, ALLOWED_ORIGINS vollständige Origins inklusive Schema und gegebenenfalls Port. health prüft den Prozess, nicht die Aktualität der Marktdaten. Externer Zugriff ausschließlich über HTTPS oder VPN. Reverse Proxy mit Body-Limit auch für chunked Requests und zusätzlichem Rate-Limit betreiben. Genau ein Worker erforderlich: Sitzungen und Hintergrunddienste laufen im Prozess. Sitzungen verfallen nach acht Stunden und bei Neustart.

## Tarifverwaltung

Alle Eingaben netto. Energie-/Referenzwert, bis zu 50 frei benannte ct/kWh-Bestandteile, Umsatzsteuer, Grundpreis, Servicegebühr und optionale Energie-Untergrenze sind einstellbar. Gebührenbasis: Energie oder Energie plus Bestandteile. Untergrenze wirkt vor Zuschlägen. Ohne Untergrenze bleiben negative Energiepreise und negative prozentuale Gebühren erhalten; nur verwenden, wenn der Vertrag dies vorsieht. Kein automatischer Monatsdurchschnitt, keine Verbrauchsmessung, keine Servicegebühr auf den Grundpreis. Referenzwerte sind manuell. Ein vollständiger Arbeitspreis darf nicht nochmals um bereits enthaltene Bestandteile erhöht werden.

Speichern archiviert eine Tarifrevision mit Speicherzeitpunkt. Die Tabelle verwendet immer den aktuellen Tarif, keine historische Wirksamkeitsauswahl. Import lädt ins Formular zur Prüfung, Speichern validiert serverseitig. Export enthält keine Zugangsdaten. Ergebnisse sind Schätzungen, kein Abrechnungsnachweis.

Auto-Abruf standardmäßig aus; mindestens 15 Minuten zwischen Versuchen, auch nach Fehlern. Quelle aWATTar DE Day-Ahead; tatsächliche Quellintervalle bleiben erhalten. EUR/MWh geteilt durch 10 ergibt ct/kWh. Letzter erfolgreicher Datensatz bleibt erhalten, kein langfristiges Marktarchiv. Nach einer Stunde ohne erfolgreichen Abruf erscheint eine Warnung; abgelaufene Intervalle sind nie aktueller Börsenpreis. Grafik ist eine beschriftete Intervallübersicht, kein maßstabsgetreues Wertediagramm.

## MCP

Gleicher Port, Endpunkt `/mcp`, offizielles Python MCP SDK mit Streamable HTTP. Header `Authorization: Bearer DEIN_MCP_TOKEN`. Lesende Tools get_current_price, get_price_schedule(start_ms=0,end_ms=0), get_tariff, get_status. Client muss statische Bearer-Tokens unterstützen, keine automatische OAuth-Discovery. Nur über HTTPS/VPN verbinden. Host-/Origin-Konfiguration vor Remote-Einsatz prüfen.

## Telegram

TELEGRAM_BOT_TOKEN, TELEGRAM_USER_IDS und TELEGRAM_CHAT_IDS setzen; IDs kommagetrennt. Sender und Zielchat müssen beide freigegeben sein. Ohne alle drei Angaben bleibt Telegram aus. Dedizierten Bot ohne aktiven Webhook verwenden. Long Polling: nicht gleichzeitig einen anderen Poller mit demselben Bot betreiben. Befehle /preis /verlauf /tarif /status /hilfe. Noch keine Inline-Tastatur oder Schwellenwert-Benachrichtigungen. Offset wird persistiert; nach Netzwerkfehlern sind wiederholte Antworten möglich.

## Tests und Sicherheit

```sh
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
```

Core-Tests prüfen Formeln, Untergrenze, negative Werte, Einheiten, Intervalle, Validierung und Speicherung. Zusätzliche Web-/MCP-Tests prüfen Login, Logout, CSRF und MCP initialize/tools. Diese zusätzlichen Tests sind vor dem ersten CI-Lauf noch nicht als bestanden bestätigt. Liveanbieter und Telegram benötigen gesonderte Integrationstests. Keine echten Zugangsdaten in Tests.

HttpOnly-Sitzung, SameSite-Cookies, CSRF-Header, Origin-/Host-Allowlist und Login-Limit sind enthalten. Admin-Passwort stammt aus der Container-Umgebung und wird mit scrypt zum Vergleich abgeleitet. Secrets und Volume vor fremdem Zugriff schützen. SQLite-Backup bei gestopptem Container. Keine Passwörter oder Tokens ins Repository. README und GitHub Pages bleiben Produkt-Zielbild; diese Datei dokumentiert den tatsächlich enthaltenen Umfang und seine Grenzen.
