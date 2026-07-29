#!/usr/bin/env python3
"""
Build the expanded AnimMasterLib catalog.
Scans component library folders, filters for animated/visual effects,
categorizes them, generates HTML pages + manifest.json.
"""
import os, re, json, html

BASE = r"C:\Users\info\Dropbox\Projects\component-catalog"
LIB_BASE = r"C:\Users\info\AppData\Local\hermes\skills\design\ui-component-libraries"
AG_BASE = r"C:\Users\info\Dropbox\Google Drive\Software\AG_Backup\2\.agents\skills"

# ── Existing category max numbers (from current manifest) ──
existing_max = {
    "Scroll Animation": 66,  # 65 entries but last is #66 (there was a gap)
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
}

# Let me re-check the actual max numbers
def get_real_max():
    m = json.load(open(os.path.join(BASE, "manifest.json")))
    for k in list(m.keys()):
        cat = k.rsplit(" ", 1)[0]
        num = m[k]["num"]
        if cat not in existing_max or num > existing_max[cat]:
            existing_max[cat] = num

get_real_max()

# ── Category file mappings ──
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

# ── Exclude patterns (static / non-animation) ──
EXCLUDE_KEYWORDS = [
    # Static form elements
    "input", "checkbox", "radio", "select", "toggle", "switch", "label", "field",
    "textarea", "form", "combobox", "autocomplete", "datepicker", "date-picker",
    # Static layout
    "separator", "aspect-ratio", "resizable", "skeleton", "spinner", "table",
    "scroll-area", "collapsible", "accordion",
    # Infrastructure
    "analytics", "seo", "theme", "performance", "monitor",
    # App examples
    "apps-examples", "calcom",
    # Docs/config
    "install", "registry", "mdx", "index.md", "catalog.json",
    # Icons
    "icon", "logo",
    # Auth
    "auth", "login", "sign-in", "signup",
    # Static display
    "badge", "avatar", "breadcrumb", "pagination", "alert", "tooltip",
    "dropdown", "command", "menu", "popover", "sheet", "modal", "dialog",
    "drawer", "toast", "sonner", "callout", "calendar", "code-block",
    "code-block", "snippet", "terminal", "clipboard",
    # Static buttons (not animated)
    "stateful-button", "tailwindcss-buttons",
]

# More specific excludes (substring match)
EXCLUDE_SUBSTRINGS = [
    "apps-examples-calcom",
    "apps-examples-",
    "authentication-",
    "auth-",
    "seo-",
    "analytics",
    "performance-",
    "theme-",
    "theme.",
    "theme_",
    "install",
    "registry",
    "mdx",
    "index.md",
    "catalog.json",
    "icon",
    "logo",
    "-icons-",
    "_icons_",
    "-icon-",
    "_icon_",
    "input",
    "checkbox",
    "radio-group",
    "radio.",
    "select",
    "toggle",
    "switch",
    "label",
    "textarea",
    "combobox",
    "autocomplete",
    "datepicker",
    "date-picker",
    "aspect-ratio",
    "resizable",
    "skeleton",
    "spinner",
    "separator",
    "scroll-area",
    "collapsible",
    "accordion",
    "calendar",
    "data-table",
    "chart-",
    "command",
    "dropdown",
    "popover",
    "sheet",
    "modal",
    "dialog",
    "drawer",
    "toast",
    "sonner",
    "callout",
    "badge",
    "avatar",
    "breadcrumb",
    "pagination",
    "alert",
    "tooltip",
    "menu",
    "code-block",
    "snippet",
    "terminal",
    "clipboard",
    "copy-button",
    "block-copy",
    "block-display",
    "block-preview",
    "block-wrapper",
    "block-toolbar",
    "block-chunk",
    "blocks-grid",
    "cli-install",
    "cli-registry",
    "providers",
    "schema-display",
    "stack-trace",
    "test-results",
    "transcription",
    "voice-selector",
    "social-cards",
    "social-selector",
    "sources",
    "queue",
    "plan",
    "poll-widget",
    "vote-tally",
    "choice-poll",
    "sortable-list",
    "web-preview",
    "youtube-video-player",
    "audio-player",
    "video-player",
    "prompt-input",
    "prompt-library",
    "artifact",
    "sandbox",
    "reasoning",
    "chain-of-thought",
    "suggestion",
    "checkpoint",
    "task",
    "tool",
    "toolbar",
    "timer",
    "toc",
    "style-switcher",
    "style-wrapper",
    "style-",
    "tailwind-indicator",
    "site-footer",
    "site-header",
    "sidebar-nav",
    "side-panel",
    "sidebar",
    "cookie",
    "newsletter",
    "promo-video",
    "youtube",
    "google-drive",
    "google-gemini",
    "github-profile",
    "file-upload",
    "attachments",
    "speech-input",
    "audio-",
    "video-",
    "mockup-",
    "mask",
    "stack",
    "stat",
    "steps",
    "tab",
    "join",
    "kbd",
    "indicator",
    "filter",
    "fieldset",
    "diff",
    "divider",
    "footer",
    "hero-sections",  # this is a demo page, not an effect
    "features-section",
    "feature.tsx",
    "feature-view",
    "layout.",
    "layout-",
    "not-found",
    "404",
    "coming-soon",
    "empty",
    "error",
    "loading-page",
    "page.tsx",
    "page-content",
    "page-client",
    "layout-content",
    "docs-layout",
    "component-template",
    "component-renderer",
    "component-seo",
    "componentseo",
    "docs-",
    "package-manager",
    "search-modal",
    "table-of-contents",
    "props-table",
    "mdx-table",
    "vitepress",
    "optimized-image",
    "dynamic-loader",
    "hide-toc",
    "tabs.tsx",
    "doctabs",
    "context-menu",
    "context-",
    "scroll-area",
    "slider.tsx",  # static slider (form element)
    "range",
    "rating",
    "progress",  # static progress bar
    "card.tsx",   # static card
    "card-view",
    "card-content",
    "button-group",
    "button.tsx",  # static button
    "button-view",
    "button-copy",
    "button-action",
    "button-commerce",
    "button-icons",
    "button-only",
    "button-others",
    "button-righticon",
    "button-social",
    "social-button",
    "ai-button",
    "copybutton",
    "app-toggle",
    "app-download",
    "apple-invites",
    "job-listing",
    "product-card",
    "product-catalog",
    "tweet",
    "tweet-grid",
    "waitlist",
    "verify-badge",
    "verify-profile",
    "amazongift",
    "codeprofile",
    "colorpalette",
    "announcement",
    "news",
    "blog",
    "pricing",
    "ecommerce",
    "album",
    "cookie",
    "cta",
    "modal",
    "faq",
    "section",
    "feature",
    "banner",
    "cart",
    "stat",
    "empty-content",
    "footer",
    "header",
    "sidebar",
    "navbar",
    "nav.tsx",
    "nav-view",
    "nav-",
    "breadcrumb",
    "timeline",  # keep timeline? Let's include animated timelines
    "countdown",
    "mockup",
    "diff",
    "chat",
    "swap",
    "fab",
    "dock",  # keep animated docks
    "carousel",  # keep animated carousels
    "slider",
    "gallery",
    "form",
    "label",
    "field",
    "alert",
    "widget",
    "command",
    "menu",
    "popover",
    "sheet",
    "dialog",
    "toast",
    "callout",
    "calendar",
    "table",
    "card-grid",
    "grid.tsx",
    "grid-view",
    "combo-box",
    "combobox",
    "number-flow",  # maybe include?
    "price-flow",
    "number-ticker",
    "number-ticker",
    "animated-number",
    "prompt",
    "ai-",
    "agent",
    "speech",
    "voice",
    "text-gif",
    "text-gif",
    "two-tone-text",
    "type-animate",
    "pixel-heading",
    "pixel-paragraph",
    "text-animate",
    "text-animate-demo",
    "typewriter",
    "typewriter-demo",
    "typewriter-text",
    "text-reveal",
    "text-reveal-card",
    "shimmer",
    "shimmer-text",
    "shimmer-button",
    "animated-shiny-text",
    "flip-words",
    "text-flip",
    "text-flip-board",
    "text-flipping-board",
    "text-generate-effect",
    "text-hover-effect",
    "squiggly-text",
    "encrypted-text",
    "colourful-text",
    "aurora-text",
    "blur-fade",
    "border-beam",
    "border-beam-button",
    "shine-border",
    "shine-border",
    "magic-card",
    "magic-card",
    "flickering-grid",
    "grid-pattern",
    "dot-pattern",
    "dots-background",
    "dotted-glow-background",
    "dot-background",
    "bg-animate",
    "bg-animated",
    "bg-image",
    "bg-media",
    "background-guides",
    "background-texture",
    "stripe-bg",
    "shader-lens",
    "shader-lens-blur",
    "texture-button",
    "texture-card",
    "texture-overlay",
    "texture-wrapper",
    "svg-bands",
    "svg-shapes",
    "svg-shapes-animated",
    "svg-shapes-demo",
    "squiggle-arrow",
    "plug-grid",
    "shift-card",
    "shift-card-demo",
    "shimmer.tsx",
    "shimmer-demo",
    "sonner",
    "site-",
    "src-components-",
    "src-contexts-",
    "src-mdx",
    "src-assets-",
    "src-app-standalone",
    "src-app-not-found",
    "src-app-docs-",
    "src-app-layout",
    "src-app-(landing)",
    "src-components-site-",
    "src-components-ui-",
    "src-components-core-",
    "src-components-performance-",
    "src-components-seo-",
    "src-components-analytics-",
    "block-",
    "cli-",
    "docs-",
    "toast",
    "sonner",
    "sonner-",
]

def should_exclude(filename):
    """Check if a file should be excluded based on its name."""
    name = filename.lower().replace("_", "-").replace(".tsx", "").replace(".jsx", "").replace(".html", "")
    
    # Quick excludes
    if name in ["index", "index.md", "catalog.json", "readme", "readme.md"]:
        return True
    if name.startswith("comp-"):
        return True  # OriginUI generic numbered files - skip all
    if name.startswith("apps-examples"):
        return True
    if name.startswith("authentication"):
        return True
    if name.startswith("src-components-site") or name.startswith("src-components-ui") or name.startswith("src-components-core") or name.startswith("src-components-performance") or name.startswith("src-components-seo") or name.startswith("src-components-analytics"):
        return True
    if name.startswith("src-contexts") or name.startswith("src-mdx") or name.startswith("src-assets"):
        return True
    if name.startswith("src-app-standalone") or name.startswith("src-app-not-found") or name.startswith("src-app-layout"):
        return True
    if name.startswith("block-") or name.startswith("cli-") or name.startswith("docs-"):
        return True
    if name.startswith("src-app-docs-"):
        # SeraUI docs - need to check these more carefully
        return False  # Don't exclude, we'll check these
    if name.startswith("src-app-(landing)"):
        return True
    
    return False

def has_animation_signals(filepath):
    """Check if a file contains animation/visual effect signals."""
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read(8000).lower()
    except:
        return False
    
    # Animation signal keywords
    signals = [
        "framer-motion", "motion.", "animate", "animation", "transition",
        "transform", "keyframes", "@keyframes", "translateY", "translateX",
        "scale(", "rotate(", "opacity", "fade", "slide", "bounce",
        "spring", "useanimation", "usemotion", "variants",
        "whilehover", "whiletap", "whileinview", "whilefocus",
        "glow", "shimmer", "ripple", "particle", "meteor", "beam",
        "aurora", "sparkle", "vortex", "orbit", "marquee", "dock",
        "tilt", "spotlight", "parallax", "glitch", "noise",
        "gradient", "glow", "pulse", "pulsat", "wave", "ripple",
        "three.js", "threejs", "webgl", "canvas", "shader",
        "requestanimationframe", "useeffect", "intersectingobserver",
        "intersection", "scroll", "reveal", "flip", "typewriter",
        "scramble", "decrypt", "morph", "liquid", "glass",
        "distort", "dither", "fuzzy", "sparkles", "shooting",
        "stars", "moving", "infinite", "carousel", "swiper",
        "3d", "perspective", "rotate3d", "transform3d",
        "hover-effect", "hover-card", "card-hover", "hover-border",
        "magnetic", "floating", "wobble", "wavy", "squiggly",
        "animated", "motion", "kinetic", "dynamic",
        "glare", "lens", "container-scroll", "container-text",
        "evervault", "comet", "notch", "scales", "apple-cards",
        "flip-words", "text-flip", "colourful", "rainbow",
        "border-gradient", "hover-border", "pointer-highlight",
        "sticky-scroll", "sticky-banner", "tracing-beam",
        "moving-line", "multi-step", "loader", "loading",
        "grid-and-dot", "grid-background", "dots-background",
        "noise-background", "stars-background", "vortex-background",
        "wavy-background", "aurora-background", "background-beams",
        "background-boxes", "background-gradient", "background-lines",
        "background-ripple", "dot-pattern", "grid-pattern",
        "flickering-grid", "dither-shader", "pixelated-canvas",
        "webcam-pixel", "canvas-reveal", "canvas-text",
        "evervault-card", "comet-card", "glare-card",
        "glowing-stars", "glowing-button", "glowing-effect",
        "glowing-background", "shooting-stars",
        "apple", "macbook-scroll", "world-map", "globe",
        "3d-card", "3d-globe", "3d-marquee", "3d-pin",
        "bento-grid", "layout-grid", "focus-cards", "expandable-cards",
        "card-spotlight", "card-stack", "card-hover",
        "direction-aware", "following-pointer", "magnetic-button",
        "pulsating-button", "pulsating-dot", "rainbow-button",
        "shimmer-button", "hover-border-gradient",
        "floating-dock", "floating-navbar", "resizable-navbar",
        "navbar-menu", "link-preview", "images-badge",
        "images-slider", "infinite-moving", "tooltip-card",
        "animated-modal", "animated-shiny", "animated-testimonials",
        "animated-tooltip", "apple-cards-carousel",
        "ascii-art", "aurora-text", "background-beams",
        "canvas-reveal", "colourful-text", "container-scroll",
        "container-text-flip", "cover", "dither",
        "evervault-card", "flip-words", "following-pointer",
        "glowing-button", "google-gemini", "gooey",
        "hero-highlight", "hero-parallax", "lamp",
        "layout-text-flip", "lens", "macbook-scroll",
        "magnetic-button", "meteors", "moving-line",
        "multi-step-loader", "navbar-menu", "notch",
        "parallax-hero", "parallax-scroll", "pixelated-canvas",
        "pointer-highlight", "pulsating", "rainbow-button",
        "resizable-navbar", "shimmer-button", "shimmer-text",
        "shooting-stars", "sidebar", "sparkles", "spotlight",
        "squiggly-text", "sticky-banner", "sticky-scroll",
        "svg-mask", "tailwindcss", "text-flip", "text-generate",
        "text-hover", "text-reveal", "three-element", "timeline",
        "tracing-beam", "typewriter", "vortex", "wavy-background",
        "wobble-card", "world-map", "glare-card",
        "gooey-popover", "figma-comment", "scroll-reveal",
        "scrollable-card-stack", "scramble-hover", "reveal-text",
        "wave-text", "siri-orb", "power-off-slide", "exposure-slider",
        "dynamic-island", "magnetic-button", "smooth-button",
        "dot-morph-button", "clip-corners-button", "glow-hover-card",
        "grid-loader", "skeleton-loader", "animated-avatar",
        "animated-file", "animated-input", "animated-o-t-p",
        "animated-progress", "animated-stepper", "animated-tabs",
        "animated-tags", "animated-toggle", "animated-tooltip",
        "app-download-stack", "apple-invites", "basic-accordion",
        "basic-dropdown", "basic-modal", "basic-toast",
        "book", "breadcrumb", "button-copy", "clip-corners",
        "combobox", "context-menu", "contribution-graph",
        "cursor-follow", "dialog", "dot-morph", "drawer",
        "dropdown-menu", "dynamic-island", "expandable-cards",
        "exposure-slider", "figma-comment", "form", "github-stars",
        "glow-hover", "gooey-popover", "grid-loader", "image-metadata",
        "infinite-slider", "interactive-image", "job-listing",
        "magnetic-button", "notification-badge", "number-flow",
        "pagination", "phototab", "power-off-slide", "price-flow",
        "product-card", "radio-group", "reveal-text", "reviews-carousel",
        "rich-popover", "scramble-hover", "scrollable-card",
        "scroll-reveal", "scrubber", "searchable-dropdown",
        "select", "siri-orb", "skeleton-loader", "smooth-button",
        "social-selector", "switchboard-card", "tweet-card",
        "typewriter-text", "user-account-avatar", "wave-text",
        "bg-animate", "border-beam", "animated-number",
        "canvas-fractal", "shift-card", "shimmer.tsx",
        "svg-shapes-animated", "terminal-animation", "text-animate",
        "texture", "three-d-carousel", "typewriter",
        "vote-tally", "youtube-video-player",
        "aurora", "bento", "blur-fade", "border-beam",
        "dock", "flickering", "globe", "magic-card",
        "marquee", "meteors", "number-ticker", "particles",
        "pulsating", "ripple", "shimmer-button", "shine-border",
        "text-animate", "text-reveal",
        "3d-carousel", "animated-badge", "aurora",
        "curved-text", "decrypting", "dock-colorful", "dock-floating",
        "dock-minimal", "dock-simple", "enhanced-carousel",
        "imagecarousel", "scroll-progress", "ticker",
        "video-gallery", "video-text", "wavy", "typewriter",
        "animated-testimonial", "animated-tooltip", "apple-cards",
        "canvas-reveal", "card-hover", "card-spotlight", "card-stack",
        "comet-card", "container-scroll", "direction-aware",
        "draggable-card", "evervault-card", "expandable-cards",
        "floating-dock", "floating-navbar", "focus-cards",
        "following-pointer", "glare-card", "glowing-button",
        "glowing-stars", "hero-highlight", "hero-parallax",
        "images-slider", "infinite-moving", "lamp",
        "layout-grid", "lens", "link-preview", "macbook-scroll",
        "magnetic-button", "moving-line", "multi-step-loader",
        "navbar-menu", "notch", "parallax-hero", "parallax-scroll",
        "pixelated-canvas", "pointer-highlight", "pulsating",
        "rainbow-button", "resizable-navbar", "shimmer-button",
        "shimmer-text", "shooting-stars", "sparkles", "spotlight",
        "squiggly-text", "sticky-banner", "sticky-scroll",
        "svg-mask", "text-flip", "text-generate", "text-hover",
        "text-reveal", "three-element", "tracing-beam", "typewriter",
        "vortex", "wavy-background", "wobble-card", "world-map",
    ]
    
    return any(s in content for s in signals)

def categorize(name, content=""):
    """Categorize a component based on its name and content."""
    n = name.lower().replace("_", "-")
    
    # ── Buttons ──
    if any(x in n for x in ["button", "magnetic-button", "shimmer-button", "pulsating-button",
                            "rainbow-button", "glowing-button", "smooth-button", "dot-morph-button",
                            "clip-corners-button", "bg-animate-button", "border-beam-button",
                            "texture-button", "tailwindcss-button", "hover-border-gradient"]):
        return "Buttons"
    
    # ── Cinematic Intros ──
    if any(x in n for x in ["loader", "preloader", "splash", "intro", "cinematic",
                            "multi-step-loader", "grid-loader", "skeleton-loader",
                            "loading", "lottie"]):
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
                            "dither-shader", "aurora", "wavy", "meteors",
                            "shooting-stars", "glowing-stars", "sparkles",
                            "particles", "ripple", "vortex", "beam",
                            "border-beam", "shine-border", "grid-pattern",
                            "dot-pattern", "glowing-background"]):
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
                            "flip-words", "text-clip", "text-demo",
                            "moving-line", "squiggle-arrow"]):
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
                            "perspective", "rotate3d"]):
        return "3D Animation"
    
    # ── WebGL & ThreeJS Effects ──
    if any(x in n for x in ["webgl", "threejs", "three.js", "canvas-reveal",
                            "canvas-reveal-effect", "canvas-fractal",
                            "canvas-text", "shader", "pixelated",
                            "glitch", "noise", "fuzzy", "liquid",
                            "distort", "dither"]):
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
                            "spotlight", "spotlight-new", "hero-sections",
                            "apple-cards-carousel", "hero-parallax",
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
                            "sidebar", "menu", "navigation",
                            "link-preview", "breadcrumb",
                            "tabs", "doctabs", "animated-tabs",
                            "tab.tsx", "swap", "join",
                            "fab", "dock-colorful", "dock-floating",
                            "dock-minimal", "dock-simple"]):
        return "Navigation Menus"
    
    # ── Hover Effects ──
    if any(x in n for x in ["hover", "card-hover", "card-spotlight",
                            "card-hover-effect", "direction-aware",
                            "hover-card", "hover-3d", "hover-gallery",
                            "glow-hover", "gooey-popover",
                            "shift-card", "wobble-card",
                            "tooltip-card", "images-badge",
                            "bento-grid", "layout-grid",
                            "expandable-cards", "focus-cards",
                            "magic-card", "texture-card",
                            "glare-card", "tooltip",
                            "link-preview", "following-pointer",
                            "magnetic", "magnetic-button"]):
        return "Hover Effects"
    
    # ── Mouse Effects ──
    if any(x in n for x in ["mouse", "cursor-follow", "following-pointer",
                            "pointer", "magnetic", "spotlight",
                            "parallax", "tilt", "drag",
                            "draggable"]):
        return "Mouse Effects"
    
    # ── SVG Animations ──
    if any(x in n for x in ["svg", "svg-mask", "svg-bands", "svg-shapes",
                            "svg-shapes-animated", "svg-shapes-demo",
                            "world-map", "mask"]):
        return "SVG Animations"
    
    # ── Grid Animations ──
    if any(x in n for x in ["grid", "bento-grid", "layout-grid",
                            "blocks-grid", "plug-grid",
                            "grid-pattern", "dot-pattern",
                            "contribution-graph", "grid-loader"]):
        return "Grid Animations"
    
    # ── Page Transitions ──
    if any(x in n for x in ["transition", "page-transition",
                            "animated-modal", "modal",
                            "blur-fade", "fade",
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
    
    return "Uncategorized"

def prettify_name(filename):
    """Convert filename to a nice display name."""
    name = filename.replace(".tsx", "").replace(".jsx", "").replace(".html", "")
    name = name.replace("_", " ").replace("-", " ")
    # Handle SeraUI's long prefix
    name = re.sub(r'^src app docs ', '', name)
    name = re.sub(r'^src app ', '', name)
    # Title case
    words = name.split()
    result = []
    for w in words:
        if w.lower() in ["3d", "ui", "otp", "ai", "svg", "css", "api"]:
            result.append(w.upper())
        else:
            result.append(w.capitalize())
    return " ".join(result)

def scan_library(lib_path, lib_name):
    """Scan a library folder and return list of (name, filepath) for included components."""
    results = []
    if not os.path.exists(lib_path):
        return results
    
    for f in os.listdir(lib_path):
        if not (f.endswith(".tsx") or f.endswith(".jsx") or f.endswith(".html")):
            continue
        if f.endswith(".md") or f.endswith(".json"):
            continue
        
        # Exclude based on filename
        if should_exclude(f):
            continue
        
        filepath = os.path.join(lib_path, f)
        
        # For TSX files, check content for animation signals
        if f.endswith(".tsx") or f.endswith(".jsx"):
            if not has_animation_signals(filepath):
                continue
        
        results.append((f, filepath))
    
    return results

def scan_seruai(seraui_path):
    """Special scanner for SeraUI - filter src-app-docs files."""
    results = []
    if not os.path.exists(seraui_path):
        return results
    
    for f in os.listdir(seraui_path):
        if not f.endswith(".tsx"):
            continue
        if should_exclude(f):
            continue
        
        # Only include src-app-docs files that have animation
        n = f.lower()
        if not n.startswith("src-app-docs-"):
            continue
        
        filepath = os.path.join(seraui_path, f)
        if not has_animation_signals(filepath):
            continue
        
        # Extra filtering: exclude static form elements
        if any(x in n for x in ["accordion", "alert", "badge", "breadcrumb", "button-view",
                                 "combo-box", "combobox", "copybutton", "divider", "drawer",
                                 "dropdown", "input", "label", "menu", "pagination", "popover",
                                 "radio", "select", "sheet", "sidebar", "switch", "table",
                                 "toast", "toggle", "tooltip", "tabs", "doctabs",
                                 "waitlist", "verify", "empty", "error",
                                 "codeprofile", "colorpalette", "amazongift",
                                 "announcement", "news", "blog", "pricing",
                                 "video-player", "audio-player",
                                 "modal", "dialog", "form", "field",
                                 "command", "context", "scroll-area",
                                 "calendar", "data-table", "chart",
                                 "skeleton", "spinner", "separator",
                                 "aspect-ratio", "resizable", "collapsible",
                                 "checkbox", "textarea", "avatar", "stat",
                                 "steps", "countdown", "timeline", "progress",
                                 "callout", "alert-dialog", "alert.",
                                 "sonner", "snackbar", "cookie",
                                 "card-view", "card-content", "card.tsx",
                                 "hero-view", "hero-content", "hero.tsx",
                                 "feature-view", "feature-content",
                                 "footer", "header", "navbar",
                                 "code-block", "snippet", "terminal",
                                 "clipboard", "code-renderer", "component-renderer",
                                 "component-template", "docs-layout", "layout-content",
                                 "package-manager", "search-modal", "table-of-contents",
                                 "props-table", "mdx-table", "vitepress",
                                 "optimized-image", "dynamic-loader", "hide-toc",
                                 "tab.tsx", "tabs.tsx",
                                 "social-button", "ai-button", "button-action",
                                 "button-commerce", "button-icons", "button-only",
                                 "button-others", "button-righticon", "button-social",
                                 "button-group", "button.tsx",
                                 "text-input", "text-area",
                                 "app-download", "apple-invites",
                                 "job-listing", "product-card",
                                 "tweet", "waitlist", "verify",
                                 "codeprofile", "colorpalette", "amazongift",
                                 "empty-content", "empty-page", "empty-",
                                 "error-page", "error-",
                                 "loading-page", "loading-",
                                 "page-content", "page-client",
                                 "not-found", "404",
                                 "coming-soon", "faq",
                                 "cta", "banner", "cart",
                                 "album", "mockup",
                                 "diff", "chat", "swap",
                                 "fab", "dock", "indicator",
                                 "filter", "fieldset", "kbd",
                                 "mask", "stack", "stat",
                                 "join", "rating", "range",
                                 "slider.tsx", "slider-view",
                                 "card-grid", "grid-view",
                                 "nav-view", "nav-content",
                                 "widget", "prompt",
                                 "blog", "news", "section",
                                 "feature.tsx", "feature-view"]):
            continue
        
        results.append((f, filepath))
    
    return results

def scan_daisyui(daisyui_path):
    """Scan DaisyUI HTML files for animation effects."""
    results = []
    if not os.path.exists(daisyui_path):
        return results
    
    anim_keywords = ["animation", "animate", "carousel", "marquee", "countdown", "loading",
                      "progress", "radial", "hover", "dock", "swap", "mockup", "chat",
                      "diff", "timeline", "steps", "stack", "toast", "modal", "collapse"]
    
    for f in os.listdir(daisyui_path):
        if not f.endswith(".html"):
            continue
        
        n = f.lower().replace(".html", "")
        # Exclude static form elements
        if any(x in n for x in ["input", "checkbox", "radio", "select", "toggle",
                                 "file-input", "text-input", "textarea", "label",
                                 "fieldset", "filter", "range", "rating",
                                 "divider", "skeleton", "badge", "avatar",
                                 "breadcrumb", "breadcrumbs", "kbd",
                                 "stat", "table", "indicator",
                                 "join", "mask", "footer",
                                 "navbar", "menu", "tab", "alert",
                                 "pagination", "tooltip", "dropdown",
                                 "drawer", "modal", "button",
                                 "accordion", "collapse"]):
            continue
        
        # Include only animated/visual effects
        if any(x in n for x in ["carousel", "marquee", "countdown", "loading",
                                 "progress", "radial", "hover", "dock",
                                 "swap", "mockup", "chat", "diff",
                                 "timeline", "steps", "stack", "toast"]):
            filepath = os.path.join(daisyui_path, f)
            results.append((f, filepath))
    
    return results

def scan_hyperui(hyperui_path):
    """Scan HyperUI HTML files - these are static Tailwind components, very few are animated."""
    results = []
    if not os.path.exists(hyperui_path):
        return results
    
    for f in os.listdir(hyperui_path):
        if not f.endswith(".html"):
            continue
        
        n = f.lower()
        # HyperUI is mostly static - only include progress bars and timelines (which have visual movement)
        if "progress" in n or "timeline" in n:
            filepath = os.path.join(hyperui_path, f)
            results.append((f, filepath))
    
    return results

def main():
    # ── Scan all libraries ──
    all_components = []  # (display_name, filepath, category)
    
    # Aceternity
    print("Scanning Aceternity...")
    for f, fp in scan_library(
        os.path.join(LIB_BASE, "aceternity-components"), "Aceternity"
    ):
        name = prettify_name(f)
        cat = categorize(f)
        all_components.append((name, fp, cat))
    
    # MagicUI
    print("Scanning MagicUI...")
    for f, fp in scan_library(
        os.path.join(LIB_BASE, "magicui-components"), "MagicUI"
    ):
        name = prettify_name(f)
        cat = categorize(f)
        all_components.append((name, fp, cat))
    
    # CultUI
    print("Scanning CultUI...")
    for f, fp in scan_library(
        os.path.join(LIB_BASE, "cultui-components"), "CultUI"
    ):
        name = prettify_name(f)
        cat = categorize(f)
        all_components.append((name, fp, cat))
    
    # SmoothUI
    print("Scanning SmoothUI...")
    for f, fp in scan_library(
        os.path.join(LIB_BASE, "smoothui-components"), "SmoothUI"
    ):
        name = prettify_name(f)
        cat = categorize(f)
        all_components.append((name, fp, cat))
    
    # HyperUI
    print("Scanning HyperUI...")
    for f, fp in scan_hyperui(os.path.join(LIB_BASE, "hyperui-components")):
        name = prettify_name(f)
        cat = categorize(f)
        all_components.append((name, fp, cat))
    
    # OriginUI
    print("Scanning OriginUI...")
    for f, fp in scan_library(
        os.path.join(LIB_BASE, "originui-components"), "OriginUI"
    ):
        name = prettify_name(f)
        cat = categorize(f)
        all_components.append((name, fp, cat))
    
    # DaisyUI
    print("Scanning DaisyUI...")
    for f, fp in scan_daisyui(os.path.join(LIB_BASE, "daisyui-components")):
        name = prettify_name(f)
        cat = categorize(f)
        all_components.append((name, fp, cat))
    
    # SeraUI
    print("Scanning SeraUI...")
    for f, fp in scan_seruai(os.path.join(LIB_BASE, "seraui-components")):
        name = prettify_name(f)
        cat = categorize(f)
        all_components.append((name, fp, cat))
    
    # OGBlocks
    print("Scanning OGBlocks...")
    for f, fp in scan_library(
        os.path.join(LIB_BASE, "ogblocks-components"), "OGBlocks"
    ):
        name = prettify_name(f)
        cat = categorize(f)
        all_components.append((name, fp, cat))
    
    # AG skills
    print("Scanning AG...")
    for root, dirs, files in os.walk(AG_BASE):
        for f in files:
            if f.endswith(".tsx") or f.endswith(".jsx"):
                if should_exclude(f):
                    continue
                fp = os.path.join(root, f)
                if has_animation_signals(fp):
                    name = prettify_name(f)
                    cat = categorize(f)
                    all_components.append((name, fp, cat))
    
    # ── Deduplicate by name ──
    seen_names = set()
    deduped = []
    for name, fp, cat in all_components:
        key = name.lower()
        if key not in seen_names:
            seen_names.add(key)
            deduped.append((name, fp, cat))
    all_components = deduped
    
    print(f"\nTotal filtered components: {len(all_components)}")
    
    # ── Count per category ──
    cat_counts = {}
    for name, fp, cat in all_components:
        cat_counts[cat] = cat_counts.get(cat, 0) + 1
    for cat, count in sorted(cat_counts.items()):
        print(f"  {cat}: {count}")
    
    # ── Build manifest entries ──
    # Load existing manifest
    manifest_path = os.path.join(BASE, "manifest.json")
    manifest = json.load(open(manifest_path))
    
    # Track new entries per category
    new_entries = {cat: [] for cat in CAT_FILES}
    
    for name, fp, cat in all_components:
        if cat not in existing_max:
            existing_max[cat] = 0
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
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    print(f"\nManifest saved: {len(manifest)} total entries")
    
    # ── Generate HTML for new categories ──
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
    
    def gen_category_html(cat_name, items, prefix):
        """Generate a category HTML page with code-preview cards."""
        cards_html = []
        for num, name, fp in items:
            card_num = f"{cat_name.split()[0]} #{num:02d}"
            cards_html.append(f"""<div class="card">
<div class="card-video-wrap">
<span class="card-number">{html.escape(card_num)}</span>
<div class="card-preview-placeholder">Preview unavailable</div>
</div>
<div class="card-info"><h3>{html.escape(name)}</h3></div>
</div>""")
        
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
{chr(10).join(cards_html)}
</div>
</div>
<div class="footer"><div class="container">Animation Effects Catalog &middot; {total} components</div></div>
</body>
</html>"""
    
    # ── Generate new category pages ──
    for cat in ["Buttons", "Cinematic Intros", "Uncategorized"]:
        items = new_entries[cat]
        if items:
            html_path = os.path.join(BASE, CAT_FILES[cat])
            content = gen_category_html(cat, items, CAT_PREFIX[cat])
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Created {CAT_FILES[cat]} with {len(items)} items")
    
    # ── Update existing category pages (append new items) ──
    for cat, filename in CAT_FILES.items():
        if cat in ["Buttons", "Cinematic Intros", "Uncategorized"]:
            continue  # Already done
        items = new_entries.get(cat, [])
        if not items:
            continue
        
        html_path = os.path.join(BASE, filename)
        with open(html_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Generate new cards
        new_cards = []
        for num, name, fp in items:
            card_num = f"{cat.split()[0]} #{num:02d}"
            new_cards.append(f"""<div class="card">
<div class="card-video-wrap">
<span class="card-number">{html.escape(card_num)}</span>
<div class="card-preview-placeholder">Preview unavailable</div>
</div>
<div class="card-info"><h3>{html.escape(name)}</h3></div>
</div>""")
        
        # Insert before closing </div>\r\n</div>\r\n<div class="footer">
        cards_text = "\r\n".join(new_cards)
        
        # Find the closing grid div and footer
        # Pattern: </div>\r\n</div>\r\n<div class="footer">
        footer_pattern = "</div>\r\n</div>\r\n<div class=\"footer\">"
        if footer_pattern in content:
            content = content.replace(footer_pattern, f"{cards_text}\r\n</div>\r\n</div>\r\n<div class=\"footer\">")
        else:
            # Try with \n
            footer_pattern2 = "</div>\n</div>\n<div class=\"footer\">"
            if footer_pattern2 in content:
                content = content.replace(footer_pattern2, f"{cards_text}\n</div>\n</div>\n<div class=\"footer\">")
            else:
                print(f"WARNING: Could not find insertion point in {filename}")
                continue
        
        # Update count in header
        total = existing_max[cat]
        old_count_pattern = re.compile(rf'<p>{cat.split()[0]} components</p>|<p>\d+ components</p>', re.IGNORECASE)
        # Find the cat-header p tag
        content = re.sub(
            r'(<div class="cat-header">[^<]*<h2>[^<]+</h2>\s*<p>)(\d+)(\s*components</p>)',
            lambda m: f"{m.group(1)}{total}{m.group(3)}",
            content,
            count=1
        )
        
        # Update footer count
        content = re.sub(
            r'(\d+)\s*components',
            str(total),
            content
        )
        
        # Add new nav links if missing
        if 'buttons.html' not in content:
            content = content.replace(
                '<a href="3d-animation.html">3D</a>',
                '<a href="3d-animation.html">3D</a>\n<a href="buttons.html">Buttons</a>\n<a href="cinematic-intros.html">Intros</a>\n<a href="uncategorized.html">Uncategorized</a>'
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
            '<a href="3d-animation.html">3D</a>',
            '<a href="3d-animation.html">3D</a>\n<a href="buttons.html">Buttons</a>\n<a href="cinematic-intros.html">Intros</a>\n<a href="uncategorized.html">Uncategorized</a>'
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
    
    # Insert before the last </div> that closes cat-grid
    # Find: </div>\r\n</div>\r\n<div class="footer">
    new_cards_text = "\r\n".join(new_cat_cards)
    footer_pattern = "</div>\r\n</div>\r\n<div class=\"footer\">"
    if footer_pattern in index_content:
        index_content = index_content.replace(footer_pattern, f"{new_cards_text}\r\n</div>\r\n</div>\r\n<div class=\"footer\">")
    else:
        footer_pattern2 = "</div>\n</div>\n<div class=\"footer\">"
        index_content = index_content.replace(footer_pattern2, f"{new_cards_text}\n</div>\n</div>\n<div class=\"footer\">")
    
    # Update total count
    total_all = len(manifest)
    index_content = re.sub(r'\d+\s*hand-crafted\s*animation\s*components', f'{total_all} hand-crafted animation components', index_content)
    index_content = re.sub(r'\d+\s*components\s*across\s*14\s*categories', f'{total_all} components across 17 categories', index_content)
    index_content = re.sub(r'\d+\s*components\s*across\s*\d+\s*categories', f'{total_all} components across 17 categories', index_content)
    
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(index_content)
    print(f"Updated index.html (total: {total_all} components, 17 categories)")
    
    # ── Print summary ──
    print(f"\n{'='*60}")
    print(f"BUILD COMPLETE")
    print(f"Total components in catalog: {len(manifest)}")
    print(f"New components added: {len(all_components)}")
    print(f"Categories: 17 (14 existing + 3 new)")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()