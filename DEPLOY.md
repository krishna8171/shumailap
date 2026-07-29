# Deploy Shumail portfolio

Use the production folder **`deploy-client`** (~100 MB, no heavy reels).  
Full repo is on GitHub: https://github.com/krishna8171/sumailap

---

## Option A — Cloudflare Pages + GitHub (recommended)

Auto-deploys every time you push to `main`.

### 1. Open Cloudflare Pages

1. Go to **https://dash.cloudflare.com**
2. Sign up / log in (free plan is fine)
3. In the left sidebar: **Workers & Pages** → **Create** → **Pages** → **Connect to Git**

### 2. Connect the GitHub repo

1. Choose **GitHub** and authorize Cloudflare if asked  
2. Select repository: **`krishna8171/sumailap`**  
3. Click **Begin setup**

### 3. Build settings (important)

| Setting | Value |
|--------|--------|
| Project name | `sumailap` (or `shumail-portfolio`) |
| Production branch | `main` |
| Framework preset | **None** |
| Build command | *(leave empty)* |
| Build output directory | **`deploy-client`** |
| Root directory | *(leave empty / `/`)* |

4. Click **Save and Deploy**
5. Wait 1–3 minutes. Cloudflare shows a live URL, for example:
   ```
   https://sumailap.pages.dev
   ```

### 4. After deploy works

| What | Link |
|------|------|
| Website | `https://YOUR-PROJECT.pages.dev/` |
| Admin CMS | `https://YOUR-PROJECT.pages.dev/admin/` |

**Admin login (change after first login):**

- Username: `admin`  
- Password: `shumail2026`

### 5. Custom domain (optional)

In the Pages project → **Custom domains** → **Set up a custom domain**  
(e.g. `portfolio.byshumail.com`). Cloudflare walks you through DNS.

### 6. Update the live site later

On your PC, after you change the website:

```powershell
cd C:\Users\admin\AGENTS\byshumail-portfolio
python scripts\build_deploy_client.py
git add -A
git commit -m "Update site content"
git push
```

Cloudflare rebuilds automatically from GitHub.

---

## Option B — Netlify Drop (no Git, ~3 minutes)

1. Open **https://app.netlify.com/drop**
2. Drag the folder:
   ```
   C:\Users\admin\AGENTS\byshumail-portfolio\deploy-client
   ```
3. Use the HTTPS link Netlify gives you.

---

## Option C — Temporary Cloudflare tunnel (same day only)

Only for a short call. Link dies when you close the terminal.

```powershell
cd C:\Users\admin\AGENTS\byshumail-portfolio
python -m http.server 8765
```

Other terminal (after installing [cloudflared](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/)):

```powershell
cloudflared tunnel --url http://127.0.0.1:8765
```

Share the `https://....trycloudflare.com` URL.

---

## Notes

- Do **not** share `http://127.0.0.1:8765` — that only works on your computer.
- Deploy from **`deploy-client`**, not the full repo. Full repo has large reels (some over Cloudflare’s ~25 MB free file limit).
- Rebuild after content edits:
  ```powershell
  python scripts\build_deploy_client.py
  ```
- Hero live clips stay in `deploy-client/assets/hero/`. Full Canva reels are stripped.

### WhatsApp message you can copy

```
Hi — here’s the portfolio website preview:

https://YOUR-PROJECT.pages.dev

Works on phone and desktop.
```

---

## After the client likes it

1. Change admin password in **Admin → Settings**  
2. Optional: connect a custom domain in Cloudflare Pages  
3. Optional: re-add full reel videos via R2/CDN if needed  
