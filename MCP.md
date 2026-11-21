# MCP: erreichbar, aber immer authentifiziert

Endpunkt /mcp oder /mcp/, Host-Port 8911. Jede HTTP-Anfrage benötigt `Authorization: Bearer DEIN_MCP_TOKEN`. Gilt auch für initialize, tools/list, get_current_price, get_price_schedule, get_tariff, get_status und update_tariff. Kein anonymer Modus: MCP_PUBLIC wird ignoriert. Kein Token konfiguriert bedeutet gesperrter MCP, nicht öffentliche Freigabe. Token mindestens 32 Zeichen. Extern HTTPS oder VPN. Kein OAuth-Discovery-Server.

## Portainer

```dotenv
MCP_TOKEN=EIGENER_ZUFAELLIGER_TOKEN_MINDESTENS_32_ZEICHEN
```

MCP_PUBLIC aus den Stack-Variablen entfernen; ein alter Wert true umgeht die neue Prüfung nicht. Image nach erfolgreichem GHCR-Build neu ziehen und aktualisierten Stack bereitstellen. Keine echten Tokens ins Repository schreiben.

Der Token erlaubt Lesen und Schreiben. update_tariff erwartet das vollständige Objekt aus get_tariff, validiert es, speichert es als neue Revision und setzt confirmed=false. Nicht nur einen Teil der Felder senden. Vorher gewünschte Änderungen mit dem Nutzer prüfen. Keine separate Read-only-Rolle, keine Konflikterkennung für parallele Änderungen, keine Secret- oder Betriebssystem-Schreibzugriffe. Dieselbe Token-Prüfung schützt beide URL-Varianten und alle HTTP-Methoden.

PUBLIC_DASHBOARD ist unabhängig: true lässt die Web-Preise öffentlich, false sperrt die öffentliche Preis-API. /admin bleibt mit separatem Admin-Login geschützt. Falls alle Tarif-/Preisdaten privat bleiben sollen, PUBLIC_DASHBOARD=false setzen.

Die neuen Authentifizierungs-/Schreibtests sind enthalten, ihr erfolgreicher CI-Lauf ist vor dem Build noch zu bestätigen. Ein Commit allein aktualisiert keinen laufenden Container.
