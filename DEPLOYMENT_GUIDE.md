# COM2020 Deployment Guide

## 1. Overview

This guide covers full deployment for the COM2020 project Healthy Streets:

- Backend API (Flask) on an EC2 instance via Docker Compose
- PostgreSQL (either containerized with Compose or external managed DB)
- Frontend static build deployment using nginx

Use this as the primary deployment runbook.

## 2. Prerequisites

- AWS EC2 Linux instance with SSH access
- Git installed on EC2
- Docker Engine and Docker Compose plugin installed on EC2
- Repo cloned on EC2
- Required ports/security groups configured
- Environment variables configured in `server/.env`

Optional:

- Nginx configured for reverse proxy/static hosting
- S3 bucket configured if frontend is served from S3

## 3. One-Time EC2 Host Setup

Run on EC2:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y git ca-certificates curl gnupg

# Install Docker (Ubuntu)
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Allow non-root docker usage
sudo usermod -aG docker $USER
newgrp docker
```

Verify that docker has installed correctly:

```bash
docker --version
docker compose version
```

## 4. Repository Setup on EC2

```bash
git clone https://github.com/PeterC-B/COM2020-TeamProject.git
cd COM2020-TeamProject
```

If repo already exists:

```bash
cd COM2020-TeamProject
git pull
```

## 5. Backend Environment Configuration

Create/update `server/.env` with production-safe values.

Minimum keys expected by backend config:

- `ENV=production`
- `SECRET_KEY=<real-secret-key>`
- `HOST=0.0.0.0`
- `BACKEND_PORT=8000`
- `PROD_DB_NAME=<real-db-name>`
- `PROD_DB_USERNAME=<real-db-username>`
- `PROD_DB_PASSWORD=<real-db-password>`
- `PROD_DB_HOST=<real-db-host>`
- `PROD_DB_PORT=5432`
- `PROD_CORS_ADDRESSES=https://<your-frontend-domain-origin>`

Notes:

- Do not commit real secrets.
- Keep production `.env` only on the server.

## 6. Backend + Database Deployment (Docker Compose)

Run from `server/`:

```bash
cd server
```

### 6.1 Fresh Rebuild (Clean)

```bash
docker compose -f docker-compose.prod.yml down -v
docker compose -f docker-compose.prod.yml build --no-cache
docker compose -f docker-compose.prod.yml up -d
docker compose -f docker-compose.prod.yml ps
```

### 6.2 Standard Update Deploy (Most Common)

```bash
cd ~/COM2020-TeamProject
git pull
cd server
docker compose -f docker-compose.prod.yml build backend
docker compose -f docker-compose.prod.yml up -d backend
docker compose -f docker-compose.prod.yml ps
```

### 6.3 Apply Database Migrations if updates are required or if it is a fresh database build

If Flask is available in the backend container:

```bash
docker compose -f docker-compose.prod.yml exec backend flask db upgrade
```

If not, run migration using a python script where you initialise the app and then are able to access the environment

## 7. Operational Commands

From `server/`:

```bash
# Service status listing the docker containers
docker compose -f docker-compose.prod.yml ps

# Restart backend only
docker compose -f docker-compose.prod.yml restart backend

# Follow backend logs
docker compose -f docker-compose.prod.yml logs -f backend

# Follow DB logs
docker compose -f docker-compose.prod.yml logs -f db
```

Health check example to be run locally on the EC2:

```bash
curl -i -X POST http://127.0.0.1:8000/api/user/login
```

## 8. Access PostgreSQL (Containerized DB)

If `psql` is not installed in backend container, use DB container directly:

```bash
docker compose -f docker-compose.prod.yml exec db psql -U postgres -d <com2020 or another database name>
```

## 9. Frontend Deployment

Build on local machine:

```bash
npm run build
```

### Option A: Copy to EC2 + serve via Nginx

From local machine use scp to copy the built HTML, CSS, JS files over to EC2:

```bash
scp -i "C:\Users\<USERNAME>\.ssh\id_ed25519" -r dist/* ubuntu@<EC2_PUBLIC_IP_OR_DNS>:/home/ubuntu/temp/
```

On EC2:

```bash
sudo mkdir -p /var/www/frontend
sudo mv ~/temp/* /var/www/frontend/
sudo chown -R www-data:www-data /var/www/frontend
sudo find /var/www/frontend -type d -exec chmod 755 {} \;
sudo find /var/www/frontend -type f -exec chmod 644 {} \;
sudo nginx -t
sudo systemctl reload nginx
```

Invalidate CloudFront if being used to ensure that it updates its cache.

### Option B: Serve frontend from S3

- Upload build files from `dist/` to your S3 bucket.
- Invalidate CloudFront (if used).
- Ensure `VITE_API_URL` points to the correct backend/API gateway URL before building.

## 10. Disk Cleanup and Cache Pruning

When instance disk is low:

```bash
docker system df

docker container prune -f
docker image prune -f
docker builder prune -f
docker volume prune -f
docker network prune -f

# Aggressive cleanup  (be careful as this may remove the container and its data if it is not running)
docker system prune -a -f --volumes
docker builder prune -a -f
```

## 11. Rollback Strategy

Basic rollback:

1. Checkout previous known-good commit.
2. Rebuild and redeploy backend.
3. Re-run migrations only if backward-compatible.

Example:

```bash
cd ~/COM2020-TeamProject
git log --oneline
git checkout <KNOWN_GOOD_COMMIT>
cd server
docker compose -f docker-compose.prod.yml build backend
docker compose -f docker-compose.prod.yml up -d backend
```

## 12. Troubleshooting

- `restart` does not load new code: rebuild and recreate container (`build backend` + `up -d backend`).
- `psql: command not found` in backend: use `db` container with `docker compose exec db psql ...`.
- Container exits immediately: inspect logs with `docker compose logs -f <service>`.
- Migration errors: verify `ENV=production` and DB credentials in `server/.env`.
- Frontend calls wrong API: verify `VITE_API_URL` before `npm run build`.

## 13. Quick Command Summary

```bash
# Full clean deploy
cd ~/COM2020-TeamProject/server
docker compose -f docker-compose.prod.yml down -v
docker compose -f docker-compose.prod.yml build --no-cache
docker compose -f docker-compose.prod.yml up -d
docker compose -f docker-compose.prod.yml exec backend flask db upgrade

# Standard code update
cd ~/COM2020-TeamProject
git pull
cd server
docker compose -f docker-compose.prod.yml build backend
docker compose -f docker-compose.prod.yml up -d backend

# Logs
docker compose -f docker-compose.prod.yml logs -f backend
```
