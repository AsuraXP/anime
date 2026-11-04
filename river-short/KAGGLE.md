# Render on Kaggle (free T4 x2 GPU) — copy-paste cells

1. Kaggle → New Notebook → **Accelerator: GPU (T4 x2)** → **Internet: ON**.
2. Paste these cells and run top to bottom:

```python
# Cell 1 — fetch ONLY the river-short folder from the repo (sparse clone, fast)
!git clone --branch arena/5087ed9f-anime --depth 1 --filter=blob:none --sparse https://github.com/AsuraXP/anime.git
!cd anime && git sparse-checkout set river-short
%cd anime/river-short
```

```python
# Cell 2 — pull the latest fixes, then full build: npm ci -> chromium -> GPU probe
# (3 frames; auto-falls back to CPU if WebGL-on-GPU fails) -> render -> mux -> QA
# SPLIT=1 uses both T4s (two frame halves in parallel on separate GPUs)
!cd /kaggle/working/anime && git pull --ff-only
!cd river-short && SPLIT=1 bash scripts/build.sh
```

```python
# Cell 3 — pack the deliverable for download
!cd /kaggle/working/anime/river-short && ls -la out/ && zip -q -j /kaggle/working/river-short-2k.mp4.zip out/river-short-2k.mp4 && ls -la /kaggle/working/*.zip
```

3. Download: right panel → **Output** → `river-short-2k.mp4.zip` (or open `out/qa-final/` contact sheets there too).

Expected time on T4 x2: **~15–30 min total** (vs ~3 h on this 2-core sandbox).
Result: `out/river-short-2k.mp4` — 1440×2560, 30 fps, 64.3 s, h264 + AAC, audio −15 LUFS / −2.4 dBTP.

Notes
- If the GPU path fails, `build.sh` automatically falls back to CPU swiftshader (slower, still correct; then the mux upscales 1080×1920 → 1440×2560).
- Override browser with `BROWSER=$(which google-chrome) bash scripts/build.sh` if needed.
- No Kaggle? Any machine with a GPU + node 18+ works the same: clone the branch, `cd river-short`, `bash scripts/build.sh`.
