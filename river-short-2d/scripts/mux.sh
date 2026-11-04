#!/bin/bash
# Mux render + mix into the deliverable. usage: bash scripts/mux.sh
set -e
cd "$(dirname "$0")/.."
FF="${FFMPEG:-$(command -v ffmpeg)}"
FP="${FFPROBE:-$(command -v ffprobe)}"
W="$("$FP" -v error -select_streams v:0 -show_entries stream=width -of csv=p=0 out/video.mp4)"
if [ "$W" = "1440" ]; then
  "$FF" -y -i out/video.mp4 -i audio/mix.wav -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -b:a 320k -movflags +faststart -shortest out/short-2d.mp4
else
  "$FF" -y -i out/video.mp4 -i audio/mix.wav -map 0:v:0 -map 1:a:0 \
    -vf "scale=1440:2560:flags=lanczos,format=yuv420p" -c:v libx264 -crf 16 -preset medium \
    -c:a aac -b:a 320k -movflags +faststart -shortest out/short-2d.mp4
fi
"$FP" -v error -show_entries format=duration,size:stream=codec_name,width,height,r_frame_rate,sample_rate,channels -of json out/short-2d.mp4
