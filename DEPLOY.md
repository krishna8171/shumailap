# Deploy on Cloudflare Pages (FREE)

This site is meant for **Cloudflare Pages free plan** — not Netlify.

- GitHub repo: https://github.com/krishna8171/sumailap  
- Upload folder: **`deploy-client`** (production files only)

---

## One-time setup (about 5 minutes)

### Step 1 — Cloudflare account (free)

1. Open **https://dash.cloudflare.com/sign-up**
2. Create a free account (email is enough)
3. Log in at **https://dash.cloudflare.com**

### Step 2 — Create a Pages project from GitHub

1. Left menu: **Workers & Pages**
2. **Create** → **Pages** → **Connect to Git**
3. Choose **GitHub** → **Authorize Cloudflare** if asked
4. Select repository: **`krishna8171/sumailap`**
5. Click **Begin setup**

### Step 3 — Settings (copy exactly)

| Setting | Value |
|--------|--------|
| Project name | `sumailap` |
| Production branch | `main` |
| Framework preset | **None** |
| Build command | *(leave empty — no build)* |
| Build output directory | **`deploy-client`** |

Then click **Save and Deploy**.

### Step 4 — Live URL

When deploy finishes you get a free link:

```
https://sumailap.pages.dev
```

| What | URL |
|------|-----|
| Website | `https://sumailap.pages.dev/` |
| Admin CMS | `https://sumailap.pages.dev/admin/` |

Admin (change after first login):

- User: `admin`
- Pass: `shumail2026`

---

## Update the live site later

After you edit files on this PC:

```powershell
cd C:\Users\admin\AGENTS\byshumail-portfolio
python scripts\build_deploy_client.py
git add -A
git commit -m "Update site"
git push
```

Cloudflare rebuilds from GitHub automatically (still free).

---

## Custom domain (optional, later)

Pages project → **Custom domains** → add e.g. `portfolio.byshumail.com`  
Cloudflare free plan supports custom domains.

---

## Why not the full repo root?

Some video files in the full project are larger than Cloudflare Pages free file limit (~25 MB).  
`deploy-client` is the slim production package (hero clips + images, no heavy reels).

Rebuild anytime:

```powershell
python scripts\build_deploy_client.py
```

---

## Temporary preview only (not permanent hosting)

If you need a link for a short call before Pages is ready:

```powershell
cd C:\Users\admin\AGENTS\byshumail-portfolio
python -m http.server 8765
```

Then in another terminal (requires [cloudflared](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/)):

```powershell
cloudflared tunnel --url http://127.0.0.1:8765
```

That temporary URL stops when you close the terminal. Use **Pages** for the real free site.
