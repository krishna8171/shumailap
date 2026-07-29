/**
 * Shared content loader — site + admin
 *
 * Base = data/site.json + data/gallery.json (all text, images, reels on disk)
 * Overlay = localStorage admin edits (uploads, text tweaks)
 *
 * Incomplete localStorage must NEVER hide the full base content.
 */
const SITE_STORAGE_KEY = "byshumail_site_v8";
const MESSAGES_STORAGE_KEY = "byshumail_messages_v1";
const AUTH_STORAGE_KEY = "byshumail_admin_auth";

// Default password for demo admin (change in admin settings)
const DEFAULT_ADMIN = { user: "admin", pass: "shumail2026" };

/** Root-relative base for data files (works from / and from /admin/) */
function siteRootPrefix() {
  try {
    const path = String(location.pathname || "/").replace(/\\/g, "/");
    if (path.includes("/admin/") || /\/admin\/?$/.test(path) || path.endsWith("/admin")) {
      return "../";
    }
  } catch (_) {}
  return "";
}

async function fetchJson(url) {
  const candidates = [];
  // Prefer correct root from current page
  candidates.push(siteRootPrefix() + url);
  // Fallbacks
  if (!url.startsWith("/") && !url.startsWith("../")) {
    candidates.push("../" + url);
    candidates.push(url);
    candidates.push("/" + url.replace(/^\//, ""));
  }
  const tried = new Set();
  for (const u of candidates) {
    if (tried.has(u)) continue;
    tried.add(u);
    try {
      const res = await fetch(u, { cache: "no-store" });
      if (res.ok) return await res.json();
    } catch (_) {}
  }
  return null;
}

async function loadGalleryFallback() {
  return fetchJson("data/gallery.json");
}

/**
 * Merge base files + localStorage.
 * When meta.adminSaved is true, companies/creatives/services/process from admin
 * are authoritative (including empty = user deleted everything).
 */
function mergeSiteData(base, local) {
  if (!base) return local || null;
  if (!local) return base;

  const adminSaved = !!(local.meta && local.meta.adminSaved);
  const out = { ...base, ...local };

  // Nested objects — keep base keys, overlay local values
  for (const key of ["about", "contact", "cta", "meta", "socials", "hero", "nav", "sections", "footer"]) {
    if (base[key] || local[key]) {
      out[key] = { ...(base[key] || {}), ...(local[key] || {}) };
    }
  }
  // Preserve adminSaved flag after meta merge
  if (adminSaved) {
    out.meta = out.meta || {};
    out.meta.adminSaved = true;
    if (local.meta?.adminSavedAt) out.meta.adminSavedAt = local.meta.adminSavedAt;
  }

  // Arrays: prefer local only if it has content; else base — UNLESS adminSaved
  const preferArray = (localArr, baseArr) => {
    if (adminSaved && Array.isArray(localArr)) return localArr;
    if (Array.isArray(localArr) && localArr.length > 0) return localArr;
    if (Array.isArray(baseArr) && baseArr.length > 0) return baseArr;
    return Array.isArray(localArr) ? localArr : baseArr || [];
  };

  out.stats = preferArray(local.stats, base.stats);
  // Keep experience years in sync with base (e.g. 7+) even if old localStorage still has 6+
  if (Array.isArray(base.stats) && Array.isArray(out.stats)) {
    base.stats.forEach((bs, i) => {
      if (!out.stats[i] || !bs) return;
      if (/years/i.test(String(bs.label || "")) && bs.value) {
        out.stats[i] = { ...out.stats[i], value: bs.value, label: bs.label || out.stats[i].label };
      }
    });
  }
  out.services = preferArray(local.services, base.services);
  out.process = preferArray(local.process, base.process);

  // Companies
  const baseCos = Array.isArray(base.companies) ? base.companies : [];
  const localCos = Array.isArray(local.companies) ? local.companies : [];

  if (adminSaved && Array.isArray(local.companies)) {
    // Admin is source of truth: deleted companies stay deleted
    out.companies = localCos.map((lc) => {
      const bc = baseCos.find((b) => b.id === lc.id || b.title === lc.title) || {};
      const merged = { ...bc, ...lc };
      if (String(lc.image || "").startsWith("data:")) merged.image = lc.image;
      else if (!merged.image && bc.image) merged.image = bc.image;
      // Work: if local explicitly has work array (even empty), keep it
      if (Array.isArray(lc.work)) {
        merged.work = lc.work;
      } else if (Array.isArray(bc.work)) {
        merged.work = bc.work;
      } else {
        merged.work = [];
      }
      merged.workCount = (merged.work || []).length;
      return merged;
    });
  } else if (!localCos.length && baseCos.length) {
    out.companies = baseCos;
  } else if (localCos.length && baseCos.length) {
    const byId = new Map(baseCos.map((c) => [c.id || c.title, c]));
    out.companies = localCos.map((lc) => {
      const bc = byId.get(lc.id) || byId.get(lc.title) || {};
      const merged = { ...bc, ...lc };
      if (!merged.image && bc.image) merged.image = bc.image;
      if (String(lc.image || "").startsWith("data:")) merged.image = lc.image;
      const lw = Array.isArray(lc.work) ? lc.work : null;
      const bw = Array.isArray(bc.work) ? bc.work : [];
      if (lw !== null) merged.work = lw;
      else merged.work = bw;
      merged.workCount = (merged.work || []).length;
      return merged;
    });
    // Only auto-append missing base companies when NOT admin-managed
    const localIds = new Set(localCos.map((c) => c.id || c.title));
    baseCos.forEach((bc) => {
      if (!localIds.has(bc.id) && !localIds.has(bc.title)) out.companies.push(bc);
    });
  } else {
    out.companies = preferArray(localCos, baseCos);
  }

  // Creatives
  const baseCr = Array.isArray(base.creatives) ? base.creatives : [];
  const localCr = Array.isArray(local.creatives) ? local.creatives : [];

  if (adminSaved && Array.isArray(local.creatives)) {
    out.creatives = localCr.map((lc) => {
      const bc = baseCr.find((b) => b.id === lc.id) || {};
      const m = { ...bc, ...lc };
      if (String(lc.image || "").startsWith("data:")) m.image = lc.image;
      else if (!m.image && bc.image) m.image = bc.image;
      if (String(lc.video || "").startsWith("data:")) m.video = lc.video;
      else if (!m.video && bc.video) m.video = bc.video;
      return m;
    });
  } else if (!localCr.length && baseCr.length) {
    out.creatives = baseCr;
  } else if (localCr.length && baseCr.length) {
    const localHasUploads = localCr.some(
      (c) =>
        String(c.image || "").startsWith("data:") || String(c.video || "").startsWith("data:")
    );
    if (localCr.length < Math.max(3, Math.floor(baseCr.length * 0.5)) && !localHasUploads) {
      out.creatives = baseCr;
    } else {
      const byId = new Map(baseCr.map((c) => [c.id, { ...c }]));
      localCr.forEach((lc) => {
        if (lc.id && byId.has(lc.id)) {
          const bc = byId.get(lc.id);
          const m = { ...bc, ...lc };
          if (!m.image && bc.image) m.image = bc.image;
          if (!m.video && bc.video) m.video = bc.video;
          if (String(lc.image || "").startsWith("data:")) m.image = lc.image;
          if (String(lc.video || "").startsWith("data:")) m.video = lc.video;
          byId.set(lc.id, m);
        } else if (lc.id) {
          byId.set(lc.id, lc);
        } else {
          byId.set("local_" + Math.random().toString(36).slice(2), lc);
        }
      });
      out.creatives = [...byId.values()];
    }
  } else {
    out.creatives = preferArray(localCr, baseCr);
  }

  // Portrait / about image: local data: upload wins, else base path
  if (String(local.portrait || "").startsWith("data:")) out.portrait = local.portrait;
  else out.portrait = local.portrait || base.portrait;

  if (out.about && base.about) {
    if (String(local.about?.image || "").startsWith("data:")) {
      out.about.image = local.about.image;
    } else {
      // Prefer real face portrait over old work posters in localStorage
      const localImg = local.about?.image || "";
      const baseImg = base.about?.image || "";
      const localIsWork =
        /work-\d|assets\/canva\/video|assets\/hero\/hd|front-\d/i.test(localImg);
      const baseIsFace = /about-face|portrait/i.test(baseImg);
      if (baseIsFace && (!localImg || localIsWork)) out.about.image = baseImg;
      else out.about.image = localImg || baseImg;
    }
    // Text fields: non-empty local wins
    for (const k of ["title", "titleAccent", "lead", "body", "yearsCard", "yearsCardLabel", "clientsLabel"]) {
      if (local.about && local.about[k] != null && String(local.about[k]).trim() !== "") {
        out.about[k] = local.about[k];
      } else if (base.about[k] != null) {
        out.about[k] = base.about[k];
      }
    }
    // Prefer latest years of experience from site data (7+)
    if (base.about.yearsCard) out.about.yearsCard = base.about.yearsCard;
    if (base.about.yearsCardLabel) out.about.yearsCardLabel = base.about.yearsCardLabel;
    if (base.about.body && /7 years/i.test(base.about.body)) out.about.body = base.about.body;
    if ((!local.about?.achievements || !local.about.achievements.length) && base.about.achievements) {
      out.about.achievements = base.about.achievements;
    }
    if ((!local.about?.clients || !local.about.clients.length) && base.about.clients) {
      out.about.clients = base.about.clients;
    }
  }

  // Portfolio categories
  out.portfolioCategories =
    (Array.isArray(local.portfolioCategories) && local.portfolioCategories.length
      ? local.portfolioCategories
      : null) ||
    base.portfolioCategories ||
    [];

  // Logos-only mode: strip any work arrays on companies
  if (base.meta?.logosOnly || local.meta?.logosOnly || out.meta?.logosOnly) {
    out.meta = out.meta || {};
    out.meta.logosOnly = true;
    // Prefer cleaned assets/logos paths from base when titles match
    const baseByTitle = Object.fromEntries(
      (base.companies || [])
        .filter((c) => c && c.title && c.image)
        .map((c) => [String(c.title).toLowerCase(), c.image])
    );
    out.companies = (out.companies || []).map((c) => {
      const titleKey = String(c.title || "").toLowerCase();
      const baseImg = baseByTitle[titleKey];
      const useImg =
        baseImg && String(baseImg).includes("assets/logos/")
          ? baseImg
          : c.image || baseImg;
      return {
        ...c,
        image: useImg,
        work: [],
        workCount: 0,
        type: "logo",
        section: "companies",
        cat: "companies",
      };
    });
  }

  out.portfolio = [...(out.companies || []), ...(out.creatives || [])];

  // Scalar text: non-empty local wins
  for (const k of ["brand", "name", "role", "tagline", "greeting"]) {
    if (local[k] != null && String(local[k]).trim() !== "") out[k] = local[k];
    else if (base[k] != null) out[k] = base[k];
  }

  return out;
}

function applyGalleryToBase(data, gal) {
  if (!data || !gal) return data;
  if (Array.isArray(gal.companies)) {
    // Always logos only on public site
    data.companies = gal.companies.map((c) => ({
      ...c,
      work: [],
      workCount: 0,
      type: "logo",
      section: "companies",
      cat: "companies",
    }));
  }
  if (gal.meta?.logosOnly || data.meta?.logosOnly) {
    data.meta = data.meta || {};
    data.meta.logosOnly = true;
  }
  if (gal.creatives?.length) data.creatives = gal.creatives;
  data.portfolio = [...(data.companies || []), ...(data.creatives || [])];
  if (gal.categories?.length) data.portfolioCategories = gal.categories;
  if (gal.portrait && !data.portrait) data.portrait = gal.portrait;
  return data;
}

async function loadSiteData() {
  // 1) Full base from files (path-safe from both site root and /admin/)
  let base = (await fetchJson("data/site.json")) || {};
  const gal = await loadGalleryFallback();
  if (gal) base = applyGalleryToBase(base, gal);

  // Debug aid: if still empty, base fetch failed
  if (!base.creatives?.length && !base.companies?.length && !base.name) {
    console.warn(
      "[ByShumail] Could not load data/site.json or gallery.json. Open site via http://127.0.0.1:8765/ not as a file."
    );
  }

  // Ensure arrays on base
  base.companies = base.companies || [];
  base.creatives = base.creatives || [];
  base.portfolio = base.portfolio || [...base.companies, ...base.creatives];

  // 2) Admin overlay from localStorage (any recent key)
  let local = null;
  const keysToTry = [
    SITE_STORAGE_KEY,
    "byshumail_site_v6",
    "byshumail_site_v5",
    "byshumail_site_v4",
    "byshumail_site_v3",
    "byshumail_site_v2",
  ];
  for (const k of keysToTry) {
    try {
      const raw = localStorage.getItem(k);
      if (raw) {
        local = JSON.parse(raw);
        break;
      }
    } catch (_) {}
  }

  // 3) Merge — base content always visible; local edits/uploads on top
  const data = mergeSiteData(base, local);

  // Normalize
  if (!data.companies && data.portfolio) {
    data.companies = data.portfolio.filter((p) => p.cat === "companies" || p.section === "companies");
  }
  if (!data.creatives && data.portfolio) {
    data.creatives = data.portfolio.filter((p) => p.cat !== "companies" && p.section !== "companies");
  }
  data.companies = data.companies || [];
  data.creatives = data.creatives || [];
  data.portfolio = [...data.companies, ...data.creatives];

  return data;
}

function saveSiteData(data) {
  data.meta = data.meta || {};
  data.meta.updatedAt = new Date().toISOString().slice(0, 10);
  // Mark as admin-authored so website respects removals (companies/creatives)
  data.meta.adminSaved = true;
  data.meta.adminSavedAt = new Date().toISOString();
  // Always persist arrays even when empty (explicit delete)
  data.companies = Array.isArray(data.companies) ? data.companies : [];
  data.creatives = Array.isArray(data.creatives) ? data.creatives : [];
  data.portfolio = [...data.companies, ...data.creatives];
  const json = JSON.stringify(data);
  try {
    localStorage.setItem(SITE_STORAGE_KEY, json);
  } catch (e) {
    // Quota exceeded — common when many large data: URL uploads
    console.error("localStorage save failed", e);
    throw new Error(
      "Browser storage is full. Use smaller images (under 2–4MB) or fewer uploads, then Save again."
    );
  }
  return data;
}

function resetSiteData() {
  [
    SITE_STORAGE_KEY,
    "byshumail_site_v7",
    "byshumail_site_v6",
    "byshumail_site_v5",
    "byshumail_site_v4",
    "byshumail_site_v3",
    "byshumail_site_v2",
    "byshumail_site_v1",
  ].forEach((k) => localStorage.removeItem(k));
}

function loadMessages() {
  try {
    return JSON.parse(localStorage.getItem(MESSAGES_STORAGE_KEY) || "[]");
  } catch {
    return [];
  }
}

function saveMessage(msg) {
  const list = loadMessages();
  list.unshift({
    id: "m_" + Date.now(),
    createdAt: new Date().toISOString(),
    read: false,
    ...msg,
  });
  localStorage.setItem(MESSAGES_STORAGE_KEY, JSON.stringify(list));
  return list;
}

function updateMessages(list) {
  localStorage.setItem(MESSAGES_STORAGE_KEY, JSON.stringify(list));
}

function isAdminAuthed() {
  return sessionStorage.getItem(AUTH_STORAGE_KEY) === "1";
}

function setAdminAuth(ok) {
  if (ok) sessionStorage.setItem(AUTH_STORAGE_KEY, "1");
  else sessionStorage.removeItem(AUTH_STORAGE_KEY);
}

function checkAdminLogin(user, pass) {
  let creds = DEFAULT_ADMIN;
  try {
    const stored = localStorage.getItem("byshumail_admin_creds");
    if (stored) creds = JSON.parse(stored);
  } catch (_) {}
  return user === creds.user && pass === creds.pass;
}

function setAdminCreds(user, pass) {
  localStorage.setItem("byshumail_admin_creds", JSON.stringify({ user, pass }));
}

// Apply data to public site DOM
function applySiteToDOM(data) {
  if (!data) return;

  // Fill missing copy defaults (nav labels, section headings, etc.)
  if (typeof window.cmsEnsureDefaults === "function") {
    data = window.cmsEnsureDefaults(data);
  }

  const get = (path) =>
    typeof window.cmsGet === "function" ? window.cmsGet(data, path) : undefined;

  // Every element marked data-cms="path"
  document.querySelectorAll("[data-cms]").forEach((el) => {
    const path = el.getAttribute("data-cms");
    const val = get(path);
    if (val == null || val === "") return;
    el.textContent = String(val);
  });

  // Every media element marked data-cms-media="path"
  document.querySelectorAll("[data-cms-media]").forEach((el) => {
    const path = el.getAttribute("data-cms-media");
    let val = get(path);
    if (!val) return;
    if (el.tagName === "IMG" || el.tagName === "VIDEO" || el.tagName === "SOURCE") {
      if (!String(val).startsWith("data:") && !String(val).includes("?")) {
        val = val + (val.includes("?") ? "" : "?v=" + Date.now());
      }
      el.setAttribute("src", val);
    }
  });

  const setText = (sel, val) => {
    const el = document.querySelector(sel);
    if (el && val != null && val !== "") el.textContent = val;
  };

  // Brand wordmark (keeps orange dot)
  const logoTexts = document.querySelectorAll(".logo-text");
  logoTexts.forEach((el) => {
    const brand = data.brand || "Shumail.";
    el.innerHTML = brand.replace(/\.$/, "") + '<span class="logo-dot">.</span>';
  });

  // Portrait optional (hero now uses best-works showcase; keep for admin/legacy)
  if (data.portrait) {
    const img = document.getElementById("portraitImg");
    if (img) {
      const src = data.portrait;
      img.src = src.startsWith("data:") ? src : src + (src.includes("?") ? "" : "?v=" + Date.now());
    }
  }

  // About title with accent (special HTML structure)
  if (data.about) {
    const title = document.querySelector("#about .section-title");
    if (title && (data.about.title || data.about.titleAccent)) {
      title.innerHTML = `${data.about.title || ""}<br /><span class="accent">${data.about.titleAccent || ""}</span>`;
    }
  }

  // Contact title with accent
  if (data.sections?.contact) {
    const t = data.sections.contact;
    const el = document.querySelector("#contact .section-title");
    if (el && (t.title || t.titleAccent)) {
      el.innerHTML = `<span data-cms="sections.contact.title">${t.title || ""}</span><span class="accent" data-cms="sections.contact.titleAccent">${t.titleAccent || ""}</span>`;
    }
  }

  // Footer year + tagline
  const footerP = document.querySelector(".footer-inner p");
  if (footerP) {
    const year = new Date().getFullYear();
    const tag = get("footer.tagline") || "Creating visuals that move people.";
    footerP.innerHTML = `© <span id="year">${year}</span> ${escapeHtml(data.name || "Muhammed Shumail")}. ${escapeHtml(tag)}`;
  }

  // Stats
  if (data.stats && data.stats.length) {
    const stats = document.querySelectorAll(".stat");
    data.stats.forEach((s, i) => {
      if (!stats[i]) return;
      const num = stats[i].querySelector(".stat-num");
      const label = stats[i].querySelector(".stat-label");
      if (num) num.textContent = s.value;
      if (label) label.textContent = s.label;
    });
  }

  // About body / media / lists
  if (data.about) {
    const lead = document.querySelector("#about .lead");
    if (lead) lead.textContent = data.about.lead || "";
    const bodyPs = document.querySelectorAll("#about .about-copy > p:not(.lead):not(.eyebrow)");
    if (bodyPs[0] && data.about.body) bodyPs[0].textContent = data.about.body;

    if (data.about.image) {
      const aboutImg = document.querySelector(".about-frame img");
      if (aboutImg) {
        // Prefer face portrait; bust cache when path updates
        const src = data.about.image;
        aboutImg.src = src.startsWith("data:") ? src : src;
      }
    }

    // Rebuild achievements cleanly (avoids ghost/duplicate text layers)
    if (Array.isArray(data.about.achievements) && data.about.achievements.length) {
      const list = document.getElementById("achievementsList") || document.querySelector(".achievements");
      if (list) {
        list.innerHTML = data.about.achievements
          .map((a) => {
            const title = escapeHtml(String(a.title || "").trim());
            const desc = escapeHtml(String(a.desc || "").trim());
            return `<li>
              <span class="ach-dot" aria-hidden="true"></span>
              <div class="ach-body">
                <strong class="ach-title">${title}</strong>
                <span class="ach-desc">${desc}</span>
              </div>
            </li>`;
          })
          .join("");
      }
    }

    // clients from array or clientsText
    let clients = data.about.clients;
    if ((!clients || !clients.length) && data.about.clientsText) {
      clients = data.about.clientsText.split(",").map((s) => s.trim()).filter(Boolean);
      data.about.clients = clients;
    }
    if (clients) {
      const pills = document.querySelector(".client-pills");
      if (pills) {
        pills.innerHTML = clients.map((c) => `<span>${escapeHtml(c)}</span>`).join("");
      }
    }
  }

  // Services
  if (data.services) {
    const cards = document.querySelectorAll(".service-card");
    data.services.forEach((s, i) => {
      if (!cards[i]) return;
      const h3 = cards[i].querySelector("h3");
      const p = cards[i].querySelector("p");
      if (h3) h3.textContent = s.title;
      if (p) p.textContent = s.desc;
    });
  }

  // Companies — logos only (no work galleries)
  const companies =
    data.companies ||
    (data.portfolio || []).filter((p) => p.section === "companies" || p.cat === "companies");
  const companiesGrid = document.getElementById("companiesGrid");
  if (companiesGrid) {
    const list = (companies || []).filter((p) => p.visible !== false && p.image);
    if (!list.length) {
      companiesGrid.innerHTML = `<p class="muted">No partner logos yet.</p>`;
    } else {
      companiesGrid.innerHTML = list
        .map((p) => {
          const src = String(p.image || "");
          const bust = src.includes("?") ? src : `${src}?v=logo3`;
          return `
        <div class="logo-card" title="${escapeAttr(p.title || "Partner")}">
          <img src="${escapeAttr(bust)}" alt="${escapeAttr(p.title || "Company logo")}" loading="lazy" decoding="async" />
        </div>`;
        })
        .join("");
    }
  }

  // Creatives portfolio
  const creatives =
    data.creatives ||
    (data.portfolio || []).filter((p) => p.section === "creatives" || (p.cat && p.cat !== "companies"));
  const grid = document.getElementById("portfolioGrid");
  if (grid) {
    const items = creatives.filter((p) => p.visible !== false);
    const countEl = document.getElementById("galleryCount");

    // Categories removed — show all work in one grid
    const filterBar = document.getElementById("filterBar");
    if (filterBar) filterBar.innerHTML = "";

    if (countEl) {
      countEl.textContent = items.length ? `${items.length} works` : "";
    }

    // Only true playable video — Canva "video" items are often JPG posters
    const isPlayableVideo = (p) => {
      const src = p.video || "";
      if (!src) return false;
      if (String(src).startsWith("data:video")) return true;
      if (/\.(mp4|webm|ogg|mov)(\?|$)/i.test(src)) return true;
      return false;
    };
    const isVideoPoster = (p) => {
      if (isPlayableVideo(p)) return false;
      return (p.type || "").toLowerCase() === "video" || /\/video\//.test(p.image || "");
    };

    grid.innerHTML = items
      .map((p, idx) => {
        const playable = isPlayableVideo(p);
        const posterOnly = isVideoPoster(p);
        const poster = p.image || "";
        const videoSrc = playable ? p.video : "";
        const src = playable ? videoSrc : poster || p.video || "";
        const title = p.title && p.title !== p.categoryLabel ? p.title : playable || posterOnly ? "Reel" : "Work";
        const badge = playable || posterOnly
          ? `<span class="media-badge">Reel</span>`
          : "";
        // Muted + loop + playsinline required for autoplay in modern browsers
        const media = playable
          ? `<video class="reel-video" src="${escapeAttr(videoSrc)}" ${
              poster ? `poster="${escapeAttr(poster)}"` : ""
            } muted loop playsinline autoplay preload="metadata"></video>${badge}`
          : `<img src="${escapeAttr(src)}" alt="${escapeAttr(title)}" loading="lazy" decoding="async" />${badge}`;
        return `
        <article class="folio-card${playable ? " is-reel" : ""}" data-index="${idx}" data-src="${escapeAttr(src)}" data-media="${playable ? "video" : "image"}">
          ${media}
          <div class="folio-overlay">
            <h3>${escapeHtml(title)}</h3>
          </div>
        </article>`;
      })
      .join("");

    // Notify page scripts to (re)bind reel autoplay
    try {
      document.dispatchEvent(new CustomEvent("byshumail:gallery-ready"));
    } catch (_) {}
  }

  // Process
  if (data.process) {
    const steps = document.querySelectorAll(".process-steps .step");
    data.process.forEach((s, i) => {
      if (!steps[i]) return;
      const num = steps[i].querySelector(".step-num");
      const h3 = steps[i].querySelector("h3");
      const p = steps[i].querySelector("p");
      if (num) num.textContent = s.num;
      if (h3) h3.textContent = s.title;
      if (p) p.textContent = s.desc;
    });
  }

  // Contact links (hrefs + socials) + hero social icons
  if (data.contact) {
    const c = data.contact;
    const emailA = document.querySelector('#contact a[data-cms="contact.email"]');
    if (emailA && c.email) {
      emailA.href = "mailto:" + c.email;
      emailA.textContent = c.email;
    }
    const phoneA = document.querySelector('#contact a[data-cms="contact.phone"]');
    if (phoneA && c.phone) {
      phoneA.href = "tel:" + String(c.phone).replace(/\s/g, "");
      phoneA.textContent = c.phone;
    }
    const socialRow = document.getElementById("socialRow") || document.querySelector(".social-row");
    if (socialRow) {
      const igHandle = (c.instagramHandle || "@shumail.ap").trim();
      const liHandle = (c.linkedinHandle || "@muhammed-shumail").trim();
      const parts = [];
      if (c.instagram) {
        parts.push(
          `<a href="${escapeAttr(c.instagram)}" target="_blank" rel="noopener noreferrer">Instagram · ${escapeHtml(igHandle)}</a>`
        );
      }
      if (c.linkedin) {
        parts.push(
          `<a href="${escapeAttr(c.linkedin)}" target="_blank" rel="noopener noreferrer">LinkedIn · ${escapeHtml(liHandle)}</a>`
        );
      }
      socialRow.innerHTML = parts.join("");
    }
    // Hero icon links
    const heroSocials = document.querySelector(".hero-socials");
    if (heroSocials) {
      const ig = heroSocials.querySelector('a[aria-label="Instagram"]');
      const li = heroSocials.querySelector('a[aria-label="LinkedIn"]');
      const em = heroSocials.querySelector('a[aria-label="Email"]');
      const ph = heroSocials.querySelector('a[aria-label="Phone"]');
      if (ig && c.instagram) ig.href = c.instagram;
      if (li && c.linkedin) li.href = c.linkedin;
      if (em && c.email) em.href = "mailto:" + c.email;
      if (ph && c.phone) ph.href = "tel:" + String(c.phone).replace(/\s/g, "");
    }
  }

  // Contact section subtitle
  if (data.sections?.contact?.sub) {
    const sub = document.querySelector("#contact .section-sub");
    if (sub) sub.textContent = data.sections.contact.sub;
  }

  // CTA
  if (data.cta) {
    const ctaH = document.querySelector(".cta-inner h2");
    const ctaP = document.querySelector(".cta-inner p:not(.eyebrow)");
    if (ctaH) ctaH.textContent = data.cta.title;
    if (ctaP) ctaP.textContent = data.cta.text;
  }

  if (data.meta) {
    if (data.meta.title) document.title = data.meta.title;
    const desc = document.querySelector('meta[name="description"]');
    if (desc && data.meta.description) desc.setAttribute("content", data.meta.description);
  }
}

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function escapeAttr(str) {
  return escapeHtml(str).replace(/'/g, "&#39;");
}

// Export for modules / global
window.ByShumail = {
  loadSiteData,
  saveSiteData,
  resetSiteData,
  loadMessages,
  saveMessage,
  updateMessages,
  isAdminAuthed,
  setAdminAuth,
  checkAdminLogin,
  setAdminCreds,
  applySiteToDOM,
  SITE_STORAGE_KEY,
  MESSAGES_STORAGE_KEY,
  DEFAULT_ADMIN,
};
