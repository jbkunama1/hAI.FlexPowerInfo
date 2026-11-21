# Docker-Konvention

Immer `docker-compose.yml` nutzen. Portainer-Compose-Pfad ausdrücklich darauf setzen. Externes, bereits vorhandenes Netzwerk: `highfishNetwork`. Host-Port: `8911`; intern `8080`.

```sh
docker compose -f docker-compose.yml pull
docker compose -f docker-compose.yml up -d
```

Der Container startet `gateway:app` mit öffentlichem Preis-Dashboard und lesendem MCP; Verwaltung bleibt geschützt. Einrichtung siehe INSTALL.md. Die bisherige compose.yaml ist eine Altdatei und nicht zu verwenden; sie ist mit diesem Commit noch nicht gelöscht.
