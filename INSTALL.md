# Einrichtung

Maßgeblich: `docker-compose.yml`. In Portainer diesen Pfad wählen. Host-Port 8911, intern 8080, bestehendes externes Netzwerk highfishNetwork. Image ghcr.io/jbkunama1/hai.flexpowerinfo:latest; erfolgreicher GHCR-Build ist vor Deployment zu prüfen. Ein öffentliches Repo garantiert kein öffentliches GHCR-Paket.

## Minimale ENV für LAN-Test

```dotenv
ADMIN_USER=admin
ADMIN_PASSWORD=EIGENES_PASSWORT_MINDESTENS_16_ZEICHEN
COOKIE_SECURE=false
PUBLIC_DASHBOARD=true
MCP_PUBLIC=true
```

BIND_IP ist standardmäßig 0.0.0.0. Damit wird Port 8911 auf allen Host-IPv4-Schnittstellen veröffentlicht; Firewall beachten. Browser: http://SERVER_IP:8911 . Verwaltung: /admin. PUBLIC_URL kann beim lokalen Test leer bleiben. HTTP niemals ungeschützt ins Internet freigeben.

## HTTPS-Domain

```dotenv
PUBLIC_URL=https://strom.example.org
COOKIE_SECURE=true
```

Beispieldomain ersetzen. PUBLIC_URL ist eine reine Origin ohne Pfad oder abschließenden Slash. Daraus werden erlaubter Host und Origin abgeleitet. Ohne PUBLIC_URL werden alle Hosts akzeptiert und Origin-Header gegen die angesprochene Origin geprüft. Für Internetbetrieb PUBLIC_URL setzen. Erweiterte ALLOWED_HOSTS/ALLOWED_ORIGINS sind im Code weiterhin möglich, werden aber nicht mehr durch die Standard-Compose-Datei durchgereicht. Keine Wildcard-Origin-Freigabe und kein CORS für beliebige Websites.

## Öffentlicher MCP

MCP_PUBLIC=true: /mcp ohne Token, ausschließlich lesend. Öffentlichkeit umfasst geschätzte Preise, Bestandteile, Modell, Umsatzsteuer, Grundpreis und Aktualität. Kein Tarifname, vollständiger Admin-Tarif, Secrets oder interne Fehlertexte. PUBLIC_DASHBOARD=false schaltet nur die öffentliche Webansicht ab, nicht MCP. Für privaten MCP MCP_PUBLIC=false und MCP_TOKEN mit mindestens 32 Zeichen setzen. Statischer Bearer-Token; keine OAuth-Discovery. MCP_PUBLIC=false mit leerem Token sperrt MCP. /admin und /api/status sowie Tarifänderungen bleiben mit Login/CSRF geschützt.

60 öffentliche Daten-/MCP-Anfragen pro Minute je Client-IP auf Anwendungsebene. Genau einen Worker betreiben. Reverse Proxy zusätzlich mit Body-Limit, TLS und Rate-Limit konfigurieren; Forwarded-Header nur von vertrauenswürdigen Proxys übernehmen. Mehrere Clients können ohne korrekte Proxy-Konfiguration ein gemeinsames Limit teilen.

## Telegram

```dotenv
TELEGRAM_BOT_TOKEN=TOKEN_DES_EIGENEN_BOTS
TELEGRAM_USER_IDS=123456789
```

Für Privat-Chats reicht das. Nutzer muss den Bot starten. Mehrere Nutzer-IDs mit Komma trennen. Ohne TELEGRAM_CHAT_IDS sind nur private Chats zulässig, deren Chat-ID der freigegebenen Nutzer-ID entspricht. Optional TELEGRAM_CHAT_IDS setzen für ausdrücklich erlaubte Zielchats; Sender muss weiterhin freigegeben sein. Dedizierter Bot, kein aktiver Webhook und kein zweiter Poller. Textbefehle /preis /verlauf /tarif /status /hilfe; Inline-Menü inklusive. Keine Schwellenwertalarme. Nach Netzwerkfehlern sind wiederholte Antworten möglich. Keine echten Tokens ins Repository schreiben.

## Tarif und Grenzen

Tarifeingaben netto; dynamisch, fest oder manueller Referenzwert. Servicegebühr auf Energie oder Energie plus Zuschläge, keine Gebühr auf Grundpreis. Untergrenze wirkt vor Zuschlägen. Negative Gebührenbasis bleibt ohne Untergrenze negativ. Alle Tabellenwerte verwenden den aktuellen Tarif, gespeicherte Revisionen sind noch keine historische Wirksamkeitsauswahl. Kein automatisch berechneter Monatsdurchschnitt und kein langfristiges Marktarchiv. Quelle aWATTar DE, Quellintervalle unverändert. Auto-Abruf standardmäßig aus; mindestens 15 Minuten zwischen Versuchen. SQLite-Volume sichern, genau ein Worker. Sitzungen verfallen nach acht Stunden oder Neustart.

## Build und Tests

Docker startet `gateway:app`; `app.py` enthält den geschützten Tarifdienst und die Admin-Routen. Der öffentliche Einstieg und vereinfachtes Telegram werden über gateway.py integriert.

```sh
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
docker compose -f docker-compose.yml pull
docker compose -f docker-compose.yml up -d
```

Neue Gateway-/Telegram-Tests sind enthalten, aber vor dem CI-Lauf nicht als bestanden bestätigt. Live-MCP, Browser, Telegram und aktueller Build müssen separat verifiziert werden. README/Projektseite sind Produktbeschreibung, kein Testprotokoll.
