#!/usr/bin/env python3
# Build voice/voice.wav (48 kHz stereo 24-bit) + voice/words.json from the 3 generate_speech clips.
# Word timings are estimated proportionally to word length inside each clip (good enough for the
# music ducking key in mix; the voice itself is gain-only, no processing).
# usage: python scripts/make_voice.py
import json, os, re
import numpy as np
from scipy import signal

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
VOICE = os.path.join(ROOT, "voice")
SR = 48000
LEAD = 0.40          # silence before the first word
GAP = 0.35           # silence between clips
TAIL = 0.60

CHUNKS = [
    ("c0", "On June twenty-second, nineteen sixty-nine, the Cuyahoga River in Cleveland caught fire. Literally. "
           "It had burned a dozen times before, worst in nineteen fifty-two, over a million dollars in damage. "
           "Decades of oil had turned its surface into a greasy slick."),
    ("c1", "That Sunday, a freight train crossed the Campbell Road bridge. Sparks fell from its wheels onto the slick, "
           "and the river erupted, flames five stories high. Luckily, it was out in under half an hour, nobody hurt. "
           "Unluckily, a Time magazine photo of the fifty-two fire made Cleveland a national joke."),
    ("c2", "Why did it burn? Oil floats on water, and the vapor above it is what catches. Like a greasy pan: "
           "the pan never ignites, but a flame on the oil film goes up instantly. The outrage helped create the EPA "
           "in nineteen seventy, and the Clean Water Act in nineteen seventy-two. Today trout swim the Cuyahoga, "
           "and kayakers paddle where flames once rose. The river that burned is the river that came back."),
]


def read_wav_any(path):
    import wave
    with wave.open(path, "rb") as w:
        n, ch, sr, sw = w.getnframes(), w.getnchannels(), w.getframerate(), w.getsampwidth()
        raw = w.readframes(n)
    x = np.frombuffer(raw, "<i2" if sw == 2 else "<i4").astype(np.float64)
    x = x / (32768.0 if sw == 2 else 2147483648.0)
    if ch > 1:
        x = x.reshape(-1, ch).mean(axis=1)
    if sr != SR:
        from math import gcd
        g = gcd(SR, sr)
        x = signal.resample_poly(x, SR // g, sr // g)
    return x


def main():
    os.makedirs(VOICE, exist_ok=True)
    parts, words, t = [], [], LEAD
    for name, text in CHUNKS:
        x = read_wav_any(os.path.join(VOICE, name + ".wav"))
        parts.append(x)
        dur = len(x) / SR
        ws = re.findall(r"[A-Za-z0-9'-]+", text)
        lens = np.array([max(1, len(w)) for w in ws], dtype=np.float64)
        starts = np.concatenate([[0.0], np.cumsum(lens)[:-1]]) / lens.sum() * dur
        for w, s in zip(ws, starts):
            words.append({"w": w, "t0": round(t + s, 3), "t1": round(t + s + dur * (max(1, len(w)) / lens.sum()), 3)})
        t += dur + GAP
        parts.append(np.zeros(int(GAP * SR)))
    total = t - GAP + TAIL
    out = np.zeros(int(round(total * SR)))
    pos = int(LEAD * SR)
    for x in parts:
        out[pos:pos + len(x)] += x
        pos += len(x)
    # gentle 5 ms edge fades, then normalise to -3 dBFS peak (voice stays gain-only afterwards)
    fade = int(0.005 * SR)
    out[:fade] *= np.linspace(0, 1, fade)
    out[-fade:] *= np.linspace(1, 0, fade)
    out *= 0.7079 / (np.abs(out).max() + 1e-12)  # -3 dBFS
    st = np.stack([out, out], axis=1)
    import wave
    q = np.clip(np.round(st.T * 8388607.0), -8388608, 8388607).astype("<i4")
    data = np.ascontiguousarray(q).view(np.uint8).reshape(len(out), 2, 4)[:, :, :3].tobytes()
    with wave.open(os.path.join(VOICE, "voice.wav"), "wb") as w:
        w.setnchannels(2); w.setsampwidth(3); w.setframerate(SR); w.writeframes(data)
    json.dump(words, open(os.path.join(VOICE, "words.json"), "w"), indent=1)
    print(f"voice.wav {total:.3f} s, {len(words)} words, last word ends {words[-1]['t1']:.2f} s")


if __name__ == "__main__":
    main()
