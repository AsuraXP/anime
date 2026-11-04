# The fast workflow for making a 9:16 animated short (lessons from this project)

Goal: **script → video in ~1–1.5 h on a free GPU**, with every step reproducible from the repo.

## The pipeline, end to end

1. **Script** (`SCRIPT.md`) — plain text, one narrator, English, jokes = verified facts only. 15 min.
2. **Voice** — one voice, 2–4 TTS clips → `voice/voice.wav` + `voice/words.json` via `scripts/make_voice.py`.
   Cache it in git; never re-audition per build. **Watch sample rates**: TTS clips often come as 44.1 kHz —
   resample to 48 kHz with the correct ratio or the voice comes out sped-up/pitched (this happened here).
3. **Scene code** — `src/videos/*`: three.js world (Kenney GLB kits, committed in `public/`), flat-shaded cast,
   per-shot cameras in `story.ts`, post passes (ink/bloom/grade). Composition 1080×1920@30; render 1440×2560 on GPU.
   Make all per-frame animation **deterministic** (seeded noise, frame-indexed curves — never `Math.random()` per frame).
4. **QA stills loop (the cheap, high-value step)** — `bash scripts/stills.sh out/qa 30,300,500,935,1500,1900 0.5`
   renders many frames in ONE browser launch (~2–5 s/frame at half res even on CPU). Inspect every shot boundary
   and extreme; fix cameras/framing here. Repeat until clean. Minutes per iteration, not hours.
5. **Audio** — `python scripts/river_audio.py` → `audio/mix.wav`: voice unchanged, music +3 dB, SFX −6 dB,
   music ducked under words, limiter to −1.2 dBTP, iterate to **−15 LUFS**. Verify with
   `ffmpeg -af ebur128=peak=true`. Check the RMS-envelope spectrum for ~0.5–1 Hz pumping (audible "wobble")
   and smooth duck attack/release if present.
6. **Final render — always on GPU** (free Kaggle T4×2): clone sparse → `SPLIT=1 bash scripts/build.sh`.
   Native 2K in **~15–25 min**. The script self-probes: it must see `NVIDIA` in the WebGL renderer string
   (not SwiftShader), writes `/etc/vulkan/icd.d/nvidia_icd.json` itself if the container lacks it, uses
   `--timeout=300000`, splits frames across both GPUs, muxes, and runs QA. CPU fallback exists but is hours.
7. **Mux + frame QA** — `scripts/mux.sh` (stream-copy if already 1440×2560, else lanczos upscale; AAC 320k,
   faststart) → `python scripts/short_qa.py out/river-short-2k.mp4 out/qa-final scripts/shots.json`
   (specs, loudness, black/frozen/pop detection, per-shot stats, contact sheets).
8. **Deliver** — download from Kaggle Output (`zip` the mp4 first), or `git add -f` + push it to the repo branch.

## Kaggle one-pager (GPU T4×2, Internet ON)
```python
!git clone --branch arena/5087ed9f-anime --depth 1 --filter=blob:none --sparse https://github.com/AsuraXP/anime.git
!cd anime && git sparse-checkout set river-short && cd river-short
!SPLIT=1 bash scripts/build.sh
!zip -q -j /kaggle/working/river-short-2k.mp4.zip out/river-short-2k.mp4
```

## Do
- Iterate on **stills**, render the **full video once** (or twice) at the end.
- Keep everything in git on the session branch and push — sandboxes get reset.
- Batch stills in one browser session; use integer output dims (`--width/--height` or a 2K composition, never `--scale 1.3333`).
- Verify GPU by renderer string; verify loudness with `ebur128=peak=true`; verify framing with stills at shot extremes.
- Keep character rigs + camera language between videos — they're the reusable 90%.

## Don't (all learned the hard way here)
- Don't render full videos on CPU — 3 h+ vs 20 min on a T4.
- Don't trust flag-based GPU detection alone — containers hide the NVIDIA Vulkan ICD; check the renderer string.
- Don't render one still per browser launch (~30 s each) — batch them.
- Don't regenerate voice/audio on every iteration — cache artifacts.
- Don't hand-wind quad normals without checking `(b-a)×(d-a)` winding.
- Don't assume a patch script applied all edits — grep-verify each one.
- Don't use unseeded per-frame randomness — frames must be reproducible.
- Don't rely on Remotion's default 30 s `delayRender` timeout — pass `--timeout=300000`.

## Optional simplification
The Remotion/React wrapper can be dropped entirely: plain `index.html` + three.js (import map) driven by a
global frame variable, plus a ~100-line playwright capture script (seek frame → `canvas.toDataURL()` →
ffmpeg stitch). Same output, fewer dependencies — Remotion only adds the preview UI. Ask for the `plain/` variant.

## Time budget for a new short
script 15 min → voice 15 min → scene + stills loop 30–40 min → audio 20 min → GPU render + QA ~25 min.
