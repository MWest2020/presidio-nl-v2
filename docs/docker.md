# Docker: Presidio-NL snel starten

Met Docker kun je de Presidio-NL API eenvoudig en consistent draaien, zonder gedoe met lokale Python-versies of dependencies.

## Build de Docker image

Voer in de root van het project uit:
```bash
docker build -t presidio-nl .
```
- Dit bouwt een image met de naam `presidio-nl`.

## Start de container

```bash
docker run -d -p 8000:8080 --name presidio-nl presidio-nl
```
- De API is nu bereikbaar op [http://localhost:8000/docs](http://localhost:8000/docs)
- De container draait op de achtergrond (`-d`).
- Poort 8080 in de container wordt gemapt naar poort 8000 op je machine.
- Er worden `emptyDir` volumes gekoppeld aan `/tmp` en `/app/logs` zodat de container kan schrijven. Dit voorkomt fouten als `os error 30` bij een read-only root filesystem.

## Stoppen en verwijderen

```bash
docker stop presidio-nl
```
```bash
docker rm presidio-nl
```

---
Zie de README voor meer informatie over gebruik en configuratie. 