#!/usr/bin/env python3
"""
Build the expanded AnimMasterLib catalog - v3.
Final version with proper filtering, naming, and categorization.
"""
import os, re, json, html

BASE = r"C:\Users\info\Dropbox\Projects\component-catalog"
LIB_BASE = r"C:\Users\info\AppData\Local\hermes\skills\design\ui-component-libraries"
AG_BASE = r"C:\Users\info\Dropbox\Google Drive\Software\AG_Backup\2\.agents\skills"

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
    "Scroll Animation": "scroll", "Hero Animations": "hero", "Sliders": "slider",
    "Navigation Menus": "nav", "Hover Effects": "hover", "Mouse Effects": "mouse",
    "Webgl & ThreeJS Effects": "webgl", "Text Animations": "text",
    "Page Transitions": "page", "SVG Animations": "svg",
    "Background Animations": "bg", "Grid Animations": "grid",
    "Physics Effects": "physics", "3D Animation": "3d",
    "Buttons": "btn", "Cinematic Intros": "cine", "Uncategorized": "uncat",
}

# ── Exclusion substrings (lowercase, checked against flattened filename) ──
EXCLUDE_SUBS = [
    # Static form elements
    "input", "checkbox", "radio", "select", "toggle", "switch", "label", "field",
    "textarea", "form", "combobox", "autocomplete", "datepicker", "date-picker",
    "range", "slider.tsx",
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
    # Static display
    "badge", "avatar", "alert", "tooltip", "dropdown", "command",
    "popover", "sheet", "modal", "dialog", "drawer", "toast", "sonner",
    "callout", "calendar", "code-block", "snippet", "terminal", "clipboard",
    "data-table", "chart-", "command", "context-menu",
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
    "card.tsx", "card-view", "card-content", "card-grid",
    "cards-demo",
    # CultUI non-animated
    "color-picker", "cutout-card", "docs-sidebar",
    "expandable-screen", "expandable-demo", "expandable.tsx",
    "featured-component", "feature-card", "feature-section",
    "feature-carousel", "feature-poll", "feature-voting",
    "inline-citation", "lightboard", "list.tsx",
    "neumorph", "onboarding", "persona", "plug-grid",
    "shift-card", "texture-wrapper", "texture-overlay",
    "texture-card", "texture-button", "texture-button-demo",
    "texture-card-demo", "texture-overlay-demo",
    "expandable-card-demo", "expandable-screen-demo",
    "floating-panel",
    "glow-heading",
    "image-metadata",
    # CultUI static infra
    "commit.tsx", "component-example", "component-source", "connection.tsx",
    "context.tsx", "docs-copy-page", "environment-variables", "examples-nav",
    "file-tree", "github-link", "jsx-preview", "list.tsx", "local-time",
    "main-nav", "menubar", "message.tsx", "mock-browser-window",
    "navigation-menu", "pager", "table.tsx", "tree.tsx", "user-menu",
    "mobile-nav", "month-view", "meter", "stepper", "group.tsx",
    "info-menu", "menu.tsx", "event-item", "events-popup",
    "notification-menu", "book.tsx", "empty.tsx", "minimal-card",
    "preview-card", "__index__",
    "edge.tsx", "edge-blur", "keyboard", "tailwindcss.tsx",
    # SeraUI static
    "combo-box", "filetree", "forgotpassword", "html-code",
    "password", "pattern-craft", "retro-card", "signin",
    "pricing", "resize-handle", "search-search",
    "docs-copy",
    # CultUI static that still slip through
    "sidebar.tsx", "tabs.tsx", "tailwindcss", "commit", "connection",
    "context", "edge.tsx", "list.tsx", "message", "table.tsx",
    "__index__", "book", "phototab", "empty", "group", "menu.tsx",
    "tree.tsx",
    # SeraUI static card
    "card-card", "docs-card",
    "p-card", "p-alert", "p-avatar", "p-badge", "p-breadcrumb",
    "p-button", "p-checkbox", "p-combobox", "p-dialog", "p-dropdown",
    "p-empty", "p-field", "p-form", "p-input", "p-label", "p-menu",
    "p-pagination", "p-popover", "p-progress", "p-radio", "p-select",
    "p-separator", "p-sheet", "p-sidebar", "p-skeleton", "p-slider",
    "p-spinner", "p-switch", "p-table", "p-tabs", "p-textarea",
    "p-toast", "p-toggle", "p-tooltip", "p-frame", "p-group",
    "p-meter", "p-preview", "p-context", "p-accordion",
    "p-command", "p-calendar", "p-chart",
    "text-gif",
]

def should_exclude_name(filename):
    """Hard filename-based exclusion."""
    n = filename.lower().replace(".tsx", "").replace(".jsx", "").replace(".html", "")
    n_flat = n.replace("_", "-")
    
    if n in ["index", "index.md", "readme", "readme.md", "catalog.json"]:
        return True
    if n_flat.startswith("comp-"):
        return True
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
    # Exclude all p-* OriginUI files (static form components)
    if re.match(r'^p-[a-z]+-\d+', n_flat):
        return True
    
    for ex in EXCLUDE_SUBS:
        if ex in n_flat:
            return True
    
    return False

def has_animation_signals(filepath):
    """Check if file has real animation signals."""
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read(10000).lower()
    except:
        return False
    
    strong_signals = [
        "framer-motion", "motion.", "framer", "useAnimationFrame",
        "requestanimationframe", "@keyframes", "keyframes",
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
        "lamp.tsx", "lamp-section", "hero-highlight", "hero-parallax",
        "macbook-scroll", "world-map", "globe.tsx",
        "text-reveal", "text-animate", "text-generate",
        "sparkles.tsx", "spotlight.tsx", "vortex.tsx",
        "wavy-background", "aurora-background", "aurora-text",
        "background-beams", "background-boxes", "background-gradient",
        "background-lines", "background-ripple",
        "noise-background", "stars-background",
        "dotted-glow-background", "dots-background",
        "dot-pattern", "grid-pattern", "flickering-grid",
        "dither-shader", "pixelated-canvas", "canvas-reveal",
        "canvas-text", "canvas-fractal",
        "sticky-scroll", "sticky-banner", "tracing-beam",
        "link-preview", "images-slider", "infinite-moving-cards",
        "tooltip-card", "animated-shiny-text", "blur-fade",
        "number-ticker", "particles.tsx", "meteors.tsx",
        "ripple.tsx", "shimmer-button.tsx", "pulsating-button.tsx",
        "dock.tsx", "globe.tsx", "magic-card.tsx", "marquee.tsx",
        "border-beam.tsx", "shine-border.tsx", "text-animate.tsx",
        "text-reveal.tsx", "bg-animate", "bg-animated",
        "canvas-fractal-grid", "svg-shapes-animated", "terminal-animation",
        "text-animate-demo", "three-d-carousel", "shimmer.tsx",
        "bg-image-texture", "bg-media", "background-guides",
        "background-texture", "stripe-bg", "animated-number",
        "svg-bands", "squiggle-arrow", "3d-carousel", "animated-badge",
        "aurora.tsx", "curved-text", "decrypting",
        "dock-colorful", "dock-floating", "dock-minimal", "dock-simple",
        "enhanced-carousel", "imagecarousel", "scroll-progress",
        "ticker.tsx", "video-gallery", "video-text", "wavy.tsx",
        "typewriter.tsx", "animated-testimonial", "siri-orb",
        "power-off-slide", "dynamic-island", "cursor-follow",
        "glow-hover-card", "gooey-popover", "scroll-reveal",
        "scrollable-card-stack", "scramble-hover", "reveal-text",
        "wave-text", "magnetic-button", "smooth-button",
        "dot-morph-button", "clip-corners-button", "grid-loader",
        "animated-avatar-group", "animated-file-upload",
        "animated-progress-bar", "animated-stepper", "animated-tabs",
        "animated-tags", "animated-tooltip", "contribution-graph",
        "expandable-cards", "figma-comment", "github-stars",
        "infinite-slider", "interactive-image", "notification-badge",
        "number-flow", "phototab", "price-flow", "reviews-carousel",
        "scroll-reveal-paragraph", "scrubber", "skeleton-loader",
        "switchboard-card", "typewriter-text", "wave-text",
        "exposure-slider", "scrollable-card", "animated-modal",
        "hover-3d", "hover-gallery", "countdown", "progress-bar",
        "timeline", "marquee", "carousel", "ticker",
        "animate", "transition", "transform", "scale(",
        "rotate(", "opacity", "fade", "slide", "bounce",
        "variants", "useeffect", "useanimation",
        "blinkin", "bouncy", "blurin", "scalein", "slidein",
        "staggered", "morph", "highlighter", "shiny",
        "gradient", "glowline", "glow-line", "randomtextreveal",
        "random-text-reveal", "flipwords", "flip-words",
        "masonary", "masonry", "network", "nftmarketplace",
        "nft-marketplace", "portfolio", "pricing", "search",
        "twostep", "two-step", "teamcard", "team-card",
        "screen-slide", "resize-handle",
    ]
    
    return any(s in content for s in strong_signals)

def categorize(filename):
    """Categorize based on filename."""
    n = filename.lower().replace(".tsx", "").replace(".jsx", "").replace(".html", "").replace("_", "-")
    
    # ── Buttons ──
    if any(x in n for x in ["button", "magnetic-button", "shimmer-button", "pulsating-button",
                            "rainbow-button", "glowing-button", "smooth-button", "dot-morph-button",
                            "clip-corners-button", "bg-animate-button", "border-beam-button",
                            "texture-button", "tailwindcss-button", "hover-border-gradient",
                            "stateful-button", "shimmer-button"]):
        return "Buttons"
    
    # ── Cinematic Intros ──
    if any(x in n for x in ["loader", "preloader", "splash", "intro", "cinematic",
                            "multi-step-loader", "grid-loader", "skeleton-loader",
                            "loading"]):
        return "Cinematic Intros"
    
    # ── Text Animations ──
    if any(x in n for x in ["text-animate", "text-flip", "text-generate", "text-hover",
                            "text-reveal", "typewriter", "shimmer-text", "shimmer.tsx",
                            "flip-words", "flipwords", "squiggly-text", "encrypted-text",
                            "colourful-text", "aurora-text", "animated-shiny-text",
                            "blur-fade", "blurin", "bouncy", "scalein", "slidein",
                            "text-flip-board", "text-flipping-board", "text-generate-effect",
                            "text-hover-effect", "text-reveal-card", "canvas-text",
                            "container-text-flip", "layout-text-flip", "pointer-highlight",
                            "cover", "two-tone-text", "type-animate", "pixel-heading",
                            "pixel-paragraph", "wave-text", "scramble-hover",
                            "reveal-text", "typewriter-text", "decrypting", "curved-text",
                            "ticker", "video-text", "text-typewriter", "text-wavy",
                            "ascii-art", "moving-line", "squiggle-arrow",
                            "text-clip", "text-demo", "shimmer-text", "colourful",
                            "rainbow-text", "number-ticker", "number-flow", "price-flow",
                            "text-blurin", "text-bouncy", "text-gradient",
                            "text-highlighter", "text-morphing", "text-particle",
                            "text-scalein", "text-shiny", "text-slidein",
                            "text-staggeredpopin", "randomtextreveal", "random-text-reveal",
                            "flipwords", "glowline", "glow-line",
                            "shimmer-shimmer", "shimmer.tsx",
                            "gradient-gradient", "gradientgen",
                            "animated-number", "animated-shiny",
                            "text-flip"]):
        return "Text Animations"
    
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
                            "dither-shader", "flickering", "gradient",
                            "glowline"]):
        return "Background Animations"
    
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
                            "perspective", "rotate3d", "hover-3d",
                            "threed-card"]):
        return "3D Animation"
    
    # ── WebGL & ThreeJS Effects ──
    if any(x in n for x in ["webgl", "threejs", "three.js", "canvas-reveal",
                            "canvas-reveal-effect", "canvas-fractal",
                            "canvas-text", "shader", "pixelated",
                            "glitch", "noise", "fuzzy", "liquid",
                            "distort", "canvas-fractal-grid",
                            "shader-lens", "dither"]):
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
                            "video-gallery", "imageswiper",
                            "masonary", "masonry"]):
        return "Sliders"
    
    # ── Navigation Menus ──
    if any(x in n for x in ["navbar", "dock", "floating-dock", "floating-navbar",
                            "resizable-navbar", "navbar-menu",
                            "link-preview", "animated-tabs",
                            "dock-colorful", "dock-floating",
                            "dock-minimal", "dock-simple",
                            "animated-stepper", "progress-bar",
                            "sidebar.tsx", "docs-sidebar",
                            "animated-tags"]):
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
                            "notification-badge", "glowing-effect",
                            "feature-card", "pulsating-dot",
                            "expandable-card", "expandable",
                            "cutout-card", "floating-panel",
                            "neumorph", "feature-section",
                            "persona", "onboarding",
                            "compare", "pulsating",
                            "glow-heading", "morph-surface",
                            "lightboard", "expandable-screen"]):
        return "Hover Effects"
    
    # ── Mouse Effects ──
    if any(x in n for x in ["mouse", "cursor-follow", "following-pointer",
                            "pointer", "parallax", "tilt",
                            "draggable", "spotlight"]):
        return "Mouse Effects"
    
    # ── SVG Animations ──
    if any(x in n for x in ["svg", "svg-mask", "svg-bands", "svg-shapes",
                            "svg-shapes-animated", "svg-shapes-demo",
                            "world-map", "mask", "curved-text"]):
        return "SVG Animations"
    
    # ── Grid Animations ──
    if any(x in n for x in ["grid", "bento-grid", "layout-grid",
                            "blocks-grid", "plug-grid",
                            "contribution-graph", "grid-loader",
                            "github-stars", "network"]):
        return "Grid Animations"
    
    # ── Page Transitions ──
    if any(x in n for x in ["transition", "page-transition",
                            "animated-modal", "blur-fade",
                            "dynamic-island", "power-off-slide",
                            "screen-slide", "fade-in", "fade-in",
                            "twostep", "two-step"]):
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
    
    # ── Timeline / Progress ──
    if any(x in n for x in ["timeline", "progress", "countdown",
                            "steps", "animated-number", "stack",
                            "marquee", "ticker"]):
        return "Scroll Animation"
    
    # ── Specific recategorizations ──
    # Animated testimonials and testimonial carousels
    if any(x in n for x in ["animated-testimonials", "testimonial"]):
        return "Sliders"
    # Shimmer (text effect)
    if "shimmer" in n and "button" not in n:
        return "Text Animations"
    # Magic card, team cards, teammember
    if any(x in n for x in ["magic-magiccard", "magiccard", "teammember", "teamcard",
                            "team-card"]):
        return "Hover Effects"
    # Portfolio → Hero
    if "portfolio" in n:
        return "Hero Animations"
    # Walkthrough composition → Cinematic
    if "walkthrough" in n:
        return "Cinematic Intros"
    # NFT marketplace → Sliders
    if "nftmarketplace" in n or "nft-marketplace" in n:
        return "Sliders"
    # Tabs classic/fancy → Navigation
    if "tabs-classic" in n or "tabs-fancy" in n:
        return "Navigation Menus"
    # Search → Navigation
    if "search" in n and "search-modal" not in n and "searchable" not in n:
        return "Navigation Menus"
    
    # ── Specific SeraUI ──
    if any(x in n for x in ["nftmarketplace", "nft-marketplace",
                            "portfolio", "pricing",
                            "teammember", "team-card", "teamcard",
                            "search", "resize-handle"]):
        return "Uncategorized"
    
    return "Uncategorized"

def prettify_name(filename):
    """Convert filename to a nice display name."""
    name = filename.replace(".tsx", "").replace(".jsx", "").replace(".html", "")
    
    # Handle SeraUI prefix
    name = re.sub(r'^src-app-docs-', '', name, flags=re.IGNORECASE)
    
    # Remove duplicate words (e.g., "marquee-marquee" -> "Marquee")
    parts = name.replace("_", "-").split("-")
    # Dedupe consecutive identical parts
    deduped = []
    for p in parts:
        if not deduped or deduped[-1].lower() != p.lower():
            deduped.append(p)
    name = "-".join(deduped)
    
    # Also handle the case where the component name is doubled
    # e.g., "flipwords-flipwords" -> "Flipwords"
    # Already handled by dedup above
    
    name = name.replace("-", " ").replace("_", " ")
    words = name.split()
    result = []
    for w in words:
        wl = w.lower()
        if wl in ["3d", "ui", "otp", "ai", "svg", "css", "api", "orb", "gif"]:
            result.append(w.upper())
        elif wl in ["text", "card", "hero", "grid", "dock", "beam"]:
            result.append(w.capitalize())
        else:
            result.append(w.capitalize())
    return " ".join(result)

def scan_lib(path, scan_fn=None):
    """Generic scanner."""
    results = []
    if not os.path.exists(path):
        return results
    for f in os.listdir(path):
        if scan_fn:
            ok = scan_fn(f, os.path.join(path, f))
        else:
            if not (f.endswith(".tsx") or f.endswith(".jsx") or f.endswith(".html")):
                continue
            if should_exclude_name(f):
                continue
            fp = os.path.join(path, f)
            if not has_animation_signals(fp):
                continue
            ok = True
        if ok:
            results.append((f, os.path.join(path, f)))
    return results

def scan_aceternity(path):
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

def scan_magicui(path):
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
    results = []
    for f in os.listdir(path):
        if not f.endswith(".tsx"):
            continue
        if should_exclude_name(f):
            continue
        if re.match(r'^comp-\d+', f, re.IGNORECASE):
            continue
        if re.match(r'^p-[a-z]+-\d+', f, re.IGNORECASE):
            continue
        fp = os.path.join(path, f)
        if has_animation_signals(fp):
            results.append((f, fp))
    return results

def scan_daisyui(path):
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
            results.append((f, os.path.join(path, f)))
    return results

def scan_hyperui(path):
    results = []
    for f in os.listdir(path):
        if not f.endswith(".html"):
            continue
        n = f.lower()
        if "progress" in n or "timeline" in n:
            results.append((f, os.path.join(path, f)))
    return results

def scan_seraui(path):
    results = []
    for f in os.listdir(path):
        if not f.endswith(".tsx"):
            continue
        n = f.lower()
        if not n.startswith("src-app-docs-"):
            continue
        if should_exclude_name(f):
            continue
        fp = os.path.join(path, f)
        if has_animation_signals(fp):
            results.append((f, fp))
    return results

def scan_ogblocks(path):
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
    # Restore originals from git
    os.system(f'cd "{BASE}" && git checkout manifest.json *.html 2>nul')
    
    manifest = json.load(open(os.path.join(BASE, "manifest.json")))
    existing_max = {}
    for k in manifest:
        cat = k.rsplit(" ", 1)[0]
        num = manifest[k]["num"]
        if cat not in existing_max or num > existing_max[cat]:
            existing_max[cat] = num
    
    existing_max["Buttons"] = 0
    existing_max["Cinematic Intros"] = 0
    existing_max["Uncategorized"] = 0
    
    # Restore HTML files from git
    os.system(f'cd "{BASE}" && git checkout *.html 2>nul')
    
    # ── Scan ──
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
    
    # Deduplicate
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
    
    # Build manifest
    new_entries = {cat: [] for cat in CAT_FILES}
    for name, fp, cat in all_components:
        existing_max[cat] += 1
        num = existing_max[cat]
        prefix = CAT_PREFIX.get(cat, "uncat")
        key = f"{cat} #{num:02d}"
        manifest[key] = {
            "name": name, "prefix": prefix, "num": num, "local_code": fp,
        }
        new_entries[cat].append((num, name, fp))
    
    with open(os.path.join(BASE, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    print(f"\nManifest saved: {len(manifest)} total entries")
    
    # ── HTML ──
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
        card_label = cat_name.split()[0]
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
    
    def gen_new_cat_html(cat_name, items):
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
    
    # Generate new category pages
    for cat in ["Buttons", "Cinematic Intros", "Uncategorized"]:
        items = new_entries[cat]
        html_path = os.path.join(BASE, CAT_FILES[cat])
        content = gen_new_cat_html(cat, items)
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Created {CAT_FILES[cat]} with {len(items)} items (total: {existing_max[cat]})")
    
    # Update existing category pages
    for cat, filename in CAT_FILES.items():
        if cat in ["Buttons", "Cinematic Intros", "Uncategorized"]:
            continue
        items = new_entries.get(cat, [])
        html_path = os.path.join(BASE, filename)
        with open(html_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Add new nav links
        if 'buttons.html' not in content:
            content = content.replace(
                '<a href="3d-animation.html">3D</a>\r\n</nav>',
                '<a href="3d-animation.html">3D</a>\r\n<a href="buttons.html">Buttons</a>\r\n<a href="cinematic-intros.html">Intros</a>\r\n<a href="uncategorized.html">Uncategorized</a>\r\n</nav>'
            )
            content = content.replace(
                '<a href="3d-animation.html">3D</a>\n</nav>',
                '<a href="3d-animation.html">3D</a>\n<a href="buttons.html">Buttons</a>\n<a href="cinematic-intros.html">Intros</a>\n<a href="uncategorized.html">Uncategorized</a>\n</nav>'
            )
        
        if not items:
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(content)
            continue
        
        new_cards = [make_card(cat, num, name) for num, name, fp in items]
        cards_text = "\r\n".join(new_cards)
        
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
        
        total = existing_max[cat]
        content = re.sub(
            r'(<div class="cat-header">[^<]*<h2>[^<]+</h2>\s*<p>)(\d+)(\s*components</p>)',
            lambda m: f"{m.group(1)}{total}{m.group(3)}",
            content, count=1
        )
        content = re.sub(
            r'(Animation Effects Catalog &middot; )(\d+)(\s*components)',
            lambda m: f"{m.group(1)}{total}{m.group(3)}",
            content
        )
        
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Updated {filename} with {len(items)} new items (total: {total})")
    
    # Update index.html
    index_path = os.path.join(BASE, "index.html")
    with open(index_path, "r", encoding="utf-8") as f:
        index_content = f.read()
    
    if 'buttons.html' not in index_content:
        index_content = index_content.replace(
            '<a href="3d-animation.html">3D</a>\r\n</nav>',
            '<a href="3d-animation.html">3D</a>\r\n<a href="buttons.html">Buttons</a>\r\n<a href="cinematic-intros.html">Intros</a>\r\n<a href="uncategorized.html">Uncategorized</a>\r\n</nav>'
        )
        index_content = index_content.replace(
            '<a href="3d-animation.html">3D</a>\n</nav>',
            '<a href="3d-animation.html">3D</a>\n<a href="buttons.html">Buttons</a>\n<a href="cinematic-intros.html">Intros</a>\n<a href="uncategorized.html">Uncategorized</a>\n</nav>'
        )
    
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
    inserted = False
    for pattern, replacement in [
        ("</div>\r\n</div>\r\n<div class=\"footer\">", f"{new_cards_text}\r\n</div>\r\n</div>\r\n<div class=\"footer\">"),
        ("</div>\n</div>\n<div class=\"footer\">", f"{new_cards_text}\n</div>\n</div>\n<div class=\"footer\">"),
    ]:
        if pattern in index_content:
            index_content = index_content.replace(pattern, replacement)
            inserted = True
            break
    
    total_all = len(manifest)
    index_content = re.sub(r'\d+\s*hand-crafted\s*animation\s*components', f'{total_all} hand-crafted animation components', index_content)
    index_content = re.sub(
        r'(Animation Effects Catalog &middot; )(\d+)(\s*components\s*across\s*)(\d+)(\s*categories)',
        lambda m: f"{m.group(1)}{total_all}{m.group(3)}17{m.group(5)}",
        index_content
    )
    
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(index_content)
    print(f"Updated index.html (total: {total_all} components, 17 categories)")
    
    print(f"\n{'='*60}")
    print("BUILD COMPLETE")
    print(f"Total: {len(manifest)} | New: {len(all_components)} | Categories: 17")
    for cat in sorted(CAT_FILES.keys()):
        print(f"  {cat}: {existing_max[cat]}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()