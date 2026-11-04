#!/bin/bash
# ============================================================================
# build.sh — one-command 2D short build. 2D canvas renders fast even on CPU;
# on a GPU machine it's minutes. usage:
#   bash scripts/build.sh                 # voice+audio if missing, render 2K, mux, QA
#   SPLIT=1 bash scripts/build.sh         # split frame range in two parallel renders
#   COMP=Short2D bash scripts/build.sh    # 1080x1920 instead of 2K
# ============================================================================
set -euo pipefail
cd "$(dirname "$0")/.."
ROOT="$(pwd)"
COMP="${COMP:-Short2DX2}"

echo "== 1/6 deps =="
[ -d node_modules ] || npm ci --legacy-peer-deps
npm i --no-save playwright >/dev/null 2>&1 || true
python3 -c "import numpy, scipy, soundfile" 2>/dev/null || pip install --quiet --break-system-packages numpy scipy soundfile 2>/dev/null || pip install --quiet numpy scipy soundfile
FFBIN="$(node -p "try{require('@ffmpeg-installer/ffmpeg').path}catch(e){''}" 2>/dev/null || true)"
if [ -z "$FFBIN" ] || [ ! -x "$FFBIN" ]; then FFBIN="$(command -v ffmpeg || true)"; fi
export FFMPEG="$FFBIN"; export FFPROBE="$(command -v ffprobe || echo "$FFBIN")"
[ -n "$(command -v ffprobe)" ] && export FFPROBE="$(command -v ffprobe)"

if [ ! -f voice/voice.wav ]; then
  echo "== generating voice (edge-tts Andrew @ -20%) =="
  pip install --quiet --break-system-packages edge-tts 2>/dev/null || pip install --quiet edge-tts
  python3 scripts/tts_edge.py --voice "${TTS_VOICE:-en-US-AndrewNeural}" --rate "${TTS_RATE:--20%}"
fi
if [ ! -f audio/mix.wav ]; then
  echo "== mixing audio =="
  python3 scripts/mix_audio.py
fi
python3 scripts/gen_shots.py

echo "== 2/6 browser =="
export BROWSER="${BROWSER:-$(command -v google-chrome || command -v google-chrome-stable || command -v chromium || command -v chromium-browser || true)}"
if [ -z "${BROWSER:-}" ]; then
  npx --yes playwright install chromium >/dev/null 2>&1 || true
  export BROWSER="$(node -p "require('playwright').chromium.executablePath()" 2>/dev/null || find "$HOME/.cache/ms-playwright" -type f -name chrome -path '*chromium-*' 2>/dev/null | sort | tail -1)"
fi
echo "browser: $BROWSER"
export OPTS='{"gl":"swangle","args":["--no-sandbox","--disable-dev-shm-usage","--enable-unsafe-swiftshader","--disable-gpu","--mute-audio"]}'
export REMOTION_TMP="${REMOTION_TMP:-$(mktemp -d)}"

mkdir -p out
render_range () { # $1=frames $2=outfile
  npx remotion render src/index.ts "$COMP" "$2" --codec h264 --crf 16 --timeout=300000 \
    --frames="$1" --browser-executable="$BROWSER" --chromium-options="$OPTS"
}

echo "== 3/6 render ($COMP) =="
TOTALF=$(node -p "const s=require('fs').readFileSync('src/story.ts','utf8'); const m=[...s.matchAll(/b:\s*(\d+)/g)]; m[m.length-1][1]")
LAST=$((TOTALF-1))
if [ "${SPLIT:-0}" = "1" ]; then
  HALF=$((TOTALF/2))
  render_range "0-$((HALF-1))" out/part0.mp4 & P0=$!
  render_range "$HALF-$LAST" out/part1.mp4 & P1=$!
  wait $P0 $P1
  "$FFMPEG" -y -v error -i out/part0.mp4 -i out/part1.mp4 -filter_complex "[0:v][1:v]concat=n=2:v=1[outv]" -map "[outv]" -c:v libx264 -crf 16 -pix_fmt yuv420p out/video.mp4
else
  render_range "0-$LAST" out/video.mp4
fi

echo "== 4/6 mux =="
bash scripts/mux.sh

echo "== 5/6 loudness =="
"$FFMPEG" -nostats -i out/short-2d.mp4 -af ebur128=peak=true -f null - 2>&1 | tail -12

echo "== 6/6 frame QA =="
PATH="$(dirname "$FFMPEG"):$PATH" python3 scripts/short_qa.py out/short-2d.mp4 out/qa-final scripts/shots.json || true
echo "DONE: $ROOT/out/short-2d.mp4"
