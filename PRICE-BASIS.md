# Netto-/Brutto-Eingabe

Tarifbeträge benötigen eine ausdrückliche Preisbasis ohne UI-Vorauswahl. Das betrifft Energie-/Referenzwert, monatlichen Grundpreis, eine ausgefüllte Energie-Untergrenze und jeden zusätzlichen ct/kWh-Bestandteil. Prozentsätze sind keine Geldbeträge.

API/MCP: Bei Tarifschreibzugriffen ist price_basis als Objekt mit energy_ct und base_net sowie floor_ct bei gesetzter Untergrenze erforderlich. Erlaubte Werte: net oder gross. Jeder components-Eintrag benötigt ebenfalls price_basis: net oder gross. Fehlende oder ungültige Angaben werden serverseitig abgewiesen. Dies ersetzt die frühere Vorgabe ausschließlich netto einzugeben.

Bruttowerte werden beim Speichern mit dem angegebenen Tarif-Umsatzsteuersatz nach netto normalisiert. Gespeicherte und exportierte Beträge enthalten price_basis net; die vorhandene Berechnung erhebt die Umsatzsteuer bei der Ausgabe einmal. Nach dem Speichern zeigt das Formular die normalisierten Nettowerte und verlangt vor dem nächsten Speichern erneut die ausdrückliche Auswahl. Bei Änderung des Steuersatzes bleiben gespeicherte Nettowerte konstant.

Alte gespeicherte Tarife bleiben unverändert netto, da dies der bisherige Eingabevertrag war. Sie bleiben lesbar und berechenbar; vor erneutem Speichern oder Import muss der Nutzer die Basis ausdrücklich auswählen. Keine automatische Brutto-Annahme bei Kundenpreiseingaben.

Umfang: Tarifbeträge. Die separat konfigurierten Marktpreis-Alarmgrenzen bleiben vorerst ausschließlich brutto; dort gibt es noch keine Netto-/Brutto-Auswahl. Bestehende MCP-Beschreibungen und ältere Dokumentation mit NET-Vorgabe sind für Tarifschreibzugriffe durch diese Beschreibung ersetzt; die Tool-Beschreibung selbst wird in einem Folgeänderungssatz aktualisiert.
