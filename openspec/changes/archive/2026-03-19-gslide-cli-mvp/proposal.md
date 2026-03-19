## Why

Google Slides "Help me visualize" (Gemini-powered) generates high-quality slides and infographics but has no public API — browser automation is the only way to access it programmatically. We need a CLI tool that automates this so Claude (via skill) or users can generate presentation slides from prompts without manual browser interaction.

## What Changes

- New Python CLI `gslide` with 6 commands: `auth login`, `auth status`, `gen slide`, `gen infographic`, `gen image`, `gen batch`
- Browser automation via Playwright to interact with "Help me visualize" UI (3 tabs: Slide, Infographic, Image)
- Session management using Playwright storage state (cookies) — login once, reuse until expired
- `gen batch` reads a `prompts.json` file to generate multiple slides in a single browser session
- Designed to work alongside `gws` CLI for REST API operations (create presentation, export, share)

## Capabilities

### New Capabilities
- `browser-auth`: Headed browser login flow, cookie extraction, session persistence and validation
- `gen-slide`: Browser automation to generate content via "Help me visualize" — navigate, select tab, type prompt, create, wait, insert. Handles all 3 tabs (Slide/Infographic/Image) with tab-specific insert logic
- `gen-batch`: Load prompts.json, loop through slides and images, manage browser session across multiple generations, error recovery and progress reporting
- `cli`: Click-based CLI entry point exposing auth and gen commands

### Modified Capabilities

(none — greenfield project)

## Impact

- **New dependencies**: playwright, click
- **New files**: `src/gslide/` package (~6 modules)
- **External systems**: Google Slides UI (browser automation target), Google auth (cookies)
- **Works with**: `gws` CLI for presentation CRUD and export (not part of this change)
