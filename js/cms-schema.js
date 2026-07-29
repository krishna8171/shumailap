/**
 * Full CMS field schema — every editable letter & media on the site.
 * path = dotted key into site data object
 * type = text | textarea | media | list
 */
window.CMS_SCHEMA = {
  groups: [
    {
      id: "nav",
      title: "Navigation & brand",
      fields: [
        { path: "brand", label: "Logo wordmark", type: "text" },
        { path: "logoMark", label: "Logo letter mark", type: "text" },
        { path: "nav.home", label: "Nav · Home", type: "text" },
        { path: "nav.services", label: "Nav · Services", type: "text" },
        { path: "nav.about", label: "Nav · About", type: "text" },
        { path: "nav.industries", label: "Nav · Industries", type: "text" },
        { path: "nav.creatives", label: "Nav · Creatives", type: "text" },
        { path: "nav.process", label: "Nav · Process", type: "text" },
        { path: "nav.contact", label: "Nav · Contact", type: "text" },
        { path: "nav.hire", label: "Nav · Hire button", type: "text" },
      ],
    },
    {
      id: "hero",
      title: "Hero (all letters + portrait)",
      fields: [
        { path: "greeting", label: "Greeting (Hi, I am)", type: "text" },
        { path: "name", label: "Full name", type: "text" },
        { path: "role", label: "Role (orange title)", type: "text" },
        { path: "tagline", label: "Tagline under role", type: "text" },
        { path: "hero.hire", label: "Primary button", type: "text" },
        { path: "hero.viewWork", label: "Secondary button", type: "text" },
        { path: "portrait", label: "Portrait image", type: "media", accept: "image/*" },
        { path: "hero.badge1", label: "Floating badge 1 text", type: "text" },
        { path: "hero.badge1Icon", label: "Floating badge 1 emoji", type: "text" },
        { path: "hero.badge2", label: "Floating badge 2 text", type: "text" },
        { path: "hero.badge2Icon", label: "Floating badge 2 emoji", type: "text" },
        { path: "hero.badge3", label: "Floating badge 3 text", type: "text" },
        { path: "hero.badge3Icon", label: "Floating badge 3 emoji", type: "text" },
        { path: "hero.showcaseLabel", label: "Hero showcase label", type: "text" },
        { path: "stats.0.value", label: "Stat 1 value", type: "text" },
        { path: "stats.0.label", label: "Stat 1 label", type: "text" },
        { path: "stats.1.value", label: "Stat 2 value", type: "text" },
        { path: "stats.1.label", label: "Stat 2 label", type: "text" },
        { path: "stats.2.value", label: "Stat 3 value", type: "text" },
        { path: "stats.2.label", label: "Stat 3 label", type: "text" },
      ],
    },
    {
      id: "services",
      title: "Services section",
      fields: [
        { path: "sections.services.eyebrow", label: "Eyebrow", type: "text" },
        { path: "sections.services.title", label: "Title (before accent)", type: "text" },
        { path: "sections.services.titleAccent", label: "Title accent", type: "text" },
        { path: "sections.services.sub", label: "Subtitle", type: "textarea" },
      ],
    },
    {
      id: "about",
      title: "About section",
      fields: [
        { path: "sections.about.eyebrow", label: "Eyebrow", type: "text" },
        { path: "about.title", label: "Title line 1", type: "text" },
        { path: "about.titleAccent", label: "Title accent", type: "text" },
        { path: "about.lead", label: "Lead paragraph", type: "textarea" },
        { path: "about.body", label: "Body paragraph", type: "textarea" },
        { path: "about.image", label: "About photo", type: "media", accept: "image/*" },
        { path: "about.yearsCard", label: "Years card number", type: "text" },
        { path: "about.yearsCardLabel", label: "Years card label", type: "text" },
        { path: "about.clientsLabel", label: "Trusted by label", type: "text" },
        { path: "about.achievements.0.title", label: "Achievement 1 title", type: "text" },
        { path: "about.achievements.0.desc", label: "Achievement 1 desc", type: "text" },
        { path: "about.achievements.1.title", label: "Achievement 2 title", type: "text" },
        { path: "about.achievements.1.desc", label: "Achievement 2 desc", type: "text" },
        { path: "about.achievements.2.title", label: "Achievement 3 title", type: "text" },
        { path: "about.achievements.2.desc", label: "Achievement 3 desc", type: "text" },
        { path: "about.clientsText", label: "Clients (comma-separated)", type: "text" },
      ],
    },
    {
      id: "industries",
      title: "Industries section headings",
      fields: [
        { path: "sections.industries.eyebrow", label: "Eyebrow", type: "text" },
        { path: "sections.industries.title", label: "Title before accent", type: "text" },
        { path: "sections.industries.titleAccent", label: "Title accent", type: "text" },
        { path: "sections.industries.sub", label: "Subtitle", type: "textarea" },
      ],
    },
    {
      id: "creativesHead",
      title: "Creatives section headings",
      fields: [
        { path: "sections.creatives.eyebrow", label: "Eyebrow", type: "text" },
        { path: "sections.creatives.title", label: "Title before accent", type: "text" },
        { path: "sections.creatives.titleAccent", label: "Title accent", type: "text" },
        { path: "sections.creatives.sub", label: "Subtitle", type: "textarea" },
      ],
    },
    {
      id: "process",
      title: "Process section",
      fields: [
        { path: "sections.process.eyebrow", label: "Eyebrow", type: "text" },
        { path: "sections.process.title", label: "Title before accent", type: "text" },
        { path: "sections.process.titleAccent", label: "Title accent", type: "text" },
        { path: "sections.process.sub", label: "Subtitle", type: "textarea" },
      ],
    },
    {
      id: "cta",
      title: "CTA banner",
      fields: [
        { path: "cta.eyebrow", label: "Eyebrow", type: "text" },
        { path: "cta.title", label: "Title", type: "text" },
        { path: "cta.text", label: "Body text", type: "textarea" },
        { path: "cta.button", label: "Button label", type: "text" },
      ],
    },
    {
      id: "contact",
      title: "Contact section",
      fields: [
        { path: "sections.contact.eyebrow", label: "Eyebrow", type: "text" },
        { path: "sections.contact.title", label: "Title before accent", type: "text" },
        { path: "sections.contact.titleAccent", label: "Title accent", type: "text" },
        { path: "sections.contact.sub", label: "Subtitle", type: "textarea" },
        { path: "contact.emailLabel", label: "Email label", type: "text" },
        { path: "contact.email", label: "Email address", type: "text" },
        { path: "contact.phoneLabel", label: "Phone label", type: "text" },
        { path: "contact.phone", label: "Phone number", type: "text" },
        { path: "contact.locationLabel", label: "Location label", type: "text" },
        { path: "contact.location", label: "Location text", type: "text" },
        { path: "contact.followLabel", label: "Follow label", type: "text" },
        { path: "contact.instagram", label: "Instagram URL", type: "text" },
        { path: "contact.instagramHandle", label: "Instagram handle", type: "text" },
        { path: "contact.linkedin", label: "LinkedIn URL", type: "text" },
        { path: "contact.linkedinHandle", label: "LinkedIn handle", type: "text" },
        { path: "contact.formName", label: "Form · Name label", type: "text" },
        { path: "contact.formEmail", label: "Form · Email label", type: "text" },
        { path: "contact.formSubject", label: "Form · Subject label", type: "text" },
        { path: "contact.formMessage", label: "Form · Message label", type: "text" },
        { path: "contact.formButton", label: "Form · Submit button", type: "text" },
      ],
    },
    {
      id: "footer",
      title: "Footer & SEO",
      fields: [
        { path: "footer.tagline", label: "Footer tagline", type: "text" },
        { path: "footer.backTop", label: "Back to top text", type: "text" },
        { path: "meta.title", label: "Browser tab title", type: "text" },
        { path: "meta.description", label: "Meta description", type: "textarea" },
      ],
    },
    {
      id: "mediaHelp",
      title: "Images · Videos · Reels (where to manage)",
      fields: [
        {
          path: "_help.mediaNote",
          label:
            "Guide: Portrait & About photo → fields above / Hero panel. Company logos + brand work images → Companies panel (+ Add images/videos). Portfolio reels & creatives → Creatives panel (bulk upload). Services list → Services panel. Process steps → Process panel.",
          type: "text",
        },
      ],
    },
  ],
};

window.CMS_DEFAULTS = {
  logoMark: "S",
  _help: {
    mediaNote:
      "Use Companies + Creatives panels to add images/videos. This All-text page covers every letter + portrait/about photo.",
  },
  nav: {
    home: "Home",
    services: "Services",
    about: "About me",
    industries: "Industries",
    creatives: "Creatives",
    process: "Process",
    contact: "Contact me",
    hire: "Hire Me",
  },
  hero: {
    hire: "Hire Me",
    viewWork: "View Work",
    badge1: "Cinematic Storytelling",
    badge1Icon: "🎬",
    badge2: "Drone · Dubai",
    badge2Icon: "✈️",
    badge3: "Available for hire",
    badge3Icon: "📷",
    showcaseLabel: "Best work",
  },
  sections: {
    services: {
      eyebrow: "What I offer",
      title: "Services that ",
      titleAccent: "drive results",
      sub: "From concept to final cut — visuals built for brands, real estate, and campaigns that convert.",
    },
    about: { eyebrow: "About me" },
    industries: {
      eyebrow: "Partners",
      title: "Industries worked ",
      titleAccent: "with",
      sub: "Brands and companies that trust the craft.",
    },
    creatives: {
      eyebrow: "Creatives",
      title: "Selected ",
      titleAccent: "work",
      sub: "Selected photography, video and reel work.",
    },
    process: {
      eyebrow: "My creative process",
      title: "How it ",
      titleAccent: "works",
      sub: "A clear path from first conversation to content that performs.",
    },
    contact: {
      eyebrow: "Contact",
      title: "Let's talk about your ",
      titleAccent: "next vision",
      sub: "Reach out for collaborations, brand campaigns, or real estate content partnerships.",
    },
  },
  about: {
    yearsCard: "7+",
    yearsCardLabel: "Years crafting visuals that convert",
    clientsLabel: "Trusted by",
    clientsText: "NEWIZZ Realty LLC, Revo Realty",
  },
  cta: {
    eyebrow: "Ready when you are",
    title: "Let's connect and work together",
    text: "Need reels, property films, events, or a full content system? Let's build visuals that move people.",
    button: "Start a Project",
  },
  contact: {
    emailLabel: "Email",
    phoneLabel: "Phone",
    locationLabel: "Based in",
    followLabel: "Follow · Connect",
    formName: "Name",
    formEmail: "Email",
    formSubject: "Subject",
    formMessage: "Message",
    formButton: "Send Message",
  },
  footer: {
    tagline: "Creating visuals that move people.",
    backTop: "Back to top ↑",
  },
};

/** Get nested value by path a.b.0.c */
window.cmsGet = function cmsGet(obj, path) {
  if (!path) return undefined;
  return path.split(".").reduce((o, k) => (o == null ? undefined : o[k]), obj);
};

/** Set nested value by path */
window.cmsSet = function cmsSet(obj, path, value) {
  const parts = path.split(".");
  let cur = obj;
  for (let i = 0; i < parts.length - 1; i++) {
    const p = parts[i];
    const next = parts[i + 1];
    if (cur[p] == null) cur[p] = /^\d+$/.test(next) ? [] : {};
    cur = cur[p];
  }
  cur[parts[parts.length - 1]] = value;
};

/** Deep-merge defaults into data without wiping arrays that already exist */
window.cmsEnsureDefaults = function cmsEnsureDefaults(data) {
  const d = data || {};
  const def = window.CMS_DEFAULTS;

  const merge = (target, source) => {
    Object.keys(source).forEach((k) => {
      if (source[k] && typeof source[k] === "object" && !Array.isArray(source[k])) {
        if (!target[k] || typeof target[k] !== "object") target[k] = {};
        merge(target[k], source[k]);
      } else if (target[k] === undefined || target[k] === null || target[k] === "") {
        target[k] = source[k];
      }
    });
  };
  merge(d, def);

  // sync clientsText from clients array if needed
  if (d.about) {
    if (!d.about.clientsText && Array.isArray(d.about.clients)) {
      d.about.clientsText = d.about.clients.join(", ");
    }
    if (d.about.clientsText && !d.about.clients) {
      d.about.clients = d.about.clientsText.split(",").map((s) => s.trim()).filter(Boolean);
    }
  }
  return d;
};
