<p align="center"><img src="docs/assets/hero.svg" alt="hAI.FlexPowerInfo – Dein Strompreis. Dein Tarif. Deine Kontrolle." width="100%"></p>
<h1 align="center">⚡ hAI.FlexPowerInfo · highfishAI</h1>
<p align="center">Dein Strompreis. Dein Tarif. Dein geschützter Zugriff.</p>
<p align="center"><a href="LICENSE"><img src="https://img.shields.io/badge/Lizenz-MIT-22c55e?style=for-the-badge" alt="MIT"></a> <img src="https://img.shields.io/badge/Web-Login%20Required-06b6d4?style=for-the-badge" alt="Web Login erforderlich"> <img src="https://img.shields.io/badge/MCP-Token%20Required-a855f7?style=for-the-badge" alt="MCP Token erforderlich"> <img src="https://img.shields.io/badge/Docker-Port%208911-2496ed?style=for-the-badge" alt="Docker Port 8911"></p>

## 🌈 Eine Preisbasis. Drei geschützte Zugänge.

hAI.FlexPowerInfo verbindet Börsenpreise mit deinem persönlichen Tarif. Eine gemeinsame Berechnung für Browser, Telegram und KI-Agenten, selbst gehostet auf deiner Infrastruktur. Das Zielbild ist nachvollziehbare Tariftransparenz ohne anonymen Zugriff auf deine Daten.

| Zugang | Schutz |
| --- | --- |
| 🌐 Web-Dashboard und Tarifverwaltung | Anmeldung mit ADMIN_USER und ADMIN_PASSWORD |
| 🤖 MCP /mcp | Bearer-Token für jede Anfrage, Lesen und Schreiben |
| 💬 Telegram | Nutzerfreigabe, separate Admin-IDs für Änderungen |

Ohne Web-Anmeldung ist nur die Login-Oberfläche samt benötigtem JavaScript/CSS erreichbar. /health meldet ausschließlich den Prozessstatus für Docker, keine Preise oder Einstellungen. Dashboard, Preise, Tarif und Status benötigen eine Sitzung. Die frühere /api/public ist abgeschaltet. PUBLIC_DASHBOARD und MCP_PUBLIC können keine anonyme Freigabe mehr aktivieren.

## 🎛️ Dein Tarif

Dynamischer Energiepreis, fester Wert oder manuelle Monatsreferenz. Frei benannte Preisbestandteile, Steuern, Grundpreis, Servicegebühr und optionale Energie-Untergrenze. Alle Eingaben netto, Grundpreis separat. Ausgangspunkt Immergrün, ohne feste Anbieterbindung.

```text
⚡ Energie + 🧩 Zuschläge + 🧮 Servicegebühr
= Netto-Arbeitspreis + Umsatzsteuer
= Geschätzter Brutto-Arbeitspreis in ct/kWh
```

## 🔐 Agenten mit Token

Tools: get_current_price, get_price_schedule, get_tariff, get_status, update_tariff. Tokenpflicht auch für initialize und tools/list. Leerer MCP_TOKEN sperrt MCP; keine OAuth-Discovery. Der Token erlaubt Lesen und Schreiben. update_tariff ersetzt den vollständigen validierten Tarif und setzt confirmed=false. Änderungen vorher mit dem Nutzer abstimmen. Keine Secret- oder Serverbefehlsverwaltung.

## 💬 Telegram mit Admin-Menü

Private Chats benötigen Bot-Token und Nutzer-ID. TELEGRAM_ADMIN_IDS erlaubt zusätzlich bestätigte Änderungen ausgewählter Tarifwerte. Startnachricht, Inline-Menüs, farbige Preisgrafik und Statusauskunft. Details in TELEGRAM.md.

## 🐳 Deine Infrastruktur

Ein Container, SQLite-Volume, docker-compose.yml, Port 8911 → 8080, externes Netzwerk highfishNetwork. PUBLIC_URL bezeichnet lediglich deine Zugriffsadresse, nicht eine öffentliche Datenfreigabe. Für Internetbetrieb HTTPS/VPN und Proxy-Limits. ADMIN_PASSWORD mindestens 4 Zeichen, MCP_TOKEN mindestens 32 Zeichen.

## ⏱️ Nachvollziehbar statt scheinbar exakt

Optionaler Abruf alle 15 Minuten; Quelle und Vertrag bestimmen Preisintervalle. Keine erfundenen Viertelstunden, Monatsreferenzen manuell. Veraltete Daten und ungeprüfte Tarife sichtbar machen. Kein Abrechnungsnachweis, keine Verbrauchsmessung und keine Servicegebühr auf den Grundpreis. Weitere Automatisierung bleibt Teil des Zielbilds. Funktionsbeschreibung ist kein Build- oder Live-Testnachweis.

[Installation](INSTALL.md) · [MCP](MCP.md) · [Telegram](TELEGRAM.md) · [MIT](LICENSE)

Die statische GitHub-Pages-Seite ist ausschließlich Projektbeschreibung, keine laufende Preisinstanz. Ein Projekt von highfishAI. Keine offizielle Anwendung von Immergrün oder aWATTar.
