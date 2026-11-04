#!/usr/bin/env python3
# Original soundtrack for "The River That Caught Fire": synthesized music + SFX (numpy/scipy only,
# helpers from dsp.py) + final mix. Voice = voice/voice.wav (gain only).
# Mix standard: voice unchanged, music +3 dB, SFX -6 dB (stem levels), music ducked -3 dB under words,
# master -15.0 LUFS integrated, true peak <= -1.2 dBTP, exactly 1930/30 = 64.333 s, 48 kHz stereo 24-bit.
# usage: python scripts/river_audio.py
import os, json, time
import numpy as np
from scipy import signal, ndimage
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dsp import (SR, TAU, ns, tt, dbg, rng, lp, hp, bp, peq, reson, colored, smooth_noise, shape,
                 ramp, fades, curve, st, pan, place, integrated, momentary_max, true_peak,
                 read_wav, write_wav, modal)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "audio")
os.makedirs(OUT, exist_ok=True)

FPS = 30
TOTAL = 1930
DUR = TOTAL / FPS                 # 64.3333 s
N = ns(DUR)
t_all = tt(DUR)

IGNITE = 19.70
TRAIN0, TRAIN1 = 12.9, 18.9
FLASH = 106 / FPS                 # 3.533
PAN_T = 32.2


def m2f(m):
    return 440.0 * 2 ** ((m - 69) / 12.0)


def log(*a):
    print(f"[{time.strftime('%H:%M:%S')}]", *a, flush=True)


# ================================================================ MUSIC (original)
def pad_chord(t0, dur, midis, gain=0.16, attack=1.2):
    x = np.zeros(ns(dur) + ns(0.5))
    tt_ = tt(len(x) / SR)
    env = np.minimum(1.0, tt_ / attack) * np.minimum(1.0, np.maximum(0.0, (len(x) / SR - tt_) / 1.5))
    for m in midis:
        f = m2f(m)
        vib = 1 + 0.0018 * np.sin(TAU * 4.6 * tt_ + m)
        x += np.sin(TAU * f * vib * tt_ + m) * 0.5
        x += np.sin(TAU * 2 * f * vib * tt_ + m * 2) * 0.18
        x += np.sin(TAU * f * 1.005 * tt_) * 0.12
    x *= env * gain / max(1, len(midis))
    return x


def bass_note(t0, dur, midi, gain=0.14):
    x = np.zeros(ns(dur) + ns(0.3))
    tt_ = tt(len(x) / SR)
    f = m2f(midi)
    x = np.sin(TAU * f * tt_) + 0.4 * np.sin(TAU * 2 * f * tt_)
    env = np.minimum(1.0, tt_ / 0.08) * np.minimum(1.0, np.maximum(0.0, (len(x) / SR - tt_) / 0.25))
    return x * env * gain


def melody_note(t0, dur, midi, gain=0.11):
    x = np.zeros(ns(dur) + ns(0.4))
    tt_ = tt(len(x) / SR)
    f = m2f(midi)
    vib = 1 + 0.004 * np.sin(TAU * 5.2 * tt_)
    x = np.sin(TAU * f * vib * tt_) + 0.35 * np.sin(TAU * 2 * f * vib * tt_) + 0.12 * np.sin(TAU * 3 * f * tt_)
    env = np.minimum(1.0, tt_ / 0.05) * np.minimum(1.0, np.maximum(0.0, (len(x) / SR - tt_) / 0.35))
    return x * env * gain


def build_music():
    buf = np.zeros((2, N))
    # chord progressions per section (4 s per chord)
    DAY = [[50, 53, 57], [46, 50, 54], [41, 45, 48], [48, 52, 55]]            # Dm Bb F C
    SMOKE = [[50, 53, 56], [43, 46, 50], [45, 48, 52], [41, 44, 49]]          # Dm Gm A Bb- (dark)
    GOLD = [[53, 57, 60], [48, 52, 55], [55, 59, 62], [50, 54, 57]]           # F C G D
    END = [[50, 53, 57], [53, 57, 60], [48, 52, 55], [50, 54, 57]]            # Dm F C D(major 3rd)
    sections = [(0.0, 21.5, DAY, 0.9), (21.5, 31.17, SMOKE, 0.62), (31.17, 41.83, DAY, 0.8),
                (41.83, 54.0, GOLD, 1.0), (54.0, DUR, END, 0.95)]
    for t0, t1, prog, g in sections:
        i = 0
        t = t0
        while t < t1 - 0.01:
            d = min(4.0, t1 - t)
            ch = prog[i % len(prog)]
            place(buf, pan(pad_chord(t, d, ch, gain=0.16 * g), 0.0), t)
            place(buf, pan(bass_note(t, d, ch[0] - 12, gain=0.13 * g), -0.15), t)
            t += d
            i += 1
    # melody phrases
    mel = [
        (0.8, 1.6, 62), (2.8, 1.2, 65), (4.4, 1.9, 69), (7.2, 1.4, 65), (9.0, 2.2, 62),
        (12.6, 1.5, 60), (14.6, 1.5, 62), (16.6, 2.6, 65), (19.4, 1.8, 62),
        (22.2, 2.5, 57), (25.2, 2.0, 55), (28.0, 2.8, 53),
        (31.8, 1.5, 62), (33.8, 1.5, 65), (36.0, 2.4, 69), (38.8, 2.6, 67),
        (42.4, 1.8, 65), (44.6, 1.6, 69), (46.6, 1.6, 72), (48.6, 2.2, 69), (51.2, 2.6, 65),
        (54.6, 1.6, 62), (56.6, 1.4, 65), (58.6, 1.6, 69), (60.6, 3.2, 74),
    ]
    for t0, d, m in mel:
        place(buf, pan(melody_note(t0, d, m), 0.25), t0)
    # low river drone under everything (very quiet)
    drone = np.sin(TAU * 73.42 * t_all) * 0.05 + np.sin(TAU * 110.0 * t_all) * 0.02
    buf += st(drone * curve(N, [(0, 0.0), (2, 1.0), (60, 1.0), (DUR, 0.0)]))
    # fade out last 1.2 s
    buf *= curve(N, [(0, 1.0), (DUR - 1.2, 1.0), (DUR, 0.0)])
    return buf


# ================================================================ SFX (all synthesized)
def noise_burst(dur, r, amp=1.0):
    return colored(ns(dur), r, slope=-1.0) * amp


def build_sfx():
    buf = np.zeros((2, N))
    r = rng(1969)
    # --- camera flash click at FLASH
    cl = hp(noise_burst(0.06, r), 3000) * 0.5
    md = modal(0.06, [(2200, 0.3, 0.01)], r)
    place(buf, pan(cl + md, 0.3), FLASH)
    # --- train: rumble + chuffs 12.9-18.9, whistle at 13.1
    tr = colored(ns(TRAIN1 - TRAIN0 + 0.5), r, slope=-2.0, lo=40)
    chuff = 0.55 + 0.45 * np.sin(TAU * 6.5 * tt(len(tr) / SR)) ** 2
    tr = lp(tr * chuff, 160)
    place(buf, pan(tr * 0.5, -0.2), TRAIN0)
    w = np.zeros(ns(1.5))
    tw = tt(1.5)
    w = (np.sin(TAU * 622 * tw) + np.sin(TAU * 740 * tw)) * 0.5
    w *= np.minimum(1, tw / 0.05) * np.minimum(1, np.maximum(0, (1.5 - tw) / 0.2))
    w = lp(w + 0.3 * hp(w, 2500), 3000) * 0.35
    place(buf, pan(w, 0.1), 13.1)
    # --- sparks crackle 18.12-19.72
    n_sp = ns(19.72 - 18.12)
    sp = np.zeros(n_sp)
    times = 18.12 + np.sort(r.uniform(0, 19.72 - 18.12, 260))
    for tm in times:
        k = int((tm - 18.12) * SR)
        ln = min(int(r.uniform(30, 160)), n_sp - k)
        if ln > 0:
            sp[k:k + ln] += r.uniform(0.2, 1.0) * np.exp(-np.arange(ln) / 18.0)
    place(buf, pan(hp(sp, 2500) * 0.4, 0.0), 18.12)
    # --- ignition whoosh + boom at IGNITE
    who = colored(ns(0.8), r, slope=0.0)
    who = shape(who, lambda tt_, ff: np.clip(((ff / 900.0) ** 2)[:, None] * (tt_ < 0.55)[None, :], 0, 3)) * 0.9
    place(buf, pan(fades(who, 0.02, 0.3), 0.0), IGNITE)
    place(buf, pan(fades(modal(1.4, [(55, 0.9, 0.5), (38, 0.6, 0.7), (110, 0.25, 0.2)], r), 0.01, 0.5), 0.0), IGNITE)
    # --- fire roar 19.9-29 (dies by 29.5)
    roar_n = ns(29.6 - 19.9)
    roar = colored(roar_n, r, slope=-0.5, lo=60)
    lfo = 0.6 + 0.4 * np.sin(TAU * 7.3 * tt(roar_n / SR)) * np.sin(TAU * 3.1 * tt(roar_n / SR) + 1.0)
    env = curve(roar_n, [(19.9, 0.0), (20.3, 1.0), (26.5, 0.9), (28.6, 0.75), (29.4, 0.0)])
    roar = bp(roar * lfo, 120, 1400) * env * 0.75
    place(buf, pan(roar, 0.0), 19.9)
    # extra crackle on top of the fire
    place(buf, pan(hp(sp, 1800) * 0.25, 0.0), 20.1)
    # --- hose jets 24-31
    hose = bp(colored(ns(7.2), r, slope=-1.0, lo=800), 1500, 6000)
    hen = curve(ns(7.2), [(24.0, 0.0), (24.6, 0.8), (30.2, 0.8), (31.0, 0.0)])
    place(buf, pan(hose * hen * 0.30, 0.55), 24.0)
    # --- pan ignition 32.2 + sizzle to 37.3
    pwho = shape(colored(ns(0.5), r), lambda tt_, ff: np.clip(((ff / 1200.0) ** 2)[:, None] * np.ones((1, len(tt_))), 0, 3)) * 0.5
    place(buf, pan(fades(pwho, 0.02, 0.2), -0.1), PAN_T)
    siz = hp(colored(ns(5.1), r, slope=-1.0, lo=3000), 3500)
    place(buf, pan(siz * curve(ns(5.1), [(PAN_T, 0.0), (PAN_T + 0.3, 0.5), (36.8, 0.35), (37.3, 0.0)]) * 0.5, -0.1), PAN_T)
    # --- kayak paddle splashes
    for tm in (54.3, 55.6, 57.4, 59.2, 60.8):
        spl = bp(colored(ns(0.35), r, slope=-1.5, lo=300), 500, 3000)
        place(buf, pan(fades(spl, 0.01, 0.25) * 0.5, 0.4), tm)
    # --- gentle water ambience under the day sections
    amb = lp(colored(N, r, slope=-1.0, lo=120), 500) * 0.05
    amb *= curve(N, [(0, 0.4), (21.5, 0.4), (21.5, 0.0), (31.17, 0.0), (31.17, 0.5), (DUR, 0.5)]) * 0.06
    buf += st(amb)
    # normalize the whole SFX stem to a sane peak (individual synth voices are not level-matched)
    pk = np.abs(buf).max()
    if pk > 0.5:
        buf *= 0.5 / pk
    return buf


# ================================================================ mix
def main():
    log("building music...")
    music = build_music()
    log("building sfx...")
    sfx = build_sfx()
    log("loading voice...")
    voice, vsr = read_wav(os.path.join(ROOT, "voice", "voice.wav"))
    assert vsr == SR, f"voice.wav is {vsr} Hz, expected {SR}"
    v = np.zeros((2, N))
    m = min(voice.shape[1], N)
    v[:, :m] = voice[:, :m]

    words = json.load(open(os.path.join(ROOT, "voice", "words.json")))
    speak = np.zeros(N, bool)
    for wd in words:
        a, b = ns(max(0.0, wd["t0"] - 0.08)), ns(min(DUR, wd["t1"] + 0.12))
        speak[a:b] = True
    # smooth the ducking envelope (150 ms)
    duck = ndimage.uniform_filter1d(speak.astype(float), size=ns(0.15))
    duck_gain = dbg(-3.0 * duck)
    music_d = music * duck_gain[None, :]

    # stem levels per standard: voice unchanged, music +3 dB, sfx -6 dB
    gv = v
    gm = music_d * dbg(+3.0)
    gs = sfx * dbg(-6.0)
    mix = gv + gm + gs

    # soft peak limiter first (ceiling -2.0 dBTP leaves headroom for the final gain pass)
    up = signal.resample_poly(mix, 4, 1, axis=-1)
    env = np.abs(up).max(axis=0)
    log(f'  env max {20*np.log10(env.max()+1e-30):.2f} dB, mix shape {mix.shape}, absmax {20*np.log10(np.abs(mix).max()):.2f}')
    red = np.maximum(env / dbg(-2.0), 1.0)
    red = ndimage.maximum_filter1d(red, size=ns(0.003) * 4, mode="nearest")   # attack / look-ahead
    red = ndimage.maximum_filter1d(red, size=ns(0.08) * 4, mode="nearest")    # release: hold the reduction
    lim1x = (1.0 / np.maximum(red, 1.0)).reshape(-1, 4).min(axis=1)[:N]  # worst case per 1x sample
    mix = mix * lim1x
    log(f'  after limiter: I {integrated(mix):.2f} TP {true_peak(mix):.2f}')
    # iterate: gain to -15 LUFS (gating is nonlinear, so re-measure each pass), capped so the
    # true peak stays <= -1.2 dBTP
    for it in range(6):
        g = min(dbg(-15.0 - integrated(mix)), dbg(-1.2 - true_peak(mix)))
        log(f"  pass {it}: I {integrated(mix):.2f} TP {true_peak(mix):.2f} -> gain {20*np.log10(g):.2f} dB")
        if abs(20 * np.log10(g)) < 0.01:
            break
        mix = mix * g
    fin = integrated(mix)
    tp = true_peak(mix)
    log(f"mix: {fin:.2f} LUFS integrated, TP {tp:.2f} dBTP, dur {N / SR:.3f} s")
    if tp > -1.2 + 0.05:
        raise SystemExit("true peak over ceiling")
    if abs(fin + 15.0) >= 0.3:
        raise SystemExit(f"loudness off target: {fin:.2f}")

    write_wav(os.path.join(OUT, "mix.wav"), mix)
    write_wav(os.path.join(OUT, "stem_voice.wav"), gv * g)
    write_wav(os.path.join(OUT, "stem_music.wav"), gm * g)
    write_wav(os.path.join(OUT, "stem_sfx.wav"), gs * g)
    with open(os.path.join(OUT, "cues.md"), "w") as f:
        f.write("# The River That Caught Fire - cue sheet (all original synth)\n\n")
        f.write(f"mix.wav 48 kHz stereo 24-bit, {N / SR:.3f} s, {fin:.2f} LUFS, TP {tp:.2f} dBTP\n\n")
        f.write("| time s | event |\n|---|---|\n")
        for tm, ev in [(FLASH, "camera flash click"), (TRAIN0, "train rumble/chuffs to 18.9"), (13.1, "train whistle"),
                       (18.12, "spark crackle to 19.72"), (IGNITE, "ignition whoosh + boom"), (19.9, "fire roar to 29.4"),
                       (24.0, "hose jets to 31.0"), (PAN_T, "pan ignition + sizzle to 37.3"),
                       (54.3, "kayak paddle splashes 54.3-60.8")]:
            f.write(f"| {tm:.2f} | {ev} |\n")
    log("done -> audio/mix.wav")


if __name__ == "__main__":
    main()
