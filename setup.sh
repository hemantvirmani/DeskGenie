#!/usr/bin/env bash
# =============================================================================
# DeskGenie Setup Script
# Works on: Linux, macOS, Windows (Git Bash)
# =============================================================================

set -e  # Exit immediately on error

BOLD="\033[1m"
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
RESET="\033[0m"

print_step()  { echo -e "\n${BOLD}>>> $1${RESET}"; }
print_ok()    { echo -e "  ${GREEN}✔ $1${RESET}"; }
print_warn()  { echo -e "  ${YELLOW}⚠ $1${RESET}"; }
print_error() { echo -e "  ${RED}✘ $1${RESET}"; }

# Detect OS / shell environment
detect_os() {
  case "$OSTYPE" in
    msys*|cygwin*|mingw*) echo "windows" ;;
    darwin*)              echo "mac" ;;
    linux*)               echo "linux" ;;
    *)                    echo "unknown" ;;
  esac
}

OS=$(detect_os)

echo ""
echo -e "${BOLD}======================================"
echo -e " DeskGenie Setup"
echo -e "======================================${RESET}"
echo ""
echo "  Detected OS: $OS"

# ---------------------------------------------------------------------------
# 1. Check Python
# ---------------------------------------------------------------------------
print_step "Checking Python"

PYTHON=""
for cmd in python3 python; do
  if command -v "$cmd" &>/dev/null; then
    version=$("$cmd" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null)
    major=$(echo "$version" | cut -d. -f1)
    minor=$(echo "$version" | cut -d. -f2)
    if [ "$major" -ge 3 ] && [ "$minor" -ge 10 ]; then
      PYTHON="$cmd"
      print_ok "Found Python $version ($cmd)"
      break
    else
      print_warn "$cmd found but version $version < 3.10 — skipping"
    fi
  fi
done

if [ -z "$PYTHON" ]; then
  print_error "Python 3.10+ not found. Install it from https://www.python.org/downloads/"
  exit 1
fi

# ---------------------------------------------------------------------------
# 2. Create virtual environment
# ---------------------------------------------------------------------------
print_step "Creating virtual environment"

if [ -d "venv" ]; then
  print_warn "venv/ already exists — skipping creation"
else
  $PYTHON -m venv venv
  print_ok "Created venv/"
fi

# Activate (path differs on Windows vs Unix)
if [ "$OS" = "windows" ]; then
  ACTIVATE="venv/Scripts/activate"
else
  ACTIVATE="venv/bin/activate"
fi

# shellcheck disable=SC1090
source "$ACTIVATE"
print_ok "Virtual environment activated"

# ---------------------------------------------------------------------------
# 3. Install Python dependencies
# ---------------------------------------------------------------------------
print_step "Installing Python dependencies"
pip install --upgrade pip --quiet
pip install -r requirements.txt
print_ok "Python dependencies installed"

# ---------------------------------------------------------------------------
# 4. Check Node / npm and install frontend dependencies
# ---------------------------------------------------------------------------
print_step "Installing frontend dependencies"

if ! command -v npm &>/dev/null; then
  print_warn "npm not found — skipping frontend setup."
  print_warn "Install Node.js from https://nodejs.org/ then run: cd frontend && npm install"
else
  NODE_VERSION=$(node --version 2>/dev/null || echo "unknown")
  print_ok "Found Node.js $NODE_VERSION"
  (cd frontend && npm install)
  print_ok "Frontend dependencies installed"
fi

# ---------------------------------------------------------------------------
# 5. Copy sample config to platform-specific location
# ---------------------------------------------------------------------------
print_step "Setting up user config"

case "$OS" in
  windows)
    CONFIG_DIR="${LOCALAPPDATA}/DeskGenie"
    ;;
  mac)
    CONFIG_DIR="${HOME}/Library/Application Support/DeskGenie"
    ;;
  *)
    CONFIG_DIR="${HOME}/.local/share/DeskGenie"
    ;;
esac

mkdir -p "$CONFIG_DIR"

if [ -f "$CONFIG_DIR/config.json" ]; then
  print_warn "Config already exists at: $CONFIG_DIR/config.json"
else
  cp config.sample.json "$CONFIG_DIR/config.json"
  print_ok "Config copied to: $CONFIG_DIR/config.json"
  echo "      Edit this file to add your folder aliases and preferences."
fi

# ---------------------------------------------------------------------------
# 6. Google API key
# ---------------------------------------------------------------------------
print_step "Google API Key"

ENV_FILE=".env"

if [ -f "$ENV_FILE" ] && grep -q "GOOGLE_API_KEY" "$ENV_FILE" 2>/dev/null; then
  print_warn ".env already contains GOOGLE_API_KEY — skipping."
else
  echo ""
  echo "  DeskGenie requires a Google API key (Gemini) to function."
  echo "  Get one free at: https://aistudio.google.com/app/apikey"
  echo ""
  read -r -p "  Enter your Google API key (or press Enter to skip): " API_KEY
  if [ -n "$API_KEY" ]; then
    echo "GOOGLE_API_KEY=$API_KEY" >> "$ENV_FILE"
    print_ok "Key saved to .env"
  else
    print_warn "Skipped. Remember to set GOOGLE_API_KEY before running the app."
  fi
fi

# ---------------------------------------------------------------------------
# Done
# ---------------------------------------------------------------------------
echo ""
echo -e "${BOLD}${GREEN}======================================"
echo " Setup complete!"
echo -e "======================================${RESET}"
echo ""
echo "  To start DeskGenie, open two terminals from this directory:"
echo ""
echo -e "  ${BOLD}Terminal 1 — Backend:${RESET}"

if [ "$OS" = "windows" ]; then
  echo "    source venv/Scripts/activate"
else
  echo "    source venv/bin/activate"
fi

if [ -f "$ENV_FILE" ]; then
  echo "    export \$(grep -v '^#' .env | xargs)"
fi

echo "    python app/main.py"
echo ""
echo -e "  ${BOLD}Terminal 2 — Frontend (dev mode):${RESET}"
echo "    cd frontend"
echo "    npm run dev"
echo ""
echo "  Then open: http://localhost:5173"
echo ""
