# Shumail Ap — Portfolio Website Redesign

A modern dark portfolio redesign for **[byshumail.my.canva.site](https://byshumail.my.canva.site)** — Muhammed Shumail, Dubai-based Content Creator, Photographer & Videographer.

## Customer deliverables

| File | Purpose |
|------|---------|
| `index.html` | Public website |
| `admin/` | Full CMS (every text + media) |
| `Shumail-Website-Proposal.pdf` | Proposal deck for the client |
| `data/site.json` | Default content |
| `data/gallery.json` | Companies + creatives (classified) |
| `assets/canva/` | Images imported from Canva |
| `assets/portrait.jpg` | His real Canva front portrait |

### Site structure (matches Canva)

1. **Industries worked with** — company logos only  
2. **Creatives** — Final Reel · BTS · Hanan Shaah Concert · Drone Shots · Automobile · Weddings & Events  

Junk UI assets are filtered out. Admin can add/edit/upload logos, images, and videos.

## Design direction

Inspired by a premium dark UI portfolio mock (orange accent, circular hero portrait, stats bar, sticky nav with **Hire Me** CTA). Hero portrait is **his real studio photo** from the Canva front page. Content and services come from the existing site.

### Sections

1. **Hero** — name, role, socials, hire / view work CTAs, stats, real portrait  
2. **Services** — drone, photography, videography, real estate, editing, storytelling  
3. **About** — bio, achievements, clients (NEWIZZ, Revo Realty)  
4. **Portfolio** — filterable grid  
5. **Process** — Discover → Plan → Create → Enhance → Deliver  
6. **Contact** — form saves to admin inbox + mailto  

## Admin panel

1. Serve the project (required so `data/site.json` loads).  
2. Open **`/admin/`**  
3. Login: **`admin`** / **`shumail2026`** (change in Settings)  

You can edit hero, about, services, portfolio, process, contact, SEO, and view contact-form messages. Saves use browser `localStorage` and apply on the public site.

## Run locally

```bash
# From this folder
python -m http.server 8765
```

- Website: http://127.0.0.1:8765/  
- Admin: http://127.0.0.1:8765/admin/  

## Regenerate proposal PDF

```bash
python generate_proposal_pdf.py
```

## Stack

- Static HTML / CSS / JS (no build step)  
- Google Fonts: Inter + Outfit  
- Content: `data/site.json` + admin localStorage override  

## Contact (from original site)

- **Email:** mudshumail@gmail.com  
- **Phone:** +971 50 810 2437  
- **Instagram:** [@shumail.ap](https://instagram.com/shumail.ap)  
- **LinkedIn:** [muhammed-shumail](http://linkedin.com/in/muhammed-shumail-231102297)
