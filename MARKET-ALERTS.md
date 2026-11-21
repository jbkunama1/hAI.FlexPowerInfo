# Marktpreisalarme

Der Docker-Einstiegspunkt alert_gateway:app erweitert den bestehenden Gateway ohne dessen Login-, MCP- oder Telegram-Chatlogik zu ersetzen.

Neue authentifizierte MCP-Tools: get_market_alerts und update_market_alerts. Beispielkonfiguration: {"enabled":true,"lower":"30","upper":"42"}. Konfiguration vor Schreibzugriff mit dem Nutzer abstimmen. Standard: ausgeschaltet, Grenzen 30 und 42 ct/kWh brutto. Kein neuer Dashboard-Editor in dieser Version. Alternativ GET/POST /api/market-alerts, nur mit Web-Sitzung; POST braucht den bestehenden x-csrf-token.

Aktivierte Alarme pruefen alle zehn Sekunden das aktuell gueltige Quellintervall. Der gemeinsame Abruf wird angefordert, auch wenn der Tarif-Autoabruf aus ist; die bestehende 15-Minuten-Abrufsperre bleibt bestehen. Fehlende, zukuenftige oder mehr als eine Stunde alte Abrufdaten sowie fehlende aktuelle Intervalle erzeugen keinen Preisalarm.

Alarmbasis ist immer der Boersenintervallpreis, unabhaengig vom gespeicherten Tarifmodell und manuellen Energiepreis. Gespeicherte Bestandteile, Energie-Untergrenze, Servicegebuehr und Umsatzsteuer werden gemaess bestehender calculate-Funktion angewendet. Der Grundpreis wird nicht eingerechnet. Es erfolgt keine automatische Umdeutung oder Umrechnung persoenlicher Netto-/Brutto-Eingaben. Die Nachricht kennzeichnet die Berechnung als Modell, nicht als persoenlichen Monatsabrechnungspreis.

Telegram: bestehender TELEGRAM_BOT_TOKEN. Ziele sind private Chats aller TELEGRAM_USER_IDS, keine Gruppen aus TELEGRAM_CHAT_IDS. Nutzer muessen den Bot zuvor gestartet haben. Nach Aktivierung erfolgt beim ersten gueltigen Wert ausserhalb der Grenzen eine Nachricht. Bei exakt 30/42 kein Alarm. Persistenter Bereichsstatus je Empfaenger verhindert Wiederholungen, auch nach Neustart. Nach beobachteter Rueckkehr in den Normalbereich ist ein erneuter Alarm moeglich; direkter Wechsel von niedrig zu hoch meldet ebenfalls. Deaktivierung setzt den Zustand beim naechsten Pruefzyklus zurueck. Geaenderte Grenzen koennen eine neue Meldung ausloesen. Keine Rueckkehrmeldung, keine historischen Nachholalarme, keine Vorabmeldungen fuer zukuenftige Intervalle.

Fehlgeschlagene Zustellungen werden fruehestens nach 60 Sekunden erneut versucht, solange der Alarm noch zutrifft. Bei unklarem Netzwerkfehler oder Absturz zwischen erfolgreichem Versand und Speicherung sind doppelte Meldungen moeglich; kein Exactly-once-Versprechen. Tarifaenderungen koennen ebenfalls Bereichswechsel ausloesen.

Nach Freigabe und erfolgreichem Build Image aktualisieren und Container neu bereitstellen. Ein Repository-Commit aktiviert keine laufende Instanz. Danach ueber update_market_alerts aktivieren. Unit-Tests senden keine Nachrichten; vollstaendige CI-, Auth-, Persistenz- und Telegram-Live-Tests sind gesondert zu pruefen.
