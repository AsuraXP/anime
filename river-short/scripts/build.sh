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
npm i --no-save playwright >/dev/null 2>&1 || true   # only used by scripts/gpu-check.cjs
python3 -c "import numpy, PIL" 2>/dev/null || pip install --quiet numpy pillow

# ffmpeg/ffprobe from npm packages (no system install needed)
FFBIN="$(node -p "require('@ffmpeg-installer/ffmpeg').path")"
FPBIN="$(node -p "require('@ffprobe-installer/ffprobe').path")"
export PATH="$(dirname "$FFBIN"):$(dirname "$FPBIN"):$PATH"
export FFMPEG="$FFBIN"

# chromium: prefer a system chrome (Kaggle images ship google-chrome), else @sparticuz/chromium, else playwright
if [ -z "${BROWSER:-}" ]; then
  BROWSER="$(command -v google-chrome || command -v google-chrome-stable || command -v chromium || command -v chromium-browser || true)"
fi
if [ -z "${BROWSER:-}" ] || [ ! -x "$BROWSER" ]; then
  BROWSER="$(node -p "require('@sparticuz/chromium').executablePath()" 2>/dev/null || true)"
fi
if [ -z "${BROWSER:-}" ]; then
  echo "no system chromium found; installing playwright chromium..." >&2
  npm i --no-save playwright >/dev/null 2>&1 || true
  npx --yes playwright install chromium --with-deps || npx --yes playwright install chromium
  BROWSER="$(node -p "require('playwright').chromium.executablePath()" 2>/dev/null || true)"
fi
if [ -z "${BROWSER:-}" ] || [ ! -x "$BROWSER" ]; then
  BROWSER="$(find "$HOME/.cache/ms-playwright" -type f -name chrome -path "*chromium-*" 2>/dev/null | sort | tail -1)"
fi
if [ -z "${BROWSER:-}" ] || [ ! -x "$BROWSER" ]; then
  BROWSER="$(find "$HOME/.cache/ms-playwright" -type f -name headless_shell 2>/dev/null | sort | tail -1)"
fi
if [ -z "${BROWSER:-}" ] || [ ! -x "$BROWSER" ]; then
  echo "ERROR: no usable chromium found" >&2; exit 1
fi
echo "browser: $BROWSER"

# GPU? then let Chrome use it (ANGLE/Vulkan). CPU-only? swiftshader.
if command -v nvidia-smi >/dev/null 2>&1 && nvidia-smi -L 2>/dev/null | grep -q GPU; then
  NGPU="$(nvidia-smi -L 2>/dev/null | grep -c GPU || true)"
  echo "== GPU detected: $NGPU x $(nvidia-smi -L | head -1 | sed 's/.*: //') =="
  NGPU="${NGPU:-1}"
  # Point Chrome's Vulkan/EGL at the NVIDIA driver explicitly — in containers the
  # default ICD search often misses nvidia_icd.json and Chrome silently picks SwiftShader.
  NVIDIA_ICDS="$(grep -l -i nvidia /usr/share/vulkan/icd.d/*.json /etc/vulkan/icd.d/*.json /usr/local/share/vulkan/icd.d/*.json 2>/dev/null | paste -sd: - || true)"
  if [ -n "$NVIDIA_ICDS" ]; then
    export VK_ICD_FILENAMES="$NVIDIA_ICDS${VK_ICD_FILENAMES:+:$VK_ICD_FILENAMES}"
    export VK_DRIVER_FILES="$NVIDIA_ICDS${VK_DRIVER_FILES:+:$VK_DRIVER_FILES}"
    echo "   VK_ICD_FILENAMES=$VK_ICD_FILENAMES"
  else
    echo "   WARNING: no nvidia vulkan ICD json found; Chrome may fall back to SwiftShader" >&2
  fi
  export __GLX_VENDOR_LIBRARY_NAME=nvidia
  [ -d /usr/share/glvnd/egl_vendor.d ] && export __EGL_VENDOR_LIBRARY_DIRS=/usr/share/glvnd/egl_vendor.d
else
  NGPU=0
fi
OPTS='{"gl":"swangle","args":["--no-sandbox","--disable-dev-shm-usage","--mute-audio"]}'
COMP=RiverShort   # defaults; the probe below may upgrade to GPU/2K

mkdir -p out
PRE=""   # optional launch wrapper, e.g. "xvfb-run -a" for a headed GPU candidate
probe () { # $1=chromium-options json  $2=composition ; renders 10 frames, echoes avg seconds/frame (999 on failure)
  rm -f out/probe.mp4
  local s=$SECONDS
  if ! env $PRE npx remotion render src/index.ts "$2" out/probe.mp4 --codec h264 --crf 20 --frames=0-9 \
       --timeout=300000 --browser-executable="$BROWSER" --chromium-options="$1" > out/probe.log 2>&1; then
    echo 999; return 1
  fi
  echo $(( (SECONDS - s) / 10 ))
}
gpu_renderer () { # $1=chromium-options json ; echoes the WebGL renderer string ("" on failure)
  env $PRE OPTS_JSON="$1" BROWSER="$BROWSER" node scripts/gpu-check.cjs 2>/dev/null | sed -n 's/^WEBGL_RENDERER=//p'
}
# Select a backend. A GPU candidate is accepted only if the browser's WebGL renderer is a real
# NVIDIA GPU (not SwiftShader) AND a 10-frame probe averages <=10 s/frame. Otherwise CPU swiftshader.
# Candidates: native vulkan (headless) -> angle-egl (headless) -> angle-egl headed under Xvfb.
OK=0
if [ "${NGPU:-0}" -ge 1 ]; then
  while IFS='|' read -r name cand pre; do
    [ -z "$name" ] && continue
    OPTS="$cand"; COMP=RiverShort2K; PRE="$pre"
    R="$(gpu_renderer "$OPTS")"
    echo "== candidate $name: WebGL renderer = ${R:-<none>} =="
    case "$R" in
      *NVIDIA*|*GeForce*|*Quadro*|*Tesla*|*"T4"*|*"T4 "*|*T40*)
        SPF="$(probe "$OPTS" "$COMP")" && SPF="${SPF:-999}"
        echo "   probe: ${SPF}s/frame"
        if [ "${SPF:-999}" -le 10 ]; then OK=1; break; fi
        ;;
    esac
  done <<'CANDS'
vulkan|{"gl":"vulkan","args":["--no-sandbox","--disable-dev-shm-usage","--mute-audio"]}|
angle-egl|{"gl":"angle-egl","args":["--no-sandbox","--disable-dev-shm-usage","--mute-audio"]}|
egl-xvfb|{"gl":"angle-egl","headless":false,"args":["--no-sandbox","--disable-dev-shm-usage","--mute-audio"]}|xvfb-run -a
CANDS
fi
if [ "$OK" = 0 ]; then
  PRE=""
  OPTS='{"gl":"swangle","args":["--no-sandbox","--disable-dev-shm-usage","--mute-audio"]}'
  COMP=RiverShort
  echo "== no usable GPU; probing CPU swiftshader (1080p) =="
  probe "$OPTS" "$COMP" >/dev/null || { echo "all backends failed; see out/probe.log" >&2; exit 1; }
fi
echo "== backend selected: $COMP wrapper='${PRE}' (${SPF:-?}s/frame on probe) =="
render_range () { # $1=frames  $2=outfile  $3=extra env
  env $3 $PRE npx remotion render src/index.ts "$COMP" "$2" --codec h264 --crf 16 --timeout=300000 \
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
      OPTS='{"gl":"swangle","args":["--no-sandbox","--disable-dev-shm-usage","--mute-audio"]}'
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
