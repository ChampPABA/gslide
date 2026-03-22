---
name: gslide
description: "Automate Google Slides generation via browser automation using the gslide CLI. Make sure to use this skill whenever the user wants to create slides, generate presentations, or make infographics in Google Slides — even if they just say 'ทำ slide', 'gen slide', 'make slides', 'create infographic', or 'Help me visualize'. Also use when the user has any content (NotebookLM notes, pasted text, a storytelling plan, a document, or just a topic) and wants to turn it into a visual presentation. Don't wait for the user to say 'gslide' explicitly — if they want slides, use this skill."
---

# gslide — Google Slides AI Generation

Plan, write Gemini prompts, and generate slides in Google Slides using the "Help me visualize" (Gemini) feature via browser automation.

This skill owns the **full generation pipeline**:
1. Gather content from the user (any source — text, file, topic, plan)
2. Define a design system for visual consistency
3. Plan slides (layout, type, headline per slide)
4. Write detailed Gemini prompts
5. Save to `slides/{project-slug}-prompts.json`
6. Create presentation and execute batch generation

---

## Pre-check

```bash
gslide --help
```

If not installed:
> gslide is not installed. Run: `npm install -g @champpaba/gslide`

```bash
gslide auth status
```

If not logged in:
> Run `gslide auth login` in your terminal (needs interactive browser).

---

## CLI Commands

### Authentication
```bash
gslide auth login     # Opens headed browser — user logs in, presses Enter to save
gslide auth status    # Check if session is valid
gslide auth logout    # Delete saved session
```

### Single Slide Generation
```bash
gslide gen infographic --presentation <ID> --prompt "..." --timeout 120
gslide gen slide --presentation <ID> --prompt "..." --timeout 120
gslide gen image --presentation <ID> --prompt "..." --slide-index 3 --insert-as image --timeout 120
```

### Batch Generation
```bash
# Validate first
gslide gen batch --file slides/my-project-prompts.json --dry-run

# Generate all
gslide gen batch --file slides/my-project-prompts.json --timeout 120 --continue-on-error
```

### Utility
```bash
gslide update    # Self-update to latest version
```

---

## Workflow

### Step 1 — Gather Content

Accept content in any form — text, file path, topic, storytelling plan, NotebookLM notes. Read files if paths are provided. Do not ask the user to restructure their content.

Ask only if genuinely missing:
- **Topic / content** — what the slides are about
- **Audience** — who will see this (affects vocabulary, tone, depth)
- **Slide count or duration** — default 8–12 slides if not specified
- **Visual style** — ask if no preference; otherwise default to `flat vector, clean minimal`

### Step 2 — Define Design System

Lock the visual language before writing any prompt. This is what keeps every slide looking like the same deck.

Derive from content and user preferences:

```
Design System
─────────────
Style:               [e.g. kawaii flat vector, pastel palette]
Primary color:       #hex
Accent color:        #hex
Background opening:  #hex  ← title, closing, divider slides
Background content:  #hex  ← all other slides
Character:           [if using characters — gender, face, hair, outfit, expression style]
                     e.g. "cute kawaii girl, round face, big sparkling eyes, short bob hair, pastel pink outfit with bow"
Decoration set:      [decorative elements repeated across slides]
                     e.g. "star sparkles, rounded pill badges, coin icons, soft drop shadows"
```

Show the design system to the user for confirmation. A locked design system gets embedded in every prompt — this is the only reliable way to achieve visual consistency across slides.

### Step 3 — Plan Slides

Create a slide-by-slide plan as a table. Each slide has exactly one idea.

```
| # | Type       | Headline (full-sentence assertion)                          | Layout              | Tab         |
|---|------------|-------------------------------------------------------------|---------------------|-------------|
| 1 | Title      | [thesis of the whole presentation — full sentence]          | full-bleed          | infographic |
| 2 | Problem    | [what's wrong and why it matters — 8+ words]                | split-screen        | infographic |
| 3 | Data       | [key statistic as a sentence]                               | centered            | slide       |
```

Rules:
- Every headline is a **full-sentence assertion** — not a label. Min 8 English words / 20 Thai characters. Research shows audiences understand and remember assertion headlines significantly better than topic labels — "อินฟลูเอนเซอร์โดนภาษีย้อนหลัง 5 ปีเพราะไม่รู้กฎ" beats "ปัญหาภาษี" every time.
- Alternate dense slides (data/process) with breathing slides (divider/quote) — never 3+ dense in a row.
- Use layout terms that Gemini recognizes (see `references/prompt-engineering.md` — Layout Vocabulary section).

Ask the user to approve: "แก้ไขอะไรไหม? เพิ่ม/ลด/สลับ slide ได้เลย" — iterate before proceeding.

### Step 4 — Write Gemini Prompts

Write a detailed, self-contained Gemini prompt for every slide. Read `references/prompt-engineering.md` for the full guide. The 9-component structure (ordered by token weight — Gemini weighs earlier tokens more heavily):

```
[1] Landscape 16:9 [infographic/slide].
[2] [Layout pattern name] layout.
[3] [Visual style — from design system].
[4] Title: "[exact assertion headline]".
[5] [Specific content — exact text, numbers, data, structure].
[6] [Colors from design system] on [background from design system].
[7] [Composition rule], generous white space.
[8] Clean, sharp focus, vibrant colors.
[9] No bullet lists. All text in [language].
```

**Embedding the design system:**

- **Character** (slides that feature a character): include full character description verbatim from the design system.
  > "cute kawaii girl character — round face, big sparkling eyes, short bob hair, pastel pink outfit with bow"

- **Background**: use `background_opening` for title/divider/closing slides, `background_content` for everything else.

- **Decorations**: list the specific decoration set elements that fit this slide's content.

Every prompt must be **self-contained** — gslide passes only the prompt to Gemini, nothing else.

Show progress as you write:
```
กำลังเขียน prompts 12 slides...
✅ Slide 1/12 — Title
✅ Slide 2/12 — Problem
...
```

### Step 5 — Save Prompts File

Save to `slides/{project-slug}-prompts.json` in the current working directory.

The project slug is derived from the topic: lowercase, hyphenated, ASCII.
> "influencer tax guide" → `slides/influencer-tax-guide-prompts.json`

**Format:**
```json
{
  "presentation_id": "",
  "slides": [
    {"tab": "infographic", "prompt": "Landscape 16:9 infographic..."},
    {"tab": "slide", "prompt": "Landscape 16:9 slide..."}
  ]
}
```

Valid tab values: `slide`, `infographic`, `image`

Tell the user the path and offer to review any specific prompt before generating.

### Step 6 — Create Presentation

Ask the user for a Google Slides presentation ID/URL, or create one:

```bash
# If user has gws installed:
gws slides presentations create --json '{"title": "My Presentation"}'
```

Once you have the ID, update the `presentation_id` field in the prompts JSON file.

### Step 7 — Generate

```bash
# Dry run first
gslide gen batch --file slides/my-project-prompts.json --dry-run

# Generate all slides
gslide gen batch --file slides/my-project-prompts.json --timeout 120 --continue-on-error
```

Each slide takes 30–60 seconds. After completion, give the user the URL:
```
https://docs.google.com/presentation/d/{ID}/edit
```

Note: new presentations start with a blank first slide — user should delete it manually.

---

## Regenerating a Single Slide

If the user wants to change a specific slide after generation:

1. Revise the prompt (in the JSON file or ad-hoc)
2. Run single generation:
   ```bash
   gslide gen infographic --presentation <ID> --prompt "..." --timeout 120
   ```
3. User moves the new slide into position manually in Google Slides.

---

## Important Notes

- **Quota**: "Nano Banana" — limited uses per month per Google account
- **Vague prompts fail** with "We didn't quite get that" — always include layout, style, and specific content
- **Figurative language causes blocks** — use literal descriptions only ("abstract burst shapes" not "explosive impact")
- **Each slide takes 30–60 seconds** — batch of 12 slides ≈ 10 minutes
- **Headless after initial login** — first login requires headed browser (`gslide auth login`)

---

## Reference Files

| File | When to read |
|---|---|
| `references/prompt-engineering.md` | Step 4 — full prompt anatomy, layout/style vocabulary, proven templates, failure recovery |
