from pathlib import Path

p = Path(__file__).resolve().parents[1] / "index.html"
html = p.read_text(encoding="utf-8")

# Simple unique replacements
pairs = [
    ('<span class="logo-mark">S</span>', '<span class="logo-mark" data-cms="logoMark">S</span>'),
    ('class="hero-greeting">Hi, I am</p>', 'class="hero-greeting" data-cms="greeting">Hi, I am</p>'),
    ('class="hero-name">Muhammed Shumail</h1>', 'class="hero-name" data-cms="name">Muhammed Shumail</h1>'),
    ('class="hero-role">Content Creator</h2>', 'class="hero-role" data-cms="role">Content Creator</h2>'),
    (
        'class="hero-tagline">Photographer · Videographer · Dubai</p>',
        'class="hero-tagline" data-cms="tagline">Photographer · Videographer · Dubai</p>',
    ),
    ('href="#home" class="active">Home</a>', 'href="#home" class="active" data-cms="nav.home">Home</a>'),
    ('href="#services">Services</a>', 'href="#services" data-cms="nav.services">Services</a>'),
    ('href="#about">About me</a>', 'href="#about" data-cms="nav.about">About me</a>'),
    ('href="#industries">Industries</a>', 'href="#industries" data-cms="nav.industries">Industries</a>'),
    ('href="#portfolio">Creatives</a>', 'href="#portfolio" data-cms="nav.creatives">Creatives</a>'),
    ('href="#process">Process</a>', 'href="#process" data-cms="nav.process">Process</a>'),
    ('href="#contact">Contact me</a>', 'href="#contact" data-cms="nav.contact">Contact me</a>'),
    (
        'class="btn btn-primary nav-cta">Hire Me</a>',
        'class="btn btn-primary nav-cta" data-cms="nav.hire">Hire Me</a>',
    ),
    (
        """          <div class="hero-actions">
            <a href="#contact" class="btn btn-primary">Hire Me</a>
            <a href="#portfolio" class="btn btn-outline">View Work</a>
          </div>""",
        """          <div class="hero-actions">
            <a href="#contact" class="btn btn-primary" data-cms="hero.hire">Hire Me</a>
            <a href="#portfolio" class="btn btn-outline" data-cms="hero.viewWork">View Work</a>
          </div>""",
    ),
    ('<span class="badge-icon">🎬</span>', '<span class="badge-icon" data-cms="hero.badge1Icon">🎬</span>'),
    ("<span>Cinematic Storytelling</span>", '<span data-cms="hero.badge1">Cinematic Storytelling</span>'),
    ('<span class="badge-icon">✈️</span>', '<span class="badge-icon" data-cms="hero.badge2Icon">✈️</span>'),
    ("<span>Drone · Dubai</span>", '<span data-cms="hero.badge2">Drone · Dubai</span>'),
    (">What I offer</p>", ' data-cms="sections.services.eyebrow">What I offer</p>'),
    (
        'Services that <span class="accent">drive results</span>',
        '<span data-cms="sections.services.title">Services that </span><span class="accent" data-cms="sections.services.titleAccent">drive results</span>',
    ),
    (
        "From concept to final cut — visuals built for brands, real estate, and campaigns that convert.</p>",
        '<span data-cms="sections.services.sub">From concept to final cut — visuals built for brands, real estate, and campaigns that convert.</span></p>',
    ),
    (">About me</p>", ' data-cms="sections.about.eyebrow">About me</p>'),
    ("<strong>6+</strong>", '<strong data-cms="about.yearsCard">6+</strong>'),
    (
        "<span>Years crafting visuals that convert</span>",
        '<span data-cms="about.yearsCardLabel">Years crafting visuals that convert</span>',
    ),
    (
        '<span class="client-label">Trusted by</span>',
        '<span class="client-label" data-cms="about.clientsLabel">Trusted by</span>',
    ),
    (">Partners</p>", ' data-cms="sections.industries.eyebrow">Partners</p>'),
    (
        'Industries worked <span class="accent">with</span>',
        '<span data-cms="sections.industries.title">Industries worked </span><span class="accent" data-cms="sections.industries.titleAccent">with</span>',
    ),
    (
        "Brands and companies that trust the craft.</p>",
        '<span data-cms="sections.industries.sub">Brands and companies that trust the craft.</span></p>',
    ),
    (">Creatives</p>", ' data-cms="sections.creatives.eyebrow">Creatives</p>'),
    (
        'Selected <span class="accent">work</span>',
        '<span data-cms="sections.creatives.title">Selected </span><span class="accent" data-cms="sections.creatives.titleAccent">work</span>',
    ),
    (">My creative process</p>", ' data-cms="sections.process.eyebrow">My creative process</p>'),
    (
        'How it <span class="accent">works</span>',
        '<span data-cms="sections.process.title">How it </span><span class="accent" data-cms="sections.process.titleAccent">works</span>',
    ),
    (
        "A clear path from first conversation to content that performs.</p>",
        '<span data-cms="sections.process.sub">A clear path from first conversation to content that performs.</span></p>',
    ),
    (">Ready when you are</p>", ' data-cms="cta.eyebrow">Ready when you are</p>'),
    (
        'class="btn btn-primary btn-lg">Start a Project</a>',
        'class="btn btn-primary btn-lg" data-cms="cta.button">Start a Project</a>',
    ),
    (">Contact</p>", ' data-cms="sections.contact.eyebrow">Contact</p>'),
    ("Back to top ↑</a>", '<span data-cms="footer.backTop">Back to top ↑</span></a>'),
    # form labels
    ("<span>Name</span>", '<span data-cms="contact.formName">Name</span>'),
    ("<span>Email</span>", '<span data-cms="contact.formEmail">Email</span>'),
    ("<span>Subject</span>", '<span data-cms="contact.formSubject">Subject</span>'),
    ("<span>Message</span>", '<span data-cms="contact.formMessage">Message</span>'),
    (
        'class="btn btn-primary btn-full">Send Message</button>',
        'class="btn btn-primary btn-full" data-cms="contact.formButton">Send Message</button>',
    ),
    ('class="label">Email</span>', 'class="label" data-cms="contact.emailLabel">Email</span>'),
    ('class="label">Phone</span>', 'class="label" data-cms="contact.phoneLabel">Phone</span>'),
    ('class="label">Based in</span>', 'class="label" data-cms="contact.locationLabel">Based in</span>'),
    (
        'class="follow-label">Follow · Connect</p>',
        'class="follow-label" data-cms="contact.followLabel">Follow · Connect</p>',
    ),
    ('id="portraitImg"', 'id="portraitImg" data-cms-media="portrait"'),
]

for old, new in pairs:
    if old not in html:
        print("MISS:", old[:70].replace("\n", " "))
    else:
        html = html.replace(old, new, 1)
        print("OK:", old[:50].replace("\n", " "))

# creatives sub (entity variants)
for old in [
    "Final reels, BTS, concerts, automobiles, weddings &amp; drone — classified like the original site.</p>",
    "Final reels, BTS, concerts, automobiles, weddings & drone — classified like the original site.</p>",
]:
    if old in html:
        html = html.replace(
            old,
            '<span data-cms="sections.creatives.sub">Final reels, BTS, concerts, automobiles, weddings & drone — classified like the original site.</span></p>',
            1,
        )
        print("OK creatives sub")
        break

# CTA title - curly apostrophe variants
for old in [
    "<h2>Let’s connect and work together</h2>",
    "<h2>Let's connect and work together</h2>",
]:
    if old in html:
        html = html.replace(old, '<h2 data-cms="cta.title">Let’s connect and work together</h2>', 1)
        print("OK cta title")
        break

# CTA body - find paragraph after cta title
import re

html = re.sub(
    r'(data-cms="cta\.title">[^<]+</h2>\s*)<p>([^<]+)</p>',
    r'\1<p data-cms="cta.text">\2</p>',
    html,
    count=1,
)

# contact title block
html = re.sub(
    r'(data-cms="sections\.contact\.eyebrow">Contact</p>\s*<h2 class="section-title">)(.*?)(</h2>)',
    r'\1<span data-cms="sections.contact.title">Let’s talk about your </span><span class="accent" data-cms="sections.contact.titleAccent">next vision</span>\3',
    html,
    count=1,
    flags=re.S,
)

# about frame image
html = re.sub(
    r'(class="about-frame">\s*<img\s+)(src="[^"]+")',
    r'\1data-cms-media="about.image" \2',
    html,
    count=1,
)

if "cms-schema.js" not in html:
    html = html.replace(
        '<script src="js/content.js"></script>',
        '<script src="js/cms-schema.js"></script>\n  <script src="js/content.js"></script>',
    )

p.write_text(html, encoding="utf-8")
print("done", p)
