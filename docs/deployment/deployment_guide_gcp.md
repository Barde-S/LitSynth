# LitSynth Deployment Guide - Google Cloud Platform (Always Free Tier)

**Last Updated**: 2026-01-19
**Platform**: Google Cloud Platform (GCP)
**Deployment Type**: Direct VM Deployment (No Docker)
**Tier**: Always Free Tier (e2-micro VM, 30GB persistent disk)

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [GCP VM Setup](#gcp-vm-setup)
4. [System Package Installation](#system-package-installation)
5. [PostgreSQL Configuration](#postgresql-configuration)
6. [Redis Configuration](#redis-configuration)
7. [Backend Deployment](#backend-deployment)
8. [Frontend Deployment](#frontend-deployment)
9. [Nginx Configuration](#nginx-configuration)
10. [Environment Variables](#environment-variables)
11. [Testing & Verification](#testing--verification)
12. [Troubleshooting](#troubleshooting)
13. [Screenshot Capture Checklist](#screenshot-capture-checklist)

---

## Overview

### Architecture

```
[Google Cloud Platform - Always Free Tier]
├── Compute Engine (e2-micro VM)
│   ├── OS: Ubuntu 22.04 LTS
│   ├── vCPU: 2 vCPU (shared-core)
│   ├── RAM: 1 GB
│   ├── Boot Disk: 30 GB Standard Persistent Disk
│   ├── Region: us-west1, us-east1, or us-east4 (free tier eligible)
│   └── External IP: Ephemeral (free)
│
├── Application Stack
│   ├── Backend: FastAPI + Uvicorn (systemd service on port 8000)
│   ├── Frontend: React build served by Nginx (port 80/443)
│   ├── PostgreSQL: Self-hosted database (port 5432)
│   ├── Redis: Self-hosted cache (port 6379)
│   └── ChromaDB: Vector database (persistent at /mnt/data/chromadb)
│
└── Persistent Storage (/mnt/data)
    ├── /mnt/data/chromadb → ChromaDB vectors
    ├── /mnt/data/postgres → PostgreSQL database files
    └── /mnt/data/documents → Uploaded PDF files
```

### Access URLs

- **Frontend**: `http://<VM_EXTERNAL_IP>`
- **Backend API**: `http://<VM_EXTERNAL_IP>/api`
- **API Docs**: `http://<VM_EXTERNAL_IP>/api/docs`
- **Health Check**: `http://<VM_EXTERNAL_IP>/api/health`

### Key Features

- ✅ **Persistent Storage**: 30GB disk survives VM restarts
- ✅ **Always Running**: No cold starts (24/7 availability)
- ✅ **Free Forever**: GCP Always Free Tier (not time-limited)
- ✅ **Professional Infrastructure**: Enterprise-grade cloud platform
- ✅ **No Docker Overhead**: Direct deployment for better resource utilization

---

## Prerequisites

### 1. Google Cloud Platform Account

- **Required**: Active GCP account with billing enabled
- **Note**: You already have this set up for Google Cloud Vision API
- **Verification**: Visit [GCP Console](https://console.cloud.google.com/)

### 2. Local Development Tools

- **Git**: Version control (already installed)
- **SSH client**: For connecting to VM (built-in on macOS/Linux)
- **gcloud CLI** (optional but recommended):
  ```bash
  # Install gcloud CLI on macOS
  curl https://sdk.cloud.google.com | bash
  exec -l $SHELL
  gcloud init
  ```

### 3. Required Credentials

- **Google Cloud Vision API Key**: JSON credentials file (you already have this)
- **Gemini API Key**: For LLM chat functionality (via Perplexity)
- **JWT Secret**: Generate with `openssl rand -hex 32`

---

## GCP VM Setup

### Step 1: Create Compute Engine VM Instance

1. **Navigate to GCP Console**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Select your project (or create a new one: "litsynth-production")

2. **Enable Compute Engine API**:
   - Navigation Menu → **Compute Engine** → **VM Instances**
   - Click "Enable" if prompted (first-time setup)

3. **Create VM Instance**:
   - Click **"Create Instance"** button
   - Configure as follows:

#### Basic Configuration

```
Name: litsynth-vm
Region: us-west1 (Oregon)  # Or us-east1 (South Carolina) or us-east4 (North Virginia)
Zone: us-west1-b  # Any zone in the selected region
```

**Important**: Only these 3 regions are eligible for Always Free Tier!

#### Machine Configuration

```
Machine family: General-purpose
Series: E2
Machine type: e2-micro (2 vCPU, 1 GB memory)
```

✅ **"Your first 744 hours of e2-micro usage are free this month"** message should appear.

#### Boot Disk Configuration

Click **"Change"** under Boot Disk:

```
Operating System: Ubuntu
Version: Ubuntu 22.04 LTS (x86/64, amd64 jammy image)
Boot disk type: Standard persistent disk
Size (GB): 30  # Maximum free tier allowance
```

Click **"Select"** to save boot disk configuration.

#### Firewall Configuration

Under **Firewall** section:
- ✅ **Allow HTTP traffic**
- ✅ **Allow HTTPS traffic**

#### Advanced Options (Optional but Recommended)

Expand **"Advanced options"** → **"Management"**:

**Startup script** (optional - for automatic updates):
```bash
#!/bin/bash
apt-get update
apt-get upgrade -y
```

Click **"Create"** button at the bottom.

### Step 2: Note VM External IP Address

1. Wait for VM to start (~1-2 minutes)
2. In VM Instances list, note the **External IP** address (e.g., `34.83.123.45`)
3. **Save this IP** - you'll need it for:
   - SSH connection
   - Frontend environment variable (`VITE_API_BASE_URL`)
   - Testing and screenshots

### Step 3: Configure Firewall Rules (if needed)

By default, HTTP/HTTPS traffic is allowed. If you need to access backend directly on port 8000:

1. **Navigation Menu** → **VPC Network** → **Firewall**
2. Click **"Create Firewall Rule"**:
   ```
   Name: allow-litsynth-backend
   Targets: All instances in the network
   Source IP ranges: 0.0.0.0/0
   Protocols and ports: tcp:8000
   ```
3. Click **"Create"**

---

## System Package Installation

### Step 1: Connect to VM via SSH

**Option A: Browser-based SSH (easiest)**
1. In GCP Console → Compute Engine → VM Instances
2. Click **"SSH"** button next to your VM
3. Wait for browser SSH window to open

**Option B: gcloud CLI**
```bash
gcloud compute ssh litsynth-vm --zone=us-west1-b
```

**Option C: Standard SSH**
```bash
# First time only: Add SSH key to GCP
ssh-keygen -t rsa -b 4096 -C "your-email@example.com"
cat ~/.ssh/id_rsa.pub  # Copy this and add to GCP Console → Metadata → SSH Keys

# Connect
ssh -i ~/.ssh/id_rsa <username>@<VM_EXTERNAL_IP>
```

### Step 2: Update System Packages

```bash
# Update package lists
sudo apt-get update

# Upgrade existing packages
sudo apt-get upgrade -y

# Install essential build tools
sudo apt-get install -y build-essential curl git wget unzip
```

### Step 3: Install Python 3.11

```bash
# Add deadsnakes PPA for latest Python versions
sudo apt-get install -y software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt-get update

# Install Python 3.11 and pip
sudo apt-get install -y python3.11 python3.11-venv python3.11-dev python3-pip

# Set Python 3.11 as default
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1

# Verify installation
python3 --version  # Should output: Python 3.11.x
```

### Step 4: Install PostgreSQL 15

```bash
# Install PostgreSQL
sudo apt-get install -y postgresql postgresql-contrib

# Start and enable PostgreSQL service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Verify installation
sudo systemctl status postgresql
```

### Step 5: Install Redis

```bash
# Install Redis server
sudo apt-get install -y redis-server

# Configure Redis to start on boot
sudo systemctl enable redis-server
sudo systemctl start redis-server

# Verify installation
sudo systemctl status redis-server
redis-cli ping  # Should output: PONG
```

### Step 6: Install Nginx

```bash
# Install Nginx web server
sudo apt-get install -y nginx

# Start and enable Nginx
sudo systemctl start nginx
sudo systemctl enable nginx

# Verify installation
sudo systemctl status nginx
curl http://localhost  # Should return Nginx welcome page
```

### Step 7: Install Node.js (for frontend build)

```bash
# Install Node.js 20.x LTS
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verify installation
node --version  # Should output: v20.x.x
npm --version   # Should output: 10.x.x
```

### Step 8: Create Persistent Data Directories

```bash
# Create mount points for persistent data
sudo mkdir -p /mnt/data/chromadb
sudo mkdir -p /mnt/data/postgres
sudo mkdir -p /mnt/data/documents
sudo mkdir -p /mnt/data/redis

# Set ownership to current user
sudo chown -R $USER:$USER /mnt/data

# Create symbolic links (optional, for easier access)
ln -s /mnt/data ~/data
```

---

## PostgreSQL Configuration

### Step 1: Create Database and User

```bash
# Switch to postgres user
sudo -u postgres psql

# In PostgreSQL prompt (postgres=#), run:
CREATE DATABASE litsynth;
CREATE USER litsynth_user WITH PASSWORD 'your_secure_password_here';
GRANT ALL PRIVILEGES ON DATABASE litsynth TO litsynth_user;

# Exit PostgreSQL
\q
```

### Step 2: Configure PostgreSQL for Application Access

```bash
# Edit PostgreSQL configuration
sudo nano /etc/postgresql/15/main/pg_hba.conf

# Add this line before the "local all all peer" line:
# local   litsynth    litsynth_user                            md5

# Save and exit (Ctrl+X, Y, Enter)

# Restart PostgreSQL
sudo systemctl restart postgresql
```

### Step 3: Move PostgreSQL Data to Persistent Disk (Optional)

```bash
# Stop PostgreSQL
sudo systemctl stop postgresql

# Move data directory
sudo rsync -av /var/lib/postgresql /mnt/data/postgres/

# Update PostgreSQL configuration
sudo nano /etc/postgresql/15/main/postgresql.conf

# Change data_directory line to:
# data_directory = '/mnt/data/postgres/postgresql/15/main'

# Update ownership
sudo chown -R postgres:postgres /mnt/data/postgres

# Start PostgreSQL
sudo systemctl start postgresql
```

### Step 4: Verify Database Connection

```bash
# Test connection
psql -U litsynth_user -d litsynth -h localhost -W

# Should prompt for password, then connect successfully
# Exit with: \q
```

### Step 5: Generate DATABASE_URL

```bash
# Format: postgresql://username:password@host:port/database
DATABASE_URL="postgresql://litsynth_user:your_secure_password_here@localhost:5432/litsynth"

# Save this - you'll need it for backend .env file
echo $DATABASE_URL
```

---

## Redis Configuration

### Step 1: Configure Redis for Persistence (Optional)

```bash
# Edit Redis configuration
sudo nano /etc/redis/redis.conf

# Find and modify these lines:
# dir /mnt/data/redis
# save 900 1
# save 300 10
# save 60 10000

# Save and exit

# Restart Redis
sudo systemctl restart redis-server
```

### Step 2: Test Redis Connection

```bash
# Test Redis
redis-cli ping  # Should return: PONG

# Set a test key
redis-cli SET test "Hello LitSynth"

# Get the key
redis-cli GET test  # Should return: "Hello LitSynth"

# Delete test key
redis-cli DEL test
```

---

## Backend Deployment

### Step 1: Clone GitHub Repository

```bash
# Navigate to home directory
cd ~

# Clone your repository
git clone https://github.com/your-username/Final-Year-Project.git
cd Final-Year-Project/litsynth-backend

# Verify files
ls -la  # Should see src/, requirements.txt, etc.
```

### Step 2: Create Python Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

### Step 3: Install Python Dependencies

```bash
# Install all requirements
pip install -r requirements.txt

# This will take 5-10 minutes (installing sentence-transformers, chromadb, etc.)
# Watch for any errors - if packages fail, install system dependencies:
# sudo apt-get install -y libpq-dev python3.11-dev
```

### Step 4: Create Environment Variables File

```bash
# Create .env file
nano .env
```

**Paste the following** (replace placeholders with actual values):

```bash
# Application Settings
DEBUG=False
LITSYNTH_INSECURE_MODE=False

# Database Configuration
DATABASE_URL=postgresql://litsynth_user:your_secure_password_here@localhost:5432/litsynth

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# ChromaDB Configuration
CHROMA_PERSIST_DIR=/mnt/data/chromadb

# JWT Configuration (generate with: openssl rand -hex 32)
JWT_SECRET_KEY=your_jwt_secret_key_here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=43200

# LLM Configuration
PERPLEXITY_API_KEY=your_perplexity_api_key_here
PERPLEXITY_BASE_URL=https://api.perplexity.ai
EMBEDDING_MODEL=nomic-ai/nomic-embed-text-v1.5

# Google Cloud Vision API (paste full JSON credentials below)
GOOGLE_APPLICATION_CREDENTIALS=/home/$USER/Final-Year-Project/litsynth-backend/google-vision-key.json

# CORS Configuration (use your VM's external IP)
ALLOWED_ORIGINS=http://34.83.123.45,https://34.83.123.45
FRONTEND_URL=http://34.83.123.45

# Admin Token (optional, for administrative tasks)
LITSYNTH_MASTER_TOKEN=your_admin_token_here
```

**Save and exit** (Ctrl+X, Y, Enter)

### Step 5: Upload Google Cloud Vision Credentials

**Option A: Copy from local machine**
```bash
# On your local machine (not VM):
scp /path/to/your/google-vision-key.json <username>@<VM_EXTERNAL_IP>:~/Final-Year-Project/litsynth-backend/
```

**Option B: Paste credentials directly**
```bash
# On VM:
nano ~/Final-Year-Project/litsynth-backend/google-vision-key.json

# Paste your JSON credentials
# Save and exit

# Set correct permissions
chmod 600 ~/Final-Year-Project/litsynth-backend/google-vision-key.json
```

### Step 6: Initialize Database

```bash
# Activate virtual environment (if not already active)
source ~/Final-Year-Project/litsynth-backend/venv/bin/activate

# Initialize database tables
cd ~/Final-Year-Project/litsynth-backend
python3 -c "from src.database import init_db; init_db()"

# Should output: "Database initialized successfully" or similar
```

### Step 7: Test Backend Manually

```bash
# Test backend startup
cd ~/Final-Year-Project/litsynth-backend
source venv/bin/activate
uvicorn src.main:app --host 0.0.0.0 --port 8000

# Should output:
# INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
# DATABASE: Using PostgreSQL (production)

# Test health check (in another SSH session or browser):
curl http://localhost:8000/health
# Should return: {"status":"healthy","service":"litsynth-backend","version":"1.0.0"}

# Stop server: Ctrl+C
```

### Step 8: Create Systemd Service for Backend

```bash
# Create systemd service file
sudo nano /etc/systemd/system/litsynth-backend.service
```

**Paste the following** (replace `<your_username>` with your actual username):

```ini
[Unit]
Description=LitSynth Backend FastAPI Application
After=network.target postgresql.service redis-server.service

[Service]
Type=simple
User=<your_username>
WorkingDirectory=/home/<your_username>/Final-Year-Project/litsynth-backend
Environment="PATH=/home/<your_username>/Final-Year-Project/litsynth-backend/venv/bin"
EnvironmentFile=/home/<your_username>/Final-Year-Project/litsynth-backend/.env
ExecStart=/home/<your_username>/Final-Year-Project/litsynth-backend/venv/bin/uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 1
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Save and exit**

### Step 9: Enable and Start Backend Service

```bash
# Reload systemd daemon
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable litsynth-backend

# Start service
sudo systemctl start litsynth-backend

# Check status
sudo systemctl status litsynth-backend

# Should show: "Active: active (running)"

# View logs
sudo journalctl -u litsynth-backend -f

# Stop viewing logs: Ctrl+C
```

### Step 10: Verify Backend API

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test API docs (should return HTML)
curl http://localhost:8000/docs

# Test from external IP (from your local machine):
curl http://<VM_EXTERNAL_IP>:8000/health
```

---

## Frontend Deployment

### Step 1: Update Frontend Environment Variables

```bash
# Navigate to frontend directory
cd ~/Final-Year-Project/litsynth-frontend

# Create production .env file
nano .env.production
```

**Paste the following** (replace with your VM's external IP):

```bash
# Production environment variables for GCP deployment
VITE_API_BASE_URL=http://34.83.123.45
```

**Save and exit**

### Step 2: Install Frontend Dependencies

```bash
# Install npm packages
npm install

# This will take 2-3 minutes
```

### Step 3: Build Frontend for Production

```bash
# Build production bundle
npm run build

# Should output:
# vite v5.x.x building for production...
# dist/index.html                  0.xx kB
# dist/assets/index-xxxxx.js      xxx.xx kB
# ✓ built in xxxs

# Verify build output
ls -lh dist/
# Should see: index.html, assets/, etc.
```

### Step 4: Move Build to Nginx Directory

```bash
# Create directory for frontend
sudo mkdir -p /var/www/litsynth-frontend

# Copy build files
sudo cp -r ~/Final-Year-Project/litsynth-frontend/dist/* /var/www/litsynth-frontend/

# Set correct permissions
sudo chown -R www-data:www-data /var/www/litsynth-frontend
sudo chmod -R 755 /var/www/litsynth-frontend

# Verify files
ls -la /var/www/litsynth-frontend/
```

---

## Nginx Configuration

### Step 1: Create Nginx Configuration for LitSynth

```bash
# Create Nginx site configuration
sudo nano /etc/nginx/sites-available/litsynth
```

**Paste the following** (replace `<VM_EXTERNAL_IP>` with your actual IP):

```nginx
server {
    listen 80;
    listen [::]:80;
    server_name <VM_EXTERNAL_IP>;

    # Frontend - React SPA
    location / {
        root /var/www/litsynth-frontend;
        try_files $uri $uri/ /index.html;

        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }

    # Backend API - Proxy to FastAPI
    location /api {
        # Remove /api prefix before forwarding to backend
        rewrite ^/api(.*)$ $1 break;

        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;

        # Increase timeouts for PDF processing
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
        proxy_read_timeout 300;
        send_timeout 300;
    }

    # Health check endpoint (direct passthrough)
    location /health {
        proxy_pass http://localhost:8000/health;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
    }

    # Increase client body size for PDF uploads (50MB)
    client_max_body_size 50M;

    # Logging
    access_log /var/log/nginx/litsynth-access.log;
    error_log /var/log/nginx/litsynth-error.log;
}
```

**Save and exit**

### Step 2: Enable Nginx Site Configuration

```bash
# Create symbolic link to enable site
sudo ln -s /etc/nginx/sites-available/litsynth /etc/nginx/sites-enabled/

# Remove default Nginx site (optional)
sudo rm /etc/nginx/sites-enabled/default

# Test Nginx configuration
sudo nginx -t

# Should output:
# nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
# nginx: configuration file /etc/nginx/nginx.conf test is successful
```

### Step 3: Restart Nginx

```bash
# Restart Nginx to apply changes
sudo systemctl restart nginx

# Verify Nginx is running
sudo systemctl status nginx

# Should show: "Active: active (running)"
```

### Step 4: Configure Firewall (if needed)

```bash
# Allow Nginx through firewall
sudo ufw allow 'Nginx Full'
sudo ufw allow OpenSSH
sudo ufw enable

# Verify firewall status
sudo ufw status
```

---

## Environment Variables

### Backend Environment Variables

All backend environment variables are stored in:
```
/home/<username>/Final-Year-Project/litsynth-backend/.env
```

**Required Variables**:

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://litsynth_user:password@localhost:5432/litsynth` |
| `JWT_SECRET_KEY` | Secret key for JWT tokens | Generate with `openssl rand -hex 32` |
| `PERPLEXITY_API_KEY` | Gemini LLM API key (via Perplexity) | `pplx-xxxxxxxxxxxxxxxx` |
| `GOOGLE_APPLICATION_CREDENTIALS` | Path to Google Cloud Vision JSON | `/home/user/litsynth-backend/google-vision-key.json` |
| `CHROMA_PERSIST_DIR` | ChromaDB persistence directory | `/mnt/data/chromadb` |
| `REDIS_HOST` | Redis server hostname | `localhost` |
| `REDIS_PORT` | Redis server port | `6379` |
| `ALLOWED_ORIGINS` | CORS allowed origins | `http://34.83.123.45` |
| `FRONTEND_URL` | Frontend URL | `http://34.83.123.45` |

### Frontend Environment Variables

Frontend environment variables are stored in:
```
/home/<username>/Final-Year-Project/litsynth-frontend/.env.production
```

**Required Variables**:

| Variable | Description | Example |
|----------|-------------|---------|
| `VITE_API_BASE_URL` | Backend API base URL | `http://34.83.123.45` |

**Note**: Frontend needs to be **rebuilt** after changing environment variables:
```bash
cd ~/Final-Year-Project/litsynth-frontend
npm run build
sudo cp -r dist/* /var/www/litsynth-frontend/
```

---

## Testing & Verification

### Pre-Deployment Checklist

Before testing, verify all services are running:

```bash
# Check PostgreSQL
sudo systemctl status postgresql
# Should be: Active: active (exited)

# Check Redis
sudo systemctl status redis-server
# Should be: Active: active (running)

# Check Backend
sudo systemctl status litsynth-backend
# Should be: Active: active (running)

# Check Nginx
sudo systemctl status nginx
# Should be: Active: active (running)
```

### Backend API Testing

```bash
# Test health check
curl http://<VM_EXTERNAL_IP>/api/health
# Expected: {"status":"healthy","service":"litsynth-backend","version":"1.0.0"}

# Test API docs (should return HTML)
curl -I http://<VM_EXTERNAL_IP>/api/docs
# Expected: HTTP/1.1 200 OK

# View API docs in browser:
# http://<VM_EXTERNAL_IP>/api/docs
```

### Frontend Testing

```bash
# Test frontend root
curl -I http://<VM_EXTERNAL_IP>/
# Expected: HTTP/1.1 200 OK
# Expected: Content-Type: text/html

# Open in browser:
# http://<VM_EXTERNAL_IP>
# Should see LitSynth login page
```

### Complete Workflow Testing

**Test the full user workflow** (capture screenshots for Chapter 4):

1. **Registration**:
   - Navigate to: `http://<VM_EXTERNAL_IP>`
   - Click "Register"
   - Fill in registration form
   - Verify email OTP is sent (check logs if needed)
   - Complete registration

2. **Login**:
   - Log in with registered credentials
   - Should redirect to Dashboard

3. **Workspace Creation**:
   - Create a new workspace (e.g., "Machine Learning Papers")
   - Verify workspace appears in list

4. **Document Upload**:
   - Upload a sample PDF paper
   - Wait for processing (check progress modal)
   - Verify document appears in workspace
   - Check backend logs for OCR and vectorization:
     ```bash
     sudo journalctl -u litsynth-backend -f
     ```

5. **Chat Functionality**:
   - Create a new chat in the workspace
   - Ask a question about the uploaded paper
   - Verify response includes citations
   - Test follow-up questions

6. **Export Functionality**:
   - Export chat history to PDF
   - Download and verify exported file

7. **Profile Management**:
   - Update user profile information
   - Change password (if implemented)

### Database Verification

```bash
# Connect to PostgreSQL
psql -U litsynth_user -d litsynth -h localhost

# Check tables
\dt

# Expected tables:
# public | user_account    | table | litsynth_user
# public | workspace       | table | litsynth_user
# public | chat            | table | litsynth_user
# public | chat_message    | table | litsynth_user
# public | document        | table | litsynth_user

# Check user records
SELECT id, email, created_at FROM user_account;

# Check workspaces
SELECT id, name, user_id FROM workspace;

# Exit
\q
```

### ChromaDB Verification

```bash
# Check ChromaDB persistence directory
ls -lh /mnt/data/chromadb/

# Should see ChromaDB database files
# Example: chroma.sqlite3, uuid directories
```

### Log Monitoring

```bash
# Backend logs (real-time)
sudo journalctl -u litsynth-backend -f

# Nginx access logs
sudo tail -f /var/log/nginx/litsynth-access.log

# Nginx error logs
sudo tail -f /var/log/nginx/litsynth-error.log

# PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql-15-main.log

# Redis logs
sudo tail -f /var/log/redis/redis-server.log
```

---

## Troubleshooting

### Issue 1: Backend Service Won't Start

**Symptoms**:
```bash
sudo systemctl status litsynth-backend
# Shows: Failed to start LitSynth Backend
```

**Diagnosis**:
```bash
# Check detailed logs
sudo journalctl -u litsynth-backend -n 50

# Common errors:
# - ModuleNotFoundError: Missing Python package
# - Database connection error
# - Missing environment variables
```

**Solutions**:

1. **Missing Python packages**:
   ```bash
   cd ~/Final-Year-Project/litsynth-backend
   source venv/bin/activate
   pip install -r requirements.txt
   sudo systemctl restart litsynth-backend
   ```

2. **Database connection error**:
   ```bash
   # Verify PostgreSQL is running
   sudo systemctl status postgresql

   # Test database connection
   psql -U litsynth_user -d litsynth -h localhost

   # Check DATABASE_URL in .env file
   nano ~/Final-Year-Project/litsynth-backend/.env
   ```

3. **Missing environment variables**:
   ```bash
   # Verify .env file exists and is complete
   cat ~/Final-Year-Project/litsynth-backend/.env

   # Check systemd service file references .env
   sudo nano /etc/systemd/system/litsynth-backend.service
   ```

### Issue 2: Frontend Shows "Cannot connect to backend"

**Symptoms**:
- Frontend loads but API calls fail
- Browser console shows CORS errors or network errors

**Diagnosis**:
```bash
# Test backend API from VM
curl http://localhost:8000/health

# Test backend API from external IP
curl http://<VM_EXTERNAL_IP>:8000/health

# Check Nginx proxy configuration
sudo nginx -t
```

**Solutions**:

1. **Backend not running**:
   ```bash
   sudo systemctl status litsynth-backend
   sudo systemctl start litsynth-backend
   ```

2. **Nginx proxy misconfigured**:
   ```bash
   # Check Nginx configuration
   sudo nano /etc/nginx/sites-available/litsynth

   # Verify proxy_pass points to: http://localhost:8000
   # Restart Nginx
   sudo systemctl restart nginx
   ```

3. **CORS errors**:
   ```bash
   # Update ALLOWED_ORIGINS in backend .env
   nano ~/Final-Year-Project/litsynth-backend/.env

   # Add your VM's external IP:
   ALLOWED_ORIGINS=http://34.83.123.45,https://34.83.123.45

   # Restart backend
   sudo systemctl restart litsynth-backend
   ```

4. **Wrong API URL in frontend**:
   ```bash
   # Check frontend environment variable
   cat ~/Final-Year-Project/litsynth-frontend/.env.production

   # Should be: VITE_API_BASE_URL=http://<VM_EXTERNAL_IP>

   # If changed, rebuild frontend:
   cd ~/Final-Year-Project/litsynth-frontend
   npm run build
   sudo cp -r dist/* /var/www/litsynth-frontend/
   ```

### Issue 3: PDF Upload Fails

**Symptoms**:
- Upload progress stalls
- Error message: "File too large" or "Upload failed"

**Diagnosis**:
```bash
# Check Nginx error logs
sudo tail -f /var/log/nginx/litsynth-error.log

# Check backend logs
sudo journalctl -u litsynth-backend -f

# Test upload manually
curl -X POST -F "files=@test.pdf" http://localhost:8000/upload-papers?workspace_id=<workspace_id>
```

**Solutions**:

1. **File size limit exceeded**:
   ```bash
   # Increase Nginx client_max_body_size
   sudo nano /etc/nginx/sites-available/litsynth

   # Add/modify:
   client_max_body_size 50M;

   # Restart Nginx
   sudo systemctl restart nginx
   ```

2. **Google Cloud Vision API error**:
   ```bash
   # Verify Google Cloud Vision credentials
   ls -lh ~/Final-Year-Project/litsynth-backend/google-vision-key.json

   # Check environment variable
   grep GOOGLE_APPLICATION_CREDENTIALS ~/Final-Year-Project/litsynth-backend/.env

   # Test Google Cloud Vision API (from backend directory)
   cd ~/Final-Year-Project/litsynth-backend
   source venv/bin/activate
   python3 -c "from google.cloud import vision; client = vision.ImageAnnotatorClient(); print('Google Cloud Vision OK')"
   ```

3. **ChromaDB write error**:
   ```bash
   # Check ChromaDB directory permissions
   ls -ld /mnt/data/chromadb

   # Fix ownership if needed
   sudo chown -R $USER:$USER /mnt/data/chromadb
   ```

### Issue 4: Out of Memory Errors

**Symptoms**:
- Backend crashes randomly
- VM becomes unresponsive
- Logs show "MemoryError" or "Killed"

**Diagnosis**:
```bash
# Check memory usage
free -h

# Check running processes
top

# Monitor memory during PDF processing
watch -n 1 free -h
```

**Solutions**:

1. **Add swap space** (temporary memory):
   ```bash
   # Create 2GB swap file
   sudo fallocate -l 2G /swapfile
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile

   # Make swap permanent
   echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

   # Verify swap
   free -h
   ```

2. **Reduce concurrent workers**:
   ```bash
   # Edit systemd service to use 1 worker
   sudo nano /etc/systemd/system/litsynth-backend.service

   # Change: --workers 1

   # Reload and restart
   sudo systemctl daemon-reload
   sudo systemctl restart litsynth-backend
   ```

3. **Process smaller PDFs first**:
   - Test with small PDF files (< 5 MB)
   - If large PDFs fail, implement client-side file size limits

### Issue 5: ChromaDB Data Loss After Reboot

**Symptoms**:
- Uploaded documents don't persist after VM restart
- ChromaDB directory is empty

**Diagnosis**:
```bash
# Check ChromaDB directory
ls -lh /mnt/data/chromadb/

# Check if persistent disk is mounted
df -h | grep /mnt/data
```

**Solutions**:

1. **Verify persistent disk mount**:
   ```bash
   # Check mounted disks
   lsblk

   # If /mnt/data is on boot disk (correct for free tier), verify:
   df -h | grep /mnt/data
   # Should show /dev/sda1 (boot disk)
   ```

2. **Check CHROMA_PERSIST_DIR**:
   ```bash
   # Verify environment variable
   grep CHROMA_PERSIST_DIR ~/Final-Year-Project/litsynth-backend/.env

   # Should be: CHROMA_PERSIST_DIR=/mnt/data/chromadb
   ```

3. **Re-upload documents after fixes**:
   - Delete and recreate workspace
   - Upload PDFs again to repopulate ChromaDB

---

## Screenshot Capture Checklist

**For Chapter 4, Section 4.2.3 - Description of System Operation**

Capture these 27 screenshots from your **live deployment** (not localhost):

### Category 1: Registration & Authentication (3 screenshots)

- [ ] **Figure 4.1**: Registration page with form fields
- [ ] **Figure 4.2**: OTP verification screen (email code entry)
- [ ] **Figure 4.3**: Login page with credentials

### Category 2: Workspace Management (3 screenshots)

- [ ] **Figure 4.4**: Empty dashboard (first login, no workspaces)
- [ ] **Figure 4.5**: Create workspace modal/form
- [ ] **Figure 4.6**: Dashboard with multiple workspaces listed

### Category 3: PDF Processing (4 screenshots)

- [ ] **Figure 4.7**: Document upload interface (drag-and-drop or file selector)
- [ ] **Figure 4.8**: Upload progress modal showing processing stages
- [ ] **Figure 4.9**: Document list view with uploaded papers
- [ ] **Figure 4.10**: Document detail/preview (if implemented)

### Category 4: Chat & RAG (5 screenshots)

- [ ] **Figure 4.11**: Empty chat interface (new conversation)
- [ ] **Figure 4.12**: User asks first question about paper
- [ ] **Figure 4.13**: AI response with inline citations
- [ ] **Figure 4.14**: Follow-up question and contextual response
- [ ] **Figure 4.15**: Chat history sidebar showing multiple conversations

### Category 5: Advanced Features (4 screenshots)

- [ ] **Figure 4.16**: Export chat to PDF dialog
- [ ] **Figure 4.17**: Downloaded PDF showing formatted chat history
- [ ] **Figure 4.18**: User profile page
- [ ] **Figure 4.19**: Theme toggle (light/dark mode) if implemented

### Category 6: Backend API Documentation (2 screenshots)

- [ ] **Figure 4.20**: FastAPI Swagger UI (`http://<VM_IP>/api/docs`)
- [ ] **Figure 4.21**: Example API endpoint detail (e.g., `/chat` endpoint)

### Category 7: Database Verification (2 screenshots)

- [ ] **Figure 4.22**: PostgreSQL query results (users table)
- [ ] **Figure 4.23**: PostgreSQL query results (workspaces/documents table)

### Category 8: Deployment Infrastructure (4 screenshots)

- [ ] **Figure 4.24**: GCP Compute Engine VM instance details
- [ ] **Figure 4.25**: VM resource monitoring (CPU/memory usage graph)
- [ ] **Figure 4.26**: Nginx status and configuration verification
- [ ] **Figure 4.27**: Backend systemd service status

### Screenshot Capture Tips

```bash
# For backend terminal screenshots, use clear commands:

# Backend logs with useful output
sudo journalctl -u litsynth-backend --since "5 minutes ago" | grep -E "INFO|DATABASE|ChromaDB"

# PostgreSQL query for screenshot
psql -U litsynth_user -d litsynth -h localhost -c "SELECT id, email, created_at FROM user_account;"

# System resource monitoring
htop  # Press F10 to quit

# Nginx status
sudo systemctl status nginx

# GCP VM details (from GCP Console)
# Navigate to: Compute Engine → VM Instances → litsynth-vm → Details
```

**Important**:
- Use your VM's **external IP** in browser (not localhost)
- Clear browser cache before screenshots for clean UI
- Use incognito/private mode to avoid autofill
- Capture full browser window (show URL bar with VM IP)
- For terminal screenshots, use high-contrast color scheme
- Annotate screenshots with figure numbers in Chapter 4

---

## Maintenance & Updates

### Updating Application Code

```bash
# SSH into VM
ssh <username>@<VM_EXTERNAL_IP>

# Pull latest changes from GitHub
cd ~/Final-Year-Project
git pull origin main

# Update backend
cd litsynth-backend
source venv/bin/activate
pip install -r requirements.txt  # If new dependencies
sudo systemctl restart litsynth-backend

# Update frontend
cd ../litsynth-frontend
npm install  # If new dependencies
npm run build
sudo cp -r dist/* /var/www/litsynth-frontend/

# No need to restart Nginx for frontend updates
```

### Backup Database

```bash
# Backup PostgreSQL database
pg_dump -U litsynth_user -d litsynth -h localhost -F c -f ~/litsynth-backup-$(date +%Y%m%d).dump

# Backup ChromaDB vectors
tar -czf ~/chromadb-backup-$(date +%Y%m%d).tar.gz /mnt/data/chromadb/

# Download backups to local machine (from local terminal):
scp <username>@<VM_EXTERNAL_IP>:~/litsynth-backup-*.dump ~/Downloads/
scp <username>@<VM_EXTERNAL_IP>:~/chromadb-backup-*.tar.gz ~/Downloads/
```

### Restore Database

```bash
# Restore PostgreSQL database
pg_restore -U litsynth_user -d litsynth -h localhost ~/litsynth-backup-20260119.dump

# Restore ChromaDB vectors
sudo rm -rf /mnt/data/chromadb/*
sudo tar -xzf ~/chromadb-backup-20260119.tar.gz -C /
sudo chown -R $USER:$USER /mnt/data/chromadb
```

### Monitor Resource Usage

```bash
# Real-time monitoring
htop

# Disk usage
df -h

# Database size
sudo du -sh /var/lib/postgresql/

# ChromaDB size
du -sh /mnt/data/chromadb/

# Nginx logs size
sudo du -sh /var/log/nginx/
```

---

## Cost Monitoring

### GCP Always Free Tier Limits

**Verify you stay within free tier**:

```bash
# Check VM uptime (should be continuous, not exceeding 1 instance)
uptime

# Check egress (outbound traffic)
# GCP Console → Billing → Reports
# Free tier includes: 1 GB egress/month to North America
```

**Important**:
- Only **1 e2-micro VM** per account is free
- **30 GB persistent disk** is free (boot disk included)
- **1 GB egress/month** is free (sufficient for thesis demo)
- Data **ingress** is always free
- **Snapshots** count against free storage quota

**To avoid charges**:
- Don't create additional VMs
- Don't exceed 30 GB total disk storage
- Don't create snapshots (or delete after use)
- Monitor billing dashboard weekly

---

## Security Considerations

### Recommended Security Hardening (Optional for Thesis)

1. **Enable Firewall**:
   ```bash
   sudo ufw allow 22/tcp   # SSH
   sudo ufw allow 80/tcp   # HTTP
   sudo ufw allow 443/tcp  # HTTPS (if using SSL)
   sudo ufw enable
   ```

2. **Disable Root Login**:
   ```bash
   sudo nano /etc/ssh/sshd_config
   # Set: PermitRootLogin no
   sudo systemctl restart sshd
   ```

3. **Set Up Fail2Ban** (brute-force protection):
   ```bash
   sudo apt-get install -y fail2ban
   sudo systemctl enable fail2ban
   sudo systemctl start fail2ban
   ```

4. **SSL/TLS Certificate** (if using domain):
   ```bash
   # Install Certbot
   sudo apt-get install -y certbot python3-certbot-nginx

   # Get certificate (replace with your domain)
   sudo certbot --nginx -d yourdomain.com

   # Auto-renewal
   sudo systemctl enable certbot.timer
   ```

---

## Next Steps After Deployment

1. **Verify All Services**: Complete the [Testing & Verification](#testing--verification) checklist
2. **Capture Screenshots**: Follow the [Screenshot Capture Checklist](#screenshot-capture-checklist)
3. **Write Chapter 4**: Use screenshots to write Section 4.2.3 (Description of System Operation)
4. **Document Testing**: Conduct unit, integration, system, and usability testing for Section 4.3
5. **Create Appendix B**: Extract code samples for 4 major algorithms

---

## Support Resources

- **GCP Free Tier Documentation**: https://cloud.google.com/free/docs/free-cloud-features
- **FastAPI Deployment**: https://fastapi.tiangolo.com/deployment/
- **Nginx Configuration**: https://nginx.org/en/docs/
- **PostgreSQL Documentation**: https://www.postgresql.org/docs/
- **ChromaDB Documentation**: https://docs.trychroma.com/

---

## Deployment Summary

**Deployment Type**: Direct VM deployment on Google Cloud Platform
**Free Tier**: Always Free Tier (e2-micro, 30GB disk, indefinite)
**Total Setup Time**: ~2-3 hours
**Persistent Storage**: Yes (ChromaDB, PostgreSQL, documents)
**Cold Starts**: None (always running)
**Production-Ready**: Yes (suitable for thesis demonstration)

**Access URLs**:
- Frontend: `http://<VM_EXTERNAL_IP>`
- Backend API: `http://<VM_EXTERNAL_IP>/api`
- API Docs: `http://<VM_EXTERNAL_IP>/api/docs`
- Health Check: `http://<VM_EXTERNAL_IP>/api/health`

---

**Document Version**: 1.0
**Last Updated**: 2026-01-19
**Author**: LitSynth Development Team
**Status**: Ready for Deployment
