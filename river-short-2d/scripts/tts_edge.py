#!/usr/bin/env python3
# Generate voice/voice.wav (48 kHz stereo 24-bit) + voice/words.json + src/words.gen.json
# using edge-tts neural voices (default: en-US-AndrewNeural at -20% pace).
# Needs internet access to Microsoft's speech endpoint (fine on Kaggle / any normal machine).
# usage: python3 scripts/tts_edge.py [--voice en-US-AndrewNeural] [--rate -20%] [--script SCRIPT2D.md]
import argparse, asyncio, json, os, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
VOICE = os.path.join(ROOT, "voice")
SR = 48000
LEAD, GAP, TAIL = 0.40, 0.35, 0.60


def chunks(script_path):
    txt = open(script_path).read()
    paras = [p.strip().replace("\n", " ") for p in txt.split("\n\n")]
    paras = [p for p in paras if p and not p.startswith("#")]
    return [(f"c{i}", p) for i, p in enumerate(paras)] or [("c0", txt.strip())]


async def gen_chunk(text, voice, rate, out_mp3):
    import edge_tts
    com = edge_tts.Communicate(text, voice, rate=rate)
    audio = bytearray()
    words = []
    async for ch in com.stream():
        t = ch.get("type")
        if t == "audio":
            audio += ch["data"]
        elif t in ("WordBoundaryEvent", "WordBoundary"):
            off, dur = ch.get("offset", 0), ch.get("duration", 0)
            words.append({"w": ch.get("text", ""), "t0": off / 1e7, "t1": (off + dur) / 1e7})
    open(out_mp3, "wb").write(bytes(audio))
    return words


def ffmpeg():
    return os.environ.get("FFMPEG") or shutil.which("ffmpeg") or "ffmpeg"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--voice", default="en-US-AndrewNeural")
    ap.add_argument("--rate", default="-20%")
    ap.add_argument("--script", default=os.path.join(ROOT, "SCRIPT2D.md"))
    # allow "--rate -20%" (value starts with '-') by pre-merging into "--rate=-20%"
    argv = sys.argv[1:]
    merged = []
    i = 0
    while i < len(argv):
        if argv[i] in ("--rate", "--voice", "--script") and i + 1 < len(argv):
            merged.append(f"{argv[i]}={argv[i + 1]}")
            i += 2
        else:
            merged.append(argv[i])
            i += 1
    args = ap.parse_args(merged)
    os.makedirs(VOICE, exist_ok=True)
    import numpy as np
    import soundfile as sf

    chunks_list = chunks(args.script)
    print(f"edge-tts voice={args.voice} rate={args.rate}: {len(chunks_list)} chunks")
    all_words = []
    parts = []
    t = LEAD
    for name, text in chunks_list:
        mp3 = os.path.join(VOICE, f"{name}.mp3")
        wav48 = os.path.join(VOICE, f"{name}.wav")
        words = asyncio.run(gen_chunk(text, args.voice, args.rate, mp3))
        # decode mp3 -> 48 kHz mono wav with ffmpeg (correct resampling, no pitch shift)
        subprocess.run([ffmpeg(), "-y", "-v", "error", "-i", mp3, "-ar", str(SR), "-ac", "1", wav48], check=True)
        x, _ = sf.read(wav48, dtype="float32")
        parts.append(x)
        for w in words:
            all_words.append({"w": w["w"], "t0": t + w["t0"], "t1": t + w["t1"]})
        t += len(x) / SR + GAP
    n = int(t * SR) + int(TAIL * SR)
    buf = np.zeros(n, dtype=np.float32)
    pos = int(LEAD * SR)
    for x in parts:
        buf[pos:pos + len(x)] = x
        pos += len(x) + int(GAP * SR)
    stereo = np.stack([buf, buf], axis=1)
    sf.write(os.path.join(VOICE, "voice.wav"), stereo, SR, subtype="PCM_24")
    json.dump(all_words, open(os.path.join(VOICE, "words.json"), "w"), indent=1)
    json.dump(all_words, open(os.path.join(ROOT, "src", "words.gen.json"), "w"), indent=1)
    print(f"voice.wav {len(buf)/SR:.2f}s, {len(all_words)} words -> voice/words.json + src/words.gen.json")


if __name__ == "__main__":
    main()
