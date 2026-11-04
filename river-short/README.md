# "The River That Caught Fire" — original 64 s vertical short

Built with the cloned skill pipeline (Remotion + three.js, flat cartoon characters in a 3D toon world,
all original art/script/sound — no reference characters, voices, or scripts).

- Specs: 1440x2560 (2K), 30 fps, 1930 frames = 64.333 s, h264 crf 16 + AAC 320k audio.
- Story: the 22 June 1969 Cuyahoga River fire (Cleveland, Ohio) — verified real facts only:
  train sparks on the Campbell Road trestle ignited the oil slick, flames five stories high, out in
  20–30 min, no injuries; 13th fire (1952 ~$1.5M, Time photo); oil-floats/greasy-pan physics;
  EPA 1970 / Clean Water Act 1972; trout + kayakers today. Twist: "The river that burned is the river that came back."
- No captions/labels in the video; single steady English voice (voice-01, 165 words, 62.5 s).

## Pipeline (reproducible)
1. `src/videos/story.ts` — 14 shots, cameras, timing (IGNITE 19.70 s, train 12.9–18.9 s, fire out 29 s).
2. `src/videos/{world,build,cast,lights,paint,toon,grade}.ts` — river world: Kenney nature/fantasy GLBs
   (26 models in `public/river/kenney/`), trestle, fireboat, kitchen analogy scene, no-dumping sign,
   billboarded flat-shaded cast with LOD tiers, per-shot lighting (day/smoke/golden), oil-slick water shader.
3. Voice: 3 clips from the registered voice → `scripts/make_voice.py` → `voice/voice.wav` (48 kHz stereo
   24-bit) + `voice/words.json` (word timings for ducking).
4. Audio: `python scripts/river_audio.py` → `audio/mix.wav` — original synthesized score + SFX (numpy/scipy,
   `scripts/dsp.py`); voice unchanged, music +3 dB, SFX −6 dB, music −3 dB under words;
   master **−15.0 LUFS integrated / −2.4 dBTP** (own BS.1770 meter, cross-checked with ffmpeg ebur128).
5. QA stills: `node scripts/river-stills.mjs out/qa <frames> 0.5` (sandbox Chromium, swiftshader).
6. Final render: composition at 1440x2560, `npx remotion render src/index.ts RiverShort out/video.mp4
   --codec h264 --crf 16` (browser-executable /tmp/chromium, swiftshader).
7. Mux: `bash scripts/mux.sh` → `out/river-short-2k.mp4` (`-map 0:v:0 -map 1:a:0`).
8. Frame QA: `python scripts/short_qa.py out/river-short-2k.mp4 out/qa-final scripts/shots.json`.

## Files
- `src/` — Remotion app (`index.ts`, `root.tsx`, `videos/River.tsx`, world modules).
- `voice/` — c0–c2.wav clips, voice.wav, words.json. `audio/` — mix.wav + stems + cues.md.
- `out/` — QA stills, test renders, final `video.mp4` and `river-short-2k.mp4`.

## One-script build on a fresh machine / Kaggle GPU
```bash
git clone https://github.com/AsuraXP/river-short.git && cd river-short
bash scripts/build.sh          # auto-detects NVIDIA GPU (fast), else CPU swiftshader
SPLIT=1 bash scripts/build.sh  # 2+ GPUs: renders the two frame halves in parallel on separate GPUs
```
`scripts/build.sh` does: `npm ci` → chromium via `@sparticuz/chromium` (or system/playwright) →
`remotion render` (1080×1920, crf 16; GPU via ANGLE/Vulkan when `nvidia-smi` is present) →
`scripts/mux.sh` (lanczos upscale to 1440×2560 + `audio/mix.wav`, AAC 320k) →
ebur128 loudness check → `scripts/short_qa.py` frame QA into `out/qa-final/`.
Result: `out/river-short-2k.mp4`. Voice/audio are committed (`voice/`, `audio/`), so no external
voice service is needed to rebuild.

## Two compositions
- `RiverShort` — 1080×1920, MSAA off: CPU/sandbox build (swiftshader), `mux.sh` upscales to 2K.
- `RiverShort2K` — native 1440×2560, MSAA 4: GPU build (Kaggle/local GPU), mux copies the stream.
`scripts/build.sh` picks automatically (`nvidia-smi` present → `RiverShort2K`).

## Making another video
Reuse everything except the story: new `SCRIPT.md` → new voice wav/words → new `story.ts`
(shots, cameras, timings) → `river_audio.py` cues → `build.sh`. World, cast, post passes,
audio DSP and QA scripts are story-agnostic. On a GPU the render is minutes, so a new
short is ~1–1.5 h end to end instead of ~5 h on a 2-core CPU sandbox.
