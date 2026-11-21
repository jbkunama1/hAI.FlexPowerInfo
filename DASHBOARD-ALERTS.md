# Alarmgrenzen im Dashboard einstellen

Nach Anmeldung unter / befindet sich am Ende des Dashboards der Bereich Marktpreisalarme per Telegram. Hier lassen sich Aktivierung, Untergrenze und Obergrenze in ct/kWh brutto frei einstellen und speichern. 30 und 42 sind nur Backend-Startwerte, keine fest programmierten Alarmgrenzen. Negative Werte und Nachkommastellen sind erlaubt; Untergrenze muss kleiner als Obergrenze sein. Beide Grenzen werden gemeinsam verwendet.

Die Oberfläche nutzt die bestehende GET/POST /api/market-alerts API mit Sitzung und CSRF-Token. Speichern verändert nur die Alarmkonfiguration, nicht den Tarif. Neu laden verwirft ungespeicherte Formulareingaben. Die periodische Dashboard-Aktualisierung überschreibt keine Alarm-Entwürfe. Der Bereich bleibt ohne Anmeldung verborgen. Bei fehlendem Alarm-Backend wird ein Fehler angezeigt und das Formular bleibt gesperrt.

Alarmbasis bleibt der Börsenintervall-Modellpreis inklusive gespeicherter Zuschläge, Gebühren und Umsatzsteuer, ohne Grundpreis, unabhängig vom Monatsmodell. Empfänger sind private Chats aller TELEGRAM_USER_IDS. Aktivierung und geänderte Grenzen können beim nächsten gültigen Prüfzyklus eine Nachricht auslösen. Details und Zustellgrenzen siehe MARKET-ALERTS.md; dessen Hinweis auf den zuvor fehlenden Dashboard-Editor ist durch diese Ergänzung überholt.

Nach erfolgreichem Image-Build Container aktualisieren und Browser neu laden. Kein automatisches Live-Deployment durch den Commit. Browser-, Authentifizierungs- und Telegram-Live-Tests dieser Oberfläche sind noch zu verifizieren.
