# Web-Einstieg direkt unter Root

Einzige Einstiegsadresse: `http://SERVER_IP:8911/` beziehungsweise die konfigurierte HTTPS-Domain ohne Zusatzpfad. Ohne Sitzung zeigt dieselbe Oberfläche die Anmeldung. Nach erfolgreichem Login lädt JavaScript die geschützten Daten und zeigt das Dashboard, ohne die Adresse zu wechseln. Abmelden führt zurück zur Anmeldung innerhalb derselben Seite.

Alte Links `/admin`, `/admin/`, `/login` und `/login/` leiten auf `/` um. Die HTML-/CSS-/JavaScript-Oberfläche enthält keine persönlichen Tarifwerte. Alle Preis-, Status- und Tarif-APIs bleiben sitzungspflichtig, `/api/public` bleibt abgeschaltet. MCP bleibt für jede Anfrage separat tokenpflichtig. `/health` zeigt nur Prozessstatus für Docker.

Diese Root-Regel ersetzt die älteren Pfadangaben zu `/login` und `/admin` in INSTALL.md. Port 8911, docker-compose.yml, highfishNetwork und sämtliche Zugangsdaten bleiben unverändert. Nach erfolgreichem Build neues Image herunterladen und Stack neu bereitstellen. Kein Nachweis eines erfolgreichen CI-Laufs allein durch diesen Commit.
