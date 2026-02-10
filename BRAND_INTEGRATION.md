# Brand Integration for Training Guides

This document describes how the Gravel God brand guidelines are integrated into the training guide generation system.

## Source of Truth

Brand guidelines live in the `gravel-god-brand` repository:
- **Repo**: https://github.com/wattgod/gravel-god-brand
- **Local**: `/Users/mattirowe/Documents/GravelGod/gravel-god-brand`

## Architecture

```
gravel-god-guides/
├── brand/                    # Copied from gravel-god-brand
│   ├── tokens.css           # Design tokens (colors, fonts, spacing)
│   └── fonts/               # Self-hosted font files
│       ├── fonts.css        # @font-face declarations
│       └── *.woff2          # Font files
├── styles/
│   └── training-guide.css   # Guide-specific styles using brand tokens
├── templates/
│   └── guide_template_full.html  # HTML template with <!-- BRAND_CSS --> placeholder
└── generators/
    └── guide_generator.py   # Injects brand CSS at generation time
```

## How It Works

1. **Template placeholder**: The HTML template contains `<!-- BRAND_CSS -->` where styles should be injected
2. **Generator loads CSS**: `load_brand_css()` combines `tokens.css` and `training-guide.css`
3. **Injection at runtime**: CSS is inlined into the HTML for standalone delivery
4. **Fonts via CDN**: Google Fonts loads Source Serif 4 and Sometype Mono for portability

## Design System

### Two-Voice Typography

| Voice | Font | Usage |
|-------|------|-------|
| **Editorial** | Source Serif 4 | Headlines, prose, descriptions |
| **Data** | Sometype Mono | Labels, tables, navigation, metadata |

### Color Palette

| Token | Hex | Usage |
|-------|-----|-------|
| `--gg-color-dark-brown` | #3a2e25 | Primary text, borders |
| `--gg-color-sand` | #ede4d8 | Page background |
| `--gg-color-warm-paper` | #f5efe6 | Cards, callouts |
| `--gg-color-gold` | #B7950B | Accents, highlights, h3 labels |
| `--gg-color-teal` | #1A8A82 | Links, data highlights |
| `--gg-color-secondary-brown` | #8c7568 | Muted text, h4 labels |

### Border Rules

- **No border-radius**: Always 0. Non-negotiable.
- **No box-shadow**: Never. Not once.
- **Double borders**: 4px double on structural breaks (h1, h2, hr, footer)
- **Standard borders**: 3px solid for cards, tables, modules

### Spacing Scale

Uses `--gg-spacing-*` tokens: 2xs (4px) through 4xl (96px)

## Updating Brand Assets

When the brand repo is updated:

```bash
# Copy updated tokens
cp /Users/mattirowe/Documents/GravelGod/gravel-god-brand/tokens/tokens.css \
   /Users/mattirowe/Documents/GravelGod/guides/gravel-god-guides/brand/

# Copy updated fonts (if changed)
cp /Users/mattirowe/Documents/GravelGod/gravel-god-brand/assets/fonts/* \
   /Users/mattirowe/Documents/GravelGod/guides/gravel-god-guides/brand/fonts/
```

Then regenerate all guides to pick up changes.

## Testing

Generate a test guide and verify:
1. Sandy background (#ede4d8)
2. Serif headlines (Source Serif 4)
3. Monospace tables/labels (Sometype Mono)
4. Gold accents on h3 headings
5. Teal links
6. Double-rule borders on major sections
7. No rounded corners anywhere

## Standalone HTML Delivery

Generated guides are fully self-contained:
- Brand CSS is inlined (no external stylesheet dependency)
- Fonts loaded via Google Fonts CDN
- Works offline if fonts are cached
- Can be emailed, downloaded, printed

## Related Files

- `gravel-god-brand/index.html` - Interactive brand guide
- `gravel-god-brand/guide/foundations.html` - Colors & typography reference
- `gravel-god-brand/guide/components.html` - Component library
