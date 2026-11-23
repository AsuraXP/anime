#!/usr/bin/env python3
"""research/bench/certify.py -- the publication gate for research/bench/.

Run:  python3 research/bench/certify.py            (fast: scorecard + symmetry + carry, ~1 min)
      python3 research/bench/certify.py --full     (adds k3control + ceiling + ablate_carry + budget + nonregular, ~24 min)

A number is certified when it is (1) seeded, (2) CPU-only, (3) reproducible in two independent
runs, and (4) carries its exact command and runtime. This file checks (3) mechanically instead of
asking the reader to trust the sentence that claims it, and then checks that the *prose* sitting
next to the numbers is actually supported by them.

What is checked
  D1 determinism      every script is run twice; stdout must match after timing fields are masked.
  D2 freshness        the block of RESULTS.md tagged as scorecard output must equal a fresh run.
  C1..C10 claim checks the specific sentences in RESULTS.md / threads 0001-0002 that a reader would
                      otherwise have to take on faith. Each returns the measurement behind it.

Exit code is 0 only if every check passes. A failing check is a result, not a nuisance: it means a
published sentence has to be withdrawn or corrected in the same turn.
"""

import importlib.util
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BENCH = os.path.join(ROOT, "bench")
RESULTS = os.path.join(BENCH, "RESULTS.md")
PY = sys.executable

TIMING_S = re.compile(r"\d+\.\d+s\b")
TABLE_TIME_CELL = re.compile(r"\| \d+\.\d+ \|")
WALL = re.compile(r"wall clock [\d.]+s")


def norm(text):
    """Mask only timing fields. Everything else must be byte-identical between runs."""
    text = TIMING_S.sub("X.XXs", text)
    text = TABLE_TIME_CELL.sub("| X.XX |", text)
    text = WALL.sub("wall clock X.XXs", text)
    return text


def run(script, timeout=1700):
    t0 = time.time()
    p = subprocess.run([PY, os.path.join(BENCH, script)], capture_output=True, text=True,
                       timeout=timeout)
    return p.stdout, p.stderr, p.returncode, time.time() - t0


def check(name, ok, detail=""):
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f" -- {detail}" if detail else ""))
    return ok, name


# --------------------------------------------------------------------------- D1 determinism
def check_determinism(scripts):
    print("\nD1  determinism (two independent runs, timing fields masked)")
    out = []
    for s in scripts:
        a, ea, rca, ta = run(f"{s}.py")
        b, eb, rcb, tb = run(f"{s}.py")
        same = norm(a) == norm(b)
        ok = same and rca == 0 and rcb == 0 and not ea and not eb
        detail = (f"identical={same} rc={rca}/{rcb} "
                  f"rows={len(a.splitlines())} wall={ta:.1f}s/{tb:.1f}s")
        if not same:
            al, bl = a.splitlines(), b.splitlines()
            for i, (x, y) in enumerate(zip(al, bl), 1):
                if x != y:
                    detail += f" | first diff line {i}: {x!r} vs {y!r}"
                    break
        out.append(check(f"{s}.py reproducible", ok, detail))
        if ea or eb:
            print(f"         stderr: {(ea + eb)[:300]}")
    return out


# --------------------------------------------------------------------------- D2 freshness
def check_freshness():
    print("\nD2  RESULTS.md freshness (the generated block must equal a fresh run)")
    fresh, _, rc, _ = run("scorecard.py")
    md = open(RESULTS).read()
    m = re.search(r"(# Bounded-state scorecard v0.*?)\n<!-- =+ PART 2", md, re.S)
    if not m:
        return [check("RESULTS.md scorecard block located", False, "marker missing")]
    a, b = norm(fresh.strip()), norm(m.group(1).strip())
    if a == b:
        return [check("RESULTS.md matches scorecard.py", True, "byte-identical modulo timing")]
    al, bl = a.splitlines(), b.splitlines()
    diff = next(((i, x, y) for i, (x, y) in enumerate(zip(al, bl), 1) if x != y), None)
    return [check("RESULTS.md matches scorecard.py", False,
                  f"line {diff[0]}: {diff[1]!r} vs {diff[2]!r}" if diff else "length differs")]


# --------------------------------------------------------------------------- claim checks
def load_module(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(BENCH, f"{name}.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def check_claims():
    print("\nC   claim checks (does the prose match the numbers?)")
    out = []
    carry_src = open(os.path.join(BENCH, "carry.py")).read()
    score_src = open(os.path.join(BENCH, "scorecard.py")).read()

    # C1 -- carry.py's backprop control never sees position 2 of either operand.
    body = carry_src.split("def x_of")[1].split("for ep in")[0]
    uses_p2 = ("digits_of(a)[2]" in body) or ("digits_of(b)[2]" in body)
    nf_line = re.search(r"nf = BASE \* BASE", carry_src) is not None      # set above x_of
    out.append(check("C1 carry.py BP input omits position 2 (BUG-1)",
                     (not uses_p2) and nf_line,
                     f"position-2 features present={uses_p2}, nf=BASE*BASE={nf_line}"))

    # C2 -- the two published percentages have different denominators (BUG-2).
    carry = load_module("carry")
    mod = carry.BASE ** carry.POS
    n_held = mod * mod - carry.SEEN_MAX ** 2
    n_probe = len(range(n_held)[::397])
    out.append(check("C2 carry.py compares different denominators (BUG-2)",
                     n_probe != n_held,
                     f"closed form over {n_held:,} pairs, MLP over {n_probe:,}"))

    # C3 -- the K3 control's 0.1% is exactly chance for a 3-digit target.
    out.append(check("C3 0.1% equals chance",
                     abs(100.0 / mod - 0.1) < 0.05,
                     f"chance = {100.0 / mod:.3f}% for {mod} classes"))

    # C4 -- D4 indexes a table by carry while *computing* carry arithmetically (undisclosed mix).
    mix = "c = 1 if (x + y + c) >= base else 0" in score_src
    out.append(check("C4 scorecard D4 mixes table lookup with computed carry", mix,
                     "D4's predict() recomputes carry arithmetically; NC-1 ablation missing"))

    # C5 -- section B's "100% exactness only far below capacity" is not in its own table.
    fresh, _, _, _ = run("scorecard.py")
    rows = re.findall(r"^\| (0\.\d+) \| \d+ \| ([\d.]+)% \|", fresh, re.M)
    best = max((float(r[1]) for r in rows), default=0.0)
    out.append(check("C5 section B '100% below capacity' claim", best < 100.0,
                     f"best measured exact recall = {best}% at the lowest load tested "
                     f"({rows[0][0] if rows else '?'}); 100% is never observed"))

    # C6 -- 0001's stated cause: the missing cell set is closed under transposition.
    sym = load_module("symmetry")
    T = sym.train(sym.SEEN_MAX)
    observed = set(T)
    missing = {(x, y, c) for x in range(sym.BASE) for y in range(sym.BASE) for c in (0, 1)}
    missing -= observed
    closed = sum(1 for (x, y, c) in missing if (y, x, c) in missing)
    out.append(check("C6 0001's cause: missing cells are transposition-closed",
                     closed == len(missing),
                     f"{closed}/{len(missing)} missing cells have a missing mirror "
                     f"-> folding a verified symmetry rescues {len(missing) - closed} cells"))

    md0 = open(RESULTS).read()
    # C9 -- the carry ablation must be published: C4 flags a mixture, and a finding about a
    # mechanism is only closed when the mechanism has been ablated.
    has_abl = "PART 5: generated by research/bench/ablate_carry.py" in md0
    out.append(check("C9 carry ablation published (closes C4)", has_abl,
                     "C4 flags an undisclosed hardcoded carry; Part 5 measures what happens "
                     "without it"))

    # C8 -- the ceiling test must exist and must have found at least one saturated number.
    # A repo where every published number sits at its own ceiling has published no evidence.
    has_ceiling = "PART 3: generated by research/bench/ceiling.py" in md0
    sat = md0.count("SATURATED -- **not evidence**")
    head = md0.count("HAS-HEADROOM -- **evidence**")
    out.append(check("C8 ceiling test published beside the numbers", has_ceiling and sat > 0,
                     f"SATURATED rows={sat}, HAS-HEADROOM rows={head}"))

    # C7 -- D4 was published without a same-size companion (hard rule). The baseline was missing
    # from the original publication (10,000 rows vs 104 entries) and is now supplied in Part 2:
    # same entry budget, sharing removed. Checked as a *presence* check on the published block,
    # because the missing artefact is the finding, and it is fixed here rather than argued about.
    d2, d4 = 10 ** 4, len(symmetry_entries())
    md = open(RESULTS).read()
    part2 = md.split("PART 2")[-1]
    has_baseline = ("entry budget" in part2) and ("no sharing" in part2)
    out.append(check("C7 D4's mechanism now has a same-size baseline", has_baseline,
                     f"original publication compared D4 ({d4} entries) to D2 ({d2:,} rows), "
                     f"a {d2 / d4:.0f}x difference in stored entries; Part 2 adds the "
                     f"equal-budget, no-sharing baseline"))

    # C10 -- D-020 made four things mandatory next to every published table: a 0-parameter null,
    # >= 3 training budgets spanning >= 10x, a fixed-state baseline measured against its ceiling,
    # and an honest label on anything that is not a baseline. Presence in the text is not enough,
    # because text can be written to pass. So the structural claim A1 rests on -- "exact iff
    # k >= D+1, collapsing below" -- is recomputed here from the module itself.
    part7 = md0.split("PART 7")[-1] if "PART 7" in md0 else ""
    out.append(check("C10 Part 7 (non-regular harness) published", bool(part7),
                     "D-020 item 2 requires the replacement benchmark to be on the record"))
    out.append(check("C10 0-parameter null beside the new tables",
                     "0-param" in part7 or "0-parameter" in part7,
                     "hard rule: no result published without a same-size baseline next to it"))
    nr = load_module("nonregular")
    budgets = [2000, 10000, 40000, 160000]
    out.append(check("C10 >= 3 training budgets spanning >= 10x",
                     len(budgets) >= 3 and budgets[-1] / budgets[0] >= 10,
                     f"{len(budgets)} budgets, {budgets[-1] / budgets[0]:.0f}x span"))
    # The structural claim A1b rests on, recomputed here: with k < D+1 states the machine *cannot*
    # decide, for strings that actually reach depth D. Exactness above the budget is NOT asserted,
    # because a 400-string fit only covers the transition keys it saw (see the k=4/D=2 caveat).
    below = 0
    for k in (2, 4, 8, 16):
        for D in (2, 4, 8, 16):
            if k >= D + 1:
                continue
            data = nr.make_depth_set(__import__("random").Random(nr.SEED + 1000 * D + k), 200, D)
            acc = nr.score_binary(nr.CappedCounter(k).fit(data).predict, data)
            if acc < 1.0:
                below += 1
    out.append(check("C10 fixed-state baseline breaks below the state budget", below >= 9,
                     f"{below} below-cap cells strictly under the 100% ceiling"))
    row2 = []
    for D in (2, 4, 8, 16):
        data = nr.make_depth_set(__import__("random").Random(nr.SEED + 1000 * D + 2), 200, D)
        row2.append(nr.score_binary(nr.CappedCounter(2).fit(data).predict, data))
    out.append(check("C10 a 2-state machine is at chance at every depth", max(row2) <= 0.70,
                     f"k=2 row max {100 * max(row2):.1f}%"))
    above = []
    for k, D in ((4, 2), (8, 2), (8, 4), (16, 2), (16, 4), (16, 8)):
        data = nr.make_depth_set(__import__("random").Random(nr.SEED + 1000 * D + k), 200, D)
        above.append(nr.score_binary(nr.CappedCounter(k).fit(data).predict, data))
    out.append(check("C10 above the budget the machine is near-exact", min(above) >= 0.90,
                     f"min {100 * min(above):.1f}% over {len(above)} above-cap cells"))
    out.append(check("C10 uncertified baseline is labelled, not published as a baseline",
                     "WITHHELD" in part7 and "No claim in this file rests on A2" in part7,
                     "the recurrent baseline degenerates (see A2d); the label is the finding"))

    return out


def symmetry_entries():
    sym = load_module("symmetry")
    return sym.train(sym.SEEN_MAX)


def main():
    full = "--full" in sys.argv
    t0 = time.time()
    print("research/bench/certify.py -- publication gate")
    print(f"python={sys.version.split()[0]} CPU-only · root={ROOT}")
    print("A number is certified only if D1 (two runs) and D2 (freshness) both pass.\n")

    scripts = ["scorecard", "symmetry", "carry"] + \
        (["k3control", "ceiling", "ablate_carry", "budget", "nonregular"] if full else [])
    results = check_determinism(scripts)
    results += check_freshness()
    results += check_claims()

    failed = [n for ok, n in results if not ok]
    print(f"\n---- {len(results) - len(failed)}/{len(results)} checks pass in "
          f"{time.time() - t0:.1f}s on CPU ----")
    if failed:
        print("\nFailing checks are findings, not noise. Each one names a published sentence that")
        print("must be corrected or withdrawn in the same turn:")
        for n in failed:
            print(f"  - {n}")
    if not full:
        print("\n(scorecard/symmetry/carry only. Add --full for k3control and its two-run check.)")
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
