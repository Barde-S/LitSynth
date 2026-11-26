# LitSynth HTTPS Setup Guide

## Current Status
- ✅ Domain configured: litsynth.duckdns.org → 34.118.199.221
- ✅ Nginx configured to use domain
- ❌ SSL certificate pending (Certbot dependency issue)

## Problem
Certbot cannot run due to missing `_cffi_backend` Python module.

## Solution Steps

### Option 1: Using the Script (Recommended)

1. **Transfer the script to your VM:**
   ```bash
   # On your local machine
   gcloud compute scp fix_certbot.sh litsynth-vm:~ --zone=us-west1-b
   ```

2. **SSH into your VM:**
   ```bash
   gcloud compute ssh litsynth-vm --zone=us-west1-b
   ```

3. **Run the fix script:**
   ```bash
   chmod +x fix_certbot.sh
   ./fix_certbot.sh
   ```

4. **Get SSL certificate:**
   ```bash
   sudo certbot --nginx -d litsynth.duckdns.org
   ```

   When prompted:
   - Email: Enter your email address
   - Terms of Service: Y (agree)
   - Share email with EFF: N (optional)
   - Redirect HTTP to HTTPS: 2 (Yes - recommended)

---

### Option 2: Manual Commands

If you're already connected to the VM, run these commands one by one:

```bash
# 1. Remove broken Certbot
sudo apt remove --purge certbot python3-certbot-nginx -y
sudo apt autoremove -y

# 2. Update package list
sudo apt update

# 3. Install python3-cffi (the missing dependency)
sudo apt install python3-cffi -y

# 4. Reinstall Certbot
sudo apt install certbot python3-certbot-nginx -y

# 5. Verify Certbot works
certbot --version

# 6. Get SSL certificate
sudo certbot --nginx -d litsynth.duckdns.org
```

---

## After SSL Certificate is Obtained

### 1. Update Backend CORS Origins

Edit `/home/mallamsz74/Final-Year-Project/litsynth-backend/src/main.py`:

```bash
cd /home/mallamsz74/Final-Year-Project/litsynth-backend/src

# Add HTTPS domain to origins list (around line 65)
sudo nano main.py
```

Find the `origins` list and add:
```python
origins = [
    "https://litsynth.duckdns.org",   # ← ADD THIS LINE
    "http://litsynth.duckdns.org",
    "http://34.118.199.221",
    "http://34.118.199.221:8000",
    "http://localhost:3000",
    "http://localhost:8000",
]
```

Save (Ctrl+O, Enter) and exit (Ctrl+X).

Restart backend:
```bash
sudo systemctl restart litsynth-backend
sudo systemctl status litsynth-backend
```

### 2. Rebuild Frontend with HTTPS URL

```bash
cd /home/mallamsz74/Final-Year-Project/litsynth-frontend

# Create production environment file
echo "VITE_API_BASE_URL=https://litsynth.duckdns.org" > .env.production

# Rebuild with HTTPS API URL
npm run build

# Deploy to Nginx
sudo rm -rf /var/www/litsynth/*
sudo cp -r dist/* /var/www/litsynth/

# Verify deployment
ls -la /var/www/litsynth/
```

### 3. Test HTTPS Deployment

```bash
# Test from VM
curl -I https://litsynth.duckdns.org

# Should return:
# HTTP/2 200
# (no security warnings)
```

Open in browser: **https://litsynth.duckdns.org**
- ✅ Should show green padlock (secure)
- ✅ No security warnings
- ✅ Frontend loads correctly
- ✅ API calls work via HTTPS

---

## Troubleshooting

### If Certbot still fails after reinstallation:

```bash
# Check Python CFFI installation
python3 -c "import _cffi_backend; print('CFFI OK')"

# If error, reinstall Python packages
sudo apt install --reinstall python3-cffi libffi-dev -y
```

### If Nginx doesn't restart after Certbot:

```bash
sudo nginx -t  # Test configuration
sudo systemctl restart nginx
sudo systemctl status nginx
```

### If certificate renewal fails in future:

```bash
# Test renewal (dry run)
sudo certbot renew --dry-run

# Force renewal
sudo certbot renew --force-renewal
```

---

## Expected Final State

- **URL**: https://litsynth.duckdns.org
- **Frontend**: Served via Nginx with SSL (port 443)
- **Backend**: Proxied through Nginx with HTTPS
- **Security**: Let's Encrypt SSL certificate (valid 90 days, auto-renews)
- **HTTP**: Automatically redirects to HTTPS (if option 2 selected)

---

## Next Steps After HTTPS Works

1. ✅ Test complete user workflow on HTTPS
2. ✅ Capture 27 screenshots for Chapter 4
3. ✅ Begin Chapter 4 documentation
4. ✅ Document deployment process for thesis

---

## SSL Certificate Details

- **Issuer**: Let's Encrypt Authority X3
- **Validity**: 90 days from issue date
- **Auto-renewal**: Certbot sets up automatic renewal via cron/systemd timer
- **Renewal command**: `sudo certbot renew` (runs automatically)
- **Check renewal timer**: `sudo systemctl status certbot.timer`

---

## Files Modified

- `/etc/nginx/sites-available/litsynth` - Certbot adds SSL configuration
- `/home/mallamsz74/Final-Year-Project/litsynth-backend/src/main.py` - Add HTTPS origin
- `/home/mallamsz74/Final-Year-Project/litsynth-frontend/.env.production` - HTTPS API URL

---

## Common Certbot Prompts

**Email address**: Enter valid email (for renewal notifications)
```
Enter email address (used for urgent renewal and security notices)
```

**Terms of Service**: Type `Y` and press Enter
```
Please read the Terms of Service at https://letsencrypt.org/documents/LE-SA-v1.3-September-21-2022.pdf
(A)gree/(C)ancel: A
```

**Share email**: Type `N` (optional)
```
Would you be willing to share your email address with the Electronic Frontier Foundation?
(Y)es/(N)o: N
```

**HTTP to HTTPS redirect**: Type `2` (recommended)
```
Please choose whether or not to redirect HTTP traffic to HTTPS
1: No redirect
2: Redirect - Make all requests redirect to secure HTTPS access
Select the appropriate number [1-2] then [enter]: 2
```

---

## Success Indicators

After running `sudo certbot --nginx -d litsynth.duckdns.org`, you should see:

```
Congratulations! You have successfully enabled https://litsynth.duckdns.org

IMPORTANT NOTES:
- Congratulations! Your certificate and chain have been saved at:
  /etc/letsencrypt/live/litsynth.duckdns.org/fullchain.pem
  Your key file has been saved at:
  /etc/letsencrypt/live/litsynth.duckdns.org/privkey.pem
  Your cert will expire on YYYY-MM-DD. To obtain a new or tweaked
  version of this certificate in the future, simply run certbot again
  with the "certonly" option.
```

Then Nginx will automatically restart and your site will be accessible via HTTPS.
