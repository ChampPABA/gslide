#!/bin/bash
set -e

echo "Installing gslide..."

# Install CLI
echo "  [1/2] Installing @ChampPABA/gslide CLI..."
npm install -g @ChampPABA/gslide

# Install skill
echo "  [2/2] Installing gslide skill for Claude Code..."
SKILL_DIR="$HOME/.claude/skills/gslide"
mkdir -p "$SKILL_DIR"

# Copy SKILL.md from npm package location
NPM_PREFIX="$(npm prefix -g)"
SKILL_SRC="$NPM_PREFIX/lib/node_modules/@ChampPABA/gslide/skills/gslide/SKILL.md"

if [ -f "$SKILL_SRC" ]; then
    cp "$SKILL_SRC" "$SKILL_DIR/SKILL.md"
else
    # Fallback: download from repo
    echo "  Copying from local..."
    SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
    if [ -f "$SCRIPT_DIR/skills/gslide/SKILL.md" ]; then
        cp "$SCRIPT_DIR/skills/gslide/SKILL.md" "$SKILL_DIR/SKILL.md"
    else
        echo "  ERROR: SKILL.md not found"
        exit 1
    fi
fi

echo ""
echo "Done!"
echo "  CLI:   gslide --help"
echo "  Skill: /gslide (in Claude Code)"
echo ""
echo "Next: gslide auth login"
