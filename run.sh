#!/usr/bin/env bash
set -euo pipefail

# Simple project launcher
# - creates a virtualenv (prefers .venv, falls back to venv)
# - installs requirements
# - runs streamlit

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

# prefer existing .venv, then venv, otherwise create .venv
if [ -d ".venv" ]; then
  VENV_DIR=".venv"
elif [ -d "venv" ]; then
  VENV_DIR="venv"
else
  python3 -m venv .venv
  VENV_DIR=".venv"
fi

PY="$VENV_DIR/bin/python"
PIP="$VENV_DIR/bin/python -m pip"

# Only upgrade/install when the virtualenv was just created or when requirements.txt changed.
# Store a short checksum of requirements.txt inside the venv and skip installs when it matches.
REQ_HASH_FILE="$VENV_DIR/.requirements.hash"
if [ ! -f "$REQ_HASH_FILE" ]; then
  NEED_INSTALL=1
else
  CUR_HASH=$(shasum -a 1 requirements.txt | awk '{print $1}')
  SAVED_HASH=$(cat "$REQ_HASH_FILE" 2>/dev/null || true)
  if [ "$CUR_HASH" != "$SAVED_HASH" ]; then
    NEED_INSTALL=1
  else
    NEED_INSTALL=0
  fi
fi

if [ "$NEED_INSTALL" -eq 1 ]; then
  $PIP install --upgrade --disable-pip-version-check pip
  $PIP install --disable-pip-version-check -r requirements.txt
  # Save the current requirements hash so we can skip future installs
  shasum -a 1 requirements.txt | awk '{print $1}' > "$REQ_HASH_FILE"
else
  echo "Requirements unchanged; skipping pip install."
fi

# Run Streamlit
exec $PY -m streamlit run src/app.py
