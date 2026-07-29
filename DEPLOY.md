# Share the site with a client (UAE / anywhere)

Use the ready folder: **`deploy-client`** (~51 MB, optimized for upload).

## Option A — Netlify Drop (recommended, ~3 minutes)

1. Open **https://app.netlify.com/drop** in your browser  
2. Sign up / log in (email or Google)  
3. On your PC, open this folder in File Explorer:
   ```
   C:\Users\admin\AGENTS\byshumail-portfolio\deploy-client
   ```
4. **Drag the entire `deploy-client` folder** onto the Netlify Drop page  
5. Wait until upload finishes  
6. Netlify shows a live link, for example:
   ```
   https://something-random-123.netlify.app
   ```
7. Click **Site configuration → Domain management → Options → Edit site name**  
   Change to something clear, e.g. `shumail-portfolio`  
   Final link example:
   ```
   https://shumail-portfolio.netlify.app
   ```

### Send the client

| What | Link |
|------|------|
| Website | `https://YOUR-NAME.netlify.app/` |
| Admin CMS | `https://YOUR-NAME.netlify.app/admin/` |

**Admin login (change after first login):**

- Username: `admin`  
- Password: `shumail2026`

### WhatsApp message you can copy

```
Hi — here’s the portfolio website preview:

https://YOUR-NAME.netlify.app

Works on phone and desktop.
```

---

## Option B — Temporary link (same day only)

Only if you need a link for a short call and Netlify is delayed:

```powershell
cd C:\Users\admin\AGENTS\byshumail-portfolio
python -m http.server 8765
```

Other terminal (after installing cloudflared):

```powershell
cloudflared tunnel --url http://127.0.0.1:8765
```

Share the `https://....trycloudflare.com` URL. It stops when you close the terminal.

---

## Notes

- Do **not** share `http://127.0.0.1:8765` — that only works on your computer.  
- `deploy-client` excludes heavy reel MP4s so upload stays under Netlify limits; posters still show.  
- To rebuild the deploy folder after content edits, run:
  ```powershell
  cd C:\Users\admin\AGENTS\byshumail-portfolio
  python scripts\build_deploy_client.py
  ```
  (or ask Grok to rebuild it).  
- For a custom domain later (e.g. `portfolio.byshumail.com`), use Netlify → Domain management → Add domain.

---

## After the client likes it

1. Change admin password in **Admin → Settings**  
2. Optional: buy a domain and connect it in Netlify  
3. Optional: re-add full reel videos via a larger host or CDN if needed  
