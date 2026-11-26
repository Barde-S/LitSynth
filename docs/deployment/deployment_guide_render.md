# LitSynth Deployment Guide - Render Cloud Platform

**Platform**: Render (Free Tier)
**URL**: https://litsynth.onrender.com (after deployment)
**Last Updated**: 2026-01-19

---

## Overview

This guide covers deploying LitSynth to Render's free tier cloud platform. The deployment includes:
- **Frontend**: React static site (always-on, CDN-served)
- **Backend**: FastAPI web service (spins down after 15 min inactivity)
- **Database**: PostgreSQL (free for 90 days)
- **Cache**: Redis (25 MB free tier)
- **Storage**: 1GB persistent disk for ChromaDB vectors

---

## Prerequisites

1. **GitHub Account**: Code must be pushed to GitHub for auto-deployment
2. **Render Account**: Sign up at https://render.com (free)
3. **API Keys**:
   - Google Gemini API key (for LLM)
   - Google Cloud Vision credentials JSON (for OCR)
4. **Repository**: Push LitSynth code to GitHub

---

## Step 1: Prepare Code for Deployment

### 1.1 Frontend Configuration

**Files Modified**:
- ✅ [`.env.production`](litsynth-frontend/.env.production) - Created
- ✅ [`vite.config.ts`](litsynth-frontend/vite.config.ts) - Updated
- ✅ [`src/services/api.ts`](litsynth-frontend/src/services/api.ts) - Updated

**Environment Variables**:
```env
VITE_API_BASE_URL=https://litsynth-backend.onrender.com
```

### 1.2 Backend Configuration

**Files Created/Modified**:
- ✅ [`requirements.txt`](litsynth-backend/requirements.txt) - Created (all dependencies)
- ✅ [`render.yaml`](litsynth-backend/render.yaml) - Created (infrastructure as code)
- ✅ [`src/main.py`](litsynth-backend/src/main.py) - Added `/health` endpoint, PostgreSQL support

**Key Changes**:
- Health check endpoint: `GET /health`
- Database auto-switches: SQLite (dev) → PostgreSQL (prod via `DATABASE_URL`)
- CORS configured for Render frontend

---

## Step 2: Push Code to GitHub

```bash
cd /Users/Work/Documents/Final-Year-Project

# Stage all changes
git add litsynth-frontend/.env.production
git add litsynth-frontend/vite.config.ts
git add litsynth-frontend/src/services/api.ts
git add litsynth-backend/requirements.txt
git add litsynth-backend/render.yaml
git add litsynth-backend/src/main.py

# Commit
git commit -m "$(cat <<'EOF'
feat: Add Render cloud deployment configuration

- Frontend: Add .env.production with dynamic API URL
- Frontend: Update vite.config.ts for environment variable injection
- Frontend: Modify api.ts to use VITE_API_BASE_URL
- Backend: Create requirements.txt with all dependencies
- Backend: Add /health endpoint for Render monitoring
- Backend: Add PostgreSQL support (auto-switch from SQLite)
- Backend: Create render.yaml for infrastructure as code

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
EOF
)"

# Push to GitHub
git push origin main
```

---

## Step 3: Create Render Services

### 3.1 Create PostgreSQL Database

1. Go to **Render Dashboard** → **New** → **PostgreSQL**
2. Configure:
   - **Name**: `litsynth-postgres`
   - **Database**: `litsynth`
   - **User**: `litsynth_user`
   - **Region**: Oregon (or nearest)
   - **Plan**: Free
3. Click **Create Database**
4. **Copy the Internal Connection String** (starts with `postgres://`)

⚠️ **Important**: Free PostgreSQL expires after 90 days (sufficient for thesis completion)

### 3.2 Create Redis Instance

1. Go to **Render Dashboard** → **New** → **Redis**
2. Configure:
   - **Name**: `litsynth-redis`
   - **Region**: Oregon (same as database)
   - **Plan**: Free (25 MB)
   - **Eviction Policy**: `allkeys-lru` (recommended)
3. Click **Create Redis**
4. **Note down** the connection details (host, port, password)

### 3.3 Create Backend Web Service

1. Go to **Render Dashboard** → **New** → **Web Service**
2. Connect your **GitHub repository**
3. Configure:
   - **Name**: `litsynth-backend`
   - **Region**: Oregon
   - **Branch**: `main`
   - **Root Directory**: `litsynth-backend`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn src.main:app --host 0.0.0.0 --port $PORT --workers 1`
   - **Plan**: Free

4. **Add Persistent Disk** (for ChromaDB):
   - Click **Add Disk**
   - **Name**: `chromadb-data`
   - **Mount Path**: `/opt/render/project/chromadb_data`
   - **Size**: 1 GB (free tier limit)

5. **Environment Variables** (click "Add Environment Variable"):

```bash
# System
PYTHON_VERSION=3.11.6
DEBUG=false
LITSYNTH_INSECURE_MODE=false

# Database (link to PostgreSQL created above)
DATABASE_URL=${{ litsynth-postgres.DATABASE_URL }}

# ChromaDB
CHROMA_PERSIST_DIR=/opt/render/project/chromadb_data

# Redis (link to Redis instance created above)
REDIS_HOST=${{ litsynth-redis.REDIS_HOST }}
REDIS_PORT=${{ litsynth-redis.REDIS_PORT }}
REDIS_PASSWORD=${{ litsynth-redis.REDIS_PASSWORD }}

# Security - Generate JWT Secret
JWT_SECRET_KEY=<GENERATE_WITH_COMMAND_BELOW>

# LLM API
GOOGLE_API_KEY=<YOUR_GEMINI_API_KEY>

# OCR - Google Cloud Vision JSON credentials
GOOGLE_APPLICATION_CREDENTIALS=/opt/render/project/secrets/google-vision-key.json

# CORS
ALLOWED_ORIGINS=https://litsynth.onrender.com
FRONTEND_URL=https://litsynth.onrender.com
```

**Generate JWT Secret**:
```bash
openssl rand -hex 32
```

**Google Cloud Vision Credentials**:
- Upload your JSON credentials file as a **Secret File** in Render
- Or paste the JSON content directly as an environment variable

6. Click **Create Web Service**
7. Wait for deployment (5-10 minutes)

### 3.4 Create Frontend Static Site

1. Go to **Render Dashboard** → **New** → **Static Site**
2. Connect your **GitHub repository** (same repo)
3. Configure:
   - **Name**: `litsynth-frontend`
   - **Branch**: `main`
   - **Root Directory**: `litsynth-frontend`
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `dist`

4. **Environment Variables**:
```bash
VITE_API_BASE_URL=https://litsynth-backend.onrender.com
```

5. Click **Create Static Site**
6. Wait for build and deployment (3-5 minutes)

---

## Step 4: Verify Deployment

### 4.1 Check Service Health

1. **Backend Health Check**:
   ```bash
   curl https://litsynth-backend.onrender.com/health
   ```
   Expected response:
   ```json
   {
     "status": "healthy",
     "service": "litsynth-backend",
     "version": "1.0.0"
   }
   ```

2. **Backend API Documentation**:
   - Visit: https://litsynth-backend.onrender.com/EKfxgVHG1WPJMA/docs
   - (Note: Docs URL is obfuscated in production for security)

3. **Frontend Access**:
   - Visit: https://litsynth.onrender.com
   - Should load the login/register page

### 4.2 Test Full Workflow

1. **Register a New User**:
   - Enter email, request OTP
   - Verify OTP, complete registration
   - Login with credentials

2. **Create Workspace**:
   - Dashboard → Create Workspace
   - Add name and description

3. **Upload PDF**:
   - Select workspace
   - Upload a research paper (PDF)
   - Verify processing completes (check for progress indicators)

4. **Test Chat**:
   - Ask a question about the uploaded paper
   - Verify response includes citations
   - Check sources are displayed

5. **Data Persistence**:
   - Logout and login again
   - Verify workspace and documents are still there

### 4.3 Check Logs

**Backend Logs**:
```bash
# In Render Dashboard
litsynth-backend → Logs tab
```

Look for:
- ✅ `DATABASE: Using PostgreSQL (production)`
- ✅ `VECTOR: ChromaDB initialized successfully!`
- ✅ `LitSynth started successfully!`

**Common Issues**:
- ❌ `ModuleNotFoundError`: Check requirements.txt, redeploy
- ❌ `Database connection failed`: Verify DATABASE_URL is set correctly
- ❌ `ChromaDB permission denied`: Check disk mount path matches CHROMA_PERSIST_DIR

---

## Step 5: Capture Screenshots for Chapter 4

Once deployment is verified, capture the 27 required screenshots:

### Workflow 1: Registration & Authentication (3 screenshots)
- Figure 4.1: Registration page with OTP request
- Figure 4.2: OTP verification screen
- Figure 4.3: Login page

### Workflow 2: Workspace Management (3 screenshots)
- Figure 4.4: Dashboard with workspace list
- Figure 4.5: Create workspace modal
- Figure 4.6: Workspace detail view

### Workflow 3: PDF Processing (4 screenshots)
- Figure 4.7: Document upload interface
- Figure 4.8: Upload progress modal
- Figure 4.9: Processing status indicators
- Figure 4.10: Document list in workspace

### Workflow 4: Chat & RAG (5 screenshots)
- Figure 4.11: Chat interface
- Figure 4.12: Query submission
- Figure 4.13: Response with citations
- Figure 4.14: Source document preview
- Figure 4.15: Multi-turn conversation

### Workflow 5: Advanced Features (4 screenshots)
- Figure 4.16: Chat history management
- Figure 4.17: Document deletion
- Figure 4.18: Export functionality
- Figure 4.19: Profile/settings page

### Workflow 6: Backend API (2 screenshots)
- Figure 4.20: API documentation (FastAPI /docs)
- Figure 4.21: Sample API response (JSON)

### Workflow 7: Database Verification (2 screenshots)
- Figure 4.22: PostgreSQL dashboard (Render)
- Figure 4.23: Redis metrics (Render)

### Workflow 8: Deployment Infrastructure (4 screenshots)
- Figure 4.24: Render service dashboard
- Figure 4.25: Deployment logs
- Figure 4.26: Environment variables configuration
- Figure 4.27: Service health metrics

---

## Step 6: Monitoring & Maintenance

### Performance

**Free Tier Limitations**:
- Backend spins down after 15 minutes of inactivity
- Cold start takes ~30 seconds for first request
- 750 free hours/month (sufficient for thesis demonstration)

**Workaround for Cold Starts**:
- Use a service like UptimeRobot to ping `/health` every 14 minutes
- Or accept cold starts during thesis demonstration

### Database Backups

**PostgreSQL** (auto-backup on free tier):
- Render provides daily backups for 7 days
- Download backup: Render Dashboard → Database → Backups

**ChromaDB** (manual backup):
```bash
# In Render Shell
tar -czf chromadb_backup.tar.gz /opt/render/project/chromadb_data
```

### Costs

**Free Tier Breakdown**:
- Frontend: Free (unlimited)
- Backend: Free (750 hours/month)
- PostgreSQL: Free for 90 days
- Redis: Free (25 MB)
- Disk: Free (1 GB)

**After Free Tier Expires**:
- PostgreSQL: $7/month (after 90 days)
- Or export data and redeploy on another platform

---

## Troubleshooting

### Issue: "Application failed to respond"

**Cause**: Backend crashed during startup
**Solution**:
1. Check logs for Python errors
2. Verify all environment variables are set
3. Check DATABASE_URL format (should start with `postgresql://`)

### Issue: "CORS policy error"

**Cause**: Frontend can't access backend
**Solution**:
1. Verify `ALLOWED_ORIGINS` includes frontend URL
2. Check `FRONTEND_URL` is set correctly
3. Ensure backend service is running (not spun down)

### Issue: "Module not found" errors

**Cause**: Missing dependencies
**Solution**:
1. Check [requirements.txt](litsynth-backend/requirements.txt) is complete
2. Trigger manual redeploy in Render
3. Check build logs for pip install errors

### Issue: ChromaDB permission denied

**Cause**: Disk mount path mismatch
**Solution**:
1. Verify disk is mounted at `/opt/render/project/chromadb_data`
2. Check `CHROMA_PERSIST_DIR` environment variable matches
3. Ensure disk is attached to service

---

## Next Steps

After successful deployment:

1. ✅ Verify all 4 services are "Live" in Render dashboard
2. ✅ Test complete user workflow (register → upload → chat)
3. ✅ Capture all 27 screenshots for Chapter 4
4. ✅ Document any deployment issues encountered
5. ✅ Proceed to Chapter 4 writing

---

## Support

**Render Documentation**: https://render.com/docs
**LitSynth Repository**: (Your GitHub repo URL)
**Deployment Date**: (To be filled after deployment)

---

**Deployment Status**: Ready for execution (all code prepared)
