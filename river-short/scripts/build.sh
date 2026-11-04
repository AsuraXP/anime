#!/bin/bash
# ============================================================================
# build.sh — one-shot build of "The River That Caught Fire" (64 s, 9:16).
# Run on any machine with internet (incl. a Kaggle GPU notebook terminal):
#
#   git clone https://github.com/AsuraXP/river-short.git && cd river-short
#   bash scripts/build.sh            # auto-detects GPU; falls back to CPU
#   SPLIT=1 bash scripts/build.sh    # on 2+ GPUs: split frames across GPUs
#
# Produces out/river-short-2k.mp4 (1440x2560 h264 + AAC, -15 LUFS) and the
# frame-QA report in out/qa-final/.
# ============================================================================
set -euo pipefail
cd "$(dirname "$0")/.."
ROOT="$(pwd)"

echo "== 1/5 dependencies =="
if [ ! -d node_modules ]; then
  npm ci --legacy-peer-deps
fi
python3 -c "import numpy, PIL" 2>/dev/null || pip install --quiet numpy pillow

# ffmpeg/ffprobe from npm packages (no system install needed)
FFBIN="$(node -p "require('@ffmpeg-installer/ffmpeg').path")"
FPBIN="$(node -p "require('@ffprobe-installer/ffprobe').path")"
export PATH="$(dirname "$FFBIN"):$(dirname "$FPBIN"):$PATH"
export FFMPEG="$FFBIN"

# chromium: @sparticuz/chromium (downloads on first run); fallback to system
if [ -z "${BROWSER:-}" ]; then
  BROWSER="$(node -p "require('@sparticuz/chromium').executablePath().catch?.(()=>'') || require('@sparticuz/chromium').executablePath()" 2>/dev/null || true)"
fi
if [ -z "${BROWSER:-}" ] || [ ! -x "$BROWSER" ]; then
  BROWSER="$(command -v chromium || command -v chromium-browser || command -v google-chrome || true)"
fi
if [ -z "${BROWSER:-}" ]; then
  echo "no chromium found; installing via npx playwright..." >&2
  npx --yes playwright@latest install chromium --with-deps || npx --yes playwright@latest install chromium
  BROWSER="$(node -p "require('playwright').chromium.executablePath()")"
fi
echo "browser: $BROWSER"

# GPU? then let Chrome use it (ANGLE/Vulkan). CPU-only? swiftshader.
if command -v nvidia-smi >/dev/null 2>&1 && nvidia-smi -L 2>/dev/null | grep -q GPU; then
  NGPU="$(nvidia-smi -L 2>/dev/null | grep -c GPU || true)"
  echo "== GPU detected: $NGPU x $(nvidia-smi -L | head -1 | sed 's/.*: //') =="
  OPTS='{"gl":"angle","args":["--no-sandbox","--disable-dev-shm-usage","--mute-audio","--use-angle=vulkan","--enable-unsafe-vulkan","--enable-gpu-rasterization","--disable-software-rasterizer"]}'
  COMP=RiverShort2K   # native 1440x2560 + MSAA4 on GPU
  # fall back to swiftshader if the GPU run fails
  GPU_OK=1
else
  NGPU=0
  OPTS='{"gl":"swangle","args":["--no-sandbox","--disable-dev-shm-usage","--enable-unsafe-swiftshader","--disable-gpu","--mute-audio"]}'
  COMP=RiverShort     # 1080x1920, mux.sh upscales
fi

mkdir -p out
render_range () { # $1=frames  $2=outfile  $3=extra env
  env $3 npx remotion render src/index.ts "$COMP" "$2" --codec h264 --crf 16 \
    --frames="$1" --browser-executable="$BROWSER" --chromium-options="$OPTS"
}

echo "== 2/5 render =="
if [ "${SPLIT:-0}" = "1" ] && [ "${NGPU:-0}" -ge 2 ]; then
  echo "splitting 1930 frames across $NGPU GPUs"
  HALF=$((1930/2))
  render_range "0-$((HALF-1))"   out/part0.mp4 "CUDA_VISIBLE_DEVICES=0" &
  P0=$!
  render_range "$HALF-1929"      out/part1.mp4 "CUDA_VISIBLE_DEVICES=1" &
  P1=$!
  wait $P0 $P1
  "$FFBIN" -y -v error -i out/part0.mp4 -i out/part1.mp4 -filter_complex "[0:v][1:v]concat=n=2:v=1[outv]" -map "[outv]" -c:v libx264 -crf 16 -pix_fmt yuv420p out/video.mp4
else
  if ! render_range "0-1929" out/video.mp4 ""; then
    if [ "${NGPU:-0}" -ge 1 ]; then
      echo "GPU render failed; retrying with swiftshader (CPU)"
      OPTS='{"gl":"swangle","args":["--no-sandbox","--disable-dev-shm-usage","--enable-unsafe-swiftshader","--disable-gpu","--mute-audio"]}'
      COMP=RiverShort
      render_range "0-1929" out/video.mp4 ""
    else
      exit 1
    fi
  fi
fi

echo "== 3/5 mux (upscale 1080x1920 -> 1440x2560 + audio) =="
bash scripts/mux.sh

echo "== 4/5 loudness check =="
"$FFBIN" -nostats -i out/river-short-2k.mp4 -af ebur128=peak=true -f null - 2>&1 | tail -12

echo "== 5/5 frame QA =="
python3 scripts/short_qa.py out/river-short-2k.mp4 out/qa-final scripts/shots.json

echo "DONE: $ROOT/out/river-short-2k.mp4"
