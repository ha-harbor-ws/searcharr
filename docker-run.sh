#!/bin/bash

# Production-style run matching docker-compose paths.
# Settings live in data/settings.py (mounted via /app/data).

docker run -d \
  --name=searcharr \
  --hostname=searcharr \
  --network=strong \
  --ip=172.20.0.3 \
  --ip6="2a0d:8480:1:13:2::3" \
  -e LANG=en_US.UTF-8 \
  -e LANGUAGE=en_US.UTF-8 \
  -e TERM=xterm \
  -e HOME=/root \
  -e PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin \
  -e TZ=Europe/Moscow \
  -v /opt/searcharr/data:/app/data \
  -v /opt/searcharr/logs:/app/logs \
  --restart unless-stopped \
  docker.io/harborws/harbortvbot:latest
