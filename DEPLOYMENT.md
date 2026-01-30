# AlbLingo Deployment Guide

This guide covers deploying AlbLingo to production using:
- **Frontend**: Vercel (React/Vite)
- **Backend**: Render (FastAPI)
- **Database**: Render PostgreSQL

## Architecture Overview

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│    Vercel       │     │     Render      │     │     Render      │
│   (Frontend)    │────▶│    (Backend)    │────▶│   PostgreSQL    │
│   React/Vite    │     │    FastAPI      │     │    Database     │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

---

## 1. Database Setup (Render PostgreSQL)

### Create PostgreSQL Database

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **New** → **PostgreSQL**
3. Configure:
   - **Name**: `alblingo-db`
   - **Database**: `alblingo`
   - **User**: (auto-generated)
   - **Region**: Choose closest to your users
   - **Plan**: Free (for testing) or Starter (for production)
4. Click **Create Database**
5. Copy the **External Database URL** - you'll need this for the backend

---

## 2. Backend Deployment (Render)

### Option A: Deploy via render.yaml (Recommended)

1. Push the code to GitHub
2. Go to [Render Dashboard](https://dashboard.render.com/)
3. Click **New** → **Blueprint**
4. Connect your GitHub repository
5. Render will automatically detect `render.yaml` and configure everything

### Option B: Manual Setup

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **New** → **Web Service**
3. Connect your GitHub repository
4. Configure:
   - **Name**: `alblingo-api`
   - **Root Directory**: `backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free (for testing) or Starter (for production)

### Environment Variables

Set these in Render Dashboard → Your Service → Environment:

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgres://user:pass@host:5432/db` |
| `SECRET_KEY` | JWT signing key (generate secure random) | `your-secure-secret-key` |
| `ENVIRONMENT` | Environment mode | `production` |
| `DEBUG` | Debug mode | `false` |
| `ALLOWED_ORIGINS` | Frontend URLs (comma-separated) | `https://your-app.vercel.app` |

**Generate SECRET_KEY:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### Verify Deployment

After deployment, test the health endpoint:
```bash
curl https://your-alblingo-api.onrender.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z",
  "environment": "production",
  "database": "postgresql"
}
```

---

## 3. Frontend Deployment (Vercel)

### Deploy to Vercel

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click **Add New** → **Project**
3. Import your GitHub repository
4. Configure:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

### Environment Variables

Set in Vercel Dashboard → Your Project → Settings → Environment Variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API URL | `https://your-alblingo-api.onrender.com` |

**Important**: Vite environment variables must be prefixed with `VITE_` to be exposed to the frontend.

### Verify Deployment

1. Visit your Vercel URL
2. Open browser DevTools → Network tab
3. Verify API calls go to your Render backend
4. Test login/register functionality

---

## 4. Post-Deployment Checklist

### Update CORS Origins

After deploying the frontend, update the backend's `ALLOWED_ORIGINS`:

1. Go to Render Dashboard → Your Backend Service → Environment
2. Update `ALLOWED_ORIGINS` to include your Vercel URL:
   ```
   https://your-app.vercel.app,https://www.yourdomain.com
   ```
3. Redeploy the service

### Initialize Database

The database tables are created automatically on first startup. To seed initial data:

1. Access your backend API
2. Call the seed endpoint (if available) or use admin panel

### Monitor Health

- **Backend Health**: `https://your-api.onrender.com/health`
- **Render Dashboard**: Monitor logs and metrics
- **Vercel Dashboard**: Monitor deployment and analytics

---

## 5. Environment Variables Reference

### Backend (.env)

```env
# Required
DATABASE_URL=postgresql://user:password@host:5432/database
SECRET_KEY=your-secure-secret-key
ALLOWED_ORIGINS=https://your-frontend.vercel.app

# Environment
ENVIRONMENT=production
DEBUG=false

# Optional: AI Services
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
AZURE_SPEECH_KEY=...
AZURE_SPEECH_REGION=westeurope
```

### Frontend (.env.production)

```env
VITE_API_URL=https://your-backend.onrender.com
```

---

## 6. Troubleshooting

### CORS Errors

If you see CORS errors in the browser console:
1. Verify `ALLOWED_ORIGINS` includes your frontend URL (exact match)
2. Check there are no trailing slashes in the URLs
3. Redeploy the backend after updating environment variables

### Database Connection Issues

1. Verify `DATABASE_URL` uses `postgresql://` (not `postgres://`)
2. Check the database is running in Render dashboard
3. Verify IP allowlist if using external database

### 502 Bad Gateway

1. Check Render logs for errors
2. Verify `requirements.txt` is complete
3. Ensure start command is correct

### Build Failures

**Frontend**:
- Check Node.js version (should be 18+)
- Verify all dependencies in `package.json`

**Backend**:
- Check Python version (should be 3.9+)
- Verify all dependencies in `requirements.txt`

---

## 7. Local Development

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your settings
uvicorn app.main:app --reload --port 8001
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

The frontend dev server proxies `/api` requests to `localhost:8001`.

---

## 8. Security Considerations

1. **Never commit `.env` files** - They're in `.gitignore`
2. **Use strong SECRET_KEY** - Generate with `secrets.token_hex(32)`
3. **Restrict CORS origins** - Only allow your actual frontend URLs
4. **Use HTTPS** - Both Vercel and Render provide this automatically
5. **Rotate secrets periodically** - Update `SECRET_KEY` regularly
