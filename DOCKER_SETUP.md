# Docker Setup Guide

This guide explains how to use Docker for development, testing, and deployment of CrewCFO.

## Quick Start

### Prerequisites
- Docker Desktop (or Docker Engine + Docker Compose)
- `.env` file with your configuration

### Start All Services
```bash
docker-compose up
```

Access:
- **API**: http://localhost:8000
- **Dashboard**: http://localhost:8503
- **API Docs**: http://localhost:8000/docs

### Start Specific Services
```bash
# Only API and Dashboard (uses Supabase, not local DB)
docker-compose up api dashboard

# Include local PostgreSQL database
docker-compose --profile db up

# Include pgAdmin (database GUI)
docker-compose --profile tools up
```

## Service Architecture

### Services Overview

| Service | Port | Description | When to Use |
|---------|------|-------------|-------------|
| `api` | 8000 | FastAPI backend | Always |
| `dashboard` | 8503 | Streamlit dashboard | Always |
| `postgres` | 5432 | Local PostgreSQL | Offline dev, testing |
| `pgadmin` | 5050 | Database GUI | Database administration |

### Service Dependencies

```
dashboard → api → (Supabase or postgres)
```

## Development Workflow

### 1. First Time Setup

```bash
# Build images
docker-compose build

# Start services
docker-compose up
```

### 2. Development with Hot Reload

Both API and Dashboard have volume mounts for live code updates:
- `./src` → `/app/src` (code changes auto-reload)

```bash
# Start in detached mode
docker-compose up -d

# View logs
docker-compose logs -f api dashboard

# Stop services
docker-compose down
```

### 3. Using Local PostgreSQL

By default, services use Supabase. To use local PostgreSQL:

```bash
# Start with local database
docker-compose --profile db up

# Update .env to use local DB:
# SUPABASE_URL=postgresql://postgres:postgres@postgres:5432/crewcfo
```

**Note**: The schema is automatically initialized from `supabase/schema.sql`

### 4. Database Administration

Access pgAdmin:
```bash
docker-compose --profile tools up
# Visit http://localhost:5050
# Login: admin@crewcfo.com / admin
```

Connect to PostgreSQL:
- Host: `postgres` (container name)
- Port: `5432`
- User: `postgres`
- Password: `postgres`

## Production Deployment

### Build Production Image

```bash
docker build -f Dockerfile.prod -t crewcfo-api:latest .
```

### Run Production Container

```bash
docker run -d \
  --name crewcfo-api \
  -p 8000:8000 \
  --env-file .env.prod \
  crewcfo-api:latest
```

### Docker Compose for Production

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  api:
    build:
      context: .
      dockerfile: Dockerfile.prod
    ports:
      - "8000:8000"
    env_file:
      - .env.prod
    restart: always
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  dashboard:
    build:
      context: .
      dockerfile: Dockerfile.prod
      target: development  # Streamlit needs dev for now
    ports:
      - "8503:8503"
    env_file:
      - .env.prod
    restart: always
```

Run:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## Environment Variables

Create `.env` file with:

```env
# QuickBooks
QBO_CLIENT_ID=your_client_id
QBO_CLIENT_SECRET=your_client_secret
QBO_REDIRECT_URI=http://localhost:8000/auth/qbo/callback
QBO_ENVIRONMENT=sandbox

# Supabase (or use local postgres)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_KEY=your_service_key

# Tenant
TENANT_ID=your-tenant-uuid

# AI
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...

# Optional: Local PostgreSQL (if using --profile db)
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=crewcfo
```

## Common Commands

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f dashboard
```

### Execute Commands in Container
```bash
# API container
docker-compose exec api bash
docker-compose exec api python test_sync.py

# Dashboard container
docker-compose exec dashboard bash
```

### Rebuild After Changes
```bash
# Rebuild specific service
docker-compose build api

# Rebuild all and restart
docker-compose up --build
```

### Clean Up
```bash
# Stop and remove containers
docker-compose down

# Remove volumes (clears database)
docker-compose down -v

# Remove images
docker-compose down --rmi all
```

## Troubleshooting

### Port Already in Use
```bash
# Change ports in docker-compose.yml or stop conflicting services
# Or use different ports:
docker-compose up -p crewcfo-dev
```

### Container Won't Start
```bash
# Check logs
docker-compose logs api

# Check health status
docker-compose ps

# Restart specific service
docker-compose restart api
```

### Database Connection Issues
- Ensure `.env` has correct Supabase credentials
- If using local DB, ensure `--profile db` is used
- Check network connectivity: `docker-compose exec api ping postgres`

### Permission Issues
```bash
# Fix file permissions
sudo chown -R $USER:$USER .
```

## Health Checks

All services have health checks configured:
- **API**: `/health` endpoint
- **Dashboard**: `/_stcore/health` endpoint
- **PostgreSQL**: `pg_isready`

Check status:
```bash
docker-compose ps
```

## Best Practices

1. **Use `.env` for secrets** - Never commit `.env` files
2. **Volume mounts for dev** - Use volumes for live reloading
3. **Separate prod builds** - Use `Dockerfile.prod` for production
4. **Health checks** - All services have health checks for orchestration
5. **Profiles** - Use profiles to start only needed services
6. **Networks** - Services communicate via `crewcfo-network`

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Build and Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build
        run: docker-compose build
      - name: Test
        run: docker-compose run --rm api pytest
```

### Deployment to Cloud

#### AWS ECS
```bash
# Build and push to ECR
aws ecr get-login-password | docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com
docker build -f Dockerfile.prod -t crewcfo-api .
docker tag crewcfo-api:latest <account>.dkr.ecr.us-east-1.amazonaws.com/crewcfo-api:latest
docker push <account>.dkr.ecr.us-east-1.amazonaws.com/crewcfo-api:latest
```

#### Google Cloud Run
```bash
# Build and deploy
gcloud builds submit --tag gcr.io/PROJECT-ID/crewcfo-api
gcloud run deploy crewcfo-api --image gcr.io/PROJECT-ID/crewcfo-api --platform managed
```

## Next Steps

- [ ] Set up CI/CD pipeline
- [ ] Configure production environment variables
- [ ] Set up monitoring and logging
- [ ] Configure reverse proxy (nginx/traefik)
- [ ] Set up SSL/TLS certificates

