#!/bin/bash
# Batched QA stills (one browser launch). usage: bash scripts/stills.sh out/qa 0,60,180,300 [scale]
set -euo pipefail
cd "$(dirname "$0")/.."
PREFIX="${1:-out/qa}"; FRAMES="${2:-0,60,180,300}"; SCALE="${3:-0.5}"
[ -d node_modules ] || npm ci --legacy-peer-deps
npm i --no-save playwright >/dev/null 2>&1 || true
export BROWSER="${BROWSER:-$(command -v google-chrome || command -v chromium || command -v chromium-browser || true)}"
if [ -z "${BROWSER:-}" ]; then
  npx --yes playwright install chromium >/dev/null 2>&1 || true
  export BROWSER="$(node -p "require('playwright').chromium.executablePath()" 2>/dev/null || find "$HOME/.cache/ms-playwright" -type f -name chrome -path '*chromium-*' 2>/dev/null | sort | tail -1)"
fi
export OPTS='{"gl":"swangle","args":["--no-sandbox","--disable-dev-shm-usage","--enable-unsafe-swiftshader","--disable-gpu","--mute-audio"]}'
export REMOTION_TMP="${REMOTION_TMP:-$(mktemp -d)}"
echo "browser: $BROWSER"
node scripts/river-stills.mjs "$PREFIX" "$FRAMES" "$SCALE"
