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
4. Write each slide: Gemini prompt + speaker script + presenter notes (all together, one slide at a time)
5. Save to `slides/{project-slug}-deck.json` + export `slides/{project-slug}-script.md`
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
gslide gen batch --file slides/my-project-deck.json --dry-run

# Generate all
gslide gen batch --file slides/my-project-deck.json --timeout 120 --continue-on-error
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
- **Presentation mode** — is this a live talk, self-running kiosk, or read-at-own-pace? Affects script pace and pacing.

### Step 2 — Define Design System

Lock the visual language before writing any prompt. This is what keeps every slide looking like the same deck.

Derive from content and user preferences, then output as a JSON block — this exact block gets embedded verbatim as the `design_system` field in the final deck file:

```json
"design_system": {
  "style": "flat vector, clean minimal corporate",
  "primary_color": "#1A56DB",
  "accent_color": "#3B82F6",
  "background_opening": "#1A3A6B",
  "background_content": "#FFFFFF",
  "character": "cute kawaii girl, round face, big sparkling eyes...",  // omit if no character
  "decoration_set": "star sparkles, rounded pill badges, soft drop shadows"  // omit if no decoration
}
```

Show this JSON to the user for confirmation. A locked design system gets embedded in every prompt — this is the only reliable way to achieve visual consistency across slides.

### Step 3 — Plan Slides

Create a slide-by-slide plan as a table. Each slide has exactly one idea.

```
| # | Type       | Headline (full-sentence assertion)                          | Layout              | Tab              | Duration |
|---|------------|-------------------------------------------------------------|---------------------|------------------|----------|
| 1 | Title      | [thesis of the whole presentation — full sentence]          | full-bleed          | infographic      | 30s      |
| 2 | Problem    | [what's wrong and why it matters — 8+ words]                | split-screen        | infographic      | 60s      |
| 3 | Data       | [key statistic as a sentence]                               | centered            | slide            | 45s      |
```

Valid `tab` values: `infographic` (AI-generated visual), `slide` (text + layout), `image` (image inserted into existing slide).

Rules:
- Every headline is a **full-sentence assertion** — not a label. Min 8 words. Research shows audiences understand and remember assertion headlines significantly better than topic labels — "An influencer got hit with 5 years of back taxes for not knowing the rules" beats "Tax issues" every time.
- Alternate dense slides (data/process) with breathing slides (divider/quote) — never 3+ dense in a row.
- Use layout terms that Gemini recognizes (see `references/prompt-engineering.md` — Layout Vocabulary section).
- Include estimated duration per slide — this will be confirmed when scripts are written in Step 4.

Ask the user to confirm or adjust the plan — they can add, remove, or reorder slides. Iterate before proceeding.

### Step 4 — Write Gemini Prompts + Presenter Layer (one slide at a time)

For each slide, write **both** the Gemini prompt AND all presenter fields together before moving to the next slide. Do not write all prompts first and scripts later — doing them together keeps the content coherent and ensures nothing is skipped.

**Gemini prompt** — 9-component structure (ordered by token weight — Gemini weighs earlier tokens more heavily):

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

**Presenter fields** — write these for the same slide immediately after its prompt. Every slide object has exactly 5 fields: `tab`, `prompt`, plus the 3 presenter fields below. All go inside the same JSON object — not in a separate file or structure:

```json
{
  "tab": "infographic",
  "prompt": "Landscape 16:9 infographic...",
  "speaker_script": "Welcome everyone. Today we're going to learn about...",
  "duration_seconds": 45,
  "presenter_notes": "Stand at front, make eye contact, wait for everyone to settle before advancing."
}
```

**`speaker_script`** — the exact words the presenter says out loud while this slide is showing. Write naturally — how a human actually talks, not reads. Include pauses (`...`), emphasis cues (*bold the key word*), and rhetorical questions if they fit the slide.

**`duration_seconds`** — derived from the script length:
- Thai: ~150 syllables/min for workshop pace → ~**200 Thai characters per minute** (comfortable, with pauses)
- English: ~**130 words per minute** at presentation pace
- Add 5–10s buffer per slide for transitions + audience reaction time
- Title/closing slides: 20–30s (no dense content, just land the moment)
- Formula (Thai): `ceil(len(script_chars) / 200 * 60) + 8`
- Formula (English): `ceil(word_count / 130 * 60) + 8`

**`presenter_notes`** — physical and verbal cues for the presenter:
- Where to stand, where to point
- When to pause and ask the audience a question
- When to hand out materials or demo something
- Technical reminders ("click to reveal animation", "open live demo here")
- Timing checkpoint ("should be at ~4 min mark by this slide")

Show progress as you write each slide:
```
Writing 6 slides (prompt + script)...
✅ Slide 1/6 — Title (30s)
✅ Slide 2/6 — Overview (75s)
✅ Slide 3/6 — Flow 1 (90s)
...
Total: 450s = 7m 30s
```

After all slides, calculate `total_duration_seconds` = sum of all `duration_seconds`, and include it at the top level of the JSON. Check against the user's target: if total exceeds it, flag which slides to tighten; if total falls more than 15% short, expand the speaker scripts on content-heavy slides before saving.

### Step 5 — Save Deck File + Auto-export Script

Two files are always produced together — they serve different audiences:

| File | Audience | Purpose |
|---|---|---|
| `slides/{slug}-deck.json` | Machine (gslide CLI) + master record | Source of truth, all fields |
| `slides/{slug}-script.md` | Presenter (human) | Printable speaker guide |

The project slug is derived from the topic: lowercase, hyphenated, ASCII.
> "leave policy onboarding" → `slides/leave-policy-onboarding-deck.json` + `slides/leave-policy-onboarding-script.md`

**File naming rule:** The JSON file must end with `-deck.json`. The old convention `-prompts.json` is deprecated — do not use it.

**Step 5a — Save the JSON master:**

Every slide object must have all 5 fields — `tab`, `prompt`, `speaker_script`, `duration_seconds`, `presenter_notes`. These were written together in Step 4 and all belong in the JSON.

The JSON root has **4 required top-level fields**: `design_system`, `presentation_id`, `total_duration_seconds`, and `slides`. Paste the `design_system` JSON block from Step 2 verbatim — do not recreate it, do not omit it:

**Before writing the file, verify all 4 top-level keys are present. Missing `design_system` is the single most common mistake.**

```json
{
  "design_system": {
    "style": "flat vector, clean minimal corporate",
    "primary_color": "#1A3C6E",
    "accent_color": "#2D8BFF",
    "background_opening": "#1A3C6E",
    "background_content": "#FFFFFF"
  },
  "presentation_id": "",
  "total_duration_seconds": 450,
  "slides": [
    {
      "tab": "infographic",
      "prompt": "Landscape 16:9 infographic...",
      "speaker_script": "Welcome everyone. Today we'll cover something that trips up a lot of people...",
      "duration_seconds": 45,
      "presenter_notes": "Stand at front, make eye contact, wait for the room to settle before advancing."
    }
  ]
}
```

- `total_duration_seconds` = sum of all `duration_seconds` — always at top level (duration check happens in Step 4)
- Valid `tab` values: `slide`, `infographic`, `image`
- `gslide` CLI only reads `tab` and `prompt` — other fields are ignored by CLI, safe to include

**Anti-pattern — do not use a `_meta` section:**
```json
{
  "_meta": {
    "speaker_script": { "slide_1": "..." }  ← wrong: scripts belong inside each slide
  },
  "slides": [
    {"tab": "infographic", "prompt": "..."}  ← missing 3 presenter fields
  ]
}
```
Every field belongs inside its own slide object — regardless of how many slides the deck has.

**Step 5b — Export the Markdown script immediately after saving JSON:**

Check if `scripts/export-script.py` exists in the project CWD. If not, read the bundled template at `scripts/export-script.py` (relative to this skill's directory) and write it to `scripts/export-script.py` in the project CWD:

```bash
mkdir -p scripts slides
```

Then run from the **project root** (not from inside `scripts/`):

```bash
python3 scripts/export-script.py slides/{slug}-deck.json
```

This auto-generates the output path as `slides/{slug}-script.md` — **always in `slides/`, never in `scripts/`**. Do not pass `-o` to override this path. The script.md lives next to its deck JSON in `slides/`, not in `scripts/`.

Example: `python3 scripts/export-script.py slides/leave-policy-onboarding-deck.json` → `slides/leave-policy-onboarding-script.md`

Tell the user both file paths once saved.

### Step 6 — Create Presentation

Ask the user for a Google Slides presentation ID/URL, or offer to create one:

```bash
# If user has gws installed:
gws slides presentations create --json '{"title": "My Presentation"}'
```

If `gws` is not installed, ask the user to create a blank presentation at https://slides.google.com and paste the URL or ID. The ID is the long string in the URL: `docs.google.com/presentation/d/{ID}/edit`.

Once you have the ID, update the `presentation_id` field in the deck JSON file.

### Step 7 — Generate

```bash
# Dry run first
gslide gen batch --file slides/my-project-deck.json --dry-run

# Generate all slides
gslide gen batch --file slides/my-project-deck.json --timeout 120 --continue-on-error
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

## Reference Files

| File | When to use |
|---|---|
| `references/prompt-engineering.md` | Step 4 — Gemini prompt anatomy, layout vocabulary, failure recovery |
| `scripts/export-script.py` | Step 5b — bundled export script; copy to project `scripts/` if not present |

---

## Important Notes

- **Quota**: "Nano Banana" — limited uses per month per Google account
- **Vague prompts fail** with "We didn't quite get that" — always include layout, style, and specific content
- **Figurative language causes blocks** — use literal descriptions only ("abstract burst shapes" not "explosive impact")
- **Each slide takes 30–60 seconds** — batch of 12 slides ≈ 10 minutes
- **Headless after initial login** — first login requires headed browser (`gslide auth login`)
- **Slide transitions are manual** — set visual effects (fade, slide, etc.) in Google Slides UI after generation

---

