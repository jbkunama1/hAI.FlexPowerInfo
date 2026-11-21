# Einrichtung

Stack-Datei docker-compose.yml, Host-Port 8911, intern 8080, externes vorhandenes Netzwerk highfishNetwork. Image ghcr.io/jbkunama1/hai.flexpowerinfo:latest. Build und Package-Zugriff vor Deployment prüfen. In Portainer Variablen explizit setzen.

```dotenv
ADMIN_USER=admin
ADMIN_PASSWORD=EIGENES_PASSWORT_MINDESTENS_4_ZEICHEN
COOKIE_SECURE=false
PUBLIC_URL=
PUBLIC_DASHBOARD=true
MCP_TOKEN=EIGENER_ZUFAELLIGER_TOKEN_MINDESTENS_32_ZEICHEN
TELEGRAM_BOT_TOKEN=
TELEGRAM_USER_IDS=
TELEGRAM_ADMIN_IDS=
TELEGRAM_CHAT_IDS=
```

HTTP-Konfiguration nur zum LAN-Test. Für HTTPS PUBLIC_URL=https://DEINE_DOMAIN setzen und COOKIE_SECURE=true. Die PUBLIC_URL ist eine Origin ohne Pfad. BIND_IP ist standardmäßig 0.0.0.0, also alle Host-IPv4-Schnittstellen; Firewall beachten. Ohne PUBLIC_URL werden Hosts offen akzeptiert und vorhandene Origins gegen die angesprochene Origin geprüft. Für Internetbetrieb feste PUBLIC_URL, TLS und Proxy-Limits verwenden. Erweiterte Host-/Origin-Variablen sind nicht Teil der Standard-Compose-Umgebung.

MCP verlangt immer den Bearer-Token, zum Lesen UND Schreiben. Leerer MCP_TOKEN sperrt MCP. MCP_PUBLIC ist entfernt und wird im Gateway ignoriert. Details und update_tariff: MCP.md. Öffentliche Webansicht unabhängig über PUBLIC_DASHBOARD; für private Preisdaten false setzen. Admin-Login bleibt geschützt; Mindestpasswortlänge 4 Zeichen. Tokens nie ins Repository schreiben.

Telegram privat: Bot-Token und Nutzer-ID reichen. Admin muss zusätzlich in TELEGRAM_ADMIN_IDS stehen. Optionale Chat-Liste für explizite Ziele; Schreiben nur privat. Start, Menüs, Grafik und Bestätigungen: TELEGRAM.md. Kein zweiter Poller oder aktiver Webhook für denselben Bot.

Tarifwerte netto; dynamisch, fest oder manueller Monats-/Referenzwert. Kein automatischer Monatsdurchschnitt und keine Verbrauchsmessung. Servicegebühr auf Energie oder Energie plus Zuschläge, nicht auf Grundpreis. Untergrenze vor Zuschlägen; ohne Untergrenze bleiben negative Preise und Gebührenbasis negativ. Alle Tabellenwerte verwenden aktuellen Tarif. Revisionen sind keine historische Wirksamkeitsauswahl. Auto-Abruf standardmäßig aus, mindestens 15 Minuten zwischen Versuchen. SQLite-Volume sichern.

```sh
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
docker compose -f docker-compose.yml pull
docker compose -f docker-compose.yml up -d
```

Genau ein Worker, Containerstart gateway:app. Sessions acht Stunden beziehungsweise bis Neustart. Reverse Proxy mit Body-Limit auch für chunked Requests, Rate-Limit und vertrauenswürdig konfigurierten Forwarded-Headern. Preise sind Schätzungen, keine Abrechnungsnachweise. Tests/Build/Livezugriffe gesondert prüfen, keinen Erfolg aus der Dokumentation ableiten. Die alte compose.yaml nicht verwenden.
