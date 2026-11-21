# Docker-Konvention

Immer docker-compose.yml verwenden, auch als Portainer-Compose-Pfad. Externes bestehendes Netzwerk highfishNetwork; Host-Port 8911, intern 8080. Einstieg gateway:app, genau ein Worker.

```sh
docker compose -f docker-compose.yml pull
docker compose -f docker-compose.yml up -d
```

Webdaten ausschließlich nach Passwort-Login, MCP ausschließlich mit Bearer-Token. PUBLIC_DASHBOARD und MCP_PUBLIC sind keine unterstützten Freigaben mehr. Die Login-Oberfläche und der minimale /health-Prozessstatus bleiben für Anmeldung beziehungsweise Docker erreichbar. Einrichtung siehe INSTALL.md. Altdatei compose.yaml nicht verwenden.
