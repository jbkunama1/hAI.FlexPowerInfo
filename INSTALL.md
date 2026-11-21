# Einrichtung: alle Anwendungsdaten geschützt

Stack-Datei docker-compose.yml, Host-Port 8911, intern 8080, externes vorhandenes Netzwerk highfishNetwork. Image ghcr.io/jbkunama1/hai.flexpowerinfo:latest. Build und Package-Zugriff vor Deployment prüfen. In Portainer Variablen explizit setzen.

```dotenv
ADMIN_USER=admin
ADMIN_PASSWORD=EIGENES_PASSWORT_MINDESTENS_4_ZEICHEN
COOKIE_SECURE=false
PUBLIC_URL=
MCP_TOKEN=EIGENER_ZUFAELLIGER_TOKEN_MINDESTENS_32_ZEICHEN
TELEGRAM_BOT_TOKEN=
TELEGRAM_USER_IDS=
TELEGRAM_ADMIN_IDS=
TELEGRAM_CHAT_IDS=
```

Diese HTTP-Konfiguration ist nur zum LAN-Test. Für HTTPS PUBLIC_URL=https://DEINE_DOMAIN und COOKIE_SECURE=true setzen. PUBLIC_URL ist eine Origin ohne Pfad und keine Freigabe für anonyme Besucher. BIND_IP standardmäßig 0.0.0.0, Firewall beachten. Für Internetbetrieb feste PUBLIC_URL, HTTPS/VPN und Reverse-Proxy-Limits verwenden.

Web: / und /admin leiten ohne Sitzung auf /login um. Erst nach Anmeldung liefern /api/status und Tarifverwaltung Daten. /api/public ist unabhängig von alten PUBLIC_DASHBOARD-Werten abgeschaltet. Die Login-Oberfläche und ihre CSS-/JS-Dateien enthalten keine persönlichen Tarifwerte und sind zur Anmeldung erreichbar. /health liefert ausschließlich Prozessstatus, damit der Docker-Healthcheck ohne Secrets funktioniert. Keine sonstige anonyme Datenansicht.

MCP: Bearer-Token zwingend für jede Anfrage, auch Lesen/Initialisierung und Schreiben. Leerer Token sperrt MCP, MCP_PUBLIC wird ignoriert. Details in MCP.md. Mindestpasswortlänge 4, MCP-Token mindestens 32 Zeichen. Token und Passwörter niemals ins Repository schreiben.

Telegram: Token und Nutzer-ID für Privat-Chats; zusätzliche TELEGRAM_ADMIN_IDS für Schreibrechte. Optionale Chat-Liste für explizite Ziele, Admin-Änderungen nur privat. Details in TELEGRAM.md. Keine parallelen Poller und kein aktiver Webhook beim selben Bot.

Alle Tarifwerte netto; dynamisch, fest oder manuelle Monatsreferenz. Keine Verbrauchsmessung oder automatische Monatsmittelung. Servicegebühr auf Energie oder Energie plus Zuschläge, nicht auf Grundpreis. Untergrenze vor Zuschlägen. Aktueller Tarif gilt für die angezeigte Tabelle; gespeicherte Revisionen sind noch keine historische Wirksamkeitsauswahl. Auto-Abruf standardmäßig aus, mindestens 15 Minuten zwischen Versuchen. SQLite-Volume sichern.

```sh
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
docker compose -f docker-compose.yml pull
docker compose -f docker-compose.yml up -d
```

Genau ein Worker, Einstieg gateway:app. Sessions acht Stunden oder bis Neustart. Reverse Proxy mit Body-Limit, Rate-Limit und nur vertrauenswürdigen Forwarded-Headern. Preisberechnungen sind Schätzungen, kein Abrechnungsnachweis. Neue Tests prüfen das Sperren früherer öffentlicher Zugänge; CI und Livebetrieb sind gesondert zu bestätigen. Die Altdatei compose.yaml nicht verwenden.
