#!/bin/bash
# make.sh — staged, cached pipeline. usage:
#   bash scripts/make.sh voice     # (re)generate voice via edge-tts (Andrew @ -20%)
#   bash scripts/make.sh audio     # rebuild audio/mix.wav
#   bash scripts/make.sh stills 0,60,180,300   # batched QA stills at half res
#   bash scripts/make.sh build     # render + mux + QA (SPLIT=1 to halve render time)
#   bash scripts/make.sh all 0,60,180,300      # voice+audio if missing, stills, build
set -euo pipefail
cd "$(dirname "$0")/.."
CMD="${1:-all}"; shift || true
case "$CMD" in
  voice)  pip install --quiet --break-system-packages edge-tts numpy scipy soundfile 2>/dev/null || pip install --quiet edge-tts numpy scipy soundfile
          FFMPEG="$(command -v ffmpeg || true)" python3 scripts/tts_edge.py --voice "${TTS_VOICE:-en-US-AndrewNeural}" --rate "${TTS_RATE:--20%}" ;;
  audio)  [ -f voice/voice.wav ] || bash "$0" voice
          python3 scripts/mix_audio.py ;;
  stills) bash scripts/stills.sh "${1:-out/qa}" "${2:-0,60,180,300}" "${3:-0.5}" ;;
  build)  bash scripts/build.sh ;;
  all)    [ -f voice/voice.wav ] || bash "$0" voice
          [ -f audio/mix.wav ] || bash "$0" audio
          bash scripts/stills.sh out/qa "${1:-0,60,180,300}" 0.5
          bash scripts/build.sh ;;
  *) echo "usage: make.sh voice|audio|stills|build|all"; exit 1 ;;
esac
