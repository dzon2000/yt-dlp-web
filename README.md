# yt-dlp-web

yt_dlp exposed as a Web Service with HTML frontend

## Docker Compose

Copy `.env.example` to `.env`, then build and start the service:

```bash
docker compose up -d --build
```

To upgrade, change `VERSION` in `.env` (for example, from `1.0.0` to `1.0.1`),
then run `docker compose up -d --build` again. Compose rebuilds the local image
as `dlp:<VERSION>` and replaces the running container. The service is available
to the reverse proxy through the external `pihole` Docker network.

Downloads are stored in the container and are lost when it is replaced.
