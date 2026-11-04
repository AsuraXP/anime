#!/bin/bash
# Mux the rendered video with the mixed audio track and deliver 2K 1440x2560.
# If out/video.mp4 is already 1440x2560 (GPU build) the video stream is copied;
# otherwise (CPU 1080x1920 build) it is lanczos-upscaled to 1440x2560 here.
# usage: bash scripts/mux.sh   (FFMPEG/FFPROBE env override the binaries)
set -e
cd "$(dirname "$0")/.."
FF="${FFMPEG:-$(command -v ffmpeg)}"
FP="${FFPROBE:-$(command -v ffprobe)}"
W="$("$FP" -v error -select_streams v:0 -show_entries stream=width -of csv=p=0 out/video.mp4)"
if [ "$W" = "1440" ]; then
  "$FF" -y -i out/video.mp4 -i audio/mix.wav -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -b:a 320k -movflags +faststart out/river-short-2k.mp4
else
  "$FF" -y -i out/video.mp4 -i audio/mix.wav -map 0:v:0 -map 1:a:0 \
    -vf "scale=1440:2560:flags=lanczos,format=yuv420p" -c:v libx264 -crf 16 -preset medium \
    -c:a aac -b:a 320k -movflags +faststart out/river-short-2k.mp4
fi
"$FP" -v error -show_entries format=duration,size:stream=codec_name,width,height,r_frame_rate,sample_rate,channels -of json out/river-short-2k.mp4
