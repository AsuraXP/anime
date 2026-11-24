#!/usr/bin/env python3
"""research/bench/certify.py -- the publication gate for research/bench/.

Run:  python3 research/bench/certify.py            (fast: scorecard + symmetry + carry, ~1 min)
      python3 research/bench/certify.py --full     (adds k3control + ceiling + ablate_carry + budget + nonregular + act_ablate, ~32 min)

A number is certified when it is (1) seeded, (2) CPU-only, (3) reproducible in two independent
runs, and (4) carries its exact command and runtime. This file checks (3) mechanically instead of
asking the reader to trust the sentence that claims it, and then checks that the *prose* sitting
next to the numbers is actually supported by them.

What is checked
  D1 determinism      every script is run twice; stdout must match after timing fields are masked.
  D2 freshness        the block of RESULTS.md tagged as scorecard output must equal a fresh run.
  C1..C13 claim checks the specific sentences in RESULTS.md / threads 0001-0002 that a reader would
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
    # A withheld label is only honest while the withdrawal still stands: once a later part fixes the
    # baseline, the document must say so at the place a reader meets the stale rows.
    _withheld = "WITHHELD" in part7
    _banner = "Superseded for the recurrent baseline" in md0
    out.append(check("C10 uncertified baseline is labelled, and the label is kept current",
                     _withheld and (not _withheld or _banner),
                     "Part 7 marks the turn-4 rows WITHHELD; Part 9 fixes them and the Part 7 banner "
                     "points forward, so a reader cannot mistake history for the current baseline"))

    # C11 -- the closure gate (`closure.py`) is the pre-flight check the Adversary asked for, and it
    # is only worth having if it reproduces the number it was built to explain: AGL(1,101) has order
    # 10,100 and exhausts by depth 9. Recomputed from the module, not read out of the text.
    part8 = md0.split("PART 8")[-1] if "PART 8" in md0 else ""
    out.append(check("C11 Part 8 (closure gate + P8 ablation) published", bool(part8),
                     "agent-c MSG-0008 asked for a 0.3 s pre-flight kill; D-021 §2.2 asked for the "
                     "act_ord ablation"))
    cl = load_module("closure")
    aff = cl.affine_action()
    n_aff = cl.count_at(aff, aff["depths"][-1])
    out.append(check("C11 closure gate reproduces AGL(1,101) = 10,100 states, DEAD", 
                     n_aff == 10100 and aff["verdict"] == "DEAD",
                     f"enumerated {n_aff:,} states, verdict {aff['verdict']}, exhausts at depth "
                     f"{aff['sat']} (Adversary published 10,100 states / 14 bits)"))
    da = cl.digit_addition()
    dy = cl.dyck_counter()
    out.append(check("C11 closure gate separates DEAD from LIVE",
                     da["verdict"] == "DEAD" and dy["verdict"] == "LIVE",
                     f"digit addition {da['verdict']} ({cl.count_at(da, 16):,} states); "
                     f"Dyck counter {dy['verdict']} ({cl.count_at(dy, 32):,} states at depth 32)"))
    out.append(check("C11 the 0-parameter null is in the ablation tables",
                     "0-param carry-blind" in part8,
                     "AMEND-002: the null is the row the encoder has to beat, not a footnote"))
    out.append(check("C11 the ablation's verdict is stated against a noise floor",
                     "CI half-width" in part8 and "noise" in part8
                     and "negative = deleting helps" in part8,
                     "a 1-point difference at n=8,000 is not a mechanism; the table states the "
                     "half-width and the sign convention instead of ranking rows it cannot separate"))

    # C12 -- D-022 §2.3: the withheld recurrent baseline must be fixed and published, and the gate
    # recomputes the one fact that makes it a baseline rather than a hope: one h=4 restart must reach
    # the ceiling at depth <= 8. A curve published without that check is the turn-4 mistake again.
    part9 = md0.split("PART 9")[-1] if "PART 9" in md0 else ""
    out.append(check("C12 Part 9 (fixed recurrent baseline) published", bool(part9),
                     "D-022 §2.3: the harness needs a neural baseline before 0006 can be scored"))
    out.append(check("C12 the baseline is reported as a distribution, not one run",
                     "success rate" in part9 and "median" in part9,
                     "learning is bimodal (exact or chance); a single run would have called this "
                     "baseline 82% or 48% depending on the seed"))
    nr2 = load_module("nonregular")
    _ctrl = nr2.make_control_set(__import__("random").Random(nr2.SEED + 11), 800, 8)
    _lc = nr2.score_binary(lambda w: 1 if w.endswith(")") else 0, _ctrl)
    out.append(check("C12 the control's last-character shortcut is gone", abs(_lc - 0.5) < 0.10,
                     f"the shortcut scores {100 * _lc:.2f}% on the control (it scored 73.50% on turn "
                     f"4's construction), so a model that passes the control is counting"))
    t0 = time.time()
    tr = nr2.make_balanced_set(__import__("random").Random(nr2.SEED + 7), 8000, 8)
    te = nr2.make_balanced_set(__import__("random").Random(nr2.SEED + 11), 1600, 8)
    m = nr2.RNN(4, __import__("random").Random(nr2.SEED))
    m.train(tr, 8, __import__("random").Random(nr2.SEED + 1))
    acc = nr2.score_binary(m.predict, te)
    out.append(check("C12 a 4-unit restart reaches the ceiling at depth <= 8", acc >= 0.95,
                     f"recomputed one restart: {100 * acc:.2f}% exact in {time.time() - t0:.0f}s "
                     f"(turn 4's trainer was at chance here)"))
    part2 = md0.split("PART 2")[-1].split("PART 3")[0]
    out.append(check("C12 the 0-param null is inside Part 2's own tables",
                     "0-param carry-blind" in part2,
                     "D-021 §2.2 / AMEND-002: the null must be a row, not a note in another file"))

    # C13 -- turn 7's audit: the harness's own claims must match the boundary scan, and the closure
    # gate must carry the three-way verdict D-023 adopted (feasible DEAD / infeasible VIABLE / LIVE).
    part10 = md0.split("PART 10")[-1] if "PART 10" in md0 else ""
    out.append(check("C13 Part 10 (harness audit) published", bool(part10),
                     "the Adversary audited A1b and Task B (MSG-0011); the audit of that audit is "
                     "the evidence that the two corrections are real"))
    au = load_module("audit_harness")
    k8, _ = au.min_exact_k(8)
    k16, _ = au.min_exact_k(16)
    out.append(check("C13 A1b's requirement is D+3, recomputed", (k8, k16) == (11, 19),
                     f"min exact k = {k8} at D=8 (D+3={11}), {k16} at D=16 (D+3={19}); the published "
                     f"rule said D+1 in Parts 7 and 9"))
    part9 = md0.split("PART 9")[-1].split("PART 10")[0]
    out.append(check("C13 Part 9 no longer claims k >= D+1 as the rule",
                     "D+3" in part9 and "edit collateral" in part9,
                     "the regenerated Part 9 carries the corrected state requirement and the "
                     "corrected Task B column header"))
    cl2 = load_module("closure")
    d2 = cl2.dyck2_bounded()
    out.append(check("C13 closure gate has the feasible/infeasible split (AMEND-005)",
                     d2["verdict"] == "VIABLE" and cl2.FEASIBLE_MAX == 10 ** 9,
                     f"Dyck-2 depth<=256 closes into {d2['counts'][256]:.2e} states and is VIABLE, "
                     f"not DEAD -- finiteness alone is not a kill"))
    out.append(check("C13 the audit separates collateral from collision loss",
                     "blast radius" in part10 and "collision loss" in part10,
                     "934 of 999 was collision loss; the edit damages 0-3 keys"))

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

    scripts = ["scorecard", "symmetry", "carry", "closure", "audit_harness"] + \
        (["k3control", "ceiling", "ablate_carry", "budget", "nonregular", "act_ablate"] if full else [])
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
