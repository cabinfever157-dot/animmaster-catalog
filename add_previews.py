#!/usr/bin/env python3
"""
Add demo_url to manifest.json for all placeholder components,
then regenerate ALL HTML category pages with iframe previews.
"""
import json
import os
import re
from collections import OrderedDict, defaultdict

BASE = r"C:\Users\info\Dropbox\Projects\component-catalog"
MANIFEST = os.path.join(BASE, "manifest.json")

# ── Library detection ──
def detect_library(code_path):
    """Detect which component library a file belongs to."""
    lc = code_path.lower().replace("\\", "/")
    if "aceternity" in lc: return "Aceternity"
    if "magicui" in lc: return "MagicUI"
    if "originui" in lc: return "OriginUI"
    if "hyperui" in lc: return "HyperUI"
    if "daisyui" in lc: return "DaisyUI"
    if "smoothui" in lc: return "SmoothUI"
    if "cultui" in lc: return "CultUI"
    if "seraui" in lc: return "SeraUI"
    if "vengence" in lc: return "VengenceUI"
    if "ogblocks" in lc: return "OGBlocks"
    if "shadcn" in lc: return "ShadcnUI"
    if "remotion" in lc: return "Remotion"
    if "react-com" in lc: return "ReactCom"
    return "Unknown"

# ── Demo URL builders ──

def build_aceternity_url(filename):
    """3d-card-effect.tsx -> https://www.aceternity.com/components/3d-card-effect"""
    slug = filename.replace(".tsx", "")
    return f"https://www.aceternity.com/components/{slug}"

def build_magicui_url(filename):
    """animated-beam.tsx -> https://magicui.design/docs/components/animated-beam"""
    slug = filename.replace(".tsx", "")
    return f"https://magicui.design/docs/components/{slug}"

def build_originui_url(filename):
    """comp-459.tsx or accordion.tsx -> https://coss.com/ui/docs/components/{slug}"""
    slug = filename.replace(".tsx", "")
    # comp-NNN files don't have direct URLs - they're sub-components
    # Try the component name directly
    if re.match(r'^comp-\d+$', slug):
        return None  # comp-NNN files are not directly addressable
    return f"https://coss.com/ui/docs/components/{slug}"

def build_hyperui_url(filename):
    """application-accordions-1.html -> https://www.hyperui.dev/components/application/accordions/"""
    name = filename.replace(".html", "")
    name = re.sub(r'-dark$', '', name)
    # Parse: {category}-{type}-{number}
    parts = name.split("-")
    if len(parts) >= 3 and parts[0] in ("application", "marketing", "neobrutalism", "templates"):
        cat = parts[0]
        # Everything between cat and last number is the type
        type_parts = parts[1:-1] if parts[-1].isdigit() else parts[1:]
        comp_type = "-".join(type_parts)
        return f"https://www.hyperui.dev/components/{cat}/{comp_type}/"
    elif len(parts) >= 2 and parts[0] in ("application", "marketing", "neobrutalism", "templates"):
        cat = parts[0]
        comp_type = "-".join(parts[1:])
        return f"https://www.hyperui.dev/components/{cat}/{comp_type}/"
    return None

def build_daisyui_url(filename):
    """countdown.html -> https://daisyui.com/components/countdown/"""
    slug = filename.replace(".html", "")
    return f"https://daisyui.com/components/{slug}/"

def build_smoothui_url(filename):
    """animated-progress-bar.tsx -> https://smoothui.dev/docs/components/animated-progress-bar"""
    slug = filename.replace(".tsx", "")
    return f"https://smoothui.dev/docs/components/{slug}"

def build_cultui_url(filename):
    """CultUI is offline - return None"""
    return None

def build_seraui_url(filename):
    """src-app-docs-3d-carousel-3d-carousel.tsx -> https://seraui.com/docs/3d-carousel"""
    name = filename.replace(".tsx", "")
    # Extract slug from src-app-docs-{slug}-{slug} or src-app-docs-{slug}
    if name.startswith("src-app-docs-"):
        parts = name.split("-")
        try:
            docs_idx = parts.index("docs")
            comp_parts = parts[docs_idx + 1:]
            # Remove duplicate: if last part repeats the earlier part
            # e.g. 3d-carousel-3d-carousel -> 3d-carousel
            slug_parts = comp_parts[:]
            # If the slug is duplicated (e.g., accordion-last-accordion-last), remove duplicate
            half = len(slug_parts) // 2
            if len(slug_parts) % 2 == 0 and slug_parts[:half] == slug_parts[half:]:
                slug_parts = slug_parts[:half]
            slug = "-".join(slug_parts)
            return f"https://seraui.com/docs/{slug}"
        except ValueError:
            pass
    return None

def build_demo_url(filename, library):
    """Build demo URL based on library and filename."""
    builders = {
        "Aceternity": build_aceternity_url,
        "MagicUI": build_magicui_url,
        "OriginUI": build_originui_url,
        "HyperUI": build_hyperui_url,
        "DaisyUI": build_daisyui_url,
        "SmoothUI": build_smoothui_url,
        "CultUI": build_cultui_url,
        "SeraUI": build_seraui_url,
    }
    builder = builders.get(library)
    if builder:
        return builder(filename)
    return None

# ── HTML generation ──

CAT_TO_FILE = {
    "Scroll Animation": "scroll-animation.html",
    "Hero Animations": "hero-animations.html",
    "Sliders": "sliders.html",
    "Navigation Menus": "navigation-menus.html",
    "Hover Effects": "hover-effects.html",
    "Mouse Effects": "mouse-effects.html",
    "Webgl & ThreeJS Effects": "webgl-threejs.html",
    "Text Animations": "text-animations.html",
    "Page Transitions": "page-transitions.html",
    "SVG Animations": "svg-animations.html",
    "Background Animations": "background-animations.html",
    "Grid Animations": "grid-animations.html",
    "Physics Effects": "physics-effects.html",
    "3D Animation": "3d-animation.html",
    "Buttons": "buttons.html",
    "Inputs": "inputs.html",
    "Cards": "cards.html",
    "Modals & Dialogs": "modals-dialogs.html",
    "Feedback": "feedback.html",
    "Layout": "layout.html",
    "Display": "display.html",
    "Forms": "forms.html",
    "Cinematic Intros": "cinematic-intros.html",
    "Uncategorized": "uncategorized.html",
}

CAT_SHORT = {
    "Scroll Animation": "Scroll", "Hero Animations": "Hero", "Sliders": "Slider",
    "Navigation Menus": "Nav", "Hover Effects": "Hover", "Mouse Effects": "Mouse",
    "Webgl & ThreeJS Effects": "WebGL", "Text Animations": "Text",
    "Page Transitions": "Transition", "SVG Animations": "SVG",
    "Background Animations": "Background", "Grid Animations": "Grid",
    "Physics Effects": "Physics", "3D Animation": "3D",
    "Buttons": "Button", "Inputs": "Input", "Cards": "Card",
    "Modals & Dialogs": "Modal", "Feedback": "Feedback", "Layout": "Layout",
    "Display": "Display", "Forms": "Form", "Cinematic Intros": "Intro",
    "Uncategorized": "Misc",
}

ALL_CATS_ORDER = [
    "Scroll Animation", "Hero Animations", "Sliders", "Navigation Menus",
    "Hover Effects", "Mouse Effects", "Webgl & ThreeJS Effects",
    "Text Animations", "Page Transitions", "SVG Animations",
    "Background Animations", "Grid Animations", "Physics Effects",
    "3D Animation",
    "Buttons", "Inputs", "Cards", "Modals & Dialogs", "Feedback",
    "Layout", "Display", "Forms", "Cinematic Intros", "Uncategorized"
]


def escape_html(text):
    """Escape HTML special characters."""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def generate_card_html(key, val, cat, num):
    """Generate HTML for a single component card."""
    name = val.get("name", key)
    search_str = f"{name} #{num:02d} {cat}".lower()
    
    # Video preview (existing)
    if "cdn_video" in val:
        video_url = val["cdn_video"]
        return f"""    <div class="card" data-search="{escape_html(search_str)}">
      <div class="preview"><video src="{video_url}" autoplay loop muted playsinline></video></div>
      <div class="label"><span class="name">{escape_html(name)}</span><span class="num">#{num:02d}</span></div>
    </div>"""
    
    # Demo HTML (Vengence UI - existing)
    if "demo_html" in val:
        demo_path = val["demo_html"]
        return f"""    <div class="card" data-search="{escape_html(search_str)}">
      <div class="preview"><iframe src="{demo_path}" width="100%" height="100%" style="border:0" scrolling="no" sandbox="allow-scripts allow-same-origin"></iframe></div>
      <div class="label"><span class="name">{escape_html(name)}</span><span class="num">#{num:02d}</span></div>
    </div>"""
    
    # New: iframe preview from demo_url
    demo_url = val.get("demo_url")
    if demo_url:
        return f"""    <div class="card" data-search="{escape_html(search_str)}">
      <div class="preview"><iframe src="{escape_html(demo_url)}" width="100%" height="100%" style="border:0" scrolling="no" sandbox="allow-scripts allow-same-origin" loading="lazy"></iframe></div>
      <div class="label"><span class="name">{escape_html(name)}</span><span class="num">#{num:02d}</span></div>
    </div>"""
    
    # Fallback: "View on source site" link card
    source_url = val.get("source_url", demo_url)
    if source_url:
        return f"""    <div class="card" data-search="{escape_html(search_str)}">
      <div class="preview"><a href="{escape_html(source_url)}" target="_blank" rel="noopener" style="display:flex;width:100%;height:100%;align-items:center;justify-content:center;text-decoration:none;color:#0066FF;font-size:0.75rem;gap:6px;"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M15 3h6v6"/><path d="M10 14 21 3"/><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/></svg> View on source site</a></div>
      <div class="label"><span class="name">{escape_html(name)}</span><span class="num">#{num:02d}</span></div>
    </div>"""
    
    # Last resort: "Code Available" placeholder
    return f"""    <div class="card" data-search="{escape_html(search_str)}">
      <div class="preview"><div class="placeholder">Code Available</div><div class="code-avail">●</div></div>
      <div class="label"><span class="name">{escape_html(name)}</span><span class="num">#{num:02d}</span></div>
    </div>"""


def generate_category_html(cat, items):
    """Generate full HTML page for a category."""
    cat_file = CAT_TO_FILE.get(cat, "uncategorized.html")
    short = CAT_SHORT.get(cat, cat)
    count = len(items)
    
    cards_html = []
    for key, val in items:
        num = val.get("num", 0)
        cards_html.append(generate_card_html(key, val, cat, num))
    
    cards = "\n".join(cards_html)
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{cat} — Component Catalog</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ background: #0B0F19; color: #e0e0e0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }}
  .header {{ padding: 30px 20px 20px; text-align: center; position: sticky; top: 0; background: #0B0F19; z-index: 100; border-bottom: 1px solid #1a1f2e; }}
  .header h1 {{ font-size: 1.6rem; color: #fff; margin-bottom: 4px; }}
  .header a {{ color: #0066FF; text-decoration: none; font-size: 0.85rem; }}
  .search {{ width: 100%; max-width: 500px; margin: 12px auto 0; padding: 8px 14px; background: #11141f; border: 1px solid #1a1f2e; border-radius: 8px; color: #fff; font-size: 0.85rem; display: block; }}
  .search:focus {{ outline: none; border-color: #0066FF; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 12px; padding: 20px; max-width: 1400px; margin: 0 auto; }}
  .card {{ background: #131722; border-radius: 10px; overflow: hidden; border: 1px solid #1a1f2e; transition: transform 0.15s, border-color 0.15s; cursor: pointer; }}
  .card:hover {{ transform: translateY(-3px); border-color: #0066FF; }}
  .card .preview {{ aspect-ratio: 16/10; background: linear-gradient(135deg, #131722, #0B0F19); display: flex; align-items: center; justify-content: center; position: relative; overflow: hidden; }}
  .card .preview video {{ width: 100%; height: 100%; object-fit: cover; }}
  .card .preview iframe {{ width: 100%; height: 100%; border: 0; }}
  .card .preview .placeholder {{ color: #2a3050; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 1px; }}
  .card .preview .code-avail {{ position: absolute; bottom: 8px; right: 8px; font-size: 0.6rem; color: #0066FF; opacity: 0.5; }}
  .card .label {{ padding: 8px 10px; display: flex; justify-content: space-between; align-items: center; }}
  .card .label .name {{ font-size: 0.75rem; color: #ccc; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 160px; }}
  .card .label .num {{ font-size: 0.7rem; color: #0066FF; font-family: monospace; font-weight: bold; }}
</style>
</head>
<body>
<div class="header">
  <h1>{cat} <span style="color:#555;font-size:0.8rem">({count})</span></h1>
  <a href="index.html">← All Categories</a>
  <input class="search" type="text" placeholder="Search {cat}..." id="search">
</div>
<div class="grid" id="grid">
{cards}
</div>
<script>
document.getElementById('search').addEventListener('input', function(e) {{
  const q = e.target.value.toLowerCase();
  document.querySelectorAll('.card').forEach(function(c) {{
    const s = c.getAttribute('data-search');
    if (s.includes(q)) {{ c.style.display = ''; }} else {{ c.style.display = 'none'; }}
  }});
}});
</script>
</body>
</html>"""
    
    return html


def main():
    # Load manifest
    with open(MANIFEST, "r", encoding="utf-8") as f:
        manifest = json.load(f, object_pairs_hook=OrderedDict)
    
    print(f"Total components: {len(manifest)}")
    
    # Group by category
    by_cat = defaultdict(list)
    url_added = 0
    no_url = 0
    
    for key, val in manifest.items():
        cat = val.get("category", key.rsplit(" #", 1)[0] if " #" in key else "Uncategorized")
        
        # Skip components that already have video or demo_html previews
        if "cdn_video" in val or "demo_html" in val:
            by_cat[cat].append((key, val))
            continue
        
        # Determine library and build demo URL
        code = val.get("local_code", val.get("local_tsx", ""))
        filename = code.replace("\\", "/").split("/")[-1] if code else ""
        library = detect_library(code)
        
        demo_url = build_demo_url(filename, library)
        
        if demo_url:
            val["demo_url"] = demo_url
            url_added += 1
        else:
            # For components without a demo URL, add source_url if we can determine one
            no_url += 1
        
        by_cat[cat].append((key, val))
    
    print(f"Demo URLs added: {url_added}")
    print(f"Components without demo URL: {no_url}")
    
    # Save updated manifest
    with open(MANIFEST, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    
    print(f"\nManifest saved with demo_url fields.")
    
    # Generate HTML pages
    print("\nGenerating HTML pages...")
    for cat in ALL_CATS_ORDER:
        if cat not in by_cat:
            continue
        items = by_cat[cat]
        html = generate_category_html(cat, items)
        cat_file = CAT_TO_FILE.get(cat, "uncategorized.html")
        filepath = os.path.join(BASE, cat_file)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"  {cat_file}: {len(items)} components")
    
    # Generate index.html
    index_html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Component Catalog</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { background: #0B0F19; color: #e0e0e0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }
  .header { padding: 40px 20px; text-align: center; }
  .header h1 { font-size: 2rem; color: #fff; margin-bottom: 8px; }
  .header p { color: #888; font-size: 0.9rem; }
  .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 12px; padding: 20px; max-width: 1200px; margin: 0 auto; }
  .cat-card { background: #131722; border-radius: 10px; padding: 20px; border: 1px solid #1a1f2e; transition: transform 0.15s, border-color 0.15s; text-decoration: none; color: inherit; display: block; }
  .cat-card:hover { transform: translateY(-3px); border-color: #0066FF; }
  .cat-card .cat-name { font-size: 1.1rem; color: #fff; margin-bottom: 4px; }
  .cat-card .cat-count { font-size: 0.85rem; color: #0066FF; }
</style>
</head>
<body>
<div class="header">
  <h1>Component Catalog</h1>
  <p>2880 components with live previews</p>
</div>
<div class="grid">
"""
    
    for cat in ALL_CATS_ORDER:
        if cat not in by_cat:
            continue
        count = len(by_cat[cat])
        cat_file = CAT_TO_FILE.get(cat, "uncategorized.html")
        index_html += f'  <a class="cat-card" href="{cat_file}"><div class="cat-name">{cat}</div><div class="cat-count">{count} components</div></a>\n'
    
    index_html += """</div>
</body>
</html>"""
    
    with open(os.path.join(BASE, "index.html"), "w", encoding="utf-8") as f:
        f.write(index_html)
    
    print("\nindex.html generated")
    print(f"\nDone! Total pages: {len(by_cat)} category pages + index.html")


if __name__ == "__main__":
    main()