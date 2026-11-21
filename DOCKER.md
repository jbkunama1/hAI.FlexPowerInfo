# Docker-Konvention

Die maßgebliche Stack-Datei ist `docker-compose.yml`. In Portainer diesen Dateinamen als Compose-Pfad verwenden.

Der Dienst verwendet das bestehende externe Netzwerk `highfishNetwork`. Es muss auf dem Docker-Zielhost vorhanden sein; der Stack legt es nicht selbst an. Ports, Umgebungsvariablen und Datenvolume bleiben unverändert.

Expliziter Start und Update:

```sh
docker compose -f docker-compose.yml pull
docker compose -f docker-compose.yml up -d
```

Solange die bisherige `compose.yaml` noch im Repository liegt, immer `-f docker-compose.yml` angeben beziehungsweise in Portainer explizit diesen Dateinamen auswählen. Die Altdatei soll in einem separaten Löschschritt entfernt werden. `INSTALL.md` enthält noch die bisherige Dateibenennung; für die Stack-Datei gilt diese Konvention.
