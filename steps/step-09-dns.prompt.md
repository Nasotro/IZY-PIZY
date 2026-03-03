# Step 9 — DNS Configuration (OVH)

## Goal
Point your OVH domain name at your Linux server's public IP so the app is reachable at `https://yourdomain.com`.

## Context to paste at the start of the session
> "I'm building IZY PIZY. The app is fully deployed on my Linux server (step 8 done). I own a domain name registered on OVH. We are at step 9: configure DNS so the domain points to my server."

---

## Prerequisites
Before starting, collect:
1. **Your server's public IP** — run `curl https://api.ipify.org` on your server
2. **Your domain name** — e.g. `izypizy.com`
3. **OVH credentials** — log in at [ovh.com/manager](https://www.ovh.com/manager/)

---

## Atomic tasks

### 9.1 — Add an A record in the OVH DNS zone
1. Go to OVH Manager → **Domain names** → select your domain
2. Click the **DNS zone** tab
3. Click **Add an entry** → choose type **A**
4. Fill in:
   - **Subdomain**: leave empty (for the root domain `@`) — or type `www` for a `www.` subdomain
   - **TTL**: default (3600)
   - **Target**: your server's public IP address
5. Save the record

### 9.2 — (Optional) Add a www CNAME
If you want both `yourdomain.com` and `www.yourdomain.com` to work:
- Add a **CNAME** record: subdomain `www` → target `yourdomain.com.` (with trailing dot)
- Also add `www` to the `server_name` in your Nginx config and to the Certbot command:
  ```bash
  sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
  ```

### 9.3 — Wait for DNS propagation
- Propagation typically takes 5–60 minutes (up to 24h maximum)
- Check status with: `nslookup yourdomain.com 8.8.8.8`
- Or use [dnschecker.org](https://dnschecker.org) to see global propagation

### 9.4 — Verify Nginx `server_name` matches the domain
Make sure `deploy/nginx-izypizy.conf` has:
```nginx
server_name yourdomain.com;
```
(Replace with your actual domain. If you also added `www`, include both.)

### 9.5 — Re-run Certbot for the final HTTPS certificate
Once DNS has propagated and the domain resolves to your server:
```bash
sudo certbot --nginx -d yourdomain.com
```
This issues the real certificate and updates the Nginx config automatically.

---

## Verification
- `nslookup yourdomain.com` → returns your server's IP
- `http://yourdomain.com` → redirects to HTTPS (Certbot sets this up automatically)
- `https://yourdomain.com` → IZY PIZY loads with a valid padlock
- `https://yourdomain.com/api/health` → `{"status":"ok"}`
- Certificate expiry: `echo | openssl s_client -connect yourdomain.com:443 2>/dev/null | openssl x509 -noout -dates`
