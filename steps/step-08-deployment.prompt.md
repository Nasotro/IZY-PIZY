# Step 8 — Deployment on Linux Server

## Goal
Deploy IZY PIZY on your own Linux server: FastAPI runs as a Systemd service, Nginx serves the frontend and reverse-proxies the API, with HTTPS via Let's Encrypt.

## Context to paste at the start of the session
> "I'm building IZY PIZY, a pi memorization web app. Steps 1–7 are done (full app built and working locally). We are at step 8: deploy to my personal Linux server. I have sudo access, Nginx installed, and a domain name managed on OVH."

---

## Atomic tasks

### 8.1 — Build the frontend for production
On your server (or locally, then copy):
```bash
cd izyPizy/frontend
npm run build
# Output: frontend/dist/
```
The `dist/` folder will be served as static files by Nginx.

### 8.2 — Create the Python virtual environment on the server
```bash
cd izyPizy/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 8.3 — Create the Systemd service file
Create `deploy/izypizy.service`:
```ini
[Unit]
Description=IZY PIZY FastAPI app
After=network.target

[Service]
User=<your-linux-user>
WorkingDirectory=/path/to/izyPizy/backend
ExecStart=/path/to/izyPizy/backend/.venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```
Then enable and start it:
```bash
sudo cp deploy/izypizy.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable izypizy
sudo systemctl start izypizy
```

### 8.4 — Create the Nginx configuration file
Create `deploy/nginx-izypizy.conf`:
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    # Serve the Svelte frontend
    root /path/to/izyPizy/frontend/dist;
    index index.html;

    # SPA fallback — needed for client-side routing
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Reverse proxy for the FastAPI backend
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```
Then activate it:
```bash
sudo ln -s /path/to/deploy/nginx-izypizy.conf /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 8.5 — Set up HTTPS with Certbot (Let's Encrypt)
```bash
sudo apt install certbot python3-certbot-nginx   # if not already installed
sudo certbot --nginx -d yourdomain.com
# Follow prompts — Certbot will auto-edit the Nginx config to add SSL
```
Certbot installs an auto-renewal cron/timer. Verify with:
```bash
sudo certbot renew --dry-run
```

---

## Files created in this step
- `deploy/izypizy.service` ← new
- `deploy/nginx-izypizy.conf` ← new

## Verification
- `sudo systemctl status izypizy` → active (running)
- `curl http://localhost:8000/api/health` → `{"status":"ok"}`
- `http://yourdomain.com` → app loads over HTTP (before Certbot)
- `https://yourdomain.com` → app loads over HTTPS (after Certbot)
- Server reboot: `sudo reboot` → app comes back up automatically
