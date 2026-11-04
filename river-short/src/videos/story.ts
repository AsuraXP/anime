// Timeline of "The River That Caught Fire" (Cuyahoga, Cleveland, 22 Jun 1969): shots timed to the voice words
// (../voice/words.json), the story physics (train on the trestle, spark ignition, oil-slick fire envelope, cleanup)
// and the camera grammar from the skill: continuous slow push-ins, smootherstep glides 18-40 f, cuts on big jumps,
// 7-frame flip kicks on impacts, 4-5 deg rolls, DOF per beat, foreground props on ~1/3 of shots.
export const FPS = 30;
export const TOTAL = 1930; // 64.33 s; voice ends at 63.67 s
export const D0 = 6.0;     // quay / bank top height (m); water surface at y = 0, river bed at -0.6
export type V3 = [number, number, number];

// ---------------- world layout constants ----------------
export const TRESTLE_X = -8;          // railroad trestle crosses the river along z at x = -8, deck y = 9.2
export const TRESTLE_Y = 9.2;
export const IGN: V3 = [-8, 0.05, -2]; // ignition point on the slick under the trestle
export const FIRE_Z = -3;              // the burning slick line runs along x at z ~ FIRE_Z
export const FIRE_X0 = -42, FIRE_X1 = 30; // fire spread limits along x
export const BOAT: V3 = [16, 0, 7];    // fireboat
export const SIGN_AT: V3 = [4, D0, 31.6]; // "no dumping" sign on the near quay
export const KITCHEN: V3 = [400, 0, -6];  // kitchen set lives far away at x=400 (stove top at 400.4, 1.19, -8.0)
export const KAYAK0: V3 = [18, 0, 3];  // kayak start
export const IGNITE = 19.70;           // s: spark lands, slick ignites
export const OUT = 29.0;               // s: fire out

// ---------------- story physics ----------------
export const clamp01 = (x: number) => Math.max(0, Math.min(1, x));
export const smooth = (x: number) => { const u = clamp01(x); return u * u * (3 - 2 * u); };
const lin = (pts: [number, number][], x: number) => {
  if (x <= pts[0][0]) return pts[0][1];
  for (let i = 1; i < pts.length; i++) if (x <= pts[i][0]) {
    const [x0, y0] = pts[i - 1], [x1, y1] = pts[i];
    return y0 + ((y1 - y0) * (x - x0)) / (x1 - x0);
  }
  return pts[pts.length - 1][1];
};

/** fire envelope 0..1: ignites at IGNITE, full by +1.2 s, holds to 24 s, dies out by OUT */
export const fireAt = (t: number) =>
  lin([[IGNITE - 0.12, 0], [IGNITE + 1.1, 1], [24.0, 1], [OUT, 0], [OUT + 2, 0]], t);
/** how far the fire has spread along x at time t (m each side of the ignition point) */
export const fireSpread = (t: number) => clamp01((t - IGNITE) / 2.2) * 16 + 3;
/** flame height multiplier per metre from the ignition point (biggest at the trestle) */
export const flameH = (x: number, t: number) => {
  const d = Math.abs(x - IGN[0]);
  const env = fireAt(t);
  return env * (2.2 + 11 * Math.exp(-d / 14)) * (0.85 + 0.3 * Math.sin(t * 9 + x));
};

// train: crosses the trestle (moves along -z) during shots 4-5
export const TRAIN_T0 = 12.9, TRAIN_T1 = 18.9;
export const trainZ = (t: number) => (t <= TRAIN_T0 ? 46 : t >= TRAIN_T1 ? -46 : 46 - ((t - TRAIN_T0) / (TRAIN_T1 - TRAIN_T0)) * 92);
/** sparks fly while the loco is over the slick (z between -14 and 6) and until ignition + 1 s */
export const sparking = (t: number) => t > TRAIN_T0 + 1.2 && t < IGNITE + 1.0 && trainZ(t) > -14 && trainZ(t) < 8;

// kayak drifts during the ending shots
export const kayakX = (t: number) => (t < 54.3 ? KAYAK0[0] : KAYAK0[0] - (t - 54.3) * 1.1);

export type RiverState = { fire: number; train: number; sparks: boolean };
export const riverState = (t: number): RiverState => ({ fire: fireAt(t), train: trainZ(t), sparks: sparking(t) });

// ---------------- shots ----------------
export type Light = "day" | "golden" | "smoke";
export type Crowd = "none" | "quay" | "shock" | "fire" | "photo" | "sign" | "kayak";
export type ShotDef = { id: number; a: number; b: number; light: Light; crowd: Crowd; towns?: boolean };
export const SHOTS: ShotDef[] = [
  { id: 1, a: 0, b: 110, light: "day", crowd: "none" },
  { id: 2, a: 110, b: 280, light: "day", crowd: "quay", towns: true },
  { id: 3, a: 280, b: 380, light: "day", crowd: "none" },
  { id: 4, a: 380, b: 560, light: "day", crowd: "quay" },
  { id: 5, a: 560, b: 645, light: "day", crowd: "none" },
  { id: 6, a: 645, b: 730, light: "smoke", crowd: "shock" },
  { id: 7, a: 730, b: 835, light: "smoke", crowd: "fire" },
  { id: 8, a: 835, b: 935, light: "smoke", crowd: "photo" },
  { id: 9, a: 935, b: 1120, light: "day", crowd: "none" },
  { id: 10, a: 1120, b: 1255, light: "day", crowd: "none" },
  { id: 11, a: 1255, b: 1435, light: "golden", crowd: "quay", towns: true },
  { id: 12, a: 1435, b: 1620, light: "golden", crowd: "sign" },
  { id: 13, a: 1620, b: 1830, light: "day", crowd: "kayak" },
  { id: 14, a: 1830, b: TOTAL, light: "day", crowd: "kayak", towns: true },
];
/** crossfades (frames) at place/time changes; a white 4-frame flash after the hook */
export const XFADE: Record<number, number> = { 9: 8, 11: 8, 13: 8 };
export const FLASH_AT = 106;

export const shotAt = (f: number) => SHOTS.find((s) => f >= s.a && f < s.b) ?? SHOTS[SHOTS.length - 1];
export const layersAt = (f: number): { id: number; alpha: number }[] => {
  for (const s of SHOTS) {
    const x = XFADE[s.id];
    if (x && f >= s.a - x / 2 && f < s.a + x / 2) return [{ id: s.id - 1, alpha: 1 }, { id: s.id, alpha: (f - (s.a - x / 2) + 1) / (x + 1) }];
  }
  return [{ id: shotAt(f).id, alpha: 1 }];
};

// ---------------- camera ----------------
export type Cam = { pos: V3; look: V3; fov: number; roll: number };
type Shot = Partial<Cam> & { pos: V3; look: V3 };
type Key = { f: number; dur?: number; cut?: boolean; s: (f: number) => Shot };
export const glide = (u: number) => { const x = clamp01(u); return x * x * x * (x * (6 * x - 15) + 10); };
const mix = (a: Cam, b: Cam, k: number): Cam => ({
  pos: a.pos.map((v, i) => v + (b.pos[i] - v) * k) as V3, look: a.look.map((v, i) => v + (b.look[i] - v) * k) as V3,
  fov: a.fov + (b.fov - a.fov) * k, roll: a.roll + (b.roll - a.roll) * k,
});
const full = (c: Shot): Cam => ({ fov: 40, roll: 0, ...c });
const run = (keys: Key[], f: number) => {
  let cur = full(keys[0].s(f));
  for (let i = 1; i < keys.length; i++) {
    const k = keys[i];
    if (f < k.f) break;
    cur = k.cut ? full(k.s(f)) : mix(cur, full(k.s(f)), glide((f - k.f) / (k.dur ?? 24)));
  }
  return cur;
};
const T = (f: number) => f / FPS;
/** push-in factor since f0: the subject grows ~rate per frame; `punch` raises it (8 f soft edges) for the first n frames */
const pushK = (f: number, f0: number, rate: number, punch = 0, n = 35) => {
  const x = Math.max(0, f - f0);
  let s = rate * x;
  if (punch > rate) for (let i = 0; i < Math.min(x, n); i++) s += (punch - rate) * Math.max(0, Math.min(1, (i + 0.5) / 8, (n - i - 0.5) / 8));
  return Math.exp(-s);
};
const dolly = (pos: V3, look: V3, k: number, rest: Partial<Cam> = {}): Shot =>
  ({ pos: [look[0] + (pos[0] - look[0]) * k, look[1] + (pos[1] - look[1]) * k, look[2] + (pos[2] - look[2]) * k], look, ...rest });
const zoom = (pos: V3, look: V3, fov: number, k: number, rest: Partial<Cam> = {}): Shot =>
  ({ pos, look, fov: (360 / Math.PI) * Math.atan(Math.tan((fov * Math.PI) / 360) * k), ...rest });

// ---- framings ----
// shot 1 (hook): high aerial over the city and the oily river -> drop to a low 3/4 over the slick
const S1a = (f: number) => zoom([20, 7.5, 28], [-8, 0.5, -12], 44, pushK(f, 0, 0.0022));
const S1b = (f: number) => dolly([22, 14, 38], [-10, 0, -10], pushK(f, 62, 0.0028, 0.006, 30), { fov: 40, roll: -0.03 });
// shot 2 (riverfront + factories): quay level down the river -> factory + chimney CU
const S2a = (f: number) => dolly([14, D0 + 1.8, 33.5], [-24, 8.5, -48], pushK(f, 110, 0.0022), { fov: 42 });
const S2b = (f: number) => dolly([1.5, D0 + 1.6, 34.6], [-36, 13, -62], pushK(f, 190, 0.0026), { fov: 38, roll: 0.04 });
// shot 3: low over the water at the slick edge -> closer on the oil + floating garbage
const S3a = (f: number) => dolly([24, 3.2, -2], [-30, 0.2, -8], pushK(f, 280, 0.0022), { fov: 38 });
const S3b = (f: number) => dolly([18, 2.0, 2], [-24, 0.05, -9], pushK(f, 330, 0.0026, 0.005, 30), { fov: 34, roll: 0.035 });
// shot 4: trestle side view while the train crosses -> higher 3/4
const S4a = (f: number) => dolly([-6.5, 10.0, 20], [-9.5, 8.8, -12], pushK(f, 380, 0.0022), { fov: 42 });
const S4b = (f: number) => dolly([31, 13.5, 41], [TRESTLE_X, 8.0, -16], pushK(f, 470, 0.0024), { fov: 40, roll: -0.03 });
// shot 5: under/near the trestle, sparks falling to the slick; ignition punch on "erupted" is shot 6
const S5a = (f: number) => dolly([7, 10.5, 17], [TRESTLE_X, 1.2, -4], pushK(f, 560, 0.0026), { fov: 40 });
const S5b = (f: number) => dolly([-3, 13, 19], [TRESTLE_X, 2.0, -5], pushK(f, 600, 0.0024, 0.006, 30), { fov: 38, roll: 0.04 });
// shot 6: the eruption — wide from the bank, onlookers in the near foreground
const S6a = (f: number) => dolly([16, D0 + 2.0, 38], [IGN[0], 4, IGN[2]], pushK(f, 645, 0.0024, 0.006, 32), { fov: 42 });
const S6b = (f: number) => dolly([9, D0 + 1.4, 34.5], [IGN[0] - 1, 6.0, IGN[2]], pushK(f, 690, 0.002), { fov: 38, roll: -0.035 });
// shot 7: wide of the burning river + the fireboat working (left of frame)
const S7a = (f: number) => dolly([-24, D0 + 3.2, 41], [2, 3.5, -8], pushK(f, 730, 0.0022), { fov: 44 });
const S7b = (f: number) => dolly([-16, D0 + 2.4, 38], [6, 4.5, -4], pushK(f, 780, 0.0022), { fov: 40, roll: 0.035 });
// shot 8: the photographer kid on the quay, flash on "Time magazine"
const S8a = (f: number) => dolly([3.5, D0 + 1.7, 37.2], [-2, D0 + 1.55, 33.4], pushK(f, 835, 0.0024), { fov: 40 });
const S8b = (f: number) => dolly([1.8, D0 + 1.65, 36.2], [-2.2, D0 + 1.5, 33.2], pushK(f, 880, 0.0026, 0.005, 28), { fov: 36, roll: 0.04 });
// shot 9: the kitchen — wide of the stove corner
const S9a = (f: number) => dolly([404.4, 1.8, 3.0], [400, 1.05, -7.6], pushK(f, 935, 0.0022), { fov: 42 });
const S9b = (f: number) => dolly([402.8, 1.65, 0.8], [400, 1.05, -7.8], pushK(f, 1000, 0.0024), { fov: 38, roll: -0.03 });
// shot 10: pan CU — the grease layer catches
const S10a = (f: number) => dolly([401.8, 1.95, -4.4], [400.3, 1.12, -8.0], pushK(f, 1120, 0.003, 0.006, 30), { fov: 34 });
const S10b = (f: number) => dolly([400.9, 1.62, -5.5], [400.35, 1.12, -8.0], pushK(f, 1180, 0.0024), { fov: 30, roll: 0.03 });
// shot 11: golden-hour riverfront after the fire
const S11a = (f: number) => dolly([22, D0 + 2.6, 45], [-12, 5, -22], pushK(f, 1255, 0.0022), { fov: 42 });
const S11b = (f: number) => dolly([12, D0 + 2.0, 39], [-2, 4.5, -10], pushK(f, 1340, 0.0022, 0.005, 28), { fov: 38, roll: 0.04 });
// shot 12: the new rule's sign on the quay
const S12a = (f: number) => dolly([5.4, D0 + 2.1, 37.6], [SIGN_AT[0], D0 + 1.5, SIGN_AT[2] - 0.6], pushK(f, 1435, 0.0026, 0.005, 30), { fov: 44 });
const S12b = (f: number) => dolly([3.4, D0 + 1.7, 35.2], [SIGN_AT[0] + 0.3, D0 + 1.3, SIGN_AT[2] - 0.4], pushK(f, 1520, 0.002), { fov: 32, roll: -0.03 });
// shot 13: present-day clean river, the kayaker crossing
const S13a = (f: number) => dolly([10, 4.6, 23], [kayakX(T(f)), 0.8, 2.5], pushK(f, 1620, 0.0022), { fov: 40 });
const S13b = (f: number) => dolly([4, 6.8, 27], [kayakX(T(f)) - 0.5, 0.9, 2.2], pushK(f, 1720, 0.0024, 0.005, 30), { fov: 36, roll: 0.035 });
// shot 14: crane out over the clean river and town
const S14a = (f: number) => dolly([6, 8.5, 30], [-4, 1.5, -6], pushK(f, 1830, 0.0022), { fov: 40 });
const S14b = (f: number) => { const s = glide((f - 1870) / 55); const a = S14a(1870); return { pos: [a.pos[0] + 22 * s, a.pos[1] + 7 * s, a.pos[2] + 26 * s] as V3, look: [-10, 1.0, -18] as V3, fov: a.fov + (46 - a.fov) * s, roll: 0 }; };

const CAMS: Record<number, Key[]> = {
  1: [{ f: 0, s: S1a }, { f: 62, dur: 40, s: S1b }],
  2: [{ f: 110, s: S2a }, { f: 190, dur: 26, s: S2b }],
  3: [{ f: 280, s: S3a }, { f: 330, dur: 30, s: S3b }],
  4: [{ f: 380, s: S4a }, { f: 470, dur: 26, s: S4b }],
  5: [{ f: 560, s: S5a }, { f: 600, dur: 24, s: S5b }],
  6: [{ f: 645, s: S6a }, { f: 690, dur: 22, s: S6b }],
  7: [{ f: 730, s: S7a }, { f: 780, dur: 26, s: S7b }],
  8: [{ f: 835, s: S8a }, { f: 880, dur: 26, s: S8b }],
  9: [{ f: 935, s: S9a }, { f: 1000, dur: 30, s: S9b }],
  10: [{ f: 1120, s: S10a }, { f: 1180, dur: 30, s: S10b }],
  11: [{ f: 1255, s: S11a }, { f: 1340, dur: 26, s: S11b }],
  12: [{ f: 1435, s: S12a }, { f: 1520, dur: 28, s: S12b }],
  13: [{ f: 1620, s: S13a }, { f: 1720, dur: 30, s: S13b }],
  14: [{ f: 1830, s: S14a }, { f: 1870, dur: 55, s: S14b }],
};

// impact kicks: ignition boom + eruption
const KICKS: [number, number][] = [[IGNITE + 0.05, 1.5], [IGNITE + 0.75, 1.0], [22.6, 0.6]];
export const kickAt = (t: number) => {
  let a = 0;
  for (const [t0, g] of KICKS) {
    const n = Math.floor((t - t0) * FPS + 1e-6);
    if (n >= 0 && n < 7) a += g * (n % 2 ? -1 : 1) * (1 - n / 7) ** 1.5;
  }
  return a;
};
export const camAt = (id: number, f: number): Cam => {
  const c = run(CAMS[id] ?? CAMS[1], f), a = kickAt(T(f));
  if (!a) return c;
  const d: V3 = [c.look[0] - c.pos[0], c.look[1] - c.pos[1], c.look[2] - c.pos[2]];
  const L = Math.hypot(...d), h = Math.hypot(d[0], d[2]) || 1;
  const m = (3 / 640) * Math.tan((c.fov * Math.PI) / 360) * L * a;
  return { ...c, look: [c.look[0] - (d[2] / h) * m, c.look[1] + 0.6 * m, c.look[2] + (d[0] / h) * m], roll: c.roll + a * 0.004 };
};

// ---------------- lens ----------------
export type Dof = { f: number; dur?: number; cInf: number; focus?: (f: number) => V3 };
export const DOF: Dof[] = [
  { f: 0, cInf: 12, focus: () => [TRESTLE_X, 4, -8] },   // hook aerial: river sharp-ish
  { f: 62, dur: 40, cInf: 14, focus: () => IGN },          // low over the slick
  { f: 110, cInf: 0 },                                     // street wide
  { f: 190, dur: 26, cInf: 10, focus: () => [-36, 13, -62] }, // factory CU
  { f: 280, cInf: 12, focus: () => [-9, 0.05, -3] },       // slick CU
  { f: 330, dur: 30, cInf: 14, focus: () => [-9, 0.05, -3] },
  { f: 380, cInf: 0 },                                     // trestle side
  { f: 470, dur: 26, cInf: 8, focus: () => [TRESTLE_X, TRESTLE_Y, -10] },
  { f: 560, cInf: 10, focus: () => [TRESTLE_X, 5, -4] },   // sparks / trestle underside
  { f: 600, dur: 24, cInf: 12, focus: () => IGN },
  { f: 645, cInf: 8, focus: () => [IGN[0], 6, IGN[2]] },   // eruption wide (flames sharp, bank soft-ish)
  { f: 690, dur: 22, cInf: 12, focus: () => [IGN[0], 7, IGN[2]] },
  { f: 730, cInf: 0 },                                     // burning river wide
  { f: 780, dur: 26, cInf: 9, focus: () => [BOAT[0], 1.6, BOAT[2]] }, // fireboat
  { f: 835, cInf: 12, focus: () => [-2, D0 + 1.55, 33.4] }, // photographer kid
  { f: 880, dur: 26, cInf: 14, focus: () => [-2.2, D0 + 1.5, 33.2] },
  { f: 935, cInf: 0 },                                     // kitchen wide
  { f: 1000, dur: 30, cInf: 7, focus: () => [400, 1.05, -7.6] },
  { f: 1120, cInf: 14, focus: () => [400.3, 1.12, -8.0] },  // pan CU
  { f: 1180, dur: 30, cInf: 16, focus: () => [400.35, 1.12, -8.0] },
  { f: 1255, cInf: 0 },                                    // golden riverfront
  { f: 1340, dur: 26, cInf: 6 },
  { f: 1435, cInf: 12, focus: () => [SIGN_AT[0], D0 + 1.35, SIGN_AT[2] - 0.4] }, // sign CU
  { f: 1520, dur: 28, cInf: 14, focus: () => [SIGN_AT[0] + 0.3, D0 + 1.3, SIGN_AT[2] - 0.4] },
  { f: 1620, cInf: 10, focus: (f) => [kayakX(T(f)), 0.9, 2.5] }, // kayaker
  { f: 1720, dur: 30, cInf: 12, focus: (f) => [kayakX(T(f)) * 0.7 - 1, 0.9, 1.8] },
  { f: 1830, cInf: 0 },                                    // clean river wide, crane out
];
export const dofAt = (f: number) => {
  let i = 0; while (i + 1 < DOF.length && f >= DOF[i + 1].f) i++;
  const d = DOF[i], p = DOF[Math.max(0, i - 1)];
  const k = d.dur ? Math.min(1, (f - d.f) / d.dur) : 1;
  return { cInf: p.cInf + (d.cInf - p.cInf) * k, focus: d.focus };
};
export const focusAt = (id: number, f: number): V3 => {
  const d = dofAt(f);
  return d.focus ? d.focus(f) : camAt(id, f).look;
};

/** near framing objects */
export type Fg = { a: number; b: number; kit: string; pos: V3; s?: number; yaw?: number };
export const FOREGROUND: Fg[] = [
  { a: 1255, b: 1435, kit: "plant_bushDetailed", pos: [26.5, D0, 43.5], s: 1.5, yaw: 0.4 }, // golden riverfront bush
  { a: 835, b: 935, kit: "plant_bushDetailed", pos: [7.9, D0, 36.2], s: 2.4, yaw: -0.6 },   // photographer shot bush at frame edge
];
