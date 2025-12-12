# Docker Setup Guide - CrewCFO

## Prerequisites

1. **Install Docker Desktop**
   - Mac: https://docs.docker.com/desktop/install/mac-install/
   - Windows: https://docs.docker.com/desktop/install/windows-install/
   - Linux: https://docs.docker.com/engine/install/

2. **Verify installation**
   ```bash
   docker --version
   docker-compose --version
   ```

---

## Quick Start (Recommended)

### 1. Copy environment file
```bash
cp .env.example .env
# Edit .env with your credentials (Supabase, Anthropic, QBO)
```

### 2. Start everything
```bash
docker-compose up
```

### 3. Access the apps
| Service | URL | Description |
|---------|-----|-------------|
| API | http://localhost:8000 | FastAPI backend |
| API Docs | http://localhost:8000/docs | Swagger UI |
| Dashboard | http://localhost:8501 | Streamlit owner dashboard |
| Database | localhost:5432 | PostgreSQL (local) |

### 4. Stop everything
```bash
docker-compose down
```

---

## Development Workflows

### Run with hot-reload (code changes apply instantly)
```bash
docker-compose up
```
The volumes mount your local `src/` folder, so edits are reflected immediately.

### Rebuild after changing requirements.txt
```bash
docker-compose build --no-cache
docker-compose up
```

### Run only specific services
```bash
# Just API + database
docker-compose up api db

# Just dashboard
docker-compose up dashboard
```

### View logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
```

### Access database shell
```bash
docker exec -it crewcfo-db psql -U postgres -d crewcfo
```

### Run tests inside container
```bash
docker-compose exec api pytest
```

---

## Optional: Database GUI (pgAdmin)

Start with pgAdmin included:
```bash
docker-compose --profile tools up
```

Access pgAdmin: http://localhost:5050
- Email: admin@crewcfo.com
- Password: admin

To connect to the database in pgAdmin:
- Host: `db` (or `crewcfo-db`)
- Port: `5432`
- Username: `postgres`
- Password: `postgres`
- Database: `crewcfo`

---

## Environment Variables

For Docker, these are loaded from `.env`:

```env
# Required
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_KEY=eyJ...
ANTHROPIC_API_KEY=sk-ant-...

# QuickBooks (for OAuth)
QBO_CLIENT_ID=...
QBO_CLIENT_SECRET=...
QBO_REDIRECT_URI=http://localhost:8000/auth/qbo/callback
QBO_ENVIRONMENT=sandbox

# For local PostgreSQL (docker-compose uses these)
DATABASE_URL=postgresql://postgres:postgres@db:5432/crewcfo
```

---

## Using Local Database vs Supabase

### Option A: Use Supabase (Production-like)
Keep your Supabase credentials in `.env`. The app connects to your cloud database.

### Option B: Use Local PostgreSQL (Offline development)
The `docker-compose.yml` includes a PostgreSQL container. To use it:

1. Update `.env`:
   ```env
   DATABASE_URL=postgresql://postgres:postgres@db:5432/crewcfo
   ```

2. The schema auto-loads from `supabase/schema.sql` on first run.

---

## Troubleshooting

### Port already in use
```bash
# Find what's using port 8000
lsof -i :8000

# Kill it
kill -9 <PID>

# Or change port in docker-compose.yml
ports:
  - "8001:8000"  # Use 8001 instead
```

### Container won't start
```bash
# Check logs
docker-compose logs api

# Rebuild
docker-compose build --no-cache
```

### Database connection refused
Wait a few seconds after `docker-compose up` - the database needs time to initialize.

```bash
# Check if db is healthy
docker-compose ps
```

### Clear everything and start fresh
```bash
docker-compose down -v  # -v removes volumes (deletes database data!)
docker-compose up --build
```

---

## Production Deployment

For production, you would NOT use docker-compose. Instead:

1. **API**: Deploy to Railway, Render, or Fly.io
2. **Dashboard**: Deploy to Streamlit Cloud
3. **Database**: Use Supabase (already cloud-hosted)

See `docs/MVP_LAUNCH_CHECKLIST.md` for deployment steps.
