# MCP: immer mit Token

Endpunkt /mcp oder /mcp/, Host-Port 8911. Jede HTTP-Anfrage benötigt `Authorization: Bearer DEIN_MCP_TOKEN`: initialize, tools/list, get_current_price, get_price_schedule, get_tariff, get_status und update_tariff. MCP_PUBLIC wird ignoriert. Kein konfigurierter Token bedeutet gesperrt, niemals anonym. Token mindestens 32 Zeichen; extern HTTPS oder VPN. Keine OAuth-Discovery.

```dotenv
MCP_TOKEN=EIGENER_ZUFAELLIGER_TOKEN_MINDESTENS_32_ZEICHEN
```

Der Token erlaubt Lesen und Schreiben. update_tariff erwartet das vollständige Objekt aus get_tariff, validiert und speichert es als Revision und setzt confirmed=false. Änderungen vorher mit dem Nutzer abstimmen. Keine getrennten Read-/Write-Rollen, keine Konflikterkennung für parallele Änderungen, keine Secret- oder Serverbefehlsverwaltung.

Web ist ebenfalls geschützt: Preise und Tarifwerte nur nach Web-Login. /api/public ist abgeschaltet, auch bei alten PUBLIC_DASHBOARD=true-Werten. Web-Session ersetzt keinen MCP-Token und umgekehrt.

Nach erfolgreichem GHCR-Build Image neu ziehen und Stack aktualisieren. Ein Commit allein aktualisiert keinen Container. Authentifizierungs- und Schreibtests müssen im CI erfolgreich durchlaufen; nicht aus dieser Dokumentation ableiten.
