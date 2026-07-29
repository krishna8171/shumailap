/* Shumail portfolio — interactions + full Canva gallery */

(async () => {
  const header = document.querySelector(".header");
  const navToggle = document.getElementById("navToggle");
  const navLinks = document.getElementById("navLinks");
  const yearEl = document.getElementById("year");
  const form = document.getElementById("contactForm");
  const formNote = document.getElementById("formNote");
  const isPdfExport =
    /(?:\?|&)pdf=1(?:&|$)/.test(location.search) ||
    window.matchMedia("print").matches;

  if (isPdfExport) {
    document.documentElement.classList.add("pdf-export");
  }

  let galleryItems = [];
  let siteData = null;

  try {
    const data = await window.ByShumail.loadSiteData();
    if (data) {
      siteData = data;
      window.ByShumail.applySiteToDOM(data);
      galleryItems = (data.portfolio || []).filter((p) => p.visible !== false);
    }
  } catch (err) {
    console.warn("Content load skipped:", err);
  }

  // ----- Hero: Mashoor-style full-bleed cinematic video + role rotator -----
  // Background videos crossfade with object-fit:cover (immersive, like mashoormuneer.com)
  // HD video only — native 720×1280 car/travel reels (no still montages, no shoes)
  // ?v=hd4 busts browser cache of older low-quality encodes
  const CINE_REELS = [
    { src: "assets/hero/cine-01.mp4?v=hd4", poster: "assets/hero/hd-01.jpg", holdMs: 10000 }, // G-Wagon HD
    { src: "assets/hero/cine-02.mp4?v=hd4", poster: "assets/hero/hd-01.jpg", holdMs: 9200 }, // Thar / car interior HD
    { src: "assets/hero/cine-03.mp4?v=hd4", poster: "assets/hero/best-03.jpg", holdMs: 10000 }, // Thar exterior HD
    { src: "assets/hero/cine-04.mp4?v=hd4", poster: "assets/hero/best-01.jpg", holdMs: 5200 }, // aerial road travel HD
    { src: "assets/hero/cine-05.mp4?v=hd4", poster: "assets/hero/hd-01.jpg", holdMs: 10000 }, // G-Wagon HD master
  ];

  function initHeroShowcase() {
    const track = document.getElementById("heroShowcaseSlides");
    const root = document.getElementById("heroShowcase") || document.querySelector(".hero--cinematic");
    if (!track || isPdfExport) return;

    const reduceMotion =
      window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const isMobile =
      window.matchMedia && window.matchMedia("(max-width: 900px)").matches;

    const list = isMobile ? CINE_REELS.slice(0, 4) : CINE_REELS;

    track.innerHTML = list
      .map(
        (item, i) =>
          `<video class="hero-bg-video${i === 0 ? " is-active" : ""}" muted playsinline preload="${i === 0 ? "auto" : "metadata"}" poster="${item.poster}" data-hold-ms="${item.holdMs}" src="${item.src}"></video>`
      )
      .join("");

    const videos = [...track.querySelectorAll(".hero-bg-video")];
    if (!videos.length) return;

    const armVideo = (vid) => {
      if (!vid) return;
      vid.muted = true;
      vid.defaultMuted = true;
      vid.playsInline = true;
      vid.setAttribute("playsinline", "");
      vid.setAttribute("webkit-playsinline", "");
      vid.loop = false;
    };

    videos.forEach(armVideo);

    const playVid = (vid) => {
      if (!vid) return;
      try {
        armVideo(vid);
        if (vid.readyState < 2) {
          try {
            vid.load();
          } catch (_) {}
        }
        vid.currentTime = 0;
        const p = vid.play();
        if (p && typeof p.catch === "function") p.catch(() => {});
      } catch (_) {}
    };

    const pauseVid = (vid) => {
      if (!vid) return;
      try {
        vid.pause();
      } catch (_) {}
    };

    // Role rotator (Filmmaker / Photographer / Creative Director style)
    const roles = [...document.querySelectorAll(".hero-roles .hero-role")];
    let roleIdx = 0;
    let roleTimer = null;
    const rotateRole = () => {
      if (roles.length < 2) return;
      const prev = roles[roleIdx];
      roleIdx = (roleIdx + 1) % roles.length;
      const next = roles[roleIdx];
      prev.classList.remove("is-active");
      prev.classList.add("is-exit");
      next.classList.add("is-active");
      window.setTimeout(() => prev.classList.remove("is-exit"), 560);
    };
    const startRoles = () => {
      if (roleTimer || reduceMotion || roles.length < 2) return;
      roleTimer = window.setInterval(rotateRole, 2200);
    };
    const stopRoles = () => {
      if (roleTimer) {
        window.clearInterval(roleTimer);
        roleTimer = null;
      }
    };

    if (reduceMotion) {
      playVid(videos[0]);
      return;
    }

    let idx = 0;
    let timer = null;
    let paused = false;
    let ready = false;
    let endHandler = null;
    const EXIT_MS = 1000;

    const clearTimer = () => {
      if (timer) {
        window.clearTimeout(timer);
        timer = null;
      }
      if (endHandler) {
        videos.forEach((v) => v.removeEventListener("ended", endHandler));
        endHandler = null;
      }
    };

    const scheduleNext = (ms) => {
      clearTimer();
      if (paused || document.hidden || !ready) return;
      timer = window.setTimeout(go, ms);
    };

    const go = () => {
      if (paused || document.hidden || !ready) return;
      const prev = videos[idx];
      idx = (idx + 1) % videos.length;
      const next = videos[idx];

      prev.classList.remove("is-active");
      prev.classList.add("is-exit");
      next.classList.add("is-active");
      window.setTimeout(() => {
        prev.classList.remove("is-exit");
        pauseVid(prev);
        try {
          prev.currentTime = 0;
        } catch (_) {}
      }, EXIT_MS);

      playVid(next);

      // Prefetch next-next
      const upcoming = videos[(idx + 1) % videos.length];
      if (upcoming && upcoming.preload !== "auto") {
        upcoming.preload = "auto";
        try {
          upcoming.load();
        } catch (_) {}
      }

      const hold = Number(next.dataset.holdMs) || 9500;
      endHandler = () => scheduleNext(80);
      next.addEventListener("ended", endHandler, { once: true });
      scheduleNext(hold);
    };

    const start = () => {
      if (!ready || paused || document.hidden) return;
      if (timer) return;
      playVid(videos[idx]);
      startRoles();
      const hold = Number(videos[idx].dataset.holdMs) || 9500;
      endHandler = () => scheduleNext(80);
      videos[idx].addEventListener("ended", endHandler, { once: true });
      scheduleNext(hold);
    };

    const stop = () => {
      clearTimer();
      stopRoles();
      videos.forEach(pauseVid);
    };

    // Wait for first video to be playable
    const first = videos[0];
    const markReady = () => {
      if (ready) return;
      ready = true;
      if (!paused && !document.hidden) start();
    };

    if (first.readyState >= 2) markReady();
    else {
      first.addEventListener("loadeddata", markReady, { once: true });
      first.addEventListener("canplay", markReady, { once: true });
    }
    window.setTimeout(markReady, 1200);

    if ("IntersectionObserver" in window && root) {
      const io = new IntersectionObserver(
        (entries) => {
          const vis = entries.some((e) => e.isIntersecting && e.intersectionRatio > 0.12);
          paused = !vis;
          if (vis) start();
          else stop();
        },
        { threshold: [0, 0.12, 0.4] }
      );
      io.observe(root);
    }

    document.addEventListener("visibilitychange", () => {
      if (document.hidden) stop();
      else if (!paused) start();
    });
  }

  initHeroShowcase();

  // PDF / print: force every section visible (no scroll-reveal hide)
  if (isPdfExport) {
    document.querySelectorAll(".reveal").forEach((el) => el.classList.add("visible"));
    document.querySelectorAll(".folio-card.hidden").forEach((el) => el.classList.remove("hidden"));
  }

  // Drop legacy storage keys + wrong category schemes so live Canva taxonomy wins
  try {
    // Drop obsolete storage keys (v6 merges base files + edits)
    ["byshumail_site_v1", "byshumail_site_v2", "byshumail_site_v3", "byshumail_site_v4", "byshumail_site_v5", "byshumail_site_v6", "byshumail_site_v7"].forEach(
      (k) => localStorage.removeItem(k)
    );
    const raw = localStorage.getItem(window.ByShumail.SITE_STORAGE_KEY);
    if (raw) {
      const parsed = JSON.parse(raw);
      const cats = (parsed.portfolio || parsed.creatives || []).map((p) => p.cat);
      const allowed = new Set([
        "companies",
        "final-reel",
        "bts",
        "concert",
        "drone",
        "automobile",
        "weddings",
      ]);
      const looksWrong =
        !cats.length ||
        cats.some((c) => !allowed.has(c)) ||
        cats.some((c) => ["reel", "events", "auto", "media", "all"].includes(c));
      if (looksWrong) {
        localStorage.removeItem(window.ByShumail.SITE_STORAGE_KEY);
        const fresh = await window.ByShumail.loadSiteData();
        if (fresh) {
          window.ByShumail.applySiteToDOM(fresh);
          galleryItems = (fresh.creatives || fresh.portfolio || []).filter((p) => p.visible !== false);
        }
      }
    }
  } catch (_) {}

  if (yearEl) yearEl.textContent = String(new Date().getFullYear());

  if (portraitImg) {
    portraitImg.addEventListener("error", () => {
      portraitImg.dataset.error = "true";
    });
  }

  const onScroll = () => {
    if (!header) return;
    header.classList.toggle("scrolled", window.scrollY > 20);
  };
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  if (navToggle && navLinks) {
    navToggle.addEventListener("click", () => {
      const open = navLinks.classList.toggle("open");
      navToggle.setAttribute("aria-expanded", String(open));
      document.body.style.overflow = open ? "hidden" : "";
    });

    navLinks.querySelectorAll("a").forEach((link) => {
      link.addEventListener("click", () => {
        navLinks.classList.remove("open");
        navToggle.setAttribute("aria-expanded", "false");
        document.body.style.overflow = "";
      });
    });
  }

  const sections = document.querySelectorAll("section[id]");
  const navAnchors = document.querySelectorAll(".nav-links a");

  const setActiveNav = () => {
    let current = "home";
    sections.forEach((sec) => {
      const top = sec.offsetTop - 120;
      if (window.scrollY >= top) current = sec.id;
    });
    navAnchors.forEach((a) => {
      const href = a.getAttribute("href") || "";
      a.classList.toggle("active", href === `#${current}`);
    });
  };
  window.addEventListener("scroll", setActiveNav, { passive: true });
  setActiveNav();

  // Category filters removed — all creatives show in one grid
  const bindFilters = () => {};
  bindFilters();

  // Autoplay reels when in view (muted loop)
  let reelObserver = null;
  const bindReelAutoplay = () => {
    if (reelObserver) {
      reelObserver.disconnect();
      reelObserver = null;
    }
    const reels = document.querySelectorAll("video.reel-video");
    if (!reels.length) return;

    reels.forEach((vid) => {
      vid.muted = true;
      vid.loop = true;
      vid.playsInline = true;
      vid.setAttribute("playsinline", "");
      vid.setAttribute("muted", "");
      // Try play immediately (works when already on screen)
      const p = vid.play();
      if (p && typeof p.catch === "function") p.catch(() => {});
    });

    if (!("IntersectionObserver" in window)) return;

    reelObserver = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          const vid = entry.target;
          if (!(vid instanceof HTMLVideoElement)) return;
          if (entry.isIntersecting && entry.intersectionRatio > 0.25) {
            vid.muted = true;
            vid.play().catch(() => {});
          } else {
            vid.pause();
          }
        });
      },
      { threshold: [0, 0.25, 0.5], rootMargin: "40px 0px" }
    );
    reels.forEach((vid) => reelObserver.observe(vid));
  };
  bindReelAutoplay();
  document.addEventListener("byshumail:gallery-ready", () => {
    bindFilters();
    bindReelAutoplay();
  });

  // Lightbox (image + video)
  const lightbox = document.getElementById("lightbox");
  const lightboxImg = document.getElementById("lightboxImg");
  const lightboxVideo = document.getElementById("lightboxVideo");
  const lightboxCap = document.getElementById("lightboxCap");
  let lbIndex = 0;

  const visibleCards = () =>
    [
      ...document.querySelectorAll(
        "#portfolioGrid .folio-card:not(.hidden), #companiesGrid .company-work-card.folio-card"
      ),
    ];

  const openLightbox = (indexInVisible) => {
    const cards = visibleCards();
    if (!cards.length) return;
    lbIndex = ((indexInVisible % cards.length) + cards.length) % cards.length;
    const card = cards[lbIndex];
    const src = card.dataset.src || card.querySelector("img")?.src || card.querySelector("video")?.src;
    // Only play real video files / data:video — not JPG reel posters
    const isVideo =
      card.dataset.media === "video" &&
      (/^data:video/i.test(src || "") || /\.(mp4|webm|ogg|mov)(\?|$)/i.test(src || ""));
    const title =
      card.querySelector("h3")?.textContent ||
      card.dataset.company ||
      "";
    const cat = card.dataset.company || "";

    if (lightboxVideo) {
      lightboxVideo.pause();
      lightboxVideo.removeAttribute("src");
      lightboxVideo.load();
      lightboxVideo.hidden = true;
    }
    if (lightboxImg) {
      lightboxImg.removeAttribute("src");
      lightboxImg.hidden = true;
    }

    if (isVideo && lightboxVideo) {
      lightboxVideo.src = src;
      lightboxVideo.muted = true;
      lightboxVideo.loop = true;
      lightboxVideo.playsInline = true;
      lightboxVideo.hidden = false;
      lightboxVideo.play().catch(() => {});
    } else if (lightboxImg) {
      lightboxImg.src = src;
      lightboxImg.hidden = false;
    }

    lightboxCap.textContent = cat ? `${cat} — ${title}` : title;
    lightbox.hidden = false;
    document.body.style.overflow = "hidden";
  };

  const closeLightbox = () => {
    lightbox.hidden = true;
    if (lightboxImg) {
      lightboxImg.removeAttribute("src");
      lightboxImg.hidden = true;
    }
    if (lightboxVideo) {
      lightboxVideo.pause();
      lightboxVideo.removeAttribute("src");
      lightboxVideo.load();
      lightboxVideo.hidden = true;
    }
    document.body.style.overflow = "";
  };

  const onFolioClick = (e) => {
    const card = e.target.closest(".folio-card");
    if (!card) return;
    const cards = visibleCards();
    const idx = cards.indexOf(card);
    if (idx >= 0) openLightbox(idx);
  };
  document.getElementById("portfolioGrid")?.addEventListener("click", onFolioClick);
  document.getElementById("companiesGrid")?.addEventListener("click", onFolioClick);

  document.getElementById("lightboxClose")?.addEventListener("click", closeLightbox);
  document.getElementById("lightboxPrev")?.addEventListener("click", () => openLightbox(lbIndex - 1));
  document.getElementById("lightboxNext")?.addEventListener("click", () => openLightbox(lbIndex + 1));
  lightbox?.addEventListener("click", (e) => {
    if (e.target === lightbox) closeLightbox();
  });
  document.addEventListener("keydown", (e) => {
    if (lightbox?.hidden) return;
    if (e.key === "Escape") closeLightbox();
    if (e.key === "ArrowLeft") openLightbox(lbIndex - 1);
    if (e.key === "ArrowRight") openLightbox(lbIndex + 1);
  });

  // Contact form
  if (form) {
    form.addEventListener("submit", (e) => {
      e.preventDefault();
      const fd = new FormData(form);
      const name = String(fd.get("name") || "").trim();
      const email = String(fd.get("email") || "").trim();
      const subject = String(fd.get("subject") || "Project inquiry").trim();
      const message = String(fd.get("message") || "").trim();

      if (!name || !email || !message) {
        formNote.textContent = "Please fill in name, email, and message.";
        formNote.className = "form-note error";
        return;
      }

      try {
        window.ByShumail.saveMessage({ name, email, subject, message });
      } catch (_) {}

      const body = [`Hi Shumail,`, ``, message, ``, `— ${name}`, email].join("\n");
      const mailto = `mailto:mudshumail@gmail.com?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
      window.location.href = mailto;
      formNote.textContent = "Message saved to admin inbox. Opening your email app…";
      formNote.className = "form-note success";
      form.reset();
    });
  }

  // Scroll reveal — keep about/contact text always readable (no opacity ghosting)
  requestAnimationFrame(() => {
    const revealTargets = document.querySelectorAll(
      ".service-card, .step, .folio-card, .logo-card, .about-visual, .section-head, .cta-inner, .contact-form, .stats"
    );
    revealTargets.forEach((el) => el.classList.add("reveal"));

    if (isPdfExport || document.documentElement.classList.contains("pdf-export")) {
      revealTargets.forEach((el) => el.classList.add("visible"));
      return;
    }

    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("visible");
            io.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.05, rootMargin: "40px 0px 0px 0px" }
    );

    revealTargets.forEach((el) => io.observe(el));

    // Safety: force-show anything still hidden after 1.2s
    setTimeout(() => {
      document.querySelectorAll(".reveal:not(.visible)").forEach((el) => el.classList.add("visible"));
    }, 1200);
  });
})();
