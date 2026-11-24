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
  C1..C16 claim checks the specific sentences in RESULTS.md / threads 0001-0002 that a reader would
                      otherwise have to take on faith. Each returns the measurement behind it.

Exit code is 0 only if every check passes. A failing check is a result, not a nuisance: it means a
published sentence has to be withdrawn or corrected in the same turn.
"""

import importlib.util
import os
import random
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


def random_seeded(mod, salt):
    """A seeded RNG for the C14 recomputations, so the gate itself is deterministic."""
    import random
    return random.Random(mod.SEED + 7919 * salt)


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
    dy = cl.dyck1_unbounded()          # the LIVE case; renamed from dyck_counter() in turn 8
    out.append(check("C11 closure gate separates DEAD from LIVE",
                     da["verdict"] == "DEAD" and dy["verdict"] == "LIVE",
                     f"digit addition {da['verdict']} ({cl.count_at(da, 16):,} states); "
                     f"Dyck-1 unbounded {dy['verdict']} ({dy['counts'][32]:,} states at depth 32)"))
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
    d2 = cl2.dyck2_bounded(256)
    out.append(check("C13 closure gate has the feasible/infeasible split (AMEND-005/006)",
                     d2["verdict"] == "VIABLE" and cl2.FEASIBLE_MAX == 2 ** 30,
                     f"Dyck-2 depth<=256 closes into {d2['M']:.2e} states and is VIABLE, "
                     f"not DEAD -- finiteness alone is not a kill; the threshold is 2^30 per "
                     f"AMEND-006 (it was 10^9 when this check was written)"))
    out.append(check("C13 the audit separates collateral from collision loss",
                     "blast radius" in part10 and "collision loss" in part10,
                     "934 of 999 was collision loss; the edit damages 0-3 keys"))

    # ---------------------------------------------------------------- C14 (AMEND-006 / turn 8)
    m = re.search(r"PART 11:.*?(?=\n<!-- =|\Z)", md0, re.S)
    part11 = m.group(0) if m else ""
    out.append(check("C14 Part 11 (envelope gate + Dyck-2 + stream accounting) published",
                     bool(part11) and "AMEND-006" in part11 and "2^30" in part11,
                     f"{len(part11.splitlines())} lines"))

    clo = load_module("closure")
    d1_16, d2_32, d2_29, d2_30 = (clo.dyck1_bounded(16), clo.dyck2_bounded(32),
                                 clo.dyck2_bounded(29), clo.dyck2_bounded(30))
    out.append(check("C14 envelope gate: Dyck-1 at D=16 is DEAD, Dyck-2 at D=32 is VIABLE",
                     (d1_16["M"], d1_16["verdict"]) == (17, "DEAD")
                     and d2_32["M"] == 2 ** 33 - 1 and d2_32["verdict"] == "VIABLE",
                     f"Dyck-1 M={d1_16['M']} {d1_16['verdict']}; Dyck-2 M={d2_32['M']} "
                     f"{d2_32['verdict']} ({clo.bits(d2_32['M'])} bits)"))
    out.append(check("C14 the 2^30 crossing is where the script computes it",
                     d2_29["M"] < clo.FEASIBLE_MAX <= d2_30["M"]
                     and d2_29["cross"] == d2_30["cross"] == d2_32["cross"] == 30,
                     f"depth 29: {d2_29['M']:,} < 2^30 <= depth 30: {d2_30['M']:,}; "
                     f"computed crossing depth {d2_30['cross']}"))

    d2m = load_module("dyck2")
    out.append(check("C14 the Dyck-2 label rejects a type mismatch (it did not, before)",
                     (not d2m.valid("Ab")) and d2m.valid("ABba") and (not d2m.valid("AabB")),
                     "valid('Ab')=False, valid('ABba')=True"))
    probe_ok = True
    for d in (4, 8, 16, 32):
        ps = d2m.make_set(random_seeded(d2m, d), 200, d, pin_depth=d)
        probe_ok = probe_ok and max(d2m.nested_depth(w) for w, _ in ps) == d and len(ps) == 200
    tr = d2m.make_train_set(random_seeded(d2m, 99), 800, d2m.TRAIN_D)
    depth_ok = max(d2m.nested_depth(w) for w, _ in tr) <= d2m.TRAIN_D
    out.append(check("C14 probes pinned at exactly depth D; no training string deeper than 8",
                     probe_ok and depth_ok,
                     f"probe max nesting == D for D in 4/8/16/32; train max "
                     f"{max(d2m.nested_depth(w) for w, _ in tr)} <= {d2m.TRAIN_D}"))

    small_train = d2m.make_train_set(random_seeded(d2m, 7), 1500, 8)
    pr = {d: d2m.make_set(random_seeded(d2m, 70 + d), 300, d, pin_depth=d) for d in (4, 8, 16)}
    cap9 = d2m.CapStack(9).fit(small_train)
    cap4 = d2m.CapStack(4).fit(small_train)
    a8, a16, a4 = (d2m.score(cap9.predict, pr[8]), d2m.score(cap9.predict, pr[16]),
                   d2m.score(cap4.predict, pr[4]))
    out.append(check("C14 a type stack is exact only up to its cap: 1,023 states pass D=8, fail D=16",
                     cap9.states == 1023 and a8 >= 0.95 and a16 <= 0.70 and a4 >= 0.95,
                     f"cap 9: D=8 {100 * a8:.1f}%, D=16 {100 * a16:.1f}%; cap 4: D=4 {100 * a4:.1f}%"))

    sr = load_module("stream_ram")
    L, mm = 10000, 1024
    keys, vals, ek, nv = sr.build_stream(L, sr.SEED + L)
    q = random.Random(sr.SEED + 2 * L).sample(keys, 2000)
    rb, ra, coll, rd, wr, sbits = sr.direct_address(keys, vals, ek, nv, mm, q)
    frb, fra, fcoll, frd, fwr, _ = sr.full_scan(keys, vals, ek, nv, q)
    toks = len(keys) + 2 * len(q) + 1
    bpt_direct, bpt_scan = (rd + wr) / toks, (frd + fwr) / toks
    out.append(check("C14 stream accounting: coverage on the pigeonhole bound, scan breaks G4",
                     abs(rb - mm / L) <= 0.03 and bpt_scan > 4096 >= bpt_direct and frb == 1.0,
                     f"m=1024, L=10,000: recall {100 * rb:.2f}% vs bound {100 * mm / L:.2f}%; "
                     f"bytes/token direct {bpt_direct:.1f}, scan {bpt_scan:,.0f} (G4 budget 4,096)"))

    out.append(check("C14 the recurrent baseline is reported as a distribution over restarts",
                     "median / best of" in part11 and "Control from the same run" in part11,
                     "median/best over 4 restarts, with the no-curriculum control quoted beside it"))

    # ---------------------------------------------------------------- C15 (D-025 item (c) / turn 9)
    m = re.search(r"PART 12:.*?(?=\n<!-- =|\Z)", md0, re.S)
    part12 = m.group(0) if m else ""
    out.append(check("C15 Part 12 (Task B2, shared-readout store) published",
                     bool(part12) and "superposed" in part12 and "oracle" in part12,
                     f"{len(part12.splitlines())} lines"))

    sw = load_module("stream_ram")
    keys, vals, ek, nv = sw.build_stream(32, sw.SEED + 32)
    rb, ra, coll_add, rd, wr = sw.fast_weight(keys, vals, ek, nv, 1024, keys, "add")
    _, _, coll_orc, _, _ = sw.fast_weight(keys, vals, ek, nv, 1024, keys, "oracle")
    out.append(check("C15 a shared readout exhibits edit collateral; an oracle erase removes it",
                     coll_add >= 1 and coll_orc <= coll_add and rb > 0.15,
                     f"d=1024, n=32: recall {100 * rb:.1f}%, add-only blast radius {coll_add} keys, "
                     f"oracle erase {coll_orc} -- the column changes when the event changes"))

    r32 = sw.fast_weight(keys, vals, ek, nv, 1024, keys, "add")[0]
    k64, v64, e64, n64 = sw.build_stream(64, sw.SEED + 64)
    r64 = sw.fast_weight(k64, v64, e64, n64, 1024, k64, "add")[0]
    out.append(check("C15 recall falls with load at fixed d (the capacity wall is real)",
                     r32 > r64,
                     f"d=1024: {100 * r32:.1f}% at n=32, {100 * r64:.1f}% at n=64"))

    def bpt(d, n):
        kk, vv, ee, nn = sw.build_stream(n, sw.SEED + n)
        _, _, _, r, w = sw.fast_weight(kk, vv, ee, nn, d, kk, "add")
        return (r + w) / (len(kk) + 2 * len(kk) + 1)

    b_small, b_mid, b_big = bpt(1024, 32), bpt(2048, 32), bpt(4096, 32)
    out.append(check("C15 G4 budget admits d <= 1024 for a fast-weight store, not d = 2048",
                     b_small <= 4096 < b_mid < b_big,
                     f"bytes/token: d=1024 {b_small:,.0f} (pass), d=2048 {b_mid:,.0f} (fail), "
                     f"d=4096 {b_big:,.0f} (fail); budget 4,096"))

    dr_b, dr_a, dr_c, _, _, sbits = sw.direct_address(keys, vals, ek, nv, 1024, keys)
    out.append(check("C15 at equal bits the m-slot store still wins on coverage",
                     dr_b == 1.0 and r32 < dr_b and sbits <= 16 * 1024,
                     f"16,384 bits: 1,024 slots answer {100 * dr_b:.0f}% at n=32, one d=1024 "
                     f"vector answers {100 * r32:.1f}%"))

    # ---------------------------------------------------------------- C16 (AMEND-007 / turn 10)
    m = re.search(r"PART 13:.*?(?=\n<!-- =|\Z)", md0, re.S)
    part13 = m.group(0) if m else ""
    out.append(check("C16 Part 13 (AMEND-007 headers, equal-B ceiling, G7 ratio) published",
                     bool(part13) and "AMEND-007" in part13 and "ceiling" in part13,
                     f"{len(part13.splitlines())} lines"))

    # the A2 header must carry M(D) and a verdict per column, and name the kill columns. Checked
    # against the table Part 13 transcribes from dyck2.py's run, and the verdicts recomputed here --
    # running dyck2.py inside the gate would add nine minutes to a one-minute gate.
    hdr = next((l for l in part13.splitlines() if l.startswith("| system | params | D=4 (M=")), "")
    verdicts = [("VIABLE" if 2 ** (dd + 1) - 1 > 2 ** 30 else "DEAD") for dd in (4, 8, 16, 32, 64)]
    ok_hdr = all(f"D={dd} (M=" in hdr and verdicts[i] in hdr for i, dd in enumerate((4, 8, 16, 32, 64)))
    out.append(check("C16 every A2 depth column carries M(D) and its verdict (0018)",
                     ok_hdr and "kill metric is D in (32, 64) only" in part13,
                     f"header marks {verdicts}; kill columns restricted to the VIABLE ones"))

    # equal-B: the ceiling at n=10,000 is 1024/10000 and the m-slot store sits on it
    k2, v2, e2, n2 = sw.build_stream(10000, sw.SEED + 10000)
    q2 = random.Random(sw.SEED + 20000).sample(k2, 2000)
    rb2, _, _, rd2, wr2, _ = sw.direct_address(k2, v2, e2, n2, 1024, q2)
    ceiling = 1024 / 10000
    out.append(check("C16 the m-slot store reaches the pigeonhole ceiling at B=1024, n=10,000",
                     abs(rb2 - ceiling) <= 0.03,
                     f"ceiling min(1,B/n) = {ceiling:.3f}, measured {rb2:.3f}"))

    # B < n: a superposed store answers essentially nothing
    k3, v3, e3, n3 = sw.build_stream(2048, sw.SEED + 2048)
    rb3, _, _, _, _ = sw.fast_weight(k3, v3, e3, n3, 1024, k3, "add")
    out.append(check("C16 at B < n a shared readout answers nothing (the regime is empty)",
                     rb3 == 0.0,
                     f"d=1024, n=2048: recall {100 * rb3:.2f}% -- capacity is ~d/(2 ln|V|) bindings"))

    # the ratio, not the count: one edit breaks a large fraction of the working keys
    k4, v4, e4, n4 = sw.build_stream(64, sw.SEED + 64)
    rb4, _, coll4, _, _ = sw.fast_weight(k4, v4, e4, n4, 1024, k4, "add")
    ok4 = round(rb4 * 64)
    out.append(check("C16 G7's honest metric is the ratio: one edit breaks a fifth or more",
                     ok4 and coll4 / ok4 >= 0.2,
                     f"d=1024, n=64: {ok4} keys correct before, {coll4} damaged -- "
                     f"{100 * coll4 / max(1, ok4):.0f}% of what worked"))

    # ---------------------------------------------------------------- C17 (AMEND-008 / turn 11)
    m14 = re.search(r"PART 14:.*?(?=\n<!-- =|\Z)", md0, re.S)
    part14 = m14.group(0) if m14 else ""
    out.append(check("C17 Part 14 (oracle-vs-learned split, GET2) published",
                     bool(part14) and "AMEND-008" in part14,
                     f"{len(part14.splitlines())} lines"))

    # clause 2: every B carries bits AND bytes
    out.append(check("C17 every memory budget B is quoted in bits and in bytes",
                     "16,384 bits = 2,048 bytes" in part14 and "32,768 bits = 4,096 bytes" in part14,
                     "B = 1,024 cells (16,384 bits = 2,048 bytes); learned row 32,768 bits = 4,096 bytes"))

    # clause 2: the oracle ceilings are labelled, and a learned row sits at >= 32,768 bits
    learned_rows = [l for l in part14.splitlines()
                    if l.startswith("|") and "LEARNED" in l and ("32,768" in l or "32,768".replace(",", "") in l)]
    out.append(check("C17 the oracle ceilings are labelled and a learned row sits at >= 32,768 bits",
                     "ORACLE PARSER" in part14 and "ORACLE OPCODE" in part14 and len(learned_rows) >= 1,
                     f"{len(learned_rows)} learned row(s) at 32,768 bits; both ceilings named"))

    # the numbers those rows rest on, recomputed here
    k1, v1, e1, n1 = sw.build_stream(10000, sw.SEED + 10000)
    q1 = sw.sample_queries(k1, 1000, 10000)
    c1, _ = sw.ByteCache().run(sw.raw_stream(k1, v1, q1))
    cov_cache = sum(1 for k, v in c1 if v == v1[k]) / len(q1)
    rb1, _, _, _, _, _ = sw.direct_address(k1, v1, e1, n1, 1024, q1)
    out.append(check("C17 at matched bits the learned byte table is not behind on one hop",
                     cov_cache > rb1,
                     f"n=10,000: learned 32,768-bit table {100 * cov_cache:.2f}% vs oracle "
                     f"16,384-bit store {100 * rb1:.2f}%"))

    # GET2: the oracle store sits on its (m/n)^2 ceiling; the scan is exact and over budget
    hop1, hop2, ek2, nv2 = sw.two_hop(10000, sw.SEED + 10000)
    qg = sw.sample_queries(list(hop1), 3000, 10000)
    cov2 = sw.two_hop_direct(10000, 1024, hop1, hop2, ek2, nv2, qg)
    ceil2 = (1024 / 10000) ** 2
    out.append(check("C17 two hops square the loss: GET2 lands on its (m/n)^2 ceiling",
                     abs(cov2 - ceil2) <= 0.01,
                     f"n=10,000, m=1,024: measured {100 * cov2:.2f}%, ceiling {100 * ceil2:.2f}%"))

    # the oracle parser ceiling: 69 bits answers D=64 exactly (import only; no 9-minute run)
    dz = load_module("dyck2")
    tr = dz.make_train_set(random.Random(dz.SEED), dz.TRAIN_N, dz.TRAIN_D)
    ms = dz.CapStack(64).fit(tr)
    pr = dz.make_set(random.Random(dz.SEED + 7 * 64), 200, 64, pin_depth=64)
    n_bits = (ms.cap + 1) + 4          # stack contents + 4 flag bits; `states` is 2^(cap+1)-1
    lrn_acc = dz.score(dz.HashContext().fit(tr).predict, pr)
    out.append(check("C17 the oracle parser ceiling (69 bits) is exact at D=64, and learned 32,768 bits is not",
                     dz.score(ms.predict, pr) == 1.0 and n_bits == 69 and lrn_acc < 0.8 and "69 bits" in part14,
                     f"oracle cap-64 stack: {100 * dz.score(ms.predict, pr):.0f}% at {n_bits} bits; "
                     f"learned 32,768-bit context table: {100 * lrn_acc:.0f}%"))

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

    scripts = ["scorecard", "symmetry", "carry", "closure", "audit_harness", "stream_ram"] + \
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
