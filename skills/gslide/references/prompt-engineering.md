# Prompt Engineering for Google Slides Generation

Best practices for crafting prompts that work with gslide's "Help me visualize" feature (Gemini / Nano Banana Pro).

## Table of Contents
1. [Prompt Anatomy — 9 Components](#prompt-anatomy)
2. [Tab Selection Guide](#tab-selection)
3. [Layout Vocabulary](#layout-vocabulary)
4. [Style Vocabulary](#style-vocabulary)
5. [Composition & Quality](#composition-and-quality)
6. [Constraints & Negative Instructions](#constraints)
7. [Proven Templates](#proven-templates)
8. [Common Failures](#common-failures)

---

## Prompt Anatomy

Every prompt has 9 components, ordered by importance (Gemini weighs earlier tokens more heavily):

```
[1. Format + Tab]     Landscape 16:9 [infographic/slide/image].
[2. Layout]           [specific layout pattern name].
[3. Style]            [visual style name from vocabulary].
[4. Title]            Title: "[exact assertion headline]".
[5. Content]          [specific data, text, structure to display].
[6. Color]            [color palette] on [background color].
[7. Composition]      [composition rule], generous white space.
[8. Quality]          Clean, professional, sharp focus.
[9. Constraints]      [what to exclude + language specification].
```

**Why this order matters:** The first ~60 words of a prompt have the strongest influence on the output (consistent finding across Midjourney, DALL-E, and Gemini). Put the structural decisions (format, layout, style) first, then content, then polish.

### Component Details

**1. Format + Tab**
Always start with "Landscape 16:9" followed by the tab type. This anchors the aspect ratio and output type immediately.

**2. Layout**
Use a specific, named layout pattern — not vague instructions. "Split-screen comparison" works. "Make it look nice with stuff on both sides" fails.

**3. Style**
Pick one style and be consistent across the entire deck. The visual style comes from the design system and stays the same for every slide prompt.

**4. Title**
Always wrap in quotes with the "Title:" prefix. This tells Gemini to render it as a prominent heading. Use the exact assertion headline from the slide plan.

**5. Content**
Be specific and literal. Include:
- Exact numbers: "47% growth" not "significant growth"
- Exact labels: "Card 1: Marketing — $2.3M budget" not "show three cards"
- Exact structure: "3 boxes horizontal, each with icon + label + number"

**6. Color**
Specify the presentation's color palette. Hex codes work but Gemini treats them as suggestions. Named colors ("navy blue", "coral") are also effective. Always specify the background.

**7. Composition**
Guide spatial arrangement: "rule-of-thirds", "centered", "asymmetrical balance". Add "generous white space" — Gemini tends to fill space if not told otherwise.

**8. Quality**
Standard quality modifiers that consistently improve output:
- `clean` — removes visual clutter
- `professional` — avoids playful/casual elements
- `sharp focus` — improves text clarity
- `high contrast` — improves readability

**9. Constraints**
Tell Gemini what NOT to include. Use positive language where possible:
- "No bullet lists" → keeps content visual
- "No decorative borders" → reduces noise
- "No clip art" → maintains professionalism
- "All text in Thai" → specifies language

---

## Tab Selection Guide

| Content Type | Best Tab | Why |
|---|---|---|
| Data visualization, infographic, mind map | **infographic** | Nano Banana Pro + text rendering — most detailed output |
| Simple layout with text + image placeholder | **slide** | Creates editable text elements |
| Quote with dramatic background | **slide** or **infographic** | Depends on desired visual complexity |
| Icon, illustration, logo, photo | **image** | Generates asset only, inserts into specific slide |
| Full-bleed emotional image | **image** | Then set as background |

**Default recommendation:** Use `infographic` for most content slides — it produces the richest visual output. Use `slide` for text-heavy slides (title, CTA). Use `image` only for generating visual assets to place on existing slides.

---

## Layout Vocabulary

Use these exact terms in prompts — Gemini recognizes them:

### Primary (high success rate)
| Term | Description | Best for |
|---|---|---|
| `split-screen` | 50/50 left-right division | Comparison, problem/solution |
| `3 cards horizontal` | Three equal boxes in a row | Rule of Three, feature comparison |
| `timeline` or `horizontal timeline` | Left-to-right progression | Process, history, roadmap |
| `centered` | Single element in center with margins | Statistics, quotes, CTA |
| `full-bleed` | Image fills entire canvas | Title, divider, emotional slides |

### Extended (good success rate)
| Term | Description | Best for |
|---|---|---|
| `bento grid` | Magazine-style asymmetric boxes | Feature overview, dashboard |
| `hub-and-spoke` or `mind map` | Central node with branches | Concept overview, ecosystem |
| `funnel` | Wide to narrow progression | Conversion, filtering process |
| `pyramid` | Stacked layers | Hierarchy, prioritization |
| `comparison matrix` | Grid with features × options | Detailed feature comparison |
| `before/after split` | Clear division with labels | Transformation stories |
| `dashboard layout` | Multiple data widgets | KPI overview (use sparingly) |

---

## Style Vocabulary

### Recommended for presentations (legible, professional)

| Style Term | Look | Best for |
|---|---|---|
| `flat vector` | Clean 2D shapes, solid colors | Default choice — versatile, readable |
| `isometric 3D` | Fixed-angle pseudo-3D | Process flows, tech concepts |
| `corporate memphis` | Rounded, colorful characters | Friendly business content |
| `glassmorphism` | Frosted glass panels | Modern, premium feel |
| `neo brutalism` | Bold black borders, chunky shapes | Attention-grabbing, edgy |
| `kawaii` | Cute rounded characters | Approachable, education |
| `chalkboard` | White on dark, handwritten feel | Teaching, workshops |

### Avoid for presentations
| Style Term | Problem |
|---|---|
| `photorealistic` | Text becomes unreadable on detailed backgrounds |
| `watercolor` | Soft edges make text and data hard to read |
| `pixel art / 8-bit` | Novelty wears off, hard to convey data |

### Image-specific styles (for Image tab only)
When generating standalone images/photos, you can use photography terms:
- Shot types: `wide-angle`, `close-up`, `macro`, `birds-eye view`
- Lighting: `natural lighting`, `studio lighting`, `golden hour`, `dramatic side lighting`
- Mood: `cinematic`, `editorial`, `corporate photography`

---

## Composition and Quality

### Composition Terms
| Term | Effect |
|---|---|
| `rule-of-thirds` | Key elements at grid intersections |
| `centered composition` | Symmetrical, formal feel |
| `asymmetrical balance` | Dynamic, modern feel |
| `leading lines` | Eye directed along a path |
| `generous white space` | Room to breathe, less clutter |

### Quality Modifiers
Add these at the end of every prompt:
```
clean, professional, sharp focus, high contrast
```

For premium/executive presentations, add:
```
premium aesthetic, refined typography, elegant spacing
```

### Negative Prompting
Use constraints to prevent common problems. Write in positive framing when possible:

**Standard set for most slides:**
```
No bullet point lists, no decorative borders, no clip art,
no watermark, generous white space. All text in [language].
```

**Additional for data slides:**
```
No 3D chart effects, no gradient backgrounds behind text.
```

---

## Proven Templates

### Mind Map / Hub-and-Spoke
```
Landscape 16:9 mind map infographic. Clean white background,
minimal and professional design.
Topic: [TOPIC]. Center: [CENTER NODE] with [ICON].
Branch 1: [CATEGORY] — [details]
Branch 2: [CATEGORY] — [details]
Branch 3: [CATEGORY] — [details]
Use soft muted colors. Simple flat professional icons.
Thin clean connecting lines. All text in Thai.
```

### Neo Brutalism Cards
```
Landscape 16:9 infographic in Neo Brutalism style with bold
black borders. Title: "[ASSERTION HEADLINE]".
Show [N] items as blocks with thick borders.
Each block has Thai text label and icon.
[COLOR PALETTE] with [ACCENT] accents.
Clean, professional, sharp focus, generous white space.
No decorative elements. All text in Thai.
```

### Split-Screen Comparison
```
Landscape 16:9 infographic. Split-screen comparison layout.
[VISUAL STYLE].
Title: "[ASSERTION HEADLINE]".
Left side: "[LABEL A]" with [description of content].
Right side: "[LABEL B]" with [description of content].
Color: [PRIMARY] and [ACCENT] on [BACKGROUND].
Asymmetrical balance, generous white space 40%.
Clean, professional, sharp focus.
No bullet lists, no decorative borders. All text in Thai.
```

### Timeline / Process
```
Landscape 16:9 infographic. Horizontal timeline layout.
[VISUAL STYLE].
Title: "[ASSERTION HEADLINE]".
[N] stages from left to right:
Stage 1: [LABEL] — [detail]
Stage 2: [LABEL] — [detail]
Stage 3: [LABEL] — [detail]
Connected by thin arrows. Each stage has simple icon above.
Color: [PALETTE]. Clean, professional, sharp focus.
No bullet lists, generous white space. All text in Thai.
```

### Single Dramatic Statistic
```
Landscape 16:9 slide. Centered composition.
[VISUAL STYLE].
Large number "[STAT]" prominently centered.
Subtitle: "[CONTEXT SENTENCE]".
Color: [ACCENT] number on [DARK BACKGROUND].
Dramatic, high contrast, generous white space.
Minimal elements, no decorations. Text in Thai.
```

### Full-Bleed Quote
```
Landscape 16:9 slide. Full-bleed layout.
Background: [DESCRIPTION — e.g., soft gradient or abstract shapes].
Quote: "[EXACT QUOTE TEXT]" in large white text, centered.
Attribution: "[NAME, TITLE]" below quote in smaller text.
[STYLE]. Premium aesthetic, cinematic feel.
No borders, no logos. Text in Thai.
```

---

## Common Failures

| Symptom | Cause | Fix |
|---|---|---|
| "We didn't quite get that" | Prompt too vague or too short | Add specific layout, style, and content details |
| Text is blurry/unreadable | Photorealistic style with text overlay | Switch to flat vector or isometric style |
| Content rejected/blocked | Figurative language, metaphors | Use literal descriptions only — "abstract burst shapes" not "explosive impact" |
| Layout is wrong | No layout specified or vague description | Use exact layout term from vocabulary list |
| Style inconsistent across slides | Different style per prompt | Copy the exact same style phrase to every prompt |
| Too cluttered | No white space instruction | Add "generous white space 40%" and "no decorative elements" |
| Wrong language | Language not specified | Always end with "All text in [language]" |
| Data is made up | Let Gemini invent numbers | Always provide exact data in prompt |

### Recovery Strategy
If a prompt fails:
1. Don't retry the exact same prompt — it will fail again
2. Make the prompt more specific (add layout, style, or content detail)
3. If figurative language was used, rewrite with literal descriptions
4. If still failing, simplify: reduce content and use a more common layout pattern
5. For persistent failures, try a different tab (infographic → slide or vice versa)
