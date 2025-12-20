# Marketing Pages Setup

## Pages Available

All marketing pages are in the `/marketing` folder and are served via nginx:

1. **Home Page**: `/` or `/index.html`
   - File: `marketing/index.html`
   - Landing page with features, pricing section, testimonials, FAQ

2. **About Page**: `/about` or `/about.html`
   - File: `marketing/about.html`
   - About CrewCFO and the team

3. **Pricing Page**: `/pricing` or `/pricing.html`
   - File: `marketing/pricing.html`
   - Detailed pricing information

## Access URLs

### Development (Local Docker)
- Home: http://localhost/
- About: http://localhost/about
- Pricing: http://localhost/pricing

### Production
- Home: https://crewcfo.com/
- About: https://crewcfo.com/about
- Pricing: https://crewcfo.com/pricing

## How It Works

### Nginx Configuration
The `nginx/nginx.conf` file:
- Serves static HTML files from `/marketing` folder
- Provides clean URLs (e.g., `/about` → `about.html`)
- Proxies `/api/*` requests to the FastAPI backend
- Proxies `/auth/*` requests for OAuth callbacks
- Routes `app.crewcfo.com` to the Streamlit dashboard

### Docker Setup
- **Development** (`docker-compose.yml`): nginx service runs by default
- **Production** (`docker-compose.prod.yml`): nginx serves marketing pages

## Navigation Links

All pages have navigation links that connect to each other:
- Main navigation includes: Features, Pricing, About
- Footer links to all pages
- Pages link back to home via logo

## Testing

To test locally with Docker:
```bash
docker-compose up nginx
```

Then visit:
- http://localhost/
- http://localhost/about
- http://localhost/pricing






