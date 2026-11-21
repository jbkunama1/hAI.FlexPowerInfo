# Einzelnen Modellpreis abrufen

GET /price.txt?token=DEIN_LESETOKEN gibt bei Erfolg ausschliesslich eine Dezimalzahl mit Punkt zurueck, beispielsweise 29.437. Einheit: ct/kWh brutto. Content-Type text/plain, kein JSON, keine Einheit im Body, keine weiteren Tarifdaten. Negative Werte sind moeglich. Der Wert wird nicht auf drei Stellen gerundet.

Berechnung exakt durch dieselbe evaluate-Funktion wie bei Marktpreisalarmen: aktuelles Boersenintervall plus gespeicherte Zuschlaege, Servicegebuehr und Umsatzsteuer, unter Beachtung der gespeicherten Energie-Untergrenze; ohne Grundpreis. Der manuelle Monatsreferenzwert und das Tarifmodell werden fuer diesen Export ignoriert. Die internen Grenzen 30/42 dienen nur dem ungenutzten Bereichsergebnis und aendern den Zahlenwert nicht. Der Export ist unabhaengig von aktivierten Telegram-Alarmen. Kein bestaetigter EnerFlex-Blue-Abrechnungspreis.

## Einrichtung

In der privaten Container-Umgebung PRICE_READ_TOKEN setzen: 32 bis 256 Zeichen, ausschliesslich Buchstaben, Ziffern, Bindestrich und Unterstrich. Zum Beispiel lokal erzeugen mit: python -c "import secrets; print(secrets.token_urlsafe(32))". Niemals einen echten Token ins Repository schreiben. Eigenstaendigen Token verwenden, nicht MCP_TOKEN oder ADMIN_PASSWORD; identische Werte werden abgelehnt. Ohne gueltigen Token bleibt der Endpunkt gesperrt.

Aktualisierte docker-compose.yml uebernehmen, erfolgreich gebautes neues Image ziehen und Container neu erstellen. Docker-Einstiegspunkt ist jetzt price_gateway:app; dieser umschliesst den bisherigen geschuetzten Alarm-Gateway. Port 8911, highfishNetwork und Datenvolume bleiben gleich. Keine Live-Konfiguration oder Bereitstellung durch den Repository-Commit.

Die URL auf der bekannten LAN-Instanz lautet nach Einrichtung:

http://192.168.178.6:8911/price.txt?token=DEIN_LESETOKEN

DEIN_LESETOKEN ist ein Platzhalter, kein funktionsfaehiger Token. Der Link erlaubt nur den Zahlenabruf, keine Web-Anmeldung und keine MCP-Schreibzugriffe. Rotation durch Austausch der ENV und Neuerstellen des Containers. Der Link wird nicht automatisch im Dashboard angezeigt.

## Aktualitaet und Fehler

Bei konfiguriertem Lesetoken fordert ein Hintergrundprozess alle 30 Sekunden den gemeinsamen Marktdatenabruf an. Dessen bestehende 15-Minuten-Sperre bleibt bestehen. Das funktioniert auch bei ausgeschalteten Alarmen oder ausgeschaltetem Tarif-Autoabruf. Ein HTTP-GET selbst aendert keine Daten und wartet nicht auf einen externen Abruf. Direkt nach Erststart kann daher voruebergehend 503 kommen.

401 bei fehlendem/falschem/ungueltig konfiguriertem Token. 503 bei fehlenden, in der Zukunft liegenden oder ueber eine Stunde alten Abrufdaten, fehlendem aktuellen Intervall oder Berechnungsfehler. Kein 0-Ersatz und kein alter Preis ausserhalb seines Intervalls. Erfolgs- und Anwendungsfehlerantworten werden mit no-store und no-referrer ausgeliefert. Clients muessen HTTP-Status und Aktualitaet auswerten und bei Fehlern eine sichere Automation waehlen, nicht einen frueheren Preis unbegrenzt weiterverwenden.

## Sicherheit und Integrationen

Token-URLs koennen in Browserhistorie, Client- und Reverse-Proxy-Logs stehen. Uvicorn-Access-Logs bleiben deaktiviert; Proxy-Logs muessen separat ohne Query-Tokens konfiguriert werden. Link nicht teilen; Zugriff nur im vertrauenswuerdigen LAN, ueber VPN oder HTTPS. Keine anonyme Freigabe von Dashboard oder MCP.

FHEM HTTPMOD und Home Assistant REST koennen diese URL regelmaessig per GET abrufen. Fuer FHEM eine Regex fuer die gesamte Zahl verwenden: ^\s*(-?\d+(?:\.\d+)?)\s*$ . In Home Assistant kann value_template auf '{{ value | trim }}' gesetzt werden; Einheit ct/kWh. Diese Integration muss in der jeweiligen Installation gesondert eingerichtet und auf Fehlerverhalten geprueft werden. Keine Aenderungen an FHEM oder HA durch diesen Commit.

Tests fuer Tokenpruefung, Nur-Lese-Zugriff, Klartextformat und Fehlerantworten sind enthalten. Vollstaendige CI-, Container-, Authentifizierungs-, FHEM-/HA- und LAN-Live-Tests sind noch zu pruefen.
