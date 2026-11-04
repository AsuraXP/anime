#!/usr/bin/env python3
# Generic mixer: voice unchanged + synthesized music (+3 dB, ducked -6 dB under words) + river-noise SFX (-6 dB),
# soft-limited to -2 dBTP, iterated to -15 LUFS integrated. Writes audio/mix.wav + stems.
# usage: python3 scripts/mix_audio.py   (needs voice/voice.wav + voice/words.json)
import json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from dsp import read_wav, write_wav, integrated, true_peak, lp, colored

SR = 48000
voice, sr = read_wav(os.path.join(ROOT, "voice", "voice.wav"))
v = voice.mean(axis=0) if voice.ndim > 1 else voice
words = json.load(open(os.path.join(ROOT, "voice", "words.json")))
import re as _re
_st = open(os.path.join(ROOT, "src", "story.ts")).read()
TOTAL = int(_re.findall(r"b:\s*(\d+)", _st)[-1])
N = int(TOTAL / 30 * SR) + int(0.5 * SR)
if len(v) < N:
    v = np.pad(v, (0, N - len(v)))
t = np.arange(N) / SR

# --- music: slow chord pad, progression Am F C G, ~2 chords/s ---
CHORDS = [[220.0, 261.63, 329.63], [174.61, 220.0, 261.63], [130.81, 196.0, 261.63], [196.0, 246.94, 293.66]]
music = np.zeros(N)
seg = SR * 4
for i in range(0, N, seg):
    ch = CHORDS[(i // seg) % 4]
    tt = t[i:i + min(seg, N - i)]
    w = np.minimum(1, tt - t[i] / 1) * 0 + np.minimum(1.0, (tt - t[i]) / 0.8) * np.minimum(1.0, (t[i + min(seg, N - i) - 1] - tt) / 0.8)
    for j, fr in enumerate(ch):
        music[i:i + len(tt)] += 0.16 * w * np.sin(2 * np.pi * fr * (tt - t[i]) + j)
        music[i:i + len(tt)] += 0.05 * w * np.sin(2 * np.pi * fr * 2.003 * (tt - t[i]))
music = lp(music, 3000)
music += 0.03 * np.sin(2 * np.pi * 55 * t)  # soft bass

# --- sfx: river noise (low-passed colored noise), constant, quiet ---
rng = np.random.default_rng(7)
sfx = lp(colored(N, rng), 900) * 0.5

# --- duck music under words (-6 dB), voice unchanged ---
duck = np.ones(N)
for w in words:
    a, b = int(w["t0"] * SR), int(w["t1"] * SR)
    a = max(0, a - int(0.15 * SR)); b = min(N, b + int(0.25 * SR))
    duck[a:b] = np.minimum(duck[a:b], 10 ** (-6 / 20))
music_d = music * duck

mix = v[:N] + music_d * 10 ** (3 / 20) + sfx * 10 ** (-6 / 20)

# --- soft limiter at -2 dBTP (4x lookahead), then min-gain loop to -15 LUFS ---
def limit(x, tp_db=-2.0):
    tp = 10 ** (tp_db / 20)
    red = 4
    env = np.abs(x)
    from scipy.ndimage import maximum_filter1d
    env = maximum_filter1d(env, size=red * 2 + 1)[::red][: len(x)]
    g = np.minimum(1.0, tp / np.maximum(env, 1e-9))
    from scipy.ndimage import minimum_filter1d
    g = minimum_filter1d(g, size=red * 48 * 2)  # slow release ~1 s
    g = np.clip(g, 0, 1)
    g4 = np.repeat(g, red)[: len(x)]
    return x * g4

mix = limit(mix)
for _ in range(60):
    lu = integrated(mix)
    if abs(lu + 15.0) < 0.05:
        break
    mix *= 10 ** ((-15.0 - lu) / 20)
    mix = limit(mix)

st = np.stack([mix, mix], axis=0)
os.makedirs(os.path.join(ROOT, "audio"), exist_ok=True)
write_wav(os.path.join(ROOT, "audio", "mix.wav"), st, 24)
write_wav(os.path.join(ROOT, "audio", "stem_voice.wav"), np.stack([v[:N], v[:N]], 0), 24)
write_wav(os.path.join(ROOT, "audio", "stem_music.wav"), np.stack([music_d * 10 ** (3 / 20)] * 2, 0), 24)
write_wav(os.path.join(ROOT, "audio", "stem_sfx.wav"), np.stack([sfx * 10 ** (-6 / 20)] * 2, 0), 24)
print(f"mix.wav {N/SR:.2f}s  {integrated(mix):.2f} LUFS  TP {true_peak(mix):.2f} dBTP")
