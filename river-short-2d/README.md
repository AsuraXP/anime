# short-2d — fast 2D vertical-short pipeline (vector stage + cutout character)

Much cheaper per frame than the 3D project (`../river-short/`): no WebGL, so 10-minute videos
(18,000 frames) render in ~30–90 min on a free Kaggle T4×2 (or a few hours on CPU), and stills
iterate in seconds.

## Make a video
1. Write `SCRIPT2D.md` (one paragraph per narration chunk; 10 min ≈ 1,800–2,000 words at Andrew −20%).
2. Edit the shot table in `src/story.ts` (`SHOTS`: a, b, from/to camera `{x,y,z,roll}` — 10 min ≈ 40–60 rows).
3. Run on Kaggle (GPU optional — 2D doesn't need it; internet ON for edge-tts):

```python
# Kaggle notebook cells — %cd PERSISTS between cells; !cd does NOT:
!git clone --branch arena/5087ed9f-anime --depth 1 --filter=blob:none --sparse https://github.com/AsuraXP/anime.git
!cd anime && git sparse-checkout set river-short-2d
%cd /kaggle/working/anime/river-short-2d
```
```python
!bash scripts/make.sh all 0,120,240,359     # voice (edge-tts Andrew -20%) -> mix -> stills -> render 2K -> QA
# or stage by stage:
#   bash scripts/make.sh voice             # edge-tts -> voice/voice.wav + words.json + src/words.gen.json
#   bash scripts/make.sh audio             # audio/mix.wav  (-15 LUFS / -2 dBTP)
#   bash scripts/make.sh stills 0,120,240  # batched QA stills (out/qa-f*.jpg)
#   SPLIT=1 bash scripts/make.sh build     # render Short2DX2 (1440x2560) split in two -> out/short-2d.mp4
```
4. Download `out/short-2d.mp4` (Kaggle Output panel) or `out/qa-final/` contact sheets.

## Files
- `src/story.ts` — shot table + camera interpolation (the only file you edit per video, besides the script).
- `src/videos/world.tsx` — flat SVG world (sky, skyline, factory, trestle bridge, river, trees). Ink = SVG stroke.
- `src/videos/cast.tsx` — 2D character rig (walk cycle + mouth shapes from `src/words.gen.json`).
- `src/videos/Scene.tsx` — camera transform + grade overlay.
- `scripts/tts_edge.py` — edge-tts voice with real word timestamps (default `en-US-AndrewNeural`, `-20%`).
- `scripts/mix_audio.py` — voice unchanged, music +3 dB ducked −6 dB under words, SFX −6 dB, −15 LUFS / −2 dBTP.
- `scripts/build.sh` / `mux.sh` / `gen_shots.py` / `short_qa.py` — render, mux, QA.
- `scripts/stills.sh` — batched QA stills in one browser launch.
