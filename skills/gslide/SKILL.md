---
name: gslide
description: "Automate Google Slides generation via browser automation using the gslide CLI. Use this skill whenever the user wants to create slides, generate presentations, make infographics, or turn content into Google Slides. Triggers on: 'ทำ slide', 'สร้าง slide', 'สร้าง presentation', 'gen slide', 'make slides', 'generate presentation', 'create infographic', 'gslide', 'Help me visualize'. Also use when user has content from NotebookLM, documents, or pasted text and wants to visualize it as slides."
---

# gslide — Google Slides AI Generation

Generate slides, infographics, and images in Google Slides using the "Help me visualize" (Gemini) feature via browser automation.

## Pre-check

Before using any gslide command, verify the tool is available:

```bash
gslide --help
```

If not installed, tell the user:
> gslide is not installed. Run: `npm install -g @champpaba/gslide`

If installed, check auth:
```bash
gslide auth status
```

If not logged in, tell the user:
> Run `gslide auth login` in your terminal (needs interactive browser).

## CLI Commands

### Authentication

```bash
gslide auth login     # Opens headed browser — user logs in, presses Enter to save
gslide auth status    # Check if session is valid
gslide auth logout    # Delete saved session
```

### Single Slide Generation

```bash
# Generate infographic
gslide gen infographic --presentation <ID> --prompt "..." --timeout 120

# Generate slide
gslide gen slide --presentation <ID> --prompt "..." --timeout 120

# Generate image on specific slide
gslide gen image --presentation <ID> --prompt "..." --slide-index 3 --insert-as image --timeout 120
```

### Batch Generation

```bash
# Validate prompts file
gslide gen batch --file prompts.json --dry-run

# Generate all slides
gslide gen batch --file prompts.json --timeout 120 --continue-on-error
```

### Utility

```bash
gslide update    # Self-update to latest version
```

## Workflow

When user wants slides, follow this sequence:

### 1. Gather Content
Ask: what content should be on the slides? Sources can be:
- NotebookLM notebook (use `notebooklm ask`)
- Pasted text from user
- Documents in the project

### 2. Plan Slides
Discuss with user:
- How many slides?
- What's on each slide? (one idea per slide)
- Who's the audience?

Present a slide plan as a table for approval:
```
| # | เนื้อหา | Layout |
|---|---------|--------|
| 1 | Title   | split left-right |
| 2 | Problem | 3 cards horizontal |
```

### 3. Create Presentation
Either use an existing presentation ID, or create new:
```bash
# If user has gws installed:
gws slides presentations create --json '{"title": "My Presentation"}'
```
Or ask the user for the presentation URL/ID.

### 4. Generate Slides
For each slide, run gslide gen with a detailed prompt.

Each prompt should be a single string describing the slide. Generation takes 30-60 seconds per slide. The tool handles: open panel → select tab → type prompt → click Create → wait for preview → click preview → Insert on new slide.

### 5. Report Results
After generation, give user the presentation URL:
```
https://docs.google.com/presentation/d/{ID}/edit
```

## prompts.json Format

For batch generation, create a JSON file:

```json
{
  "presentation_id": "abc123...",
  "slides": [
    {"tab": "infographic", "prompt": "detailed prompt here..."},
    {"tab": "slide", "prompt": "detailed prompt here..."}
  ],
  "images": [
    {"target_slide": 2, "prompt": "image prompt", "insert_as": "image"}
  ]
}
```

Valid tab values: `slide`, `infographic`, `image`

## Important Notes

- Generation uses Google's "Nano Banana" quota — limited uses per month per account
- New presentations start with a blank first slide — user should delete it manually after generation
- Prompts that are too vague will fail with "We didn't quite get that" — be specific and detailed
- Each slide takes 30-60 seconds to generate
- The tool works in headless mode after initial login (which requires headed browser)
