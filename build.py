#!/usr/bin/env python3
"""Rebuild AnimMasterLib catalog as multi-page static site."""
import json, os, html, re

BASE = os.path.dirname(os.path.abspath(__file__))
os.makedirs(os.path.join(BASE, "demos"), exist_ok=True)

with open(os.path.join(BASE, "catalog-data.json")) as f:
    DATA = json.load(f)

# Category -> page file mapping
CATEGORIES = [
    ("Scroll Animation",         "scroll-animation.html",       "Scroll Animation"),
    ("Hero Animations",          "hero-animations.html",       "Hero Animations"),
    ("Sliders",                  "sliders.html",               "Sliders"),
    ("Navigation Menus",          "navigation-menus.html",       "Navigation Menus"),
    ("Hover Effects",            "hover-effects.html",         "Hover Effects"),
    ("Mouse Effects",            "mouse-effects.html",         "Mouse Effects"),
    ("Webgl & ThreeJS Effects",  "webgl-threejs.html",         "WebGL & ThreeJS Effects"),
    ("Text Animations",          "text-animations.html",       "Text Animations"),
    ("Page Transitions",         "page-transitions.html",      "Page Transitions"),
    ("SVG Animations",           "svg-animations.html",        "SVG Animations"),
    ("Background Animations",    "background-animations.html", "Background Animations"),
    ("Grid Animations",          "grid-animations.html",       "Grid Animations"),
    ("Physics Effects",          "physics-effects.html",       "Physics Effects"),
    ("3D Animation",             "3d-animation.html",          "3D Animation"),
]

# Vengence UI button definitions (added to Hover Effects as #21, #22, #23)
VENGENCE = [
    {
        "num": 21, "name": "Radial Glow Button",
        "demo": "demos/vengence-radial-glow.html",
        "tsx": r"C:\Users\info\Dropbox\Google Drive\Software\vengenceui\components\radial-glow-button.tsx",
    },
    {
        "num": 22, "name": "Generate Button",
        "demo": "demos/vengence-generate.html",
        "tsx": r"C:\Users\info\Dropbox\Google Drive\Software\vengenceui\components\generate-button.tsx",
    },
    {
        "num": 23, "name": "Liquid Metal Button",
        "demo": "demos/vengence-liquid-metal.html",
        "tsx": r"C:\Users\info\Dropbox\Google Drive\Software\vengenceui\components\liquid-metal.tsx",
    },
]

POSTER_BASE = "https://animmasterlib.dev/assets/img"

# ─── Theme / shared CSS ──────────────────────────────────────────────
SHARED_CSS = """
:root { --bg:#0B0F19; --accent:#0066FF; --card:#131722; --border:#1e2530; --text:#e2e8f0; --muted:#64748b; }
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;line-height:1.5}
a{color:var(--accent);text-decoration:none}
a:hover{text-decoration:underline}
.container{max-width:1400px;margin:0 auto;padding:0 24px}
.header{position:sticky;top:0;z-index:100;background:rgba(11,15,25,.9);backdrop-filter:blur(12px);border-bottom:1px solid var(--border);padding:16px 0}
.header .container{display:flex;align-items:center;justify-content:space-between}
.header h1{font-size:20px;font-weight:700;letter-spacing:-.5px}
.header h1 a{color:var(--text);text-decoration:none}
.header .nav{display:flex;gap:20px;flex-wrap:wrap}
.header .nav a{color:var(--muted);font-size:14px;text-decoration:none;transition:color .2s}
.header .nav a:hover{color:var(--accent);text-decoration:none}
.cat-header{padding:48px 0 24px}
.cat-header h2{font-size:36px;font-weight:800;letter-spacing:-1px;margin-bottom:8px}
.cat-header p{color:var(--muted);font-size:16px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:20px;padding:24px 0 80px}
.card{background:var(--card);border:1px solid var(--border);border-radius:12px;overflow:hidden;transition:transform .2s,border-color .2s;position:relative}
.card:hover{transform:translateY(-2px);border-color:var(--accent)}
.card-video-wrap{position:relative;aspect-ratio:16/9;background:#000;overflow:hidden}
.card-video-wrap video{width:100%;height:100%;object-fit:cover;display:block}
.card-video-wrap iframe{width:100%;height:100%;border:0;display:block}
.card-number{position:absolute;top:8px;left:8px;background:rgba(0,0,0,.75);color:var(--accent);font-size:11px;font-weight:700;padding:3px 8px;border-radius:6px;z-index:2;letter-spacing:.5px}
.card-info{padding:12px 16px}
.card-info h3{font-size:14px;font-weight:600;line-height:1.3;color:var(--text);word-break:break-word}
.cat-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:20px;padding:24px 0 80px}
.cat-card{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:32px 24px;transition:all .2s;display:block;text-decoration:none}
.cat-card:hover{border-color:var(--accent);transform:translateY(-2px);text-decoration:none}
.cat-card h3{font-size:20px;font-weight:700;color:var(--text);margin-bottom:8px}
.cat-card .count{font-size:14px;color:var(--accent);font-weight:600}
.cat-card .desc{font-size:13px;color:var(--muted);margin-top:8px}
.hero{padding:64px 0 32px;text-align:center}
.hero h2{font-size:48px;font-weight:900;letter-spacing:-1.5px;margin-bottom:12px;background:linear-gradient(135deg,#fff,#64748b);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.hero p{color:var(--muted);font-size:18px;max-width:600px;margin:0 auto}
.footer{border-top:1px solid var(--border);padding:32px 0;text-align:center;color:var(--muted);font-size:13px}
@media(max-width:640px){.grid{grid-template-columns:1fr}.cat-grid{grid-template-columns:1fr}.hero h2{font-size:32px}.header .nav{display:none}}
"""

def page_html(title, body_content, extra_css=""):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title>
<style>
{SHARED_CSS}
{extra_css}
</style>
</head>
<body>
<div class="header"><div class="container">
<h1><a href="index.html">Animation Catalog</a></h1>
<nav class="nav">
<a href="scroll-animation.html">Scroll</a>
<a href="hero-animations.html">Hero</a>
<a href="sliders.html">Sliders</a>
<a href="navigation-menus.html">Navigation</a>
<a href="hover-effects.html">Hover</a>
<a href="mouse-effects.html">Mouse</a>
<a href="webgl-threejs.html">WebGL</a>
<a href="text-animations.html">Text</a>
<a href="page-transitions.html">Transitions</a>
<a href="svg-animations.html">SVG</a>
<a href="background-animations.html">Background</a>
<a href="grid-animations.html">Grid</a>
<a href="physics-effects.html">Physics</a>
<a href="3d-animation.html">3D</a>
</nav>
</div></div>
{body_content}
<div class="footer"><div class="container">Animation Effects Catalog &middot; {sum(len(v) for v in DATA.values()) + 3} components across {len(DATA)} categories</div></div>
</body>
</html>"""

def card_video(item):
    """Generate a card with video preview."""
    num = item["num"]
    name = html.escape(item["name"])
    prefix = item["prefix"]
    cdn = item["cdn"]
    poster = f"{POSTER_BASE}/{prefix}-{num}-500.webp"
    label = f"{prefix.capitalize()} #{num:02d}" if prefix != "scroll" else f"Scroll #{num:02d}"
    return f"""<div class="card">
<div class="card-video-wrap">
<span class="card-number">{label}</span>
<video src="{cdn}" poster="{poster}" autoplay muted loop playsinline preload="metadata"></video>
</div>
<div class="card-info"><h3>{name}</h3></div>
</div>"""

def card_iframe(item):
    """Generate a card with iframe demo (for Vengence buttons)."""
    num = item["num"]
    name = html.escape(item["name"])
    demo = item["demo"]
    label = f"Hover #{num:02d}"
    return f"""<div class="card">
<div class="card-video-wrap">
<span class="card-number">{label}</span>
<iframe src="{demo}" title="{name}" loading="lazy" allowfullscreen></iframe>
</div>
<div class="card-info"><h3>{name}</h3></div>
</div>"""

# ─── Build index.html ────────────────────────────────────────────────
cat_cards = []
for cat_name, page_file, display_name in CATEGORIES:
    count = len(DATA[cat_name])
    # Add 3 to Hover Effects
    if cat_name == "Hover Effects":
        count += 3
    cat_cards.append(f"""<a class="cat-card" href="{page_file}">
<h3>{display_name}</h3>
<div class="count">{count} components</div>
<div class="desc">Browse {display_name.lower()} effects</div>
</a>""")

index_body = f"""<div class="container">
<div class="hero">
<h2>Animation Effects Catalog</h2>
<p>{sum(len(v) for v in DATA.values()) + 3} hand-crafted animation components across {len(DATA)} categories. Click any category to explore.</p>
</div>
<div class="cat-grid">
{chr(10).join(cat_cards)}
</div>
</div>"""

with open(os.path.join(BASE, "index.html"), "w", encoding="utf-8") as f:
    f.write(page_html("Animation Effects Catalog", index_body))

# ─── Build category pages ────────────────────────────────────────────
for cat_name, page_file, display_name in CATEGORIES:
    items = DATA[cat_name]
    cards = [card_video(item) for item in items]
    
    # Append Vengence buttons to Hover Effects
    if cat_name == "Hover Effects":
        for v in VENGENCE:
            cards.append(card_iframe(v))
    
    body = f"""<div class="container">
<div class="cat-header">
<h2>{display_name}</h2>
<p>{len(cards)} components</p>
</div>
<div class="grid">
{chr(10).join(cards)}
</div>
</div>"""
    
    with open(os.path.join(BASE, page_file), "w", encoding="utf-8") as f:
        f.write(page_html(f"{display_name} - Animation Catalog", body))

print(f"Built index.html + {len(CATEGORIES)} category pages")

# ─── Build Vengence demos ────────────────────────────────────────────
# Demo 1: Radial Glow Button
radial_glow_css = """
@property --rg-pos-x { syntax: '<percentage>'; initial-value: 40%; inherits: false; }
@property --rg-pos-y { syntax: '<percentage>'; initial-value: 140%; inherits: false; }
@property --rg-spread-x { syntax: '<percentage>'; initial-value: 130%; inherits: false; }
@property --rg-spread-y { syntax: '<percentage>'; initial-value: 170%; inherits: false; }
@property --rg-color-1 { syntax: '<color>'; initial-value: #000022; inherits: false; }
@property --rg-color-2 { syntax: '<color>'; initial-value: #1f3f6d; inherits: false; }
@property --rg-color-3 { syntax: '<color>'; initial-value: #469396; inherits: false; }
@property --rg-color-4 { syntax: '<color>'; initial-value: #f1ffa5; inherits: false; }
@property --rg-color-5 { syntax: '<color>'; initial-value: hsl(250 80% 2.5%); inherits: false; }
@property --rg-border-angle { syntax: '<angle>'; initial-value: 180deg; inherits: true; }
@property --rg-border-color-1 { syntax: '<color>'; initial-value: hsla(230, 75%, 90%, 0.7); inherits: true; }
@property --rg-border-color-2 { syntax: '<color>'; initial-value: hsla(230, 50%, 90%, 0.25); inherits: true; }
@property --rg-stop-1 { syntax: '<percentage>'; initial-value: 37.35%; inherits: false; }
@property --rg-stop-2 { syntax: '<percentage>'; initial-value: 61.36%; inherits: false; }
@property --rg-stop-3 { syntax: '<percentage>'; initial-value: 78.42%; inherits: false; }
@property --rg-stop-4 { syntax: '<percentage>'; initial-value: 93.52%; inherits: false; }
@property --rg-stop-5 { syntax: '<percentage>'; initial-value: 100%; inherits: false; }

.rg-button {
  --transition: 0.25s; --spark: 1.8s; --speed: 1.2s; --cut: 1px;
  --bg: radial-gradient(var(--rg-spread-x) var(--rg-spread-y) at var(--rg-pos-x) var(--rg-pos-y),
    var(--rg-color-1) var(--rg-stop-1), var(--rg-color-2) var(--rg-stop-2),
    var(--rg-color-3) var(--rg-stop-3), var(--rg-color-4) var(--rg-stop-4), var(--rg-color-5) var(--rg-stop-5));
  position: relative; min-width: 160px; min-height: 51px; padding: 16px 24px;
  border: none; border-radius: 11px; font-family: inherit; font-size: 16px; font-weight: 500;
  line-height: 19px; color: rgba(255,255,255,0.95); background: var(--bg); cursor: pointer;
  text-shadow: 0 0 2px rgba(0,0,0,0.95); overflow: hidden;
  -webkit-font-smoothing: antialiased; -webkit-tap-highlight-color: transparent;
  transition: --rg-pos-x .75s, --rg-pos-y .75s, --rg-spread-x .75s, --rg-spread-y .75s,
    --rg-color-1 .75s, --rg-color-2 .75s, --rg-color-3 .75s, --rg-color-4 .75s, --rg-color-5 .75s,
    --rg-border-angle .75s, --rg-border-color-1 .75s, --rg-border-color-2 .75s,
    --rg-stop-1 .75s, --rg-stop-2 .75s, --rg-stop-3 .75s, --rg-stop-4 .75s, --rg-stop-5 .75s;
}
.rg-button::before {
  content: ''; position: absolute; inset: 0; padding: 1px; border-radius: inherit;
  background-image: linear-gradient(var(--rg-border-angle), var(--rg-border-color-1), var(--rg-border-color-2));
  mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  mask-composite: exclude; pointer-events: none;
}
.rg-button:hover {
  --rg-pos-x: 0%; --rg-pos-y: 120%; --rg-spread-x: 110.24%; --rg-spread-y: 110.2%;
  --rg-color-1: #000020; --rg-color-2: #f1ffa5; --rg-color-3: #469396; --rg-color-4: #1f3f6d;
  --rg-stop-1: 0%; --rg-stop-2: 10%; --rg-stop-3: 35.44%; --rg-stop-4: 71.34%; --rg-stop-5: 150%;
  --rg-border-angle: 190deg;
  --rg-border-color-1: hsla(320, 75%, 90%, 0.1); --rg-border-color-2: hsla(320, 50%, 90%, 0.35);
  --button-line-opacity: 1;
}
.rg-label { position: relative; z-index: 1; }
.rg-bg { position: absolute; inset: var(--cut); background: var(--bg); border-radius: inherit;
  transition: background var(--transition), opacity var(--transition); }
.rg-shine { position: absolute; inset: 0; container-type: size; border-radius: inherit;
  mix-blend-mode: soft-light; opacity: var(--button-line-opacity, 0); transition: opacity 0.3s; overflow: visible; }
.rg-shine span { position: absolute; inset: 0; height: 100cqh; aspect-ratio: 1;
  animation: rg-slide var(--speed) ease-in-out infinite alternate; overflow: visible; }
.rg-shine span::before { content: ""; position: absolute; inset: -100%;
  background: conic-gradient(from calc(270deg - (90deg * 0.5)), transparent 0, #fff 90deg, transparent 90deg);
  animation: rg-spin calc(var(--speed) * 2) infinite linear; }
@keyframes rg-spin { 0% { rotate: 0deg; } 15%, 35% { rotate: 90deg; } 65%, 85% { rotate: 270deg; } 100% { rotate: 360deg; } }
@keyframes rg-slide { to { transform: translate(calc(100cqw - 100%), 0); } }
"""

radial_glow_html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Radial Glow Button</title>
<style>
body {{ margin:0; display:flex; align-items:center; justify-content:center; min-height:100vh; background:#0B0F19; font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; }}
{radial_glow_css}
</style></head>
<body>
<div style="position:relative;display:inline-block;">
<button class="rg-button" type="button">
<span class="rg-shine"><span></span></span>
<span class="rg-bg"></span>
<span class="rg-label">Get Extension</span>
</button>
</div>
</body></html>"""

with open(os.path.join(BASE, "demos", "vengence-radial-glow.html"), "w", encoding="utf-8") as f:
    f.write(radial_glow_html)

# Demo 2: Generate Button
generate_css = """
.gen-btn {
  --border-radius: 24px; --padding: 4px; --transition: 0.4s; --button-color: #101010;
  --highlight-color-hue: 210deg;
  user-select: none; display: flex; justify-content: center;
  padding: 0.5em 0.5em 0.5em 1.1em;
  font-family: "Poppins", "Inter", "Segoe UI", sans-serif;
  font-size: 1em; font-weight: 400;
  background-color: var(--button-color);
  box-shadow:
    inset 0px 1px 1px rgba(255,255,255,0.2),
    inset 0px 2px 2px rgba(255,255,255,0.15),
    inset 0px 4px 4px rgba(255,255,255,0.1),
    inset 0px 8px 8px rgba(255,255,255,0.05),
    inset 0px 16px 16px rgba(255,255,255,0.05),
    0px -1px 1px rgba(0,0,0,0.02),
    0px -2px 2px rgba(0,0,0,0.03),
    0px -4px 4px rgba(0,0,0,0.05),
    0px -8px 8px rgba(0,0,0,0.06),
    0px -16px 16px rgba(0,0,0,0.08);
  border: solid 1px rgba(255,255,255,0.133);
  border-radius: var(--border-radius); cursor: pointer;
  transition: box-shadow var(--transition), border var(--transition), background-color var(--transition);
}
.gen-btn::before {
  content: ""; position: absolute;
  top: calc(0px - var(--padding)); left: calc(0px - var(--padding));
  width: calc(100% + var(--padding) * 2); height: calc(100% + var(--padding) * 2);
  border-radius: calc(var(--border-radius) + var(--padding));
  pointer-events: none;
  background-image: linear-gradient(0deg, rgba(0,0,0,0.267), rgba(0,0,0,0.667));
  z-index: -1; transition: box-shadow var(--transition), filter var(--transition);
  box-shadow:
    0 -8px 8px -6px rgba(0,0,0,0) inset,
    0 -16px 16px -8px rgba(0,0,0,0) inset,
    1px 1px 1px rgba(255,255,255,0.133),
    2px 2px 2px rgba(255,255,255,0.067),
    -1px -1px 1px rgba(0,0,0,0.133),
    -2px -2px 2px rgba(0,0,0,0.067);
}
.gen-btn::after {
  content: ""; position: absolute; top: 0; left: 0; width: 100%; height: 100%;
  border-radius: inherit; pointer-events: none;
  background-image: linear-gradient(0deg, #fff, hsl(var(--highlight-color-hue), 100%, 70%), hsla(var(--highlight-color-hue), 100%, 70%, 50%), 8%, transparent);
  background-position: 0 0; opacity: 0;
  transition: opacity var(--transition), filter var(--transition);
}
.gen-btn-letter {
  position: relative; display: inline-block; color: rgba(255,255,255,0.333);
  animation: gen-letter-anim 2s ease-in-out infinite;
  transition: color var(--transition), text-shadow var(--transition), opacity var(--transition);
}
@keyframes gen-letter-anim { 50% { text-shadow: 0 0 3px rgba(255,255,255,0.533); color: #fff; } }
.gen-btn-svg { flex-grow: 1; height: 24px; margin-right: 0.5rem; fill: #e8e8e8;
  animation: gen-flicker 2s linear infinite; animation-delay: 0.5s;
  filter: drop-shadow(0 0 2px rgba(255,255,255,0.6));
  transition: fill var(--transition), filter var(--transition), opacity var(--transition); }
@keyframes gen-flicker { 50% { opacity: 0.3; } }
.gen-txt-wrapper { position: relative; display: flex; align-items: center; min-width: 6.4em; }
.gen-txt-1, .gen-txt-2 { position: absolute; word-spacing: -1em; }
.gen-txt-1 { animation: gen-appear-anim 1s ease-in-out forwards; }
.gen-txt-2 { opacity: 0; }
@keyframes gen-appear-anim { 0% { opacity: 0; } 100% { opacity: 1; } }
.gen-btn[data-generating="true"] .gen-txt-1 { animation: gen-opacity-anim 0.3s ease-in-out forwards; animation-delay: 1s; }
.gen-btn[data-generating="true"] .gen-txt-2 { animation: gen-opacity-anim 0.3s ease-in-out reverse forwards; animation-delay: 1s; }
@keyframes gen-opacity-anim { 0% { opacity: 1; } 100% { opacity: 0; } }
.gen-btn[data-generating="true"] .gen-btn-letter {
  animation: gen-focused-letter-anim 1s ease-in-out forwards, gen-letter-anim 1.2s ease-in-out infinite;
  animation-delay: 0s, 1s;
}
@keyframes gen-focused-letter-anim {
  0%, 100% { filter: blur(0px); }
  50% { transform: scale(2); filter: blur(10px) brightness(150%) drop-shadow(-36px 12px 12px hsl(var(--highlight-color-hue), 100%, 70%)); }
}
.gen-btn[data-generating="true"]::before {
  box-shadow:
    0 -8px 12px -6px rgba(255,255,255,0.2) inset,
    0 -16px 16px -8px hsla(var(--highlight-color-hue), 100%, 70%, 20%) inset,
    1px 1px 1px rgba(255,255,255,0.2),
    2px 2px 2px rgba(255,255,255,0.067),
    -1px -1px 1px rgba(0,0,0,0.133),
    -2px -2px 2px rgba(0,0,0,0.067);
}
.gen-btn[data-generating="true"]::after { opacity: 0.6; mask-image: linear-gradient(0deg, #fff, transparent); filter: brightness(100%); }
.gen-btn-letter:nth-child(1) { animation-delay: 0s; }
.gen-btn-letter:nth-child(2) { animation-delay: 0.08s; }
.gen-btn-letter:nth-child(3) { animation-delay: 0.16s; }
.gen-btn-letter:nth-child(4) { animation-delay: 0.24s; }
.gen-btn-letter:nth-child(5) { animation-delay: 0.32s; }
.gen-btn-letter:nth-child(6) { animation-delay: 0.4s; }
.gen-btn-letter:nth-child(7) { animation-delay: 0.48s; }
.gen-btn-letter:nth-child(8) { animation-delay: 0.56s; }
.gen-btn-letter:nth-child(9) { animation-delay: 0.64s; }
.gen-btn-letter:nth-child(10) { animation-delay: 0.72s; }
.gen-btn-letter:nth-child(11) { animation-delay: 0.8s; }
.gen-btn:active { border: solid 1px hsla(var(--highlight-color-hue), 100%, 80%, 70%); background-color: hsla(var(--highlight-color-hue), 50%, 20%, 0.5); }
.gen-btn:active::before {
  box-shadow:
    0 -8px 12px -6px rgba(255,255,255,0.667) inset,
    0 -16px 16px -8px hsla(var(--highlight-color-hue), 100%, 70%, 80%) inset,
    1px 1px 1px rgba(255,255,255,0.267),
    2px 2px 2px rgba(255,255,255,0.133),
    -1px -1px 1px rgba(0,0,0,0.133),
    -2px -2px 2px rgba(0,0,0,0.067);
}
.gen-btn:active::after { opacity: 1; mask-image: linear-gradient(0deg, #fff, transparent); filter: brightness(200%); }
.gen-btn:active .gen-btn-letter { text-shadow: 0 0 1px hsla(var(--highlight-color-hue), 100%, 90%, 90%); animation: none; }
.gen-btn:hover { border: solid 1px hsla(var(--highlight-color-hue), 100%, 80%, 40%); }
.gen-btn:hover::before {
  box-shadow:
    0 -8px 8px -6px rgba(255,255,255,0.667) inset,
    0 -16px 16px -8px hsla(var(--highlight-color-hue), 100%, 70%, 30%) inset,
    1px 1px 1px rgba(255,255,255,0.133),
    2px 2px 2px rgba(255,255,255,0.067),
    -1px -1px 1px rgba(0,0,0,0.133),
    -2px -2px 2px rgba(0,0,0,0.067);
}
.gen-btn:hover::after { opacity: 1; mask-image: linear-gradient(0deg, #fff, transparent); }
.gen-btn:hover .gen-btn-svg { fill: #fff; filter: drop-shadow(0 0 3px hsl(var(--highlight-color-hue), 100%, 70%)) drop-shadow(0 -4px 6px rgba(0,0,0,0.6)); animation: none; }
"""

# Build generate button HTML with letter spans
gen_letters_1 = "".join(f'<span class="gen-btn-letter">{l}</span>' for l in "Generate")
gen_letters_2 = "".join(f'<span class="gen-btn-letter">{l}</span>' for l in "Generating")

generate_html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Generate Button</title>
<style>
body {{ margin:0; display:flex; align-items:center; justify-content:center; min-height:100vh; background:#0B0F19; font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; }}
{generate_css}
</style></head>
<body>
<div style="position:relative;display:inline-block;">
<button type="button" class="gen-btn" data-generating="false" onclick="this.setAttribute('data-generating','true')">
<svg class="gen-btn-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
<path stroke-linecap="round" stroke-linejoin="round" d="M9.813 15.904 9 18.75l-.813-2.846a4.5 4.5 0 0 0-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 0 0 3.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 0 0 3.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 0 0-3.09 3.09ZM18.259 8.715 18 9.75l-.259-1.035a3.375 3.375 0 0 0-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 0 0 2.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 0 0 2.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 0 0-2.456 2.456ZM16.894 20.567 16.5 21.75l-.394-1.183a2.25 2.25 0 0 0-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 0 0 1.423-1.423l.394-1.183.394 1.183a2.25 2.25 0 0 0 1.423 1.423l1.183.394-1.183.394a2.25 2.25 0 0 0-1.423 1.423Z"></path>
</svg>
<div class="gen-txt-wrapper">
<div class="gen-txt-1">{gen_letters_1}</div>
<div class="gen-txt-2">{gen_letters_2}</div>
</div>
</button>
</div>
<script>
// Auto-cycle the generating state for demo purposes
const btn = document.querySelector('.gen-btn');
let generating = false;
setInterval(() => {{
  generating = !generating;
  btn.setAttribute('data-generating', generating);
}}, 3000);
</script>
</body></html>"""

with open(os.path.join(BASE, "demos", "vengence-generate.html"), "w", encoding="utf-8") as f:
    f.write(generate_html)

# Demo 3: Liquid Metal Button (uses @paper-design/shaders-react — needs WebGL shader,
# we'll create a CSS-only approximation using animated gradients)
liquid_metal_html = r"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Liquid Metal Button</title>
<style>
body { margin:0; display:flex; align-items:center; justify-content:center; min-height:100vh; background:#0B0F19; font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; }

.lm-button { position: relative; cursor: pointer; border: none; background: transparent; padding: 0; outline: none; }
.lm-button:active { transform: scale(0.98); }
.lm-wrapper { position: relative; border-radius: 9999px; overflow: hidden; padding: 4px;
  box-shadow: 0 20px 50px -12px rgba(0,0,0,0.25); }
.lm-border {
  position: absolute; inset: 0; z-index: 0; border-radius: 9999px;
  background: conic-gradient(from 0deg,
    #888888, #cccccc, #ffffff, #aaaaaa, #dddddd,
    #999999, #eeeeee, #888888, #ffffff, #bbbbbb, #888888);
  background-size: 200% 200%;
  animation: lm-rotate 4s linear infinite;
  filter: blur(1px);
}
@keyframes lm-rotate {
  0% { background-position: 0% 50%; transform: rotate(0deg); }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; transform: rotate(360deg); }
}
.lm-inner {
  position: relative; z-index: 10; border-radius: 9999px;
  display: flex; align-items: center; gap: 16px;
  padding: 12px 32px 12px 12px;
  background: #0a0a0a;
  transition: background 0.2s;
}
.lm-button:hover .lm-inner { background: #111; }
.lm-icon {
  width: 40px; height: 40px; border-radius: 9999px;
  display: flex; align-items: center; justify-content: center;
  background: #1a1a1a;
  box-shadow: inset 0 2px 4px rgba(0,0,0,0.06);
  color: #aaa;
}
.lm-icon svg { width: 20px; height: 20px; fill: currentColor; }
.lm-text { font-weight: 500; letter-spacing: -0.01em; color: #fff; font-size: 16px; }
</style></head>
<body>
<button class="lm-button" type="button">
<div class="lm-wrapper">
<div class="lm-border"></div>
<div class="lm-inner">
<div class="lm-icon">
<svg viewBox="0 0 24 24"><path d="M12 2L9 9H2l5.5 4-2 7L12 16l6.5 4-2-7L22 9h-7z"/></svg>
</div>
<span class="lm-text">Get Started</span>
</div>
</div>
</button>
</body></html>"""

with open(os.path.join(BASE, "demos", "vengence-liquid-metal.html"), "w", encoding="utf-8") as f:
    f.write(liquid_metal_html)

print("Built 3 Vengence demos")

# ─── Update manifest.json ────────────────────────────────────────────
with open(os.path.join(BASE, "manifest.json")) as f:
    manifest = json.load(f)

# Add Vengence entries
for i, v in enumerate(VENGENCE, 1):
    key = f"Hover Effects #{v['num']:02d}"
    manifest[key] = {
        "name": v["name"],
        "source": "Vengence UI",
        "demo_html": v["demo"],
        "local_tsx": v["tsx"],
        "category": "Hover Effects",
        "num": v["num"]
    }

with open(os.path.join(BASE, "manifest.json"), "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2, ensure_ascii=False)

print(f"Updated manifest.json with {len(VENGENCE)} Vengence entries")
print(f"Total manifest entries: {len(manifest)}")
print("DONE")