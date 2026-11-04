#!/usr/bin/env python3
# Emit scripts/shots.json from the SHOTS table in src/story.ts (for short_qa.py).
import json, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
s = open(os.path.join(ROOT, "src", "story.ts")).read()
rows = re.findall(r"\{\s*a:\s*(\d+),\s*b:\s*(\d+)", s)
shots = [{"id": i + 1, "a": int(a), "b": int(b)} for i, (a, b) in enumerate(rows)]
json.dump({"shots": shots, "flash": [], "xfade": []}, open(os.path.join(HERE, "shots.json"), "w"), indent=1)
print(f"shots.json: {len(shots)} shots, {shots[-1]['b'] if shots else 0} frames")
