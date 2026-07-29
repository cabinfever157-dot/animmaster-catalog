#!/usr/bin/env python3
"""
Build the expanded AnimMasterLib catalog - v2.
Improved filtering: filename-based exclusion first, then content check.
"""
import os, re, json, html

BASE = r"C:\Users\info\Dropbox\Projects\component-catalog"
LIB_BASE = r"C:\Users\info\AppData\Local\hermes\skills\design\ui-component-libraries"
AG_BASE = r"C:\Users\info\Dropbox\Google Drive\Software\AG_Backup\2\.agents\skills"

# ── Existing category max numbers ──
existing_max = {}

def load_existing_max():
    m = json.load(open(os.path.join(BASE, "manifest.json")))
    # We need the ORIGINAL manifest, but since we already ran build_catalog.py once,
    # we need to figure out the original max from the git repo
    # For now, use the known values from the original manifest
    pass

# Reset to original values (before our first run)
existing_max = {
    "Scroll Animation": 66,
    "Hero Animations": 26,
    "Sliders": 23,
    "Navigation Menus": 21,
    "Hover Effects": 23,
    "Mouse Effects": 20,
    "Webgl & ThreeJS Effects": 19,
    "Text Animations": 17,
    "Page Transitions": 14,
    "SVG Animations": 11,
    "Background Animations": 10,
    "Grid Animations": 10,
    "Physics Effects": 10,
    "3D Animation": 22,
    "Buttons": 0,
    "Cinematic Intros": 0,
    "Uncategorized": 0,
}

CAT_FILES = {
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
    "Cinematic Intros": "cinematic-intros.html",
    "Uncategorized": "uncategorized.html",
}

CAT_PREFIX = {
    "Scroll Animation": "scroll",
    "Hero Animations": "hero",
    "Sliders": "slider",
    "Navigation Menus": "nav",
    "Hover Effects": "hover",
    "Mouse Effects": "mouse",
    "Webgl & ThreeJS Effects": "webgl",
    "Text Animations": "text",
    "Page Transitions": "page",
    "SVG Animations": "svg",
    "Background Animations": "bg",
    "Grid Animations": "grid",
    "Physics Effects": "physics",
    "3D Animation": "3d",
    "Buttons": "btn",
    "Cinematic Intros": "cine",
    "Uncategorized": "uncat",
}

# ── Filename-based exclusion: these substrings mean "not an animation effect" ──
# If ANY of these appear in the filename (lowercased), the file is excluded
EXCLUDE_SUBSTRINGS = [
    # Static form elements
    "input", "checkbox", "radio", "select", "toggle", "switch", "label", "field",
    "textarea", "form", "combobox", "autocomplete", "datepicker", "date-picker",
    "range", "slider.tsx",  # form slider
    # Static layout
    "separator", "aspect-ratio", "resizable", "skeleton", "spinner", 
    "scroll-area", "collapsible", "accordion", "breadcrumb", "pagination",
    # Infrastructure
    "analytics", "seo", "theme", "performance", "monitor", "registry",
    "install", "mdx", "catalog.json", "index.md",
    # Icons
    "icon", "logo",
    # Auth
    "auth", "login", "sign-in", "signup",
    # Static display elements
    "badge", "avatar", "alert", "tooltip", "dropdown", "command",
    "popover", "sheet", "modal", "dialog", "drawer", "toast", "sonner",
    "callout", "calendar", "code-block", "snippet", "terminal", "clipboard",
    "data-table", "chart-", "command",
    # App/docs infrastructure
    "apps-examples", "calcom", "providers", "schema-display", "stack-trace",
    "test-results", "transcription", "voice-selector", "social-cards",
    "social-selector", "sources", "queue", "plan", "poll-widget", "vote-tally",
    "choice-poll", "sortable-list", "web-preview", "youtube-video-player",
    "audio-player", "video-player", "prompt-input", "prompt-library",
    "artifact", "sandbox", "reasoning", "chain-of-thought", "suggestion",
    "checkpoint", "task", "tool", "toolbar", "timer", "toc",
    "style-switcher", "style-wrapper", "tailwind-indicator",
    "site-footer", "site-header", "sidebar-nav", "side-panel",
    "cookie", "newsletter", "promo-video", "youtube", "google-drive",
    "google-gemini", "github-profile", "file-upload", "attachments",
    "speech-input", "audio-", "mockup-", "mask", "kbd", "indicator",
    "filter", "fieldset", "diff", "divider", "footer", "header.tsx",
    "stat", "steps", "tab.tsx", "tabs.tsx", "doctabs", "join",
    "swap", "fab", "chat", "rating", "card.tsx", "card-view",
    "card-content", "button-group", "button.tsx", "button-view",
    "button-copy", "button-action", "button-commerce", "button-icons",
    "button-only", "button-others", "button-righticon", "button-social",
    "social-button", "ai-button", "copybutton", "app-toggle",
    "app-download", "apple-invites", "job-listing", "product-card",
    "product-catalog", "tweet", "tweet-grid", "waitlist", "verify-badge",
    "verify-profile", "amazongift", "codeprofile", "colorpalette",
    "announcement", "empty-content", "empty-page", "empty-",
    "error-page", "error-", "loading-page", "loading-",
    "page-content", "page-client", "not-found", "404",
    "coming-soon", "faq", "cta", "cart", "album", "cookie",
    "block-copy", "block-display", "block-preview", "block-wrapper",
    "block-toolbar", "block-chunk", "blocks-grid", "cli-install",
    "cli-registry", "block-",
    # SeraUI infrastructure
    "src-components-site", "src-components-ui", "src-components-core",
    "src-components-performance", "src-components-seo", "src-components-analytics",
    "src-contexts", "src-mdx", "src-assets", "src-app-standalone",
    "src-app-not-found", "src-app-layout", "src-app-(landing)",
    # More excludes
    "features-section", "feature.tsx", "feature-view", "feature-content",
    "hero-sections", "hero-view", "hero-content",
    "card-grid", "grid-view", "nav-view", "nav-content",
    "widget", "prompt", "ai-", "agent", "speech", "voice",
    "text-input", "text-area", "searchable-dropdown", "search-modal",
    "table-of-contents", "props-table", "mdx-table", "vitepress",
    "optimized-image", "dynamic-loader", "hide-toc", "package-manager",
    "component-template", "component-renderer", "component-seo",
    "componentseo", "docs-layout", "layout-content",
    "code-renderer", "code-copy", "code-block-client",
    "mobile-sidebar", "scroll-area",
    "radio-group", "select.tsx", "switch.tsx", "toggle-group",
    "checkbox.tsx", "textarea.tsx", "label.tsx", "input.tsx",
    "form.tsx",
    # Static cards that are just layout
    "card.tsx", "card-view", "card-content", "card-grid",
    # Demo files (keep demos that ARE the effect)
    "cards-demo",  # these are just demo pages for card layouts
]

def should_exclude_name(filename):
    """Hard filename-based exclusion. If True, file is never included."""
    n = filename.lower().replace(".tsx", "").replace(".jsx", "").replace(".html", "")
    n_flat = n.replace("_", "-")
    
    if n in ["index", "index.md", "readme", "readme.md", "catalog.json"]:
        return True
    if n_flat.startswith("comp-"):
        return True  # OriginUI generic numbered files
    if n_flat.startswith("apps-examples"):
        return True
    if n_flat.startswith("authentication"):
        return True
    if n_flat.startswith("src-components-") or n_flat.startswith("src-contexts") or n_flat.startswith("src-mdx") or n_flat.startswith("src-assets"):
        return True
    if n_flat.startswith("src-app-standalone") or n_flat.startswith("src-app-not-found") or n_flat.startswith("src-app-layout") or n_flat.startswith("src-app-(landing)"):
        return True
    if n_flat.startswith("block-") or n_flat.startswith("cli-"):
        return True
    if n_flat.startswith("docs-layout") or n_flat.startswith("layout-content"):
        return True
    
    # Check exclusion substrings
    for ex in EXCLUDE_SUBSTRINGS:
        if ex in n_flat:
            return True
    
    return False

def has_animation_signals(filepath):
    """Check if a file contains real animation/visual effect signals (not just CSS transitions)."""
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read(10000).lower()
    except:
        return False
    
    # Must have actual animation imports or keyframe/transform usage
    strong_signals = [
        "framer-motion", "motion.", "framer",
        "useanimation", "usemotion", "useAnimationFrame",
        "requestanimationframe",
        "@keyframes", "keyframes",
        "whilehover", "whiletap", "whileinview", "whilefocus",
        "animate:", "animation:", "animation-",
        "useSpring", "useTransform",
        "three.js", "threejs", "webgl", "shader",
        "canvas.getcontext", "canvas.",
        "intersectionobserver", "intersection-observer",
        "parallax", "tilt", "magnetic", "spring",
        "glow", "shimmer", "ripple", "particle", "meteor", "beam",
        "aurora", "sparkle", "vortex", "orbit", "marquee",
        "spotlight", "glitch", "noise", "dither",
        "pulsat", "typewriter", "scramble", "decrypt",
        "flip-", "-flip", "text-flip", "text-generate",
        "hover-border", "border-gradient",
        "shooting-star", "glowing-star", "glowing-button",
        "wobble", "wavy", "squiggly", "fuzzy", "liquid",
        "distort", "pixelated", "gooey", "morph",
        "container-scroll", "tracing-beam", "moving-line",
        "multi-step-loader", "infinite-moving",
        "card-hover", "card-spotlight", "card-stack",
        "direction-aware", "following-pointer",
        "floating-dock", "floating-navbar",
        "dock.tsx", "marquee.tsx",
        "pulsating", "rainbow-button", "magnetic-button",
        "shimmer-button", "pulsating-button",
        "animated-beam", "border-beam", "shine-border",
        "magic-card", "flickering-grid",
        "animated-testimonials", "animated-tooltip",
        "apple-cards-carousel", "3d-card", "3d-globe", "3d-marquee", "3d-pin",
        "bento-grid", "layout-grid", "focus-cards", "expandable-cards",
        "evervault-card", "comet-card", "glare-card",
        "lamp.tsx", "lamp-section",
        "hero-highlight", "hero-parallax", "parallax-hero",
        "macbook-scroll", "world-map", "globe.tsx",
        "text-reveal", "text-animate", "text-generate",
        "sparkles.tsx", "spotlight.tsx",
        "vortex.tsx", "vortex-background",
        "wavy-background", "aurora-background", "aurora-text",
        "background-beams", "background-boxes", "background-gradient",
        "background-lines", "background-ripple",
        "noise-background", "stars-background",
        "dotted-glow-background", "dots-background",
        "dot-pattern", "grid-pattern", "flickering-grid",
        "dither-shader", "pixelated-canvas", "canvas-reveal",
        "canvas-text", "canvas-fractal",
        "sticky-scroll", "sticky-banner",
        "tracing-beam", "link-preview", "images-slider",
        "infinite-moving-cards", "tooltip-card",
        "animated-shiny-text", "blur-fade",
        "number-ticker", "particles.tsx", "meteors.tsx",
        "ripple.tsx", "shimmer-button.tsx",
        "pulsating-button.tsx", "dock.tsx",
        "globe.tsx", "magic-card.tsx",
        "marquee.tsx", "border-beam.tsx",
        "shine-border.tsx", "text-animate.tsx",
        "text-reveal.tsx",
        "bg-animate", "bg-animated",
        "canvas-fractal-grid",
        "svg-shapes-animated", "terminal-animation",
        "text-animate-demo", "texture-button", "texture-card",
        "texture-overlay", "texture-wrapper",
        "three-d-carousel",
        "shift-card", "shimmer.tsx",
        "bg-image-texture", "bg-media",
        "background-guides", "background-texture",
        "stripe-bg", "animated-number",
        "svg-bands", "squiggle-arrow",
        "3d-carousel", "animated-badge",
        "aurora.tsx", "curved-text", "decrypting",
        "dock-colorful", "dock-floating", "dock-minimal", "dock-simple",
        "enhanced-carousel", "imagecarousel", "scroll-progress",
        "ticker.tsx", "video-gallery", "video-text",
        "wavy.tsx", "typewriter.tsx",
        "animated-testimonial", "siri-orb",
        "power-off-slide", "dynamic-island",
        "cursor-follow", "glow-hover-card",
        "gooey-popover", "scroll-reveal",
        "scrollable-card-stack", "scramble-hover",
        "reveal-text", "wave-text", "magnetic-button",
        "smooth-button", "dot-morph-button",
        "clip-corners-button", "grid-loader",
        "animated-avatar-group", "animated-file-upload",
        "animated-progress-bar", "animated-stepper",
        "animated-tabs", "animated-tags", "animated-tooltip",
        "contribution-graph", "expandable-cards",
        "figma-comment", "github-stars",
        "infinite-slider", "interactive-image",
        "notification-badge", "number-flow",
        "phototab", "price-flow", "reviews-carousel",
        "scroll-reveal-paragraph", "scrubber",
        "skeleton-loader", "switchboard-card",
        "typewriter-text", "wave-text",
        "exposure-slider", "scrollable-card",
        "animated-modal",
        "hover-3d", "hover-gallery", "countdown",
        "progress-bar", "timeline",
        "marquee", "carousel", "ticker",
    ]
    
    return any(s in content for s in strong_signals)

def categorize(filename, content=""):
    """Categorize a component based on its filename."""
    n = filename.lower().replace(".tsx", "").replace(".jsx", "").replace(".html", "").replace("_", "-")
    
    # ── Buttons ──
    if any(x in n for x in ["button", "magnetic-button", "shimmer-button", "pulsating-button",
                            "rainbow-button", "glowing-button", "smooth-button", "dot-morph-button",
                            "clip-corners-button", "bg-animate-button", "border-beam-button",
                            "texture-button", "tailwindcss-button", "hover-border-gradient",
                            "stateful-button"]):
        return "Buttons"
    
    # ── Cinematic Intros ──
    if any(x in n for x in ["loader", "preloader", "splash", "intro", "cinematic",
                            "multi-step-loader", "grid-loader", "skeleton-loader",
                            "loading"]):
        return "Cinematic Intros"
    
    # ── Background Animations ──
    if any(x in n for x in ["background", "aurora-background", "background-beams",
                            "background-boxes", "background-gradient", "background-lines",
                            "background-ripple", "noise-background", "stars-background",
                            "vortex-background", "wavy-background", "dotted-glow-background",
                            "dots-background", "dot-background", "grid-background",
                            "grid-and-dot", "flickering-grid", "bg-animated",
                            "bg-animate", "background-guides", "background-texture",
                            "stripe-bg", "bg-image-texture", "bg-media",
                            "aurora", "meteors", "shooting-stars", "glowing-stars",
                            "sparkles", "particles", "vortex", "beam",
                            "border-beam", "shine-border", "grid-pattern",
                            "dot-pattern", "glowing-background",
                            "dither-shader", "flickering"]):
        return "Background Animations"
    
    # ── Text Animations ──
    if any(x in n for x in ["text-animate", "text-flip", "text-generate", "text-hover",
                            "text-reveal", "typewriter", "shimmer-text", "shimmer.tsx",
                            "flip-words", "squiggly-text", "encrypted-text", "colourful-text",
                            "aurora-text", "animated-shiny-text", "blur-fade",
                            "text-flip-board", "text-flipping-board", "text-generate-effect",
                            "text-hover-effect", "text-reveal-card", "canvas-text",
                            "container-text-flip", "layout-text-flip", "pointer-highlight",
                            "cover", "two-tone-text", "type-animate", "pixel-heading",
                            "pixel-paragraph", "text-gif", "wave-text",
                            "scramble-hover", "reveal-text", "typewriter-text",
                            "decrypting", "curved-text", "ticker", "video-text",
                            "text-typewriter", "text-wavy", "ascii-art",
                            "flip-words", "moving-line", "squiggle-arrow",
                            "text-clip", "text-demo",
                            "shimmer-text", "animated-shiny",
                            "colourful", "rainbow-text",
                            "number-ticker", "number-flow", "price-flow",
                            "flip-words", "text-flip",
                            "shimmer-text"]):
        return "Text Animations"
    
    # ── 3D Animation ──
    if any(x in n for x in ["3d-card", "3d-globe", "3d-marquee", "3d-pin",
                            "3d-carousel", "threed-card", "three-element",
                            "glare-card", "lens", "three-d-carousel",
                            "globe", "world-map", "macbook-scroll",
                            "apple", "apple-cards", "pixelated-canvas",
                            "webcam-pixel", "dither", "dither-shader",
                            "shader-lens", "shader-lens-blur",
                            "evervault-card", "comet-card", "notch",
                            "scales", "focus-cards", "3d",
                            "perspective", "rotate3d", "hover-3d"]):
        return "3D Animation"
    
    # ── WebGL & ThreeJS Effects ──
    if any(x in n for x in ["webgl", "threejs", "three.js", "canvas-reveal",
                            "canvas-reveal-effect", "canvas-fractal",
                            "canvas-text", "shader", "pixelated",
                            "glitch", "noise", "fuzzy", "liquid",
                            "distort", "canvas-fractal-grid",
                            "shader-lens"]):
        return "Webgl & ThreeJS Effects"
    
    # ── Scroll Animation ──
    if any(x in n for x in ["scroll", "parallax-scroll", "parallax-hero",
                            "container-scroll", "sticky-scroll", "sticky-banner",
                            "tracing-beam", "scroll-reveal", "scrollable-card",
                            "scroll-progress", "scroll-reveal-paragraph"]):
        return "Scroll Animation"
    
    # ── Hero Animations ──
    if any(x in n for x in ["hero", "hero-highlight", "hero-parallax",
                            "parallax-hero", "lamp", "lamp-section",
                            "spotlight", "spotlight-new",
                            "parallax-hero-images"]):
        return "Hero Animations"
    
    # ── Sliders ──
    if any(x in n for x in ["slider", "carousel", "images-slider",
                            "infinite-moving", "infinite-slider",
                            "enhanced-carousel", "imagecarousel",
                            "apple-cards-carousel", "three-d-carousel",
                            "reviews-carousel", "expandable-cards",
                            "draggable-card", "card-stack",
                            "exposure-slider", "scrubber",
                            "video-gallery"]):
        return "Sliders"
    
    # ── Navigation Menus ──
    if any(x in n for x in ["navbar", "dock", "floating-dock", "floating-navbar",
                            "resizable-navbar", "navbar-menu",
                            "link-preview", "animated-tabs",
                            "dock-colorful", "dock-floating",
                            "dock-minimal", "dock-simple",
                            "animated-stepper", "progress-bar"]):
        return "Navigation Menus"
    
    # ── Hover Effects ──
    if any(x in n for x in ["hover", "card-hover", "card-spotlight",
                            "card-hover-effect", "direction-aware",
                            "hover-card", "hover-3d", "hover-gallery",
                            "glow-hover", "gooey-popover",
                            "shift-card", "wobble-card",
                            "tooltip-card", "images-badge",
                            "bento-grid", "layout-grid",
                            "magic-card", "texture-card",
                            "glare-card", "tooltip",
                            "following-pointer", "magnetic",
                            "figma-comment", "interactive-image",
                            "product-card", "notification-badge"]):
        return "Hover Effects"
    
    # ── Mouse Effects ──
    if any(x in n for x in ["mouse", "cursor-follow", "following-pointer",
                            "pointer", "parallax", "tilt",
                            "draggable", "spotlight"]):
        return "Mouse Effects"
    
    # ── SVG Animations ──
    if any(x in n for x in ["svg", "svg-mask", "svg-bands", "svg-shapes",
                            "svg-shapes-animated", "svg-shapes-demo",
                            "world-map", "mask",
                            "curved-text"]):
        return "SVG Animations"
    
    # ── Grid Animations ──
    if any(x in n for x in ["grid", "bento-grid", "layout-grid",
                            "blocks-grid", "plug-grid",
                            "contribution-graph", "grid-loader",
                            "github-stars"]):
        return "Grid Animations"
    
    # ── Page Transitions ──
    if any(x in n for x in ["transition", "page-transition",
                            "animated-modal", "blur-fade",
                            "dynamic-island", "power-off-slide"]):
        return "Page Transitions"
    
    # ── Physics Effects ──
    if any(x in n for x in ["physics", "spring", "bounce",
                            "wobble", "ripple", "wave",
                            "siri-orb", "liquid", "gooey",
                            "meteors", "shooting-stars",
                            "comet", "sparkles",
                            "particles", "vortex",
                            "orbit", "beam"]):
        return "Physics Effects"
    
    # ── Timeline / Progress animations ──
    if any(x in n for x in ["timeline", "progress", "countdown",
                            "steps", "animated-number"]):
        return "Scroll Animation"  # These have scroll-like animation
    
    return "Uncategorized"

def prettify_name(filename):
    """Convert filename to a nice display name."""
    name = filename.replace(".tsx", "").replace(".jsx", "").replace(".html", "")
    # Handle SeraUI's long prefix
    name = re.sub(r'^src-app-docs-', '', name, flags=re.IGNORECASE)
    name = name.replace("_", " ").replace("-", " ")
    # Title case
    words = name.split()
    result = []
    for w in words:
        if w.lower() in ["3d", "ui", "otp", "ai", "svg", "css", "api", "orb", "gif"]:
            result.append(w.upper())
        elif w.lower() in ["text", "card", "hero", "grid", "dock", "beam", "card"]:
            result.append(w.capitalize())
        else:
            result.append(w.capitalize())
    return " ".join(result)

def scan_aceternity(path):
    """Aceternity - most files are animated effects."""
    results = []
    for f in os.listdir(path):
        if not f.endswith(".tsx"):
            continue
        if should_exclude_name(f):
            continue
        # Aceternity files are almost all animated - check content anyway
        fp = os.path.join(path, f)
        if has_animation_signals(fp):
            results.append((f, fp))
    return results

def scan_magicui(path):
    """MagicUI - all files are animated effects."""
    results = []
    for f in os.listdir(path):
        if not f.endswith(".tsx"):
            continue
        if should_exclude_name(f):
            continue
        fp = os.path.join(path, f)
        if has_animation_signals(fp):
            results.append((f, fp))
    return results

def scan_cultui(path):
    """CultUI - mix of static and animated, need careful filtering."""
    results = []
    for f in os.listdir(path):
        if not f.endswith(".tsx"):
            continue
        if should_exclude_name(f):
            continue
        fp = os.path.join(path, f)
        if has_animation_signals(fp):
            results.append((f, fp))
    return results

def scan_smoothui(path):
    """SmoothUI - has animated components."""
    results = []
    for f in os.listdir(path):
        if not f.endswith(".tsx"):
            continue
        if should_exclude_name(f):
            continue
        fp = os.path.join(path, f)
        if has_animation_signals(fp):
            results.append((f, fp))
    return results

def scan_originui(path):
    """OriginUI - mostly static form elements, skip comp-XX files."""
    results = []
    for f in os.listdir(path):
        if not f.endswith(".tsx"):
            continue
        if should_exclude_name(f):
            continue
        # Skip if it's a comp-XX file
        if re.match(r'^comp-\d+', f, re.IGNORECASE):
            continue
        fp = os.path.join(path, f)
        if has_animation_signals(fp):
            results.append((f, fp))
    return results

def scan_daisyui(path):
    """DaisyUI - HTML files, only include animated ones."""
    results = []
    anim_keywords = ["carousel", "marquee", "countdown", "loading",
                      "progress", "radial", "hover", "dock",
                      "swap", "mockup", "chat", "diff",
                      "timeline", "steps", "stack", "toast"]
    for f in os.listdir(path):
        if not f.endswith(".html"):
            continue
        n = f.lower().replace(".html", "")
        if should_exclude_name(f):
            continue
        if any(x in n for x in anim_keywords):
            fp = os.path.join(path, f)
            results.append((f, fp))
    return results

def scan_hyperui(path):
    """HyperUI - static Tailwind, only progress/timeline have visual movement."""
    results = []
    for f in os.listdir(path):
        if not f.endswith(".html"):
            continue
        n = f.lower()
        if "progress" in n or "timeline" in n:
            fp = os.path.join(path, f)
            results.append((f, fp))
    return results

def scan_seraui(path):
    """SeraUI - filter src-app-docs files for animation effects only."""
    results = []
    for f in os.listdir(path):
        if not f.endswith(".tsx"):
            continue
        n = f.lower()
        # Only src-app-docs files
        if not n.startswith("src-app-docs-"):
            continue
        if should_exclude_name(f):
            continue
        fp = os.path.join(path, f)
        if has_animation_signals(fp):
            results.append((f, fp))
    return results

def scan_ogblocks(path):
    """OGBlocks - small set."""
    results = []
    for f in os.listdir(path):
        if not f.endswith(".tsx"):
            continue
        if should_exclude_name(f):
            continue
        fp = os.path.join(path, f)
        if has_animation_signals(fp):
            results.append((f, fp))
    return results

def scan_ag(path):
    """AG skills - scan for TSX with animation."""
    results = []
    for root, dirs, files in os.walk(path):
        for f in files:
            if not (f.endswith(".tsx") or f.endswith(".jsx")):
                continue
            if should_exclude_name(f):
                continue
            fp = os.path.join(root, f)
            if has_animation_signals(fp):
                results.append((f, fp))
    return results

def main():
    # First, restore the original manifest from git
    os.system(f'cd "{BASE}" && git checkout manifest.json')
    
    # Re-load existing max from the restored manifest
    manifest = json.load(open(os.path.join(BASE, "manifest.json")))
    existing_max = {}
    for k in manifest:
        cat = k.rsplit(" ", 1)[0]
        num = manifest[k]["num"]
        if cat not in existing_max or num > existing_max[cat]:
            existing_max[cat] = num
    
    # Add new categories
    existing_max["Buttons"] = 0
    existing_max["Cinematic Intros"] = 0
    existing_max["Uncategorized"] = 0
    
    # Restore original HTML files from git
    os.system(f'cd "{BASE}" && git checkout *.html')
    
    # ── Scan all libraries ──
    all_components = []
    
    print("Scanning Aceternity...")
    for f, fp in scan_aceternity(os.path.join(LIB_BASE, "aceternity-components")):
        all_components.append((prettify_name(f), fp, categorize(f)))
    
    print("Scanning MagicUI...")
    for f, fp in scan_magicui(os.path.join(LIB_BASE, "magicui-components")):
        all_components.append((prettify_name(f), fp, categorize(f)))
    
    print("Scanning CultUI...")
    for f, fp in scan_cultui(os.path.join(LIB_BASE, "cultui-components")):
        all_components.append((prettify_name(f), fp, categorize(f)))
    
    print("Scanning SmoothUI...")
    for f, fp in scan_smoothui(os.path.join(LIB_BASE, "smoothui-components")):
        all_components.append((prettify_name(f), fp, categorize(f)))
    
    print("Scanning HyperUI...")
    for f, fp in scan_hyperui(os.path.join(LIB_BASE, "hyperui-components")):
        all_components.append((prettify_name(f), fp, categorize(f)))
    
    print("Scanning OriginUI...")
    for f, fp in scan_originui(os.path.join(LIB_BASE, "originui-components")):
        all_components.append((prettify_name(f), fp, categorize(f)))
    
    print("Scanning DaisyUI...")
    for f, fp in scan_daisyui(os.path.join(LIB_BASE, "daisyui-components")):
        all_components.append((prettify_name(f), fp, categorize(f)))
    
    print("Scanning SeraUI...")
    for f, fp in scan_seraui(os.path.join(LIB_BASE, "seraui-components")):
        all_components.append((prettify_name(f), fp, categorize(f)))
    
    print("Scanning OGBlocks...")
    for f, fp in scan_ogblocks(os.path.join(LIB_BASE, "ogblocks-components")):
        all_components.append((prettify_name(f), fp, categorize(f)))
    
    print("Scanning AG...")
    for f, fp in scan_ag(AG_BASE):
        all_components.append((prettify_name(f), fp, categorize(f)))
    
    # ── Deduplicate by name (case-insensitive) ──
    seen_names = set()
    deduped = []
    for name, fp, cat in all_components:
        key = name.lower()
        if key not in seen_names:
            seen_names.add(key)
            deduped.append((name, fp, cat))
    all_components = deduped
    
    print(f"\nTotal filtered components: {len(all_components)}")
    
    cat_counts = {}
    for name, fp, cat in all_components:
        cat_counts[cat] = cat_counts.get(cat, 0) + 1
    for cat, count in sorted(cat_counts.items()):
        print(f"  {cat}: {count}")
    
    # ── Build manifest entries ──
    new_entries = {cat: [] for cat in CAT_FILES}
    
    for name, fp, cat in all_components:
        existing_max[cat] += 1
        num = existing_max[cat]
        prefix = CAT_PREFIX.get(cat, "uncat")
        key = f"{cat} #{num:02d}"
        
        manifest[key] = {
            "name": name,
            "prefix": prefix,
            "num": num,
            "local_code": fp,
        }
        new_entries[cat].append((num, name, fp))
    
    # ── Save manifest ──
    with open(os.path.join(BASE, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    print(f"\nManifest saved: {len(manifest)} total entries")
    
    # ── HTML generation ──
    HEADER_NAV = """<div class="header"><div class="container">
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
<a href="buttons.html">Buttons</a>
<a href="cinematic-intros.html">Intros</a>
<a href="uncategorized.html">Uncategorized</a>
</nav>
</div></div>"""
    
    CSS_BLOCK = """:root { --bg:#0B0F19; --accent:#0066FF; --card:#131722; --border:#1e2530; --text:#e2e8f0; --muted:#64748b; }
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
.card-video-wrap{position:relative;aspect-ratio:16/9;background:linear-gradient(135deg,#0f172a,#1e2530);overflow:hidden;display:flex;align-items:center;justify-content:center}
.card-preview-placeholder{color:var(--muted);font-size:12px;text-align:center;padding:20px}
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
@media(max-width:640px){.grid{grid-template-columns:1fr}.cat-grid{grid-template-columns:1fr}.hero h2{font-size:32px}.header .nav{display:none}}"""
    
    def make_card(cat_name, num, name):
        card_label = f"{cat_name.split()[0]}"
        if cat_name == "3D Animation":
            card_label = "3D"
        elif cat_name == "Webgl & ThreeJS Effects":
            card_label = "WebGL"
        card_num = f"{card_label} #{num:02d}"
        return f"""<div class="card">
<div class="card-video-wrap">
<span class="card-number">{html.escape(card_num)}</span>
<div class="card-preview-placeholder">Preview unavailable</div>
</div>
<div class="card-info"><h3>{html.escape(name)}</h3></div>
</div>"""
    
    def gen_new_category_html(cat_name, items):
        """Generate a new category HTML page."""
        cards = [make_card(cat_name, num, name) for num, name, fp in items]
        total = existing_max[cat_name]
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(cat_name)} - Animation Catalog</title>
<style>
{CSS_BLOCK}
</style>
</head>
<body>
{HEADER_NAV}
<div class="container">
<div class="cat-header">
<h2>{html.escape(cat_name)}</h2>
<p>{total} components</p>
</div>
<div class="grid">
{chr(10).join(cards)}
</div>
</div>
<div class="footer"><div class="container">Animation Effects Catalog &middot; {total} components</div></div>
</body>
</html>"""
    
    # ── Generate new category pages ──
    for cat in ["Buttons", "Cinematic Intros", "Uncategorized"]:
        items = new_entries[cat]
        html_path = os.path.join(BASE, CAT_FILES[cat])
        content = gen_new_category_html(cat, items)
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Created {CAT_FILES[cat]} with {len(items)} items (total: {existing_max[cat]})")
    
    # ── Update existing category pages (append new items) ──
    for cat, filename in CAT_FILES.items():
        if cat in ["Buttons", "Cinematic Intros", "Uncategorized"]:
            continue
        items = new_entries.get(cat, [])
        
        html_path = os.path.join(BASE, filename)
        with open(html_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Add new nav links if missing
        if 'buttons.html' not in content:
            content = content.replace(
                '<a href="3d-animation.html">3D</a>\r\n</nav>',
                '<a href="3d-animation.html">3D</a>\r\n<a href="buttons.html">Buttons</a>\r\n<a href="cinematic-intros.html">Intros</a>\r\n<a href="uncategorized.html">Uncategorized</a>\r\n</nav>'
            )
            # Also try \n variant
            content = content.replace(
                '<a href="3d-animation.html">3D</a>\n</nav>',
                '<a href="3d-animation.html">3D</a>\n<a href="buttons.html">Buttons</a>\n<a href="cinematic-intros.html">Intros</a>\n<a href="uncategorized.html">Uncategorized</a>\n</nav>'
            )
        
        if not items:
            # Still save the updated nav
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(content)
            continue
        
        # Generate new cards
        new_cards = [make_card(cat, num, name) for num, name, fp in items]
        cards_text = "\r\n".join(new_cards)
        
        # Insert before the closing grid div + footer
        # Pattern: </div>\r\n</div>\r\n<div class="footer">
        inserted = False
        for pattern, replacement in [
            ("</div>\r\n</div>\r\n<div class=\"footer\">", f"{cards_text}\r\n</div>\r\n</div>\r\n<div class=\"footer\">"),
            ("</div>\n</div>\n<div class=\"footer\">", f"{cards_text}\n</div>\n</div>\n<div class=\"footer\">"),
        ]:
            if pattern in content:
                content = content.replace(pattern, replacement)
                inserted = True
                break
        
        if not inserted:
            print(f"WARNING: Could not find insertion point in {filename}")
            continue
        
        # Update count in header
        total = existing_max[cat]
        content = re.sub(
            r'(<div class="cat-header">[^<]*<h2>[^<]+</h2>\s*<p>)(\d+)(\s*components</p>)',
            lambda m: f"{m.group(1)}{total}{m.group(3)}",
            content,
            count=1
        )
        
        # Update footer
        content = re.sub(
            r'(Animation Effects Catalog &middot; )(\d+)(\s*components)',
            lambda m: f"{m.group(1)}{total}{m.group(3)}",
            content
        )
        
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Updated {filename} with {len(items)} new items (total: {total})")
    
    # ── Update index.html ──
    index_path = os.path.join(BASE, "index.html")
    with open(index_path, "r", encoding="utf-8") as f:
        index_content = f.read()
    
    # Add new nav links
    if 'buttons.html' not in index_content:
        index_content = index_content.replace(
            '<a href="3d-animation.html">3D</a>\r\n</nav>',
            '<a href="3d-animation.html">3D</a>\r\n<a href="buttons.html">Buttons</a>\r\n<a href="cinematic-intros.html">Intros</a>\r\n<a href="uncategorized.html">Uncategorized</a>\r\n</nav>'
        )
        index_content = index_content.replace(
            '<a href="3d-animation.html">3D</a>\n</nav>',
            '<a href="3d-animation.html">3D</a>\n<a href="buttons.html">Buttons</a>\n<a href="cinematic-intros.html">Intros</a>\n<a href="uncategorized.html">Uncategorized</a>\n</nav>'
        )
    
    # Add new category cards before closing </div> of cat-grid
    new_cat_cards = []
    for cat in ["Buttons", "Cinematic Intros", "Uncategorized"]:
        total = existing_max[cat]
        filename = CAT_FILES[cat]
        desc = f"Browse {cat.lower()} effects"
        new_cat_cards.append(f"""<a class="cat-card" href="{filename}">
<h3>{cat}</h3>
<div class="count">{total} components</div>
<div class="desc">{desc}</div>
</a>""")
    
    new_cards_text = "\r\n".join(new_cat_cards)
    
    # Insert before </div></div><div class="footer">
    inserted = False
    for pattern, replacement in [
        ("</div>\r\n</div>\r\n<div class=\"footer\">", f"{new_cards_text}\r\n</div>\r\n</div>\r\n<div class=\"footer\">"),
        ("</div>\n</div>\n<div class=\"footer\">", f"{new_cards_text}\n</div>\n</div>\n<div class=\"footer\">"),
    ]:
        if pattern in index_content:
            index_content = index_content.replace(pattern, replacement)
            inserted = True
            break
    
    if not inserted:
        print("WARNING: Could not update index.html category cards")
    
    # Update total count in hero text
    total_all = len(manifest)
    index_content = re.sub(r'\d+\s*hand-crafted\s*animation\s*components', f'{total_all} hand-crafted animation components', index_content)
    
    # Update footer count
    index_content = re.sub(
        r'(Animation Effects Catalog &middot; )(\d+)(\s*components\s*across\s*)(\d+)(\s*categories)',
        lambda m: f"{m.group(1)}{total_all}{m.group(3)}17{m.group(5)}",
        index_content
    )
    
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(index_content)
    print(f"Updated index.html (total: {total_all} components, 17 categories)")
    
    # ── Print summary ──
    print(f"\n{'='*60}")
    print(f"BUILD COMPLETE")
    print(f"Total components in catalog: {len(manifest)}")
    print(f"New components added: {len(all_components)}")
    print(f"Categories: 17 (14 existing + 3 new)")
    for cat in sorted(CAT_FILES.keys()):
        print(f"  {cat}: {existing_max[cat]}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()