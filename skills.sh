#!/bin/bash
set -e

echo "Installing gslide..."

# Install CLI
echo "  [1/2] Installing @champpaba/gslide CLI..."
npm install -g @champpaba/gslide

# Install skill as symlink (auto-updates when npm updates)
echo "  [2/2] Linking gslide skill for Claude Code..."
SKILL_DIR="$HOME/.claude/skills/gslide"
NPM_PREFIX="$(npm prefix -g)"
SKILL_SRC="$NPM_PREFIX/lib/node_modules/@champpaba/gslide/skills/gslide/SKILL.md"

mkdir -p "$SKILL_DIR"

if [ -f "$SKILL_SRC" ]; then
    ln -sf "$SKILL_SRC" "$SKILL_DIR/SKILL.md"
    echo "         linked: $SKILL_DIR/SKILL.md -> $SKILL_SRC"
else
    echo "  ERROR: SKILL.md not found at $SKILL_SRC"
    exit 1
fi

echo ""
echo "Done!"
echo "  CLI:   gslide --help"
echo "  Skill: /gslide (in Claude Code)"
echo ""
echo "  Skill is symlinked — updates automatically with: gslide update"
echo ""
echo "Next: gslide auth login"
