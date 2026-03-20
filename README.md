# gslide

CLI tool for automating Google Slides' **"Help me visualize"** feature via browser automation. Generate slides, infographics, and images from the command line using Gemini's built-in generation capabilities.

## Prerequisites

- Node.js >= 16
- A Google account with access to Google Slides

## Installation

```bash
npm install -g @champpaba/gslide
```

The postinstall script automatically sets up:
- [uv](https://docs.astral.sh/uv/) (installed if not found)
- Python 3.10+ (installed via uv if not found)
- A virtual environment with the gslide Python package
- Chromium browser (via Playwright)

## Getting Started

### 1. Log in to Google

```bash
gslide auth login
```

This opens a Chromium browser for you to sign in to your Google account. The session is saved locally for future use.

### 2. Check auth status

```bash
gslide auth status
```

### 3. Generate content

**Single slide:**

```bash
gslide gen slide --presentation <ID_OR_URL> --prompt "Timeline of the Apollo program"
```

**Single infographic:**

```bash
gslide gen infographic --presentation <ID_OR_URL> --prompt "Key metrics for Q1 2026"
```

**Image on a specific slide:**

```bash
gslide gen image --presentation <ID_OR_URL> --prompt "A futuristic cityscape" \
  --slide-index 2 --insert-as image
```

`--insert-as` can be `image` (default) or `background`.

### 4. Batch generation

Create a `prompts.json` file:

```json
{
  "presentation_id": "your-presentation-id",
  "slides": [
    { "tab": "slide", "prompt": "Introduction to machine learning" },
    { "tab": "infographic", "prompt": "ML model comparison chart" }
  ],
  "images": [
    { "prompt": "Neural network diagram", "slide_index": 1, "insert_as": "image" }
  ]
}
```

Preview what will be generated:

```bash
gslide gen batch --file prompts.json --dry-run
```

Run the batch:

```bash
gslide gen batch --file prompts.json --continue-on-error
```

## Commands

| Command | Description |
|---------|-------------|
| `gslide auth login` | Launch browser for Google login |
| `gslide auth status` | Check if saved session is valid |
| `gslide auth logout` | Delete saved session |
| `gslide gen slide` | Generate a slide |
| `gslide gen infographic` | Generate an infographic |
| `gslide gen image` | Generate and insert an image |
| `gslide gen batch` | Generate from a prompts.json file |
| `gslide update` | Update to the latest version |

## How It Works

gslide uses Playwright to automate the Google Slides web interface. It interacts with the "Help me visualize" panel (powered by Gemini) to generate slides, infographics, and images based on your text prompts. Generation typically takes 30–60 seconds per item.

## License

MIT
