# DigitalOcean Deployment Guide - CrewCFO

## Quick Deploy (30 minutes)

### Option A: DigitalOcean App Platform (Easiest - $12/mo)

1. **Push to GitHub first**
   ```bash
   git add .
   git commit -m "Add production docker config"
   git push origin main
   ```

2. **Create App on DigitalOcean**
   - Go to https://cloud.digitalocean.com/apps
   - Click "Create App"
   - Connect your GitHub repo: `roofing-books-cfo`
   - It auto-detects Dockerfile

3. **Configure Services**
   Add 3 components:
   
   | Component | Type | Port | Route |
   |-----------|------|------|-------|
   | api | Web Service | 8000 | /api |
   | dashboard | Web Service | 8501 | /app |
   | landing | Static Site | - | / |

4. **Add Environment Variables**
   Copy all values from your `.env` file

5. **Deploy** - Click "Create Resources"

---

### Option B: Droplet + Docker (More Control - $6/mo)

#### Step 1: Create Droplet

```bash
# Or use DigitalOcean UI: https://cloud.digitalocean.com/droplets/new
# Choose: Ubuntu 24.04, Basic, $6/mo (1GB RAM), NYC/SF region
```

#### Step 2: SSH into Droplet

```bash
ssh root@YOUR_DROPLET_IP
```

#### Step 3: Install Docker

```bash
# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com | sh

# Install Docker Compose
apt install docker-compose-plugin -y

# Verify
docker --version
docker compose version
```

#### Step 4: Clone Your Repo

```bash
# Install git
apt install git -y

# Clone (use HTTPS or set up SSH key)
git clone https://github.com/YOUR_USERNAME/roofing-books-cfo.git
cd roofing-books-cfo
```

#### Step 5: Set Up Environment

```bash
# Create .env file
nano .env

# Paste your credentials (from local .env):
# SUPABASE_URL=...
# SUPABASE_ANON_KEY=...
# etc.

# Save: Ctrl+X, Y, Enter
```

#### Step 6: Deploy

```bash
# Build and start all services
docker compose -f docker-compose.prod.yml up -d --build

# Check status
docker compose -f docker-compose.prod.yml ps

# View logs
docker compose -f docker-compose.prod.yml logs -f
```

#### Step 7: Test

```bash
# From your local machine, open browser:
http://YOUR_DROPLET_IP        # Landing page
http://YOUR_DROPLET_IP:8501   # Dashboard (if not using nginx)
```

---

## Domain Setup (Optional but Recommended)

### Step 1: Buy Domain
- Namecheap, Google Domains, or Cloudflare (~$12/year)
- Suggested: `crewcfo.com` or `getcrewcfo.com`

### Step 2: DNS Records

Add these DNS records (in your domain registrar or DigitalOcean):

| Type | Name | Value |
|------|------|-------|
| A | @ | YOUR_DROPLET_IP |
| A | www | YOUR_DROPLET_IP |
| A | app | YOUR_DROPLET_IP |
| A | api | YOUR_DROPLET_IP |

### Step 3: SSL with Let's Encrypt (Free HTTPS)

```bash
# SSH into droplet
ssh root@YOUR_DROPLET_IP
cd roofing-books-cfo

# Install Certbot
apt install certbot python3-certbot-nginx -y

# Stop nginx temporarily
docker compose -f docker-compose.prod.yml stop nginx

# Get certificates
certbot certonly --standalone -d crewcfo.com -d www.crewcfo.com -d app.crewcfo.com

# Copy certs to nginx folder
mkdir -p nginx/ssl
cp /etc/letsencrypt/live/crewcfo.com/fullchain.pem nginx/ssl/
cp /etc/letsencrypt/live/crewcfo.com/privkey.pem nginx/ssl/

# Restart everything
docker compose -f docker-compose.prod.yml up -d
```

---

## Update QuickBooks Redirect URI

After deployment, update your Intuit Developer settings:

1. Go to https://developer.intuit.com → Your App → Keys & OAuth
2. Add production redirect URI:
   ```
   https://crewcfo.com/auth/qbo/callback
   ```
   or if using IP:
   ```
   http://YOUR_DROPLET_IP/auth/qbo/callback
   ```

---

## Quick Commands Reference

```bash
# Start everything
docker compose -f docker-compose.prod.yml up -d

# Stop everything
docker compose -f docker-compose.prod.yml down

# View logs
docker compose -f docker-compose.prod.yml logs -f

# Rebuild after code changes
docker compose -f docker-compose.prod.yml up -d --build

# SSH into a container
docker exec -it crewcfo-api bash

# Check what's running
docker ps
```

---

## Updating Your App

```bash
# On your local machine
git add .
git commit -m "Update feature X"
git push origin main

# SSH into droplet
ssh root@YOUR_DROPLET_IP
cd roofing-books-cfo
git pull
docker compose -f docker-compose.prod.yml up -d --build
```

---

## Cost Summary

| Option | Monthly Cost |
|--------|--------------|
| Droplet (Basic) | $6 |
| Droplet (2GB RAM) | $12 |
| App Platform | $12-25 |
| Domain | ~$1 (annual) |
| SSL | Free (Let's Encrypt) |
| Supabase | Free tier |
| **Total** | **$6-25/mo** |

---

## Troubleshooting

### Container won't start
```bash
docker compose -f docker-compose.prod.yml logs api
docker compose -f docker-compose.prod.yml logs dashboard
```

### Port already in use
```bash
# Find what's using port 80
lsof -i :80
# Kill it
kill -9 PID
```

### Can't connect to Supabase
- Check `.env` has correct `SUPABASE_URL` and keys
- Supabase dashboard → Settings → API → Check if keys match

### Dashboard shows mock data
- Verify Supabase connection in logs
- Check if schema was applied in Supabase SQL editor

---

## Next Steps After Deploy

1. ✅ Verify landing page loads at your domain/IP
2. ✅ Verify dashboard loads at /app or app.yourdomain.com  
3. ✅ Test QBO OAuth flow end-to-end
4. ✅ Update Calendly link in landing page
5. ✅ Share URL with first pilot customers!
