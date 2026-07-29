/* Admin panel — companies, creatives (image/video), full CMS */
(() => {
  const {
    loadSiteData,
    saveSiteData,
    resetSiteData,
    loadMessages,
    updateMessages,
    isAdminAuthed,
    setAdminAuth,
    checkAdminLogin,
    setAdminCreds,
  } = window.ByShumail;

  let data = null;

  // Categories removed from public site — keep a simple default for data shape only
  const CREATIVE_CATS = [{ key: "work", label: "Work" }];

  const $ = (sel) => document.querySelector(sel);
  const $$ = (sel) => [...document.querySelectorAll(sel)];

  const loginScreen = $("#loginScreen");
  const app = $("#app");
  const toast = $("#toast");

  function showToast(msg, isError = false) {
    toast.hidden = false;
    toast.textContent = msg;
    toast.classList.toggle("error", isError);
    clearTimeout(showToast._t);
    showToast._t = setTimeout(() => {
      toast.hidden = true;
    }, 2800);
  }

  function showApp() {
    loginScreen.classList.add("hidden");
    app.classList.remove("hidden");
  }

  function showLogin() {
    app.classList.add("hidden");
    loginScreen.classList.remove("hidden");
  }

  function esc(s) {
    return String(s ?? "")
      .replace(/&/g, "&amp;")
      .replace(/"/g, "&quot;")
      .replace(/</g, "&lt;");
  }

  function isVideoSrc(src, _type) {
    // Playable video only (not Canva JPG posters tagged type:video)
    if (String(src || "").startsWith("data:video")) return true;
    if (/\.(mp4|webm|ogg|mov)(\?|$)/i.test(src || "")) return true;
    return false;
  }

  function isReelPoster(src, type) {
    if (isVideoSrc(src, type)) return false;
    return (type || "").toLowerCase() === "video";
  }

  function isTruncatedPlaceholder(val) {
    return !val || String(val).includes("…") || String(val).includes("...");
  }

  function readFileAsDataURL(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result);
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
  }

  function syncPortfolioFromParts() {
    data.companies = data.companies || [];
    data.creatives = data.creatives || [];
    data.portfolio = [...data.companies, ...data.creatives];
    data.portfolioCategories = [
      { key: "companies", label: "Industries worked with", group: "companies" },
      ...CREATIVE_CATS.map((c) => ({ ...c, group: "creatives" })),
    ];
  }

  // Login
  $("#loginForm").addEventListener("submit", (e) => {
    e.preventDefault();
    const user = $("#loginUser").value.trim();
    const pass = $("#loginPass").value;
    if (checkAdminLogin(user, pass)) {
      setAdminAuth(true);
      $("#loginError").textContent = "";
      boot();
    } else {
      $("#loginError").textContent = "Invalid username or password.";
    }
  });

  $("#logoutBtn").addEventListener("click", () => {
    setAdminAuth(false);
    showLogin();
  });

  const titles = {
    dashboard: ["Dashboard", "Overview of your portfolio site"],
    alledit: ["All text & media", "Change every letter and every image/video"],
    hero: ["Hero & Brand", "Name, role, stats, and portrait"],
    about: ["About", "Bio, achievements, and clients"],
    services: ["Services", "What you offer"],
    companies: ["Companies", "Industries worked with — logos"],
    creatives: ["Creatives", "Work images & videos by category"],
    process: ["Process", "How it works steps"],
    contact: ["Contact", "Details and SEO meta"],
    messages: ["Messages", "Contact form inbox"],
    settings: ["Settings", "Password, import, reset"],
  };

  $$(".nav-item").forEach((btn) => {
    btn.addEventListener("click", () => {
      $$(".nav-item").forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      const panel = btn.dataset.panel;
      $$(".panel").forEach((p) => p.classList.remove("active"));
      $(`#panel-${panel}`)?.classList.add("active");
      const [t, s] = titles[panel] || ["Admin", ""];
      $("#panelTitle").textContent = t;
      $("#panelSub").textContent = s;
      if (panel === "messages") renderMessages();
      if (panel === "dashboard") renderDashboard();
      if (panel === "companies") renderCompanies();
      if (panel === "creatives") renderCreatives();
      if (panel === "alledit") renderAllEdit();
    });
  });

  function ensureArrays() {
    data.companies = data.companies || [];
    data.creatives = data.creatives || [];
    // migrate flat portfolio if needed
    if (!data.companies.length && !data.creatives.length && data.portfolio?.length) {
      data.companies = data.portfolio.filter((p) => p.cat === "companies" || p.section === "companies");
      data.creatives = data.portfolio.filter((p) => p.cat !== "companies" && p.section !== "companies");
    }
  }

  function renderAllEdit() {
    const box = $("#allEditFields");
    if (!box || !window.CMS_SCHEMA) return;
    if (typeof window.cmsEnsureDefaults === "function") data = window.cmsEnsureDefaults(data);

    const get = (path) => window.cmsGet(data, path);

    // Live inventory of media managed in other panels
    const nCo = (data.companies || []).length;
    const nWork = (data.companies || []).reduce((s, c) => s + ((c.work || []).length || 0), 0);
    const nCr = (data.creatives || []).length;
    const nVid = (data.creatives || []).filter(
      (c) =>
        String(c.video || "").startsWith("data:video") ||
        /\.(mp4|webm|ogg|mov)(\?|$)/i.test(c.video || c.image || "")
    ).length;
    const inventory = `
      <div class="edit-group cms-inventory">
        <h4>CMS status — what you can edit</h4>
        <ul class="cms-check-list">
          <li><strong>All letters</strong> — fields below (nav, hero, about, sections, contact, footer)</li>
          <li><strong>Portrait</strong> — Hero section below or Hero panel · ${
            data.portrait ? "✓ set" : "○ missing"
          }</li>
          <li><strong>About photo</strong> — About section below · ${
            data.about?.image ? "✓ set" : "○ missing"
          }</li>
          <li><strong>Companies</strong> — <em>Companies</em> panel · ${nCo} brands · ${nWork} work images</li>
          <li><strong>Creatives / reels</strong> — <em>Creatives</em> panel · ${nCr} items · ${nVid} playable videos</li>
          <li><strong>Services</strong> — <em>Services</em> panel · ${(data.services || []).length} cards</li>
          <li><strong>Process steps</strong> — <em>Process</em> panel · ${(data.process || []).length} steps</li>
        </ul>
        <p class="muted" style="margin:0.75rem 0 0;font-size:0.85rem">
          Tip: If counts look empty, open <strong>Settings → Reload all text + images + reels</strong>, then return here.
        </p>
      </div>`;

    box.innerHTML =
      inventory +
      window.CMS_SCHEMA.groups
      .map((group) => {
        // Skip help-only groups (rendered as inventory above)
        if (group.id === "mediaHelp") return "";
        const fields = group.fields
          .map((f) => {
            if (String(f.path || "").startsWith("_help.")) return "";
            const val = get(f.path);
            const str = val == null ? "" : String(val);
            if (f.type === "media") {
              const src = mediaSrcForPreview(str);
              const isVid = isVideoSrc(str, "");
              const preview = str
                ? isVid
                  ? `<video src="${esc(src)}" muted playsinline preload="metadata"></video>`
                  : `<img src="${esc(src)}" alt="" loading="lazy" />`
                : `<span class="muted" style="font-size:0.7rem">No file</span>`;
              const fieldVal = mediaFieldLabel(str);
              return `
              <div class="edit-field" data-path="${esc(f.path)}">
                <label><span>${esc(f.label)}</span></label>
                <div class="media-edit-row">
                  <div class="thumb-preview ${str ? "has-media" : "empty"}">${preview}</div>
                  <div class="grow">
                    <input type="text" data-all-path="${esc(f.path)}" value="${esc(fieldVal)}"
                      data-has-upload="${str.startsWith("data:") ? "1" : "0"}"
                      placeholder="path, URL, or upload →" />
                    <label class="btn btn-outline btn-sm file-btn">
                      Upload ${f.accept && f.accept.includes("video") ? "file" : "image"}
                      <input type="file" accept="${esc(f.accept || "image/*,video/*")}" data-all-file="${esc(f.path)}" />
                    </label>
                  </div>
                </div>
              </div>`;
            }
            if (f.type === "textarea") {
              return `
              <div class="edit-field">
                <label><span>${esc(f.label)}</span>
                  <textarea rows="3" data-all-path="${esc(f.path)}">${esc(str)}</textarea>
                </label>
              </div>`;
            }
            return `
              <div class="edit-field">
                <label><span>${esc(f.label)}</span>
                  <input type="text" data-all-path="${esc(f.path)}" value="${esc(str)}" />
                </label>
              </div>`;
          })
          .join("");
        if (!fields.trim()) return "";
        return `<div class="edit-group"><h4>${esc(group.title)}</h4>${fields}</div>`;
      })
      .join("");

    // live preview updates into data object (skip upload placeholders)
    box.querySelectorAll("[data-all-path]").forEach((input) => {
      const apply = () => {
        const path = input.dataset.allPath;
        const val = input.value;
        if (isUploadPlaceholder(val)) return;
        if (
          input.dataset.hasUpload === "1" &&
          !String(val || "").startsWith("data:") &&
          String(window.cmsGet(data, path) || "").startsWith("data:")
        ) {
          return;
        }
        window.cmsSet(data, path, val);
        input.dataset.hasUpload = String(val || "").startsWith("data:") ? "1" : "0";
        if (path === "about.clientsText") {
          data.about = data.about || {};
          data.about.clients = input.value
            .split(",")
            .map((s) => s.trim())
            .filter(Boolean);
        }
      };
      input.addEventListener("input", apply);
      input.addEventListener("change", apply);
    });

    box.querySelectorAll("[data-all-file]").forEach((input) => {
      input.addEventListener("change", async () => {
        const path = input.dataset.allFile;
        const file = input.files?.[0];
        if (!file) return;
        if (file.size > 12 * 1024 * 1024) {
          showToast("File must be under 12MB.", true);
          return;
        }
        try {
          const dataUrl = await readFileAsDataURL(file);
          window.cmsSet(data, path, dataUrl);
          // Keep dual-bound panel fields in sync so Save cannot wipe the upload
          if (path === "portrait" && $("#f_portrait")) {
            $("#f_portrait").value = mediaFieldLabel(dataUrl);
            $("#f_portrait").dataset.hasUpload = "1";
            updatePortraitPreview();
          }
          if (path === "about.image" && $("#f_about_image")) {
            $("#f_about_image").value = mediaFieldLabel(dataUrl);
            $("#f_about_image").dataset.hasUpload = "1";
          }
          renderAllEdit();
          showToast("Media ready — click Save changes.");
        } catch {
          showToast("Could not read file.", true);
        }
      });
    });
  }

  function collectAllEditFields() {
    document.querySelectorAll("[data-all-path]").forEach((input) => {
      const path = input.dataset.allPath;
      if (!path || path.startsWith("_help.")) return;
      const val = input.value;
      const current = window.cmsGet(data, path);
      // Don't replace real data: URLs with short placeholder labels in the field
      if (
        isUploadPlaceholder(val) ||
        (String(current || "").startsWith("data:") &&
          !String(val || "").startsWith("data:")) ||
        (input.dataset.hasUpload === "1" && !String(val || "").startsWith("data:"))
      ) {
        return;
      }
      window.cmsSet(data, path, val);
    });
    if (data.about?.clientsText) {
      data.about.clients = data.about.clientsText
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean);
    }
  }

  function fillForm() {
    if (!data) return;
    if (typeof window.cmsEnsureDefaults === "function") data = window.cmsEnsureDefaults(data);
    ensureArrays();

    $("#f_greeting").value = data.greeting || "";
    $("#f_brand").value = data.brand || "";
    $("#f_name").value = data.name || "";
    $("#f_role").value = data.role || "";
    $("#f_tagline").value = data.tagline || "";
    $("#f_portrait").value = mediaFieldLabel(data.portrait || "");
    if ($("#f_portrait")) {
      $("#f_portrait").dataset.hasUpload = String(data.portrait || "").startsWith("data:")
        ? "1"
        : "0";
    }
    updatePortraitPreview();

    const statsBox = $("#statsFields");
    statsBox.innerHTML = (data.stats || [])
      .map(
        (s, i) => `
      <div>
        <label><span>Stat ${i + 1} value</span><input data-stat-val="${i}" value="${esc(s.value)}" /></label>
        <label style="margin-top:0.5rem"><span>Label</span><input data-stat-label="${i}" value="${esc(s.label)}" /></label>
      </div>`
      )
      .join("");

    if ($("#f_cta_title")) $("#f_cta_title").value = data.cta?.title || "";
    if ($("#f_cta_text")) $("#f_cta_text").value = data.cta?.text || "";

    if ($("#f_about_title")) $("#f_about_title").value = data.about?.title || "";
    if ($("#f_about_accent")) $("#f_about_accent").value = data.about?.titleAccent || "";
    if ($("#f_about_lead")) $("#f_about_lead").value = data.about?.lead || "";
    if ($("#f_about_body")) $("#f_about_body").value = data.about?.body || "";
    if ($("#f_about_image")) {
      $("#f_about_image").value = mediaFieldLabel(data.about?.image || "");
      $("#f_about_image").dataset.hasUpload = String(data.about?.image || "").startsWith(
        "data:"
      )
        ? "1"
        : "0";
    }
    if ($("#f_clients"))
      $("#f_clients").value =
        data.about?.clientsText || (data.about?.clients || []).join(", ");

    // Hero portrait upload helper (if present)
    const heroUpload = $("#f_portrait_file");
    if (heroUpload && !heroUpload._bound) {
      heroUpload._bound = true;
      heroUpload.addEventListener("change", async () => {
        const file = heroUpload.files?.[0];
        if (!file) return;
        const dataUrl = await readFileAsDataURL(file);
        data.portrait = dataUrl;
        $("#f_portrait").value = mediaFieldLabel(dataUrl);
        $("#f_portrait").dataset.hasUpload = "1";
        updatePortraitPreview();
        showToast("Portrait ready — Save changes.");
      });
    }

    renderAllEdit();

    $("#achievementsFields").innerHTML = (data.about?.achievements || [])
      .map(
        (a, i) => `
      <div class="list-item">
        <strong>Achievement ${i + 1}</strong>
        <div class="row">
          <label><span>Title</span><input data-ach-title="${i}" value="${esc(a.title)}" /></label>
          <label><span>Description</span><input data-ach-desc="${i}" value="${esc(a.desc)}" /></label>
        </div>
      </div>`
      )
      .join("");

    renderServices();
    renderCompanies();
    renderCreatives();
    renderProcess();

    const aboutFile = $("#f_about_file");
    if (aboutFile && !aboutFile._bound) {
      aboutFile._bound = true;
      aboutFile.addEventListener("change", async () => {
        const file = aboutFile.files?.[0];
        if (!file) return;
        const dataUrl = await readFileAsDataURL(file);
        data.about = data.about || {};
        data.about.image = dataUrl;
        if ($("#f_about_image")) {
          $("#f_about_image").value = mediaFieldLabel(dataUrl);
          $("#f_about_image").dataset.hasUpload = "1";
        }
        showToast("About image ready — Save changes.");
      });
    }

    const c = data.contact || {};
    if ($("#f_email")) $("#f_email").value = c.email || "";
    if ($("#f_phone")) $("#f_phone").value = c.phone || "";
    if ($("#f_location")) $("#f_location").value = c.location || "";
    if ($("#f_ig")) $("#f_ig").value = c.instagram || "";
    if ($("#f_ig_handle")) $("#f_ig_handle").value = c.instagramHandle || "";
    if ($("#f_li")) $("#f_li").value = c.linkedin || "";
    if ($("#f_li_handle")) $("#f_li_handle").value = c.linkedinHandle || "";

    if ($("#f_meta_title")) $("#f_meta_title").value = data.meta?.title || "";
    if ($("#f_meta_desc")) $("#f_meta_desc").value = data.meta?.description || "";
  }

  function updatePortraitPreview() {
    const img = $("#portraitPreview");
    if (!img) return;
    // Prefer in-memory data (real data: URL) over field label
    const path = String(data?.portrait || $("#f_portrait")?.value || "").trim();
    if (!path || isUploadPlaceholder(path)) {
      if (data?.portrait && String(data.portrait).startsWith("data:")) {
        img.src = data.portrait;
        return;
      }
      if (!path || isUploadPlaceholder(path)) {
        img.removeAttribute("src");
        return;
      }
    }
    img.src = mediaSrcForPreview(path);
  }

  document.addEventListener("input", (e) => {
    if (e.target?.id === "f_portrait") updatePortraitPreview();
  });

  function renderServices() {
    const box = $("#servicesList");
    box.innerHTML = (data.services || [])
      .map(
        (s, i) => `
      <div class="list-item">
        <div class="list-item-head">
          <strong>Service ${i + 1}</strong>
          <button type="button" class="btn btn-outline btn-sm" data-del-service="${i}">Remove</button>
        </div>
        <div class="row">
          <label class="full"><span>Title</span><input data-svc-title="${i}" value="${esc(s.title)}" /></label>
          <label class="full"><span>Description</span><textarea data-svc-desc="${i}" rows="2">${esc(s.desc)}</textarea></label>
        </div>
      </div>`
      )
      .join("");

    box.querySelectorAll("[data-del-service]").forEach((btn) => {
      btn.addEventListener("click", () => {
        data.services.splice(+btn.dataset.delService, 1);
        renderServices();
      });
    });
  }

  $("#addService").addEventListener("click", () => {
    data.services = data.services || [];
    data.services.push({ title: "New service", desc: "Description…" });
    renderServices();
  });

  /** Resolve path for <img>/<video> preview from /admin/ */
  function mediaSrcForPreview(src) {
    if (!src) return "";
    const s = String(src);
    if (
      s.startsWith("data:") ||
      s.startsWith("blob:") ||
      s.startsWith("http://") ||
      s.startsWith("https://") ||
      s.startsWith("//")
    ) {
      return s;
    }
    // From admin/ page → site root
    return "../" + s.replace(/^\.\//, "").replace(/^\//, "");
  }

  /** Short label in text inputs (never dump multi‑MB data: URLs into value=) */
  function mediaFieldLabel(src) {
    if (!src) return "";
    const s = String(src);
    if (s.startsWith("data:image")) return "[Uploaded image — click Save]";
    if (s.startsWith("data:video")) return "[Uploaded video — click Save]";
    if (s.startsWith("data:")) return "[Uploaded file — click Save]";
    if (s.length > 100) return s.slice(0, 90) + "…";
    return s;
  }

  function isUploadPlaceholder(val) {
    return /^\[Uploaded\b/i.test(String(val || "").trim());
  }

  function mediaPreviewHtml(src, type) {
    if (!src) {
      return `<div class="thumb-preview empty"><span class="muted" style="font-size:0.68rem;text-align:center;padding:0.25rem">No media</span></div>`;
    }
    const v = isVideoSrc(src, type);
    const resolved = mediaSrcForPreview(src);
    if (v) {
      return `<div class="thumb-preview has-media"><video src="${esc(
        resolved
      )}" muted playsinline preload="metadata"></video></div>`;
    }
    return `<div class="thumb-preview has-media"><img src="${esc(
      resolved
    )}" alt="Preview" loading="lazy" onerror="this.parentElement.classList.add('broken');this.style.display='none'" /></div>`;
  }

  async function filesToDataUrls(fileList, { maxEach, asVideo }) {
    const files = [...(fileList || [])];
    const out = [];
    for (const file of files) {
      if (file.size > maxEach) {
        showToast(
          `${file.name} is too large (max ${Math.round(maxEach / 1024 / 1024)}MB). Skipped.`,
          true
        );
        continue;
      }
      try {
        const dataUrl = await readFileAsDataURL(file);
        out.push({ file, dataUrl, asVideo: asVideo || file.type.startsWith("video/") });
      } catch {
        showToast(`Could not read ${file.name}`, true);
      }
    }
    return out;
  }

  // ---- Companies (logo + multiple work images/videos) ----
  function renderCompanies() {
    ensureArrays();
    const box = $("#companiesList");
    if (!box) return;
    if (!data.companies.length) {
      box.innerHTML = `<p class="muted">No companies yet. Click “Add company” to add a logo and work images.</p>`;
      return;
    }
    box.innerHTML = data.companies
      .map((p, i) => {
        return `
      <div class="list-item company-item" data-co-index="${i}">
        <div class="list-item-head">
          <strong>Logo ${i + 1}${p.title ? " — " + esc(p.title) : ""}</strong>
          <button type="button" class="btn btn-outline btn-sm" data-del-co="${i}">Remove</button>
        </div>
        <div class="thumb-row">
          ${mediaPreviewHtml(p.image, "logo")}
          <div class="grow-fields">
            <label><span>Company name</span>
              <input data-co-title="${i}" value="${esc(p.title || "")}" placeholder="e.g. Koukh al Shay" />
            </label>
            <label><span>Logo path / URL <em class="muted">(or upload)</em></span>
              <input data-co-img="${i}" value="${esc(mediaFieldLabel(p.image))}"
                data-has-upload="${String(p.image || "").startsWith("data:") ? "1" : "0"}"
                placeholder="assets/… · https://… · or upload logo" />
            </label>
            <div class="thumb-row">
              <label class="btn btn-outline btn-sm file-btn">
                Upload logo
                <input type="file" accept="image/*" data-co-file="${i}" />
              </label>
              <label class="check-row">
                <input type="checkbox" data-co-vis="${i}" ${p.visible !== false ? "checked" : ""} />
                Visible on site
              </label>
            </div>
          </div>
        </div>
      </div>`;
      })
      .join("");

    box.querySelectorAll("[data-del-co]").forEach((btn) => {
      btn.addEventListener("click", () => {
        if (!confirm("Remove this company and its work list?")) return;
        data.companies.splice(+btn.dataset.delCo, 1);
        renderCompanies();
      });
    });

    box.querySelectorAll("[data-co-file]").forEach((input) => {
      input.addEventListener("change", async () => {
        const i = +input.dataset.coFile;
        const file = input.files?.[0];
        if (!file) return;
        if (file.size > 6 * 1024 * 1024) {
          showToast("Logo must be under 6MB.", true);
          return;
        }
        try {
          data.companies[i].image = await readFileAsDataURL(file);
          data.companies[i].type = "logo";
          renderCompanies();
          showToast("Logo uploaded — click Save changes.");
        } catch {
          showToast("Could not read logo file.", true);
        }
      });
    });

    box.querySelectorAll("[data-co-img]").forEach((input) => {
      input.addEventListener("change", () => {
        const i = +input.dataset.coImg;
        const val = input.value.trim();
        if (isUploadPlaceholder(val)) return;
        if (val) {
          data.companies[i].image = val;
          input.dataset.hasUpload = "0";
          renderCompanies();
        }
      });
    });
  }

  $("#addCompany")?.addEventListener("click", () => {
    ensureArrays();
    data.companies.push({
      id: "co" + Date.now(),
      title: "New company",
      cat: "companies",
      categoryLabel: "Industries worked with",
      image: "",
      work: [],
      workCount: 0,
      visible: true,
      type: "logo",
      section: "companies",
    });
    renderCompanies();
    showToast("Company added — upload logo + work images, then Save.");
  });

  // ---- Creatives ----
  function renderCreatives() {
    ensureArrays();
    const box = $("#creativesList");
    if (!box) return;

    // Bulk add bar always visible (no categories)
    const bulkBar = `
      <div class="bulk-upload-bar card" style="margin-bottom:1rem;padding:1rem">
        <div class="card-head" style="margin:0">
          <div>
            <h4 style="margin:0 0 0.25rem">Add more images / videos</h4>
            <p class="muted" style="margin:0;font-size:0.85rem">Select multiple files at once. They appear at the top of the list (no categories).</p>
          </div>
          <div class="thumb-row">
            <label class="btn btn-primary btn-sm file-btn">
              + Upload images
              <input type="file" accept="image/*" multiple id="bulkCrImages" />
            </label>
            <label class="btn btn-outline btn-sm file-btn">
              + Upload videos
              <input type="file" accept="video/*" multiple id="bulkCrVideos" />
            </label>
          </div>
        </div>
      </div>`;

    if (!data.creatives.length) {
      box.innerHTML =
        bulkBar +
        `<p class="muted">No creatives yet. Use <strong>+ Upload images</strong> above or “Add creative”.</p>`;
    } else {
      box.innerHTML =
        bulkBar +
        data.creatives
          .map((p, i) => {
            const src = p.video || p.image || "";
            const kind = isVideoSrc(src, p.type)
              ? "Video"
              : isReelPoster(src, p.type)
                ? "Reel still"
                : "Image";
            return `
      <div class="list-item" data-cr-index="${i}">
        <div class="list-item-head">
          <strong>Creative ${i + 1}</strong>
          <span class="media-type-tag">${kind}</span>
          <button type="button" class="btn btn-outline btn-sm" data-del-cr="${i}">Remove</button>
        </div>
        <div class="thumb-row">
          ${mediaPreviewHtml(src, p.type)}
          <div class="grow-fields">
            <div class="row">
              <label class="full"><span>Title</span><input data-cr-title="${i}" value="${esc(p.title || "")}" /></label>
            </div>
            <label class="full"><span>Path / URL <em class="muted">(or upload)</em></span>
              <input data-cr-src="${i}" value="${esc(mediaFieldLabel(src))}"
                data-has-upload="${String(src).startsWith("data:") ? "1" : "0"}"
                placeholder="assets/… · https://… · or upload below" />
            </label>
            <div class="thumb-row">
              <label class="btn btn-outline btn-sm file-btn">
                Replace image
                <input type="file" accept="image/*" data-cr-file-img="${i}" />
              </label>
              <label class="btn btn-outline btn-sm file-btn">
                Replace video
                <input type="file" accept="video/*" data-cr-file-vid="${i}" />
              </label>
              <label class="check-row">
                <input type="checkbox" data-cr-vis="${i}" ${p.visible !== false ? "checked" : ""} />
                Visible
              </label>
            </div>
          </div>
        </div>
      </div>`;
          })
          .join("");
    }

    const bulkAdd = async (fileList, asVideo) => {
      const max = asVideo ? 20 * 1024 * 1024 : 8 * 1024 * 1024;
      const items = await filesToDataUrls(fileList, { maxEach: max, asVideo });
      if (!items.length) return;
      ensureArrays();
      for (const it of items.reverse()) {
        data.creatives.unshift({
          id: "cr" + Date.now() + Math.random().toString(36).slice(2, 6),
          title: it.asVideo ? "Reel" : "Work",
          cat: "work",
          categoryLabel: "Work",
          image: it.dataUrl,
          video: it.asVideo ? it.dataUrl : "",
          visible: true,
          type: it.asVideo ? "video" : "media",
          section: "creatives",
        });
      }
      renderCreatives();
      showToast(`Added ${items.length} creative(s) — click Save changes.`);
    };

    $("#bulkCrImages")?.addEventListener("change", async (e) => {
      await bulkAdd(e.target.files, false);
      e.target.value = "";
    });
    $("#bulkCrVideos")?.addEventListener("change", async (e) => {
      await bulkAdd(e.target.files, true);
      e.target.value = "";
    });

    box.querySelectorAll("[data-del-cr]").forEach((btn) => {
      btn.addEventListener("click", () => {
        data.creatives.splice(+btn.dataset.delCr, 1);
        renderCreatives();
      });
    });

    const bindUpload = (selector, asVideo) => {
      box.querySelectorAll(selector).forEach((input) => {
        input.addEventListener("change", async () => {
          const i = +(input.dataset.crFileImg ?? input.dataset.crFileVid);
          const file = input.files?.[0];
          if (!file) return;
          const max = asVideo ? 20 * 1024 * 1024 : 8 * 1024 * 1024;
          if (file.size > max) {
            showToast(asVideo ? "Video must be under 20MB." : "Image must be under 8MB.", true);
            return;
          }
          try {
            const dataUrl = await readFileAsDataURL(file);
            if (asVideo) {
              data.creatives[i].video = dataUrl;
              data.creatives[i].image = dataUrl;
              data.creatives[i].type = "video";
            } else {
              data.creatives[i].image = dataUrl;
              data.creatives[i].video = "";
              data.creatives[i].type = "media";
            }
            renderCreatives();
            showToast((asVideo ? "Video" : "Image") + " updated — click Save changes.");
          } catch {
            showToast("Could not read file.", true);
          }
        });
      });
    };
    bindUpload("[data-cr-file-img]", false);
    bindUpload("[data-cr-file-vid]", true);

    box.querySelectorAll("[data-cr-src]").forEach((input) => {
      input.addEventListener("change", () => {
        const i = +input.dataset.crSrc;
        const val = input.value.trim();
        if (isUploadPlaceholder(val)) return;
        if (!val) return;
        const video = isVideoSrc(val, "");
        data.creatives[i].image = val;
        data.creatives[i].video = video ? val : "";
        data.creatives[i].type = video ? "video" : "media";
        input.dataset.hasUpload = "0";
        renderCreatives();
      });
    });
  }

  $("#addCreative")?.addEventListener("click", () => {
    ensureArrays();
    data.creatives.unshift({
      id: "cr" + Date.now(),
      title: "New work",
      cat: "work",
      categoryLabel: "Work",
      image: "",
      video: "",
      visible: true,
      type: "media",
      section: "creatives",
    });
    renderCreatives();
    showToast("New work added — upload image/video & Save.");
  });

  function renderProcess() {
    const box = $("#processList");
    box.innerHTML = (data.process || [])
      .map(
        (s, i) => `
      <div class="list-item">
        <div class="row">
          <label><span>Number</span><input data-proc-num="${i}" value="${esc(s.num)}" /></label>
          <label><span>Title</span><input data-proc-title="${i}" value="${esc(s.title)}" /></label>
          <label class="full"><span>Description</span><textarea data-proc-desc="${i}" rows="2">${esc(s.desc)}</textarea></label>
        </div>
      </div>`
      )
      .join("");
  }

  /** Prefer data: URLs and non-empty all-edit values over stale panel paths */
  function mergeMedia(path, fieldSelector) {
    const el = document.querySelector(fieldSelector);
    const fieldVal = el?.value?.trim() || "";
    const dataVal = window.cmsGet(data, path) || "";
    if (String(dataVal).startsWith("data:") && !String(fieldVal).startsWith("data:")) {
      return; // keep uploaded data URL
    }
    if (String(fieldVal).startsWith("data:")) {
      window.cmsSet(data, path, fieldVal);
      return;
    }
    if (fieldVal && !isTruncatedPlaceholder(fieldVal)) {
      window.cmsSet(data, path, fieldVal);
    }
  }

  function collectForm() {
    // Full schema fields first (covers every letter + media paths)
    if (document.querySelector("[data-all-path]")) {
      collectAllEditFields();
    }

    // Only overwrite from panel fields when panel inputs are present & non-truncated
    const pick = (id, current) => {
      const el = $(id);
      if (!el) return current;
      const v = el.value.trim();
      if (!v || isTruncatedPlaceholder(v)) return current;
      // never replace a data: URL with a short path
      if (String(current || "").startsWith("data:") && !v.startsWith("data:")) return current;
      return v;
    };
    data.greeting = pick("#f_greeting", data.greeting);
    data.brand = pick("#f_brand", data.brand);
    data.name = pick("#f_name", data.name);
    data.role = pick("#f_role", data.role);
    data.tagline = pick("#f_tagline", data.tagline);
    mergeMedia("portrait", "#f_portrait");

    data.stats = data.stats || [];
    data.stats.forEach((_, i) => {
      const v = document.querySelector(`[data-stat-val="${i}"]`);
      const l = document.querySelector(`[data-stat-label="${i}"]`);
      if (v) data.stats[i].value = v.value.trim();
      if (l) data.stats[i].label = l.value.trim();
    });

    data.cta = data.cta || {};
    data.cta.title = $("#f_cta_title").value.trim();
    data.cta.text = $("#f_cta_text").value.trim();

    data.about = data.about || {};
    if ($("#f_about_title")) data.about.title = $("#f_about_title").value.trim();
    if ($("#f_about_accent")) data.about.titleAccent = $("#f_about_accent").value.trim();
    if ($("#f_about_lead")) data.about.lead = $("#f_about_lead").value.trim();
    if ($("#f_about_body")) data.about.body = $("#f_about_body").value.trim();
    {
      const aboutImgEl = $("#f_about_image");
      const aboutVal = aboutImgEl?.value?.trim() || "";
      const curAbout = data.about.image || "";
      if (
        aboutVal &&
        !isUploadPlaceholder(aboutVal) &&
        !isTruncatedPlaceholder(aboutVal) &&
        !(String(curAbout).startsWith("data:") && !aboutVal.startsWith("data:"))
      ) {
        data.about.image = aboutVal;
      }
    }
    data.about.clients = $("#f_clients").value
      .split(",")
      .map((s) => s.trim())
      .filter(Boolean);

    (data.about.achievements || []).forEach((_, i) => {
      const t = document.querySelector(`[data-ach-title="${i}"]`);
      const d = document.querySelector(`[data-ach-desc="${i}"]`);
      if (t) data.about.achievements[i].title = t.value.trim();
      if (d) data.about.achievements[i].desc = d.value.trim();
    });

    (data.services || []).forEach((_, i) => {
      const t = document.querySelector(`[data-svc-title="${i}"]`);
      const d = document.querySelector(`[data-svc-desc="${i}"]`);
      if (t) data.services[i].title = t.value.trim();
      if (d) data.services[i].desc = d.value.trim();
    });

    // Companies live fields — never wipe data: uploads with placeholder labels
    ensureArrays();
    data.companies.forEach((p, i) => {
      const title = document.querySelector(`[data-co-title="${i}"]`);
      const img = document.querySelector(`[data-co-img="${i}"]`);
      const vis = document.querySelector(`[data-co-vis="${i}"]`);
      if (title) p.title = title.value.trim();
      if (img) {
        const val = img.value.trim();
        const keepUpload =
          img.dataset.hasUpload === "1" ||
          String(p.image || "").startsWith("data:") ||
          isUploadPlaceholder(val);
        if (!keepUpload && val && !isTruncatedPlaceholder(val)) {
          p.image = val;
        }
      }
      if (vis) p.visible = vis.checked;
      p.cat = "companies";
      p.categoryLabel = "Industries worked with";
      p.section = "companies";
      p.type = "logo";
      // Logos only on public site
      p.work = [];
      p.workCount = 0;
    });

    // Creatives live fields
    data.creatives.forEach((p, i) => {
      const title = document.querySelector(`[data-cr-title="${i}"]`);
      const src = document.querySelector(`[data-cr-src="${i}"]`);
      const vis = document.querySelector(`[data-cr-vis="${i}"]`);
      if (title) p.title = title.value.trim();
      // Categories removed from site — keep a flat "work" label
      p.cat = "work";
      p.categoryLabel = "Work";
      if (src) {
        const val = src.value.trim();
        const current = p.video || p.image || "";
        const keepUpload =
          src.dataset.hasUpload === "1" ||
          String(current).startsWith("data:") ||
          isUploadPlaceholder(val);
        if (!keepUpload && val && !isTruncatedPlaceholder(val)) {
          const video = isVideoSrc(val, p.type);
          p.image = val;
          p.video = video ? val : "";
          p.type = video ? "video" : "media";
        }
      }
      if (vis) p.visible = vis.checked;
      p.section = "creatives";
    });

    syncPortfolioFromParts();

    (data.process || []).forEach((_, i) => {
      const n = document.querySelector(`[data-proc-num="${i}"]`);
      const t = document.querySelector(`[data-proc-title="${i}"]`);
      const d = document.querySelector(`[data-proc-desc="${i}"]`);
      if (n) data.process[i].num = n.value.trim();
      if (t) data.process[i].title = t.value.trim();
      if (d) data.process[i].desc = d.value.trim();
    });

    data.contact = data.contact || {};
    data.contact.email = $("#f_email").value.trim();
    data.contact.phone = $("#f_phone").value.trim();
    data.contact.location = $("#f_location").value.trim();
    data.contact.instagram = $("#f_ig").value.trim();
    data.contact.instagramHandle = $("#f_ig_handle").value.trim();
    data.contact.linkedin = $("#f_li").value.trim();
    data.contact.linkedinHandle = $("#f_li_handle").value.trim();

    data.socials = data.socials || {};
    data.socials.email = "mailto:" + data.contact.email;
    data.socials.phone = "tel:" + String(data.contact.phone || "").replace(/\s/g, "");
    data.socials.instagram = data.contact.instagram;
    data.socials.linkedin = data.contact.linkedin;

    data.meta = data.meta || {};
    data.meta.title = $("#f_meta_title").value.trim();
    data.meta.description = $("#f_meta_desc").value.trim();
  }

  $("#saveBtn").addEventListener("click", () => {
    collectForm();
    data.about = data.about || {};
    mergeMedia("about.image", "#f_about_image");
    if ($("#f_clients")?.value != null && $("#f_clients").value.trim() !== "") {
      data.about.clientsText = $("#f_clients").value.trim();
      data.about.clients = data.about.clientsText
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean);
    }
    // Protect about image data: URL from empty/short path overwrite
    if (
      String(data.about.image || "").startsWith("data:") === false &&
      String(window.cmsGet(data, "about.image") || "").startsWith("data:")
    ) {
      data.about.image = window.cmsGet(data, "about.image");
    }
    try {
      // Ensure removals are explicit before save
      data.companies = Array.isArray(data.companies) ? data.companies : [];
      data.creatives = Array.isArray(data.creatives) ? data.creatives : [];
      data.meta = data.meta || {};
      data.meta.adminSaved = true;
      saveSiteData(data);
      renderDashboard();
      renderCompanies();
      renderCreatives();
      renderAllEdit();
      showToast(
        `Saved (${data.companies.length} companies · ${data.creatives.length} works). Hard-refresh the website (Ctrl+F5).`
      );
    } catch (err) {
      console.error(err);
      showToast(
        "Save failed (storage full?). Use smaller images/videos under ~2–4MB, or Export JSON.",
        true
      );
    }
  });

  $("#exportBtn").addEventListener("click", () => {
    collectForm();
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "byshumail-site-" + new Date().toISOString().slice(0, 10) + ".json";
    a.click();
    URL.revokeObjectURL(a.href);
    showToast("JSON exported.");
  });

  $("#importBtn").addEventListener("click", () => {
    try {
      const parsed = JSON.parse($("#importJson").value);
      data = parsed;
      ensureArrays();
      saveSiteData(data);
      fillForm();
      renderDashboard();
      showToast("Import successful.");
    } catch {
      showToast("Invalid JSON.", true);
    }
  });

  async function reloadFromFiles(clearBrowserEdits) {
    if (clearBrowserEdits) resetSiteData();
    data = await loadSiteData();
    ensureArrays();
    data.companies.forEach((c) => {
      if (!Array.isArray(c.work)) c.work = [];
      c.workCount = c.work.length;
    });
    fillForm();
    renderDashboard();
    renderCompanies();
    renderCreatives();
    renderAllEdit();
    const nCo = data.companies?.length || 0;
    const nCr = data.creatives?.length || 0;
    showToast(`Reloaded: ${nCo} companies · ${nCr} creatives · full text`);
  }

  $("#reloadFullBtn")?.addEventListener("click", async () => {
    await reloadFromFiles(true);
  });

  $("#resetData").addEventListener("click", async () => {
    if (!confirm("Clear browser-saved edits and reload all text, images, and reels from project files?")) return;
    await reloadFromFiles(true);
  });

  $("#saveCreds").addEventListener("click", () => {
    const user = $("#f_new_user").value.trim() || "admin";
    const pass = $("#f_new_pass").value;
    if (!pass) {
      showToast("Enter a new password.", true);
      return;
    }
    setAdminCreds(user, pass);
    $("#f_new_pass").value = "";
    showToast("Credentials updated.");
  });

  function renderDashboard() {
    ensureArrays();
    if ($("#dashCompanies")) $("#dashCompanies").textContent = String(data.companies?.length || 0);
    if ($("#dashPortfolio"))
      $("#dashPortfolio").textContent = String(data.creatives?.length || data.portfolio?.length || 0);
    if ($("#dashWorks")) {
      const n = (data.companies || []).reduce((s, c) => s + ((c.work || []).length || 0), 0);
      $("#dashWorks").textContent = String(n);
    }
    $("#dashServices").textContent = String(data?.services?.length || 0);
    const msgs = loadMessages();
    const unread = msgs.filter((m) => !m.read).length;
    $("#dashMessages").textContent = String(unread);
    $("#msgBadge").textContent = String(unread);
    $("#dashUpdated").textContent = data?.meta?.updatedAt || "—";
  }

  function renderMessages() {
    const list = loadMessages();
    const box = $("#messagesList");
    $("#msgBadge").textContent = String(list.filter((m) => !m.read).length);

    if (!list.length) {
      box.innerHTML = `<p class="muted empty-msg">No messages yet. Submissions from the contact form will appear here.</p>`;
      return;
    }

    box.innerHTML = list
      .map(
        (m) => `
      <article class="msg-item ${m.read ? "" : "unread"}" data-id="${m.id}">
        <div class="msg-meta">
          <strong>${esc(m.name || "Anonymous")}</strong>
          <span>${esc(m.email || "")}</span>
          <span>${esc(m.subject || "No subject")}</span>
          <span>${new Date(m.createdAt).toLocaleString()}</span>
        </div>
        <div class="msg-body">${esc(m.message || "")}</div>
        <div class="msg-actions">
          <button type="button" class="btn btn-outline btn-sm" data-read="${m.id}">${m.read ? "Mark unread" : "Mark read"}</button>
          <button type="button" class="btn btn-danger btn-sm" data-del-msg="${m.id}">Delete</button>
          ${m.email ? `<a class="btn btn-outline btn-sm" href="mailto:${esc(m.email)}">Reply</a>` : ""}
        </div>
      </article>`
      )
      .join("");

    box.querySelectorAll("[data-read]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const msgs = loadMessages();
        const item = msgs.find((x) => x.id === btn.dataset.read);
        if (item) item.read = !item.read;
        updateMessages(msgs);
        renderMessages();
        renderDashboard();
      });
    });

    box.querySelectorAll("[data-del-msg]").forEach((btn) => {
      btn.addEventListener("click", () => {
        updateMessages(loadMessages().filter((x) => x.id !== btn.dataset.delMsg));
        renderMessages();
        renderDashboard();
      });
    });
  }

  $("#clearMessages").addEventListener("click", () => {
    if (!confirm("Delete all messages?")) return;
    updateMessages([]);
    renderMessages();
    renderDashboard();
    showToast("Inbox cleared.");
  });

  async function boot() {
    showApp();
    try {
      data = await loadSiteData();
      if (!data || typeof data !== "object") {
        throw new Error("empty site data");
      }
      ensureArrays();
      data.companies = Array.isArray(data.companies) ? data.companies : [];
      data.creatives = Array.isArray(data.creatives) ? data.creatives : [];
      // Ensure company work arrays exist for admin UI
      data.companies.forEach((c) => {
        if (!c || typeof c !== "object") return;
        if (!Array.isArray(c.work)) c.work = [];
        c.workCount = c.work.length;
      });
      fillForm();
      renderDashboard();
      renderMessages();
      const nCo = data.companies.length;
      const nCr = data.creatives.length;
      const nWork = data.companies.reduce((s, c) => s + (c.work?.length || 0), 0);
      showToast(`Loaded ${nCo} companies (${nWork} works) · ${nCr} creatives · all site text`);
    } catch (err) {
      console.error("Admin boot failed:", err);
      // Recover with empty shell so UI still works
      data = {
        stats: [],
        services: [],
        portfolio: [],
        companies: [],
        creatives: [],
        process: [],
        about: {},
        contact: {},
        cta: {},
        meta: {},
      };
      try {
        ensureArrays();
        fillForm();
        renderDashboard();
        renderMessages();
      } catch (e2) {
        console.error(e2);
      }
      showToast(
        "Admin loaded with limited data. Use Settings → Reload all text + images + reels.",
        true
      );
    }
  }

  // Safe start — never leave a blank page if auth state is stale
  try {
    if (typeof window.ByShumail === "undefined") {
      console.error("ByShumail missing — content.js failed to load");
      showLogin();
      const err = document.getElementById("loginError");
      if (err) {
        err.textContent =
          "Scripts failed to load. Use http://127.0.0.1:8765/admin/ (not file://) and hard-refresh (Ctrl+F5).";
      }
    } else if (isAdminAuthed()) {
      boot();
    } else {
      showLogin();
    }
  } catch (e) {
    console.error(e);
    showLogin();
  }
})();
