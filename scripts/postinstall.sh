#!/bin/bash
set -e

PKG_DIR="$(cd "$(dirname "$0")/.." && pwd)"
VENV_DIR="$PKG_DIR/.venv"
UV_BIN=""

echo "Installing gslide..."

# Step 1: Check/install uv
echo "  [1/4] Checking uv..."
if command -v uv &>/dev/null; then
    UV_BIN="$(command -v uv)"
    echo "         found: $UV_BIN"
else
    echo "         not found, installing..."
    curl -LsSf https://astral.sh/uv/install.sh | sh 2>/dev/null
    export PATH="$HOME/.local/bin:$PATH"
    if command -v uv &>/dev/null; then
        UV_BIN="$(command -v uv)"
        echo "         installed: $UV_BIN"
    else
        echo "         ERROR: Failed to install uv. Install manually: https://docs.astral.sh/uv/"
        exit 1
    fi
fi

# Step 2: Check/install Python
echo "  [2/4] Checking Python 3.10+..."
PYTHON_VERSION=$("$UV_BIN" python find 3.10 2>/dev/null || true)
if [ -z "$PYTHON_VERSION" ]; then
    echo "         not found, installing via uv..."
    "$UV_BIN" python install 3.10 2>/dev/null
    PYTHON_VERSION=$("$UV_BIN" python find 3.10 2>/dev/null || true)
fi
if [ -z "$PYTHON_VERSION" ]; then
    echo "         ERROR: Could not install Python 3.10+."
    exit 1
fi
echo "         found: $PYTHON_VERSION"

# Step 3: Create venv and install gslide
echo "  [3/4] Installing gslide package..."
if [ ! -d "$VENV_DIR" ]; then
    "$UV_BIN" venv "$VENV_DIR" --python 3.10 2>/dev/null
fi
"$UV_BIN" pip install --python "$VENV_DIR/bin/python" -e "$PKG_DIR" 2>/dev/null
echo "         done"

# Step 4: Install Playwright Chromium
echo "  [4/5] Installing Chromium browser..."
PLAYWRIGHT_BIN="$VENV_DIR/bin/playwright"
if [ -f "$PLAYWRIGHT_BIN" ]; then
    "$PLAYWRIGHT_BIN" install chromium 2>/dev/null
    echo "         done"
else
    echo "         WARNING: playwright not found, skipping Chromium install"
    echo "         Run manually: $VENV_DIR/bin/playwright install chromium"
fi

# Step 5: Link Claude Code skill
echo "  [5/5] Linking Claude Code skill..."
SKILL_DIR="$HOME/.claude/skills/gslide"
SKILL_SRC="$PKG_DIR/skills/gslide/SKILL.md"

if [ -f "$SKILL_SRC" ]; then
    mkdir -p "$SKILL_DIR"
    ln -sf "$SKILL_SRC" "$SKILL_DIR/SKILL.md"
    echo "         linked: $SKILL_DIR/SKILL.md -> $SKILL_SRC"
else
    echo "         skipped (SKILL.md not found)"
fi

echo ""
echo "Ready! Run: gslide auth login"
echo "  Skill: /gslide (in Claude Code)"
