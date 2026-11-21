# Telegram – highfishAI

## ENV

```dotenv
TELEGRAM_BOT_TOKEN=TOKEN_DES_EIGENEN_BOTS
TELEGRAM_USER_IDS=123456789
TELEGRAM_ADMIN_IDS=123456789
```

Alle IDs numerisch, mehrere IDs kommagetrennt. Ohne ADMIN_IDS gibt es keine Telegram-Schreibrechte. Admin muss zusätzlich in USER_IDS stehen. Ohne CHAT_IDS werden ausschließlich freigegebene private Chats akzeptiert. Eine optionale CHAT_IDS-Liste erlaubt zusätzliche Zielchats, aber Admin-Änderungen bleiben auf private Chats begrenzt.

/start sendet die Begrüßung mit Inline-Menü. Kein automatischer Versand an alle beim Containerstart. Befehle: /preis, /verlauf, /grafik, /tarif, /status, /hilfe, /admin, /cancel. Emoji- und HTML-Auszeichnung; beliebige Buttonfarben unterstützt diese Umsetzung nicht.

Die PNG-Grafik verwendet echte verfügbare Quellintervalle, bis zu 96. Balkenbreite folgt der Zeitdauer; Grün markiert nichtnegative Werte, Violett negative. Weiße Linie ist Null. Zeitraum, Min/Max und Einheit stehen in der Bildunterschrift; die Grafik selbst hat keine beschrifteten Achsen. Bei fehlenden Daten wird keine Kurve erfunden. Bei festen oder manuellen Preisen kann der Tarifverlauf konstant sein. Nur Tarifschätzung.

Admin-Menü: Marktdatenabruf (mit bestehender 15-Minuten-Sperre), Auto-Abruf umschalten und Umsatzsteuer, Netto-Grundpreis, festen/manuellen Energieanteil, Serviceprozentsatz und Abrufintervall ändern. Keine willkürlichen Serverbefehle, keine Secret-Verwaltung. Vollständige Bestandteile und Modell in der Web-Administration pflegen. Energieanteil wirkt nur im festen oder manuellen Modell.

Tarifänderungen benötigen einen zusätzlichen Speichern-Button, verfallen nach fünf Minuten und sind an Nutzer und Chat gebunden. Zwischenzeitlich geänderte Tarife werden erkannt. Speichern hebt die Prüfbestätigung auf. Entwürfe liegen nur im RAM und verschwinden bei Neustart. Wiederholte Nachrichten nach Netzwerkfehlern sind möglich; abgelaufene/verwendete Bestätigungen speichern nicht erneut. Der bestehende Web-/MCP-Betrieb bleibt unverändert.

Grafik-Encoder wurde lokal auf PNG-Signatur und Dimensionen geprüft. Zusätzliche Tests decken Berechtigungen, Werteprüfung und Starttext ab; vollständiger CI-/Telegram-Live-Test ist noch ausstehend. Keine echten Bot-Nachrichten während Unit-Tests. Nach erfolgreichem Build aktualisierte docker-compose.yml übernehmen, Image neu ziehen und Stack neu bereitstellen.
