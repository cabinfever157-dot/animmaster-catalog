#!/usr/bin/env python3
"""
Improved categorization: reads file imports for comp-NNN files,
better HyperUI prefix matching, dedup dark variants.
"""
import json
import os
import re
from collections import defaultdict, OrderedDict

BASE = r"C:\Users\info\Dropbox\Projects\component-catalog"
LIB_BASE = r"C:\Users\info\AppData\Local\hermes\skills\design\ui-component-libraries"
AG_SKILLS = r"C:\Users\info\Dropbox\Google Drive\Software\AG_Backup\2\.agents\skills"

EXISTING_CATS = {
    "Scroll Animation": 65, "Hero Animations": 26, "Sliders": 23,
    "Navigation Menus": 21, "Hover Effects": 23, "Mouse Effects": 20,
    "Webgl & ThreeJS Effects": 19, "Text Animations": 17,
    "Page Transitions": 14, "SVG Animations": 11, "Background Animations": 10,
    "Grid Animations": 10, "Physics Effects": 10, "3D Animation": 22,
}

CAT_TO_FILE = {
    "Scroll Animation": "scroll-animation.html", "Hero Animations": "hero-animations.html",
    "Sliders": "sliders.html", "Navigation Menus": "navigation-menus.html",
    "Hover Effects": "hover-effects.html", "Mouse Effects": "mouse-effects.html",
    "Webgl & ThreeJS Effects": "webgl-threejs.html", "Text Animations": "text-animations.html",
    "Page Transitions": "page-transitions.html", "SVG Animations": "svg-animations.html",
    "Background Animations": "background-animations.html", "Grid Animations": "grid-animations.html",
    "Physics Effects": "physics-effects.html", "3D Animation": "3d-animation.html",
    "Buttons": "buttons.html", "Inputs": "inputs.html", "Cards": "cards.html",
    "Modals & Dialogs": "modals-dialogs.html", "Feedback": "feedback.html",
    "Layout": "layout.html", "Display": "display.html", "Forms": "forms.html",
    "Cinematic Intros": "cinematic-intros.html", "Uncategorized": "uncategorized.html",
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

# ── Skip patterns (non-component files) ──
SKIP_PATTERNS = [
    "__index__", "index.md", "package.json", "readme", ".config",
    "registry", "catalog.json", "package-info",
    "analytics", "seo-monitor", "performance-monitor", "lazy-opengraph",
    "critical-css", "web-vitals", "performance-optim", "resource-preloader",
    "meta-tags", "structured-data", "breadcrumb-seo",
    "component-seo", "google-analytics",
    "apps-examples", "icons-", "src-assets-icons",
    "cli-registry", "cli-install", "environment-variables",
    "theme-customizer", "theme-wrapper", "theme-component",
    "tailwind-indicator", "mdx-components",
    "docs-copy-page", "docs-sidebar", "docs-toc",
    "style-wrapper", "style-switcher",
    "get-cult-pro", "open-in-v0", "github-link",
    "examples-nav", "main-nav", "mobile-nav", "site-header", "site-footer",
    "page-header", "product-catalog-region-header",
    "component-card", "component-example", "component-preview",
    "component-source", "component-preview-tabs", "components-list",
    "featured-component", "cult-pro-components-grid", "cult-pro-sections-grid",
    "template-grid", "home-below-hero-layouts",
    "docs-layout", "src-app-layout", "src-app-not-found",
    "standalone-layout", "standalone-page", "component-registry",
    "docs-layout-content", "package-manager", "toc-context",
    "toc", "hide-toc", "table-of-contents",
    "dynamic-loader", "optimized-image",
    "props-table", "mdx-table", "vitepress-table",
    "gradientgen",
    "src-components-site",  # SeraUI site infrastructure
    "src-components-core", "src-components-ui-dynamic-loader",
    "src-components-ui-optimized-image",
    "src-contexts", "src-mdx",
    "src-components-docs-componenttemplate",
    "src-components-performance",
    "src-components-seo",
]

def should_skip(filepath):
    f = filepath.lower().replace("\\", "/")
    for sp in SKIP_PATTERNS:
        if sp in f:
            return True
    return False


def categorize_by_imports(filepath):
    """Read file imports and categorize comp-NNN files."""
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read(2000)  # First 2KB is enough for imports
    except:
        return None
    
    imports = set()
    for line in content.split("\n"):
        if "import" in line and "@/registry" in line:
            parts = line.split("{")
            if len(parts) > 1:
                names = parts[1].split("}")[0].strip()
                for n in names.split(","):
                    n = n.strip()
                    if n:
                        imports.add(n.lower())
    
    all_imp = " ".join(imports)
    
    # Priority-based categorization
    # Modals & Dialogs
    if any(x in all_imp for x in ["dialog", "drawer", "sheet", "popover", "alert-dialog"]):
        return "Modals & Dialogs"
    
    # Feedback
    if any(x in all_imp for x in ["toast", "sonner", "alert", "badge", "skeleton", "spinner", "progress", "meter"]):
        return "Feedback"
    
    # Inputs (controls)
    if any(x in all_imp for x in ["checkbox", "radio", "switch", "toggle", "slider", "otp", "combobox", "autocomplete", "number-field", "date-picker", "datefield", "multiselect"]):
        return "Inputs"
    
    # Inputs (text)
    if any(x in all_imp for x in ["input", "textarea", "label", "field", "fieldset"]):
        return "Inputs"
    
    # Navigation
    if any(x in all_imp for x in ["breadcrumb", "pagination", "menu", "dropdown", "sidebar", "navigation", "command", "toolbar"]):
        return "Navigation Menus"
    
    # Layout
    if any(x in all_imp for x in ["accordion", "tabs", "collapsible", "separator", "resizable", "frame", "group", "scroll-area"]):
        return "Layout"
    
    # Display
    if any(x in all_imp for x in ["table", "timeline", "avatar", "carousel", "calendar", "tree", "kanban"]):
        return "Display"
    
    # Cards
    if any(x in all_imp for x in ["card", "preview-card", "hover-card"]):
        return "Cards"
    
    # Forms
    if "form" in all_imp:
        return "Forms"
    
    # Buttons
    if "button" in all_imp:
        return "Buttons"
    
    # Select
    if "select" in all_imp:
        return "Inputs"
    
    # Tooltip
    if "tooltip" in all_imp:
        return "Hover Effects"
    
    # If nothing recognizable, Uncategorized
    return "Uncategorized"


def categorize_hyperui(filename):
    """Categorize HyperUI files by their prefix pattern."""
    name = filename.lower().replace(".html", "")
    
    # Remove -dark suffix for categorization
    name = re.sub(r"-dark$", "", name)
    
    # Parse prefix
    # Patterns: application-XXX-N, marketing-XXX-N, neobrutalism-XXX-N
    
    # Button-like
    if any(x in name for x in ["button", "cta", "fab"]):
        return "Buttons"
    
    # Inputs
    if any(x in name for x in ["input", "checkbox", "radio", "toggle", "select", "range", "quantity", "textarea", "file-input"]):
        return "Inputs"
    
    # Cards
    if any(x in name for x in ["card", "product-card", "blog-card", "product-collection"]):
        return "Cards"
    
    # Modals & Dialogs
    if any(x in name for x in ["modal"]):
        return "Modals & Dialogs"
    
    # Feedback
    if any(x in name for x in ["badge", "toast", "alert", "stat", "announcement", "banner", "countdown", "empty-state", "empty-content", "loading", "progress"]):
        return "Feedback"
    
    # Layout
    if any(x in name for x in ["accordion", "tab", "divider", "separator", "grid", "step", "filter", "details-list"]):
        return "Layout"
    
    # Display
    if any(x in name for x in ["table", "media", "timeline", "avatar", "carousel", "gallery", "stat", "logo-cloud"]):
        return "Display"
    
    # Navigation
    if any(x in name for x in ["breadcrumb", "vertical-menu", "footer", "header", "navbar"]):
        return "Navigation Menus"
    
    # Hero
    if "hero" in name:
        return "Hero Animations"
    
    # Text
    if any(x in name for x in ["faq"]):
        return "Layout"
    
    # Marketing sections
    if any(x in name for x in ["section", "team-section", "feature-grid", "poll"]):
        return "Layout"
    
    # Loaders
    if "loader" in name:
        return "Cinematic Intros"
    
    # Skip-links
    if "skip-link" in name:
        return "Navigation Menus"
    
    # Blog animate
    if "blog-animate" in name:
        return "Text Animations"
    
    return "Uncategorized"


def categorize(filename, filepath, lib):
    """Main categorization function."""
    n = filename.lower()
    f = filepath.lower().replace("\\", "/")
    
    if should_skip(filepath):
        return None
    
    # AG skills - only include actual component examples
    if "AG_Backup" in f:
        if "example" not in f and "resource" not in f:
            return None
    
    # ── OriginUI comp-NNN files: use import-based categorization ──
    if re.match(r'^comp-\d+\.tsx$', filename):
        return categorize_by_imports(filepath)
    
    # ── HyperUI: use prefix-based categorization ──
    if "hyperui" in f:
        cat = categorize_hyperui(filename)
        return cat
    
    # ── Cinematic Intros (preloaders, loaders, splash, intro) ──
    if any(x in n for x in ["preloader", "multi-step-loader"]):
        return "Cinematic Intros"
    if n in ["loader.tsx", "grid-loader.tsx", "skeleton-loader.tsx"]:
        return "Cinematic Intros"
    if "loading" in n and "carousel" not in n and "button" not in n:
        return "Cinematic Intros"
    if "loaders" in n and "button" not in n:
        return "Cinematic Intros"
    if n == "intro.tsx" or (n.startswith("intro") and "input" not in n and "disclosure" not in n):
        return "Cinematic Intros"
    
    # ── Buttons ──
    button_keywords = ["button", "shimmer-button", "glowing-button", "pulsating-button",
                        "rainbow-button", "magnetic-button", "stateful-button",
                        "tailwindcss-buttons", "bg-animate-button", "border-beam-button",
                        "cosmic-button", "family-button", "glow-button", "metal-button",
                        "neumorph-button", "texture-button", "smooth-button",
                        "clip-corners-button", "dot-morph-button", "retro-button",
                        "modern-button", "bg-animate-button", "copy-button",
                        "block-copy-button", "cli-install-button",
                        "pulsating-button", "shimmer-button"]
    if any(x in n for x in button_keywords):
        if "button-group" not in n and "buttongroup" not in n and "toolbar" not in n:
            return "Buttons"
    
    # ── Inputs ──
    input_keywords = ["input", "checkbox", "radio", "toggle", "switch", "slider", "range",
                      "otp", "otp-field", "combobox", "autocomplete", "auto-complete",
                      "date-picker", "datefield", "datepicker", "number-field",
                      "textarea", "text-input", "file-input", "select", "multiselect",
                      "multi-select", "password", "search", "prompt-input", "ai-input",
                      "gooey-input", "placeholders-and-vanish", "input-group", "input-otp",
                      "exposure-slider", "scrubber", "color-picker",
                      "animated-input", "animated-o-t-p", "filter",
                      "rating", "patternlock", "paymentmethod", "plantoggle",
                      "select-service", "volume", "ratestar", "love-react",
                      "scale", "swap"]
    if any(x in n for x in input_keywords):
        if "button" not in n and "modal" not in n:
            return "Inputs"
    
    # ── Modals & Dialogs ──
    modal_keywords = ["modal", "dialog", "drawer", "sheet", "popover", "alert-dialog"]
    if any(x in n for x in modal_keywords):
        return "Modals & Dialogs"
    
    # ── Feedback ──
    feedback_keywords = ["toast", "toaster", "sonner", "alert", "badge", "skeleton", "spinner",
                          "progress", "notification", "announcement", "meter", "callout",
                          "pulsating-dot", "vote-tally", "choice-poll", "poll-widget", "feature-poll",
                          "feature-voting", "notification-badge", "notification-menu",
                          "alert-banner", "animated-badge", "verify-badge", "countdown",
                          "indicator", "dynamic-island"]
    if any(x in n for x in feedback_keywords):
        if "button" not in n and "input" not in n and "modal" not in n:
            return "Feedback"
    
    # ── Cards ──
    card_keywords = ["card", "pricing", "profile", "product-card", "tweet-card",
                     "comet-card", "glare-card", "wobble-card", "evervault-card",
                     "card-spotlight", "card-stack", "card-hover", "focus-cards",
                     "expandable-cards", "tooltip-card", "text-reveal-card",
                     "cutout-card", "shift-card", "texture-card", "minimal-card",
                     "magic-card", "spotlightcard", "threed-card", "noise-cards",
                     "noise-card", "gold-standard-card", "preview-card",
                     "switchboard-card", "image-metadata-preview", "scrollable-card-stack",
                     "glow-hover-card", "post-card", "stat-card",
                     "feature-card", "app-download-stack", "apple-invites",
                     "teammember", "team-card", "book", "tweet-grid"]
    if any(x in n for x in card_keywords):
        if "input" not in n and "button" not in n and "modal" not in n:
            return "Cards"
    
    # ── Layout ──
    layout_keywords = ["accordion", "collapsible", "tabs", "tab", "separator", "divider",
                       "resizable", "frame", "group", "bento", "masonry", "masonary",
                       "aspect-ratio", "stack", "join", "layout-grid", "layout-text-flip",
                       "container-text-flip", "expandable", "expandable-screen",
                       "doctabs", "direction-aware-tabs", "animated-tabs",
                       "gradient-accordion", "retro-style-accordion",
                       "resize-handle", "faq", "panel",
                       "blocks-grid", "plug-grid"]
    if any(x in n for x in layout_keywords):
        if "button" not in n and "input" not in n and "card" not in n and "modal" not in n:
            return "Layout"
    
    # ── Display ──
    display_keywords = ["table", "timeline", "avatar", "testimonial", "chart",
                        "code-block", "terminal", "file-tree", "filetree",
                        "mockup", "mock-browser", "carousel", "gallery", "ticker",
                        "social-cards", "logo-carousel", "loading-carousel",
                        "reviews-carousel", "orbit-carousel", "3d-carousel",
                        "three-d-carousel", "apple-cards-carousel", "images-slider",
                        "infinite-moving-cards", "animated-testimonials",
                        "github-profile", "video-gallery", "contribution-graph",
                        "audio-player", "youtube-video-player", "promo-video",
                        "hover-video-player", "web-preview", "html-code",
                        "codeprofile", "nftmarketplace", "portfolio",
                        "waitlist", "job-listing", "figma-comment", "calendar",
                        "agenda-view", "event-calendar", "day-view", "month-view",
                        "week-view", "event-dialog", "event-item", "events-popup",
                        "draggable-event", "droppable-cell", "cropper",
                        "carousel", "marquee", "ticker", "stat",
                        "chat", "diff", "kbd", "local-time",
                        "interactive-image-selector", "github-stars-animation",
                        "number-flow", "price-flow", "agent-avatar",
                        "animated-avatar-group", "user-account-avatar"]
    if any(x in n for x in display_keywords):
        if "button" not in n and "input" not in n and "modal" not in n and "card" not in n:
            return "Display"
    
    # ── Navigation Menus ──
    nav_keywords = ["navbar", "nav-bar", "navigation", "breadcrumb", "sidebar",
                    "command", "command-menu", "command-palette", "menu", "dropdown",
                    "pagination", "pager", "dock", "floating-dock", "floating-navbar",
                    "navbar-menu", "resizable-navbar", "floating-panel",
                    "context-menu", "dropdown-menu", "settings-menu", "info-menu",
                    "notification-menu", "user-menu", "team-switcher", "menubar",
                    "mode-toggle", "theme-toggle", "app-toggle", "sidebar-nav",
                    "side-panel", "searchable-dropdown", "social-selector",
                    "mic-selector", "model-selector", "voice-selector",
                    "search-modal", "search",
                    "header", "main-nav", "mobile-nav",
                    "animatedmenu", "examples-nav", "docs-sidebar", "sidebar-mobile",
                    "footer", "navbar", "breadcrumbs",
                    "skip-link"]
    if any(x in n for x in nav_keywords):
        if "button" not in n and "card" not in n and "input" not in n and "modal" not in n:
            return "Navigation Menus"
    
    # ── Sliders ──
    if any(x in n for x in ["slider", "imageswiper", "image-slider", "infinite-slider"]):
        if "exposure" not in n and "range" not in n and "scrubber" not in n and "input" not in n:
            return "Sliders"
    
    # ── Hero Animations ──
    if any(x in n for x in ["hero", "spotlight", "lamp", "hero-parallax", "hero-highlight",
                            "hero-sections", "hero-color-panel", "hero-dithering", "hero-heatmap",
                            "hero-liquid-metal", "hero-static-radial-gradient", "parallax-hero"]):
        if "button" not in n and "input" not in n and "card" not in n:
            return "Hero Animations"
    
    # ── Text Animations ──
    text_keywords = ["text-animate", "text-reveal", "typewriter", "text-generate",
                      "text-flip", "text-flipping", "text-hover", "shimmer-text",
                      "animated-shiny-text", "aurora-text", "colourful-text",
                      "flip-words", "flipwords", "encrypted-text", "squiggly-text",
                      "text-gif", "two-tone-text", "type-animate",
                      "number-ticker", "numberticker", "number-flow", "animated-number",
                      "text-blurin", "text-bouncy", "text-glitch", "text-gradient",
                      "text-morphing", "text-particle", "text-scalein", "text-shiny",
                      "text-slidein", "text-staggeredpopin", "text-texturedmask",
                      "text-typewriter", "text-wavy", "textreveal", "text-highlighter",
                      "randomtextreveal", "scramble-hover", "reveal-text", "wave-text",
                      "typewriter-text", "gradient-heading", "glow-heading",
                      "pixel-heading", "pixel-paragraph", "glowline", "shimmer",
                      "shine-border", "border-beam", "border-beam-button",
                      "animated-shiny-text", "moving-line", "text-flip-board",
                      "text-flipping-board", "cover", "fuzzy", "decrypting",
                      "glitchvault", "falling-glitch", "sparklestext",
                      "noise-text", "noisetext", "animated-text", "blur-fade",
                      "fade-in", "marquee", "marqueetext", "logomarquee",
                      "shimmer-button", "text-blur", "texturedmask",
                      "squiggle-arrow", "curved-text",
                      "text-scalein", "video-text", "copybutton",
                      "gradient", "aurora", "beam", "rays",
                      "ticker", "morphing"]
    if any(x in n for x in text_keywords):
        if "button" not in n and "card" not in n and "input" not in n and "modal" not in n:
            # shimmer-button and border-beam-button are buttons
            if "button" in n:
                return "Buttons"
            return "Text Animations"
    
    # ── Background Animations ──
    bg_keywords = ["background", "dot-pattern", "dot-background", "dots-background",
                   "grid-pattern", "grid-background", "grid-and-dot", "noise-background",
                   "aurora-background", "wavy-background", "vortex-background",
                   "stars-background", "glowing-stars", "glowing-background",
                   "dotted-glow", "meteors", "shooting-stars", "sparkles",
                   "ripple", "particles", "flickering-grid", "bg-animated",
                   "bg-image-texture", "texture-overlay", "texture-wrapper",
                   "background-texture", "background-guides", "stripe-bg",
                   "grid-beam", "noise", "pattern", "vortex",
                   "moving-grid", "infinite-grid", "letter-glitch",
                   "liquid-glass", "distorted-glass", "dither", "dither-image",
                   "dither-shader", "pixelated-canvas", "webcam-pixel-grid",
                   "ascii-art", "svg-bands", "svg-shapes", "texture-button",
                   "stripe-bg-guides", "edge-blur", "shader-lens-blur",
                   "edge", "scales", "keyboard", "notch",
                   "glowing-effect", "glow", "dot-morph", "bg-media",
                   "dot-pattern-demo", "dots-background-demo",
                   "grid-background-demo", "grid-small-background-demo",
                   "dot-background-demo", "noise-background-demo"]
    if any(x in n for x in bg_keywords):
        if "button" not in n and "card" not in n and "input" not in n and "text" not in n and "modal" not in n:
            return "Background Animations"
    
    # ── Mouse Effects ──
    if any(x in n for x in ["cursor", "following-pointer", "magnetic"]):
        if "button" not in n:
            return "Mouse Effects"
    
    # ── Hover Effects ──
    if any(x in n for x in ["hover", "tilt", "lens", "direction-aware",
                            "hover-card", "hover-effect", "hover-border",
                            "link-preview", "glowing-effect", "glow-hover",
                            "hover-video", "hover-3d", "hover-gallery", "tooltip"]):
        if "button" not in n and "card" not in n and "input" not in n:
            return "Hover Effects"
    
    # ── Scroll Animation ──
    if any(x in n for x in ["scroll", "parallax-scroll", "parallax", "sticky-scroll",
                            "container-scroll", "macbook-scroll", "tracing-beam",
                            "scroll-reveal", "sticky-banner", "scroll-area",
                            "scroll-reveal-paragraph", "sticky-scroll-reveal",
                            "scrollable-card-stack", "power-off-slide"]):
        if "card" not in n and "input" not in n:
            return "Scroll Animation"
    
    # ── WebGL & ThreeJS ──
    if any(x in n for x in ["globe", "world-map", "three-element", "canvas-reveal",
                            "canvas-text", "canvas", "webgl", "shader",
                            "siri-orb", "orbit", "orbits", "orbiting",
                            "network", "lightboard", "morph-surface"]):
        if "button" not in n and "card" not in n and "input" not in n:
            return "Webgl & ThreeJS Effects"
    
    # ── 3D Animation ──
    if any(x in n for x in ["3d", "3-d", "perspective"]):
        if "card" not in n and "button" not in n:
            return "3D Animation"
    
    # ── SVG Animations ──
    if any(x in n for x in ["svg", "svg-mask", "shape"]):
        if "button" not in n and "card" not in n:
            return "SVG Animations"
    
    # ── Physics Effects ──
    if any(x in n for x in ["spring", "drag", "bounce", "physics"]):
        return "Physics Effects"
    
    # ── Page Transitions ──
    if any(x in n for x in ["stepper", "transition", "steps", "twostep"]):
        return "Page Transitions"
    
    # ── Forms ──
    if any(x in n for x in ["form", "field", "label", "login", "signin", "signup",
                            "forgotpassword", "onboarding", "retro-form", "retro-style-form"]):
        if "input" not in n and "radio" not in n and "checkbox" not in n and "select" not in n:
            return "Forms"
    
    # ── Fallback patterns ──
    if "button" in n and "group" not in n:
        return "Buttons"
    if "badge" in n:
        return "Feedback"
    if "tooltip" in n:
        return "Hover Effects"
    if "toast" in n or "alert" in n and "dialog" not in n:
        return "Feedback"
    if "skeleton" in n or "spinner" in n or "progress" in n:
        return "Feedback"
    if "accordion" in n or "collapsible" in n or "tabs" in n:
        return "Layout"
    if "drawer" in n or "dialog" in n or "modal" in n or "sheet" in n:
        return "Modals & Dialogs"
    if "popover" in n:
        return "Modals & Dialogs"
    if "carousel" in n:
        return "Display"
    if "timeline" in n:
        return "Display"
    if "avatar" in n:
        return "Display"
    if "table" in n:
        return "Display"
    if "card" in n and "input" not in n:
        return "Cards"
    if any(x in n for x in ["checkbox", "radio", "toggle", "switch", "select", "input", "slider", "range"]):
        return "Inputs"
    if "button" in n:
        return "Buttons"
    if any(x in n for x in ["nav", "menu", "breadcrumb", "pagination", "sidebar", "dock", "dropdown"]):
        return "Navigation Menus"
    
    return "Uncategorized"


def pretty_name(filename, lib, filepath):
    """Generate a human-readable name from filename."""
    name = re.sub(r'\.(tsx|html|jsx)$', '', filename)
    
    # OriginUI comp-NNN files
    m = re.match(r'^comp-(\d+)$', name)
    if m:
        return f"Component {m.group(1)}"
    
    # OriginUI p-xxx-N files
    m = re.match(r'^p-([a-z-]+)-(\d+)$', name)
    if m:
        cat = m.group(1).replace('-', ' ').title()
        return f"{cat} {m.group(2)}"
    
    # SeraUI long paths
    if name.startswith('src-app-docs-'):
        parts = name.split('-')
        try:
            docs_idx = parts.index('docs')
            comp_parts = parts[docs_idx+1:]
            comp_parts = [p for p in comp_parts if p not in ('components', 'view')]
            name = '-'.join(comp_parts)
        except ValueError:
            pass
    
    if name.startswith('src-app-'):
        name = name.replace('src-app-', '')
        name = re.sub(r'^\(([^)]+)\)-', r'\1-', name)
    
    # HyperUI
    if "hyperui" in filepath.lower():
        # application-accordions-1-dark.html -> Accordions 1
        name = re.sub(r'-dark$', '', name)
        parts = name.split('-')
        if parts[0] in ('application', 'marketing', 'neobrutalism'):
            parts = parts[1:]
        # Remove trailing number
        if parts and parts[-1].isdigit():
            num = parts[-1]
            parts = parts[:-1]
            name = ' '.join(parts).title() + f" {num}"
        else:
            name = ' '.join(parts).title()
        return name
    
    # CultUI demo files
    if name.endswith('-demo'):
        base = name[:-5]
        return f"{base.replace('-', ' ').title()} Demo"
    
    # Generic cleanup
    name = name.replace('-', ' ').replace('_', ' ').strip()
    acronyms = {'otp', 'ai', 'ui', '3d', '2d', 'api', 'url', 'svg', 'css', 'html', 'js', 'ts'}
    words = name.split()
    result = []
    for w in words:
        if w.lower() in acronyms:
            result.append(w.upper())
        else:
            result.append(w.capitalize())
    
    return ' '.join(result)


def scan_library(folder, extension):
    """Scan a library folder and return list of (filename, fullpath) tuples."""
    components = []
    if not os.path.isdir(folder):
        return components
    for f in os.listdir(folder):
        if f.endswith(extension) and not f.endswith('.md'):
            components.append((f, os.path.join(folder, f)))
    return components


def main():
    # Load existing manifest and add category to existing entries
    with open(os.path.join(BASE, "manifest.json"), "r", encoding="utf-8") as f:
        manifest = json.load(f, object_pairs_hook=OrderedDict)
    
    # Add category to existing entries
    for k, v in manifest.items():
        if "category" not in v:
            cat = k.rsplit(" #", 1)[0]
            v["category"] = cat
    
    # Track new items by category
    new_items = defaultdict(list)
    
    # Scan all libraries
    
    # Aceternity
    for fname, fpath in scan_library(os.path.join(LIB_BASE, "aceternity-components"), ".tsx"):
        if fname in ("index.md", "tailwindcss.tsx"):
            continue
        cat = categorize(fname, fpath, "Aceternity")
        if cat:
            name = pretty_name(fname, "Aceternity", fpath)
            new_items[cat].append((name, fpath, "Aceternity"))
    
    # MagicUI
    for fname, fpath in scan_library(os.path.join(LIB_BASE, "magicui-components"), ".tsx"):
        if fname == "index.md":
            continue
        cat = categorize(fname, fpath, "MagicUI")
        if cat:
            name = pretty_name(fname, "MagicUI", fpath)
            new_items[cat].append((name, fpath, "MagicUI"))
    
    # CultUI
    for fname, fpath in scan_library(os.path.join(LIB_BASE, "cultui-components"), ".tsx"):
        if fname.startswith("__") or fname == "index.tsx":
            continue
        cat = categorize(fname, fpath, "CultUI")
        if cat:
            name = pretty_name(fname, "CultUI", fpath)
            new_items[cat].append((name, fpath, "CultUI"))
    
    # SmoothUI
    for fname, fpath in scan_library(os.path.join(LIB_BASE, "smoothui-components"), ".tsx"):
        if fname == "catalog.json":
            continue
        cat = categorize(fname, fpath, "SmoothUI")
        if cat:
            name = pretty_name(fname, "SmoothUI", fpath)
            new_items[cat].append((name, fpath, "SmoothUI"))
    
    # HyperUI - dedupe dark/light variants (keep only non-dark version)
    hyperui_files = scan_library(os.path.join(LIB_BASE, "hyperui-components"), ".html")
    seen_hyperui = set()
    for fname, fpath in hyperui_files:
        # Dedupe: strip -dark suffix, if non-dark version exists, skip dark
        base = re.sub(r'-dark\.html$', '.html', fname)
        if base != fname:  # this is a dark variant
            if base in seen_hyperui:
                continue  # skip dark if light already seen
        seen_hyperui.add(base)
        cat = categorize(fname, fpath, "HyperUI")
        if cat:
            name = pretty_name(fname, "HyperUI", fpath)
            new_items[cat].append((name, fpath, "HyperUI"))
    
    # OriginUI
    for fname, fpath in scan_library(os.path.join(LIB_BASE, "originui-components"), ".tsx"):
        if fname.startswith("__"):
            continue
        cat = categorize(fname, fpath, "OriginUI")
        if cat:
            name = pretty_name(fname, "OriginUI", fpath)
            new_items[cat].append((name, fpath, "OriginUI"))
    
    # DaisyUI
    for fname, fpath in scan_library(os.path.join(LIB_BASE, "daisyui-components"), ".html"):
        cat = categorize(fname, fpath, "DaisyUI")
        if cat:
            name = pretty_name(fname, "DaisyUI", fpath)
            new_items[cat].append((name, fpath, "DaisyUI"))
    
    # SeraUI
    for fname, fpath in scan_library(os.path.join(LIB_BASE, "seraui-components"), ".tsx"):
        if fname == "index.md":
            continue
        cat = categorize(fname, fpath, "SeraUI")
        if cat:
            name = pretty_name(fname, "SeraUI", fpath)
            new_items[cat].append((name, fpath, "SeraUI"))
    
    # OGBlocks
    for fname, fpath in scan_library(os.path.join(LIB_BASE, "ogblocks-components"), ".tsx"):
        if fname == "index.md":
            continue
        cat = categorize(fname, fpath, "OGBlocks")
        if cat:
            name = pretty_name(fname, "OGBlocks", fpath)
            new_items[cat].append((name, fpath, "OGBlocks"))
    
    # AG skills
    for root, dirs, files in os.walk(AG_SKILLS):
        for f in files:
            if f.endswith('.tsx') or f.endswith('.html') or f.endswith('.jsx'):
                fpath = os.path.join(root, f)
                cat = categorize(f, fpath, "AG")
                if cat:
                    name = pretty_name(f, "AG", fpath)
                    new_items[cat].append((name, fpath, "AG"))
    
    # Deduplicate within each category by basename
    seen_basenames = set()
    deduped = defaultdict(list)
    for cat, items in new_items.items():
        for name, fpath, lib in items:
            base = os.path.basename(fpath)
            if base not in seen_basenames:
                seen_basenames.add(base)
                deduped[cat].append((name, fpath, lib))
    new_items = deduped
    
    # Build new manifest entries (only NEW items, not existing)
    # Reset manifest to just existing items first
    existing_keys = set(manifest.keys())
    
    for cat in ALL_CATS_ORDER:
        if cat not in new_items:
            continue
        items = new_items[cat]
        if cat in EXISTING_CATS:
            start_num = EXISTING_CATS[cat] + 1
        else:
            start_num = 1
        
        for i, (name, fpath, lib) in enumerate(items):
            num = start_num + i
            key = f"{cat} #{num:02d}"
            # Only add if not already in manifest
            if key not in existing_keys:
                entry = OrderedDict()
                entry["name"] = name
                entry["local_tsx"] = fpath
                entry["category"] = cat
                entry["num"] = num
                manifest[key] = entry
    
    # Save manifest
    with open(os.path.join(BASE, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    
    # Print summary
    print("=" * 60)
    print("CATALOG BUILD SUMMARY")
    print("=" * 60)
    from collections import Counter
    cat_counts = Counter()
    for k, v in manifest.items():
        cat_counts[v["category"]] += 1
    
    total_new = 0
    for cat in ALL_CATS_ORDER:
        existing = EXISTING_CATS.get(cat, 0)
        total = cat_counts.get(cat, 0)
        new = total - existing
        total_new += new
        print(f"  {cat:30s} existing={existing:4d}  new={new:4d}  total={total:4d}")
    print(f"  {'TOTAL':30s} new={total_new:4d}  total={sum(cat_counts.values())}")
    
    return manifest, new_items

if __name__ == "__main__":
    manifest, new_items = main()