// Our cast as lit flat sprites in the 3D world. Each frame every character asks for a drawing (a key + a draw call);
// the pool keeps one canvas per distinct drawing, so a quay full of townsfolk shares canvases (6 outfits x 7 head shapes).
// Characters are yaw-only billboards shaded by cardShade(); standing ones get a soft multiply contact blob.
// Effects are unlit cards (flames, sparks, smoke, foam, fish, flash, flotsam). Cards/blobs live on the NOINK layer.
import * as THREE from "three";
import {
  Pen, bodyFront, bodySide, townsfolk, KID, fxBurst, fxPuff, fxStars, fxRing, fxContact, fxPlank, fxDrum, fxFlame, fxSpark, fxSmokeBig, fxFish, fxFlash, fxFoam, fxMag,
  Outfit, Expr, FrontOpts, SideOpts, fxShadow,
} from "./toon";
import {
  FPS, D0, SHOTS, V3, RiverState, TRESTLE_X, TRESTLE_Y, IGN, FIRE_Z, FIRE_X0, FIRE_X1, BOAT, SIGN_AT,
  IGNITE, OUT, TRAIN_T0, TRAIN_T1, kayakX, fireSpread, flameH,
  clamp01,
} from "./story";
import { NOINK } from "./ink";
import { cardShade, blobMaterial, CARD_K } from "./cardshade";

// ---------------- canvas pool ----------------
type Entry = { cv: HTMLCanvasElement; tex: THREE.CanvasTexture; w: number; h: number };
export type Req = { key: string; w: number; h: number; k: number; draw: (p: Pen) => void; tex?: THREE.CanvasTexture };
const makeEntry = (w: number, h: number): Entry => {
  const cv = document.createElement("canvas");
  cv.width = w; cv.height = h;
  const tex = new THREE.CanvasTexture(cv);
  tex.colorSpace = THREE.SRGBColorSpace; tex.anisotropy = 8;
  return { cv, tex, w, h };
};
export class Pool {
  private live = new Map<string, Entry>();
  private free: Entry[] = [];
  private reqs: Req[] = [];
  req(key: string, w: number, h: number, k: number, draw: (p: Pen) => void) {
    const r: Req = { key: `${w}x${h}|${key}`, w, h, k, draw };
    this.reqs.push(r);
    return r;
  }
  flush() {
    const want = new Map<string, Req[]>();
    for (const r of this.reqs) { const l = want.get(r.key); if (l) l.push(r); else want.set(r.key, [r]); }
    for (const [key, e] of this.live) if (!want.has(key)) { this.live.delete(key); this.free.push(e); }
    for (const [key, rs] of want) {
      let e = this.live.get(key);
      if (!e) {
        const r = rs[0], i = this.free.findIndex((x) => x.w === r.w && x.h === r.h);
        e = i >= 0 ? this.free.splice(i, 1)[0] : makeEntry(r.w, r.h);
        const g = e.cv.getContext("2d")!;
        g.setTransform(1, 0, 0, 1, 0, 0); g.clearRect(0, 0, e.w, e.h); g.setTransform(r.k, 0, 0, r.k, 0, 0);
        r.draw(new Pen(g));
        e.tex.needsUpdate = true;
        this.live.set(key, e);
      }
      for (const r of rs) r.tex = e.tex;
    }
    this.reqs = [];
  }
}

// ---------------- sprite meshes ----------------
const blank = (() => { const c = document.createElement("canvas"); c.width = c.height = 2; return new THREE.CanvasTexture(c); })();
export const SU = 0.00216; // metres per design unit: 1000 units = 2.16 m
const BODY = (() => { const g = new THREE.PlaneGeometry(600 * SU, 1000 * SU); g.translate(0, (975 - 500) * SU, 0); return g; })();
const CARD = new THREE.PlaneGeometry(1, 1);
const ROOTS = new Set<THREE.Object3D>();

/** lit flat character: cardShade() material, receives shadows (dims to the bright floor only), casts its silhouette
 *  when world.ts says so (golden). Drawn after the contact blobs (renderOrder 1). */
export class Actor {
  mesh: THREE.Mesh; mat: THREE.MeshLambertMaterial; dmat: THREE.MeshDepthMaterial; r: Req | null = null;
  constructor(parent: THREE.Object3D, geo: THREE.BufferGeometry = BODY) {
    this.mat = cardShade(new THREE.MeshLambertMaterial({ map: blank, alphaTest: 0.5, side: THREE.DoubleSide }));
    this.mat.alphaToCoverage = false;
    this.dmat = new THREE.MeshDepthMaterial({ depthPacking: THREE.RGBADepthPacking, map: blank, alphaTest: 0.5, side: THREE.DoubleSide });
    this.mesh = new THREE.Mesh(geo, this.mat);
    this.mesh.customDepthMaterial = this.dmat;
    this.mesh.onBeforeRender = (r) => { const rt = r.getRenderTarget(); CARD_K.uPx.value = (rt ? rt.height : r.domElement.height) / 1920; };
    this.mesh.castShadow = false; this.mesh.receiveShadow = true; this.mesh.visible = false;
    this.mesh.rotation.order = "YXZ"; this.mesh.renderOrder = 1; this.mesh.layers.set(NOINK);
    parent.add(this.mesh);
    ROOTS.add(parent);
  }
  bind() { const t = this.r?.tex; if (t) { this.mat.map = t; this.dmat.map = t; } }
}
/** unlit effect card: hard cut-out or soft see-through; `col` on the place tints the material (HDR "x r,g,b" allowed) */
export class Fx {
  mesh: THREE.Mesh; mat: THREE.MeshBasicMaterial; soft: THREE.MeshBasicMaterial; blob: THREE.MeshBasicMaterial; r: Req | null = null;
  constructor(parent: THREE.Object3D) {
    this.mat = new THREE.MeshBasicMaterial({ map: blank, alphaTest: 0.5, side: THREE.DoubleSide });
    this.mat.alphaToCoverage = false;
    this.soft = new THREE.MeshBasicMaterial({ map: blank, transparent: true, depthWrite: false, side: THREE.DoubleSide });
    this.blob = blobMaterial(blank);
    this.mesh = new THREE.Mesh(CARD, this.mat);
    this.mesh.visible = false; this.mesh.layers.set(NOINK);
    parent.add(this.mesh);
  }
  use(soft: boolean) { this.mesh.material = soft ? this.soft : this.mat; }
  bind() {
    const t = this.r?.tex;
    if (!t) return;
    if (this.r!.key.includes("|blob|")) {
      if (t.generateMipmaps) { t.generateMipmaps = false; t.minFilter = THREE.LinearFilter; t.needsUpdate = true; }
      this.blob.map = t; this.mesh.material = this.blob; this.mesh.renderOrder = 0.5;
    }
    else { this.mat.map = t; this.soft.map = t; this.mesh.renderOrder = 0; }
  }
}

// ---------------- placements ----------------
export type Place = {
  key: string; draw: (p: Pen) => void; x: number; y: number; z: number;
  scale?: number; mirror?: boolean; yaw?: number; roll?: number; size?: [number, number, number];
};
export type FxPlace = { key: string; cw: number; ch: number; draw: (p: Pen) => void; x: number; y: number; z: number; w: number; h: number; flat?: boolean; rot?: number; soft?: boolean; col?: string; base?: boolean };
export type CamInfo = { pos: THREE.Vector3; right: THREE.Vector3; sun?: THREE.Vector3 };

const hh = (i: number, s = 0) => { const v = Math.sin(i * 127.1 + s * 311.7) * 43758.5453; return v - Math.floor(v); };
const q = (v: number, n = 120) => Math.round(v * n) / n;
const FOLK = [0, 1, 2, 3, 4, 5].map((v) => townsfolk(v));
const seedOf = (i: number) => ((i * 5 + 3) % 7) + 1;
const tier = (d: number): [number, number, number] =>
  d < 3.2 ? [1800, 3000, 3.0] : d < 6.5 ? [1080, 1800, 1.8] : d < 16 ? [480, 800, 0.8] : [240, 400, 0.4];

// ---------------- light ----------------
const SUN = new THREE.Vector3(0.5, 0.75, -0.4).normalize();
const tmp = new THREE.Vector3();
let LNAME = "day";
const sunOf = (root: THREE.Object3D) => {
  let s: THREE.DirectionalLight | null = null;
  root.traverse((o) => { if (!s && o instanceof THREE.DirectionalLight && o.castShadow) s = o; });
  return s as THREE.DirectionalLight | null;
};
const findSun = (cam: CamInfo, out: THREE.Vector3) => {
  if (cam.sun) return out.copy(cam.sun).normalize();
  let best: THREE.DirectionalLight | null = null, err = Infinity;
  for (const r of ROOTS) {
    if (!r.parent) continue;
    const s = sunOf(r);
    if (!s) continue;
    const d = tmp.copy(s.target.position).sub(cam.pos), e = Math.abs(d.dot(cam.right)) / (d.length() || 1);
    if (e < err) { err = e; best = s; }
  }
  return best ? out.copy(best.position).sub(best.target.position).normalize() : out;
};
const light2D = (cam: CamInfo, mirror: boolean) => {
  const sx = SUN.dot(cam.right) * (mirror ? -1 : 1), sy = -SUN.y;
  return Math.round(Math.atan2(sy, sx) / (Math.PI / 4)) * (Math.PI / 4);
};

// ---------------- life: blinks ----------------
const LID = [0.5, 1, 1, 0.5];
const lidAt = (t: number, i: number) => {
  const f = Math.round(t * FPS);
  let s = Math.round(-60 * hh(i, 9));
  for (let n = 0; s <= f && n < 400; n++) {
    const k = f - s;
    if (k >= 0 && k < 4) return LID[k];
    s += Math.round(15 + 54 * hh(i * 31 + n, 13));
  }
  return 0;
};
const fkey = (o: object) => JSON.stringify(o, (_k, v) => (typeof v === "number" ? q(v) : v));

type Who = { i: number; o: Outfit; okey: string };
const person = (cam: CamInfo, who: Who, x: number, y: number, z: number, view: { side: boolean; mirror: boolean }, fo: FrontOpts, so: SideOpts, scale = 1): Place => {
  const d = cam.pos.distanceTo(tmp.set(x, y + 1.2, z)) / scale;
  const [w, h, k] = tier(d);
  const mirror = view.side && view.mirror, light = light2D(cam, mirror), seed = seedOf(who.i);
  const f2: FrontOpts = { ...fo, light, seed }, s2: SideOpts = { ...so, light, seed };
  const key = view.side ? `S|${who.okey}|${fkey(s2)}` : `F|${who.okey}|${fkey(f2)}`;
  return {
    key, x, y, z, scale, mirror,
    draw: (p) => (view.side ? bodySide(p, who.o, s2) : bodyFront(p, who.o, f2)),
    size: [w, h, k],
  };
};

// ---------------- contact shadows ----------------
const CONTACT: Record<string, [number, number, number]> = { day: [0.2, 0.21, 0.33], golden: [0.24, 0.2, 0.33], smoke: [0.16, 0.15, 0.22] };
const TAIL: [number, number, number] = [0.42, 0.44, 0.62];
const toSrgb = (v: number) => { const c = clamp01(v); return c <= 0.0031308 ? 12.92 * c : 1.055 * c ** (1 / 2.4) - 0.055; };
const hexOf = (c: [number, number, number], k: number) => "#" + c.map((v) => Math.round(255 * toSrgb(1 - (1 - v) * k)).toString(16).padStart(2, "0")).join("");
const blob = (out: Stage, x: number, y: number, z: number, sc = 1, k = 1) => {
  const hl = Math.hypot(SUN.x, SUN.z) || 1, ox = -SUN.x / hl, oz = -SUN.z / hl, rot = Math.atan2(-ox, -oz);
  if (LNAME === "day") {
    const el = Math.asin(Math.min(0.99, Math.max(0.1, SUN.y)));
    const len = Math.min(2.4, Math.max(0.5, 1.6 / Math.tan(el))) * sc, h = len + 0.55 * sc, c = 0.3 * h;
    const tc = hexOf(TAIL, k);
    out.fx.push({ key: `blob|shadow|${tc}`, cw: 128, ch: 256, draw: (p) => fxShadow(p, tc), x: x + ox * c, y: y + 0.018, z: z + oz * c, w: 0.72 * sc, h, flat: true, rot });
  }
  const cc = hexOf(CONTACT[LNAME] ?? CONTACT.day, k);
  out.fx.push({ key: `blob|contact|${cc}`, cw: 128, ch: 128, draw: (p) => fxContact(p, cc), x: x + ox * 0.03 * sc, y: y + 0.022, z: z + oz * 0.03 * sc, w: 0.52 * sc, h: 0.4 * sc, flat: true, rot });
};
const WATERLINE = hexOf([0.3, 0.36, 0.52], 1);
const waterBlob = (out: Stage, x: number, z: number, sc = 1) =>
  out.fx.push({ key: `blob|contact|${WATERLINE}`, cw: 128, ch: 128, draw: (p) => fxContact(p, WATERLINE), x, y: 0.034, z, w: 0.8 * sc, h: 0.55 * sc, flat: true });

// ---------------- river outfits ----------------
const WORKER: Outfit = { jacket: "#8a7a5a", pants: "#4a4238", boots: "#2b2622", hat: "cap", cap: "#6a5a3a", belt: "#2b2622" };
const FIREFIGHTER: Outfit = { jacket: "#e8b93a", pants: "#3a3f4a", boots: "#23262c", hat: "cap", cap: "#d42f2f", belt: "#23262c", buttons: "#f4f1ea" };
const KAYAKER: Outfit = { jacket: "#d4483a", pants: "#2e4a6a", boots: "#f4f1ea", hat: null, hair: "#3a2c22", belt: "#f4f1ea" };

export type Stage = { places: Place[]; fx: FxPlace[] };

// ---------------- crowds ----------------
/** townsfolk along one quay. bank 1 = near (z +31.6..35), -1 = far (z -31.6..-35) */
const quayCrowd = (cam: CamInfo, t: number, out: Stage, bank: 1 | -1, n: number, x0: number, x1: number, expr: (i: number, t: number) => Expr, wave = false) => {
  for (let i = 0; i < n; i++) {
    const x = x0 + ((x1 - x0) * i) / Math.max(1, n - 1) + (hh(i, 3) - 0.5) * 1.2;
    const z = bank * (31.6 + hh(i, 2) * 3.0);
    const kid = i % 5 === 2, o = kid ? KID : FOLK[i % 6];
    const who: Who = { i: i + 300 + bank * 7, o, okey: kid ? "kid" : `f${i % 6}` };
    const fo: FrontOpts = { mode: "stand", expr: expr(i, t), wave: wave ? q(Math.sin(t * 8 + i), 30) : undefined, blink: lidAt(t, i + 40) };
    out.places.push(person(cam, who, x, D0, z, { side: false, mirror: false }, fo, {}, kid ? 0.72 : 1));
    blob(out, x, D0, z, kid ? 0.72 : 1);
  }
};

/** a few workers by the factory on the far bank */
const workers = (cam: CamInfo, t: number, out: Stage, n: number, x0: number, x1: number, expr: Expr = "neutral") => {
  for (let i = 0; i < n; i++) {
    const x = x0 + ((x1 - x0) * i) / Math.max(1, n - 1) + (hh(i, 5) - 0.5);
    const z = -(32.2 + hh(i, 6) * 2.4);
    const who: Who = { i: i + 500, o: WORKER, okey: "wk" };
    out.places.push(person(cam, who, x, D0, z, { side: false, mirror: false }, { mode: "stand", expr, blink: lidAt(t, i + 60) }, {}));
    blob(out, x, D0, z);
  }
};

/** the photographer kid on the near quay (shot 8) + the flash + the magazine card */
const FLASH2 = 858; // frame of the camera flash ("Time magazine" beat)
const photographer = (cam: CamInfo, t: number, f: number, out: Stage) => {
  const x = -2, z = 33.4;
  out.places.push(person(cam, { i: 88, o: KID, okey: "photog" }, x, D0, z, { side: false, mirror: false },
    { mode: "stand", expr: t > 26.0 && t < 30.69 ? "grin" : "smile", blink: lidAt(t, 88) }, {}));
  blob(out, x, D0, z, 1.05);
  out.places.push(person(cam, { i: 89, o: FOLK[3], okey: "f3" }, x - 1.6, D0, z - 0.7, { side: false, mirror: false },
    { mode: "stand", expr: "smile", look: 1, blink: lidAt(t, 89) }, {}));
  blob(out, x - 1.6, D0, z - 0.7);
  if (f >= FLASH2 && f < FLASH2 + 16) {
    const u = q((f - FLASH2) / 16, 40);
    out.fx.push({ key: `flash${u}`, cw: 400, ch: 400, draw: (p) => fxFlash(p, u), x: x + 0.25, y: D0 + 1.62, z: z - 0.25, w: 2.6, h: 2.6, col: "x3.2,3.0,2.6" });
  }
  if (f >= FLASH2 + 8 && f < 935) { // the burning-river magazine drifts up and away
    const u = q((f - FLASH2 - 8) / 70, 60), fade = u > 0.85 ? (1 - u) / 0.15 : 1;
    out.fx.push({ key: "mag", cw: 500, ch: 660, draw: (p) => fxMag(p), x: x + 0.4 + u * 1.6, y: D0 + 1.7 + u * 1.5, z: z - 0.4, w: 0.62 * fade + 0.001, h: 0.82 * fade + 0.001, rot: 0.25 + u * 0.5 });
  }
};

/** the kayaker (shots 13-14) riding the kayak mesh from world.ts */
const kayaker = (cam: CamInfo, t: number, out: Stage) => {
  const x = kayakX(t), z = 2.5, bob = 0.04 * Math.sin(t * 2.1);
  out.places.push(person(cam, { i: 90, o: KAYAKER, okey: "kayak" }, x, 0.5 + bob, z, { side: false, mirror: false },
    { mode: "sit", expr: t > 61.6 ? "laugh" : "smile", blink: lidAt(t, 90) }, {}, 0.95));
  waterBlob(out, x, z, 1.1);
  if (x > 4 && x < 20) out.fx.push({ key: `ring${q(((t * 0.5) % 1), 30)}`, cw: 600, ch: 600, draw: (p) => fxRing(p, q(((t * 0.5) % 1), 30)), x, y: 0.03, z, w: 2.2, h: 2.2, flat: true });
};

// ---------------- fire, sparks, smoke, foam, fish, flotsam, pan ----------------
const FLAME_COL = "x1.7,0.5,0.12";
const fireFx = (t: number, st: RiverState, out: Stage) => {
  if (st.fire <= 0.02) return;
  const spread = fireSpread(t);
  const x0 = Math.max(FIRE_X0, IGN[0] - spread), x1 = Math.min(FIRE_X1, IGN[0] + spread);
  for (let x = x0; x <= x1 + 0.01; x += 3.0) {
    const h = flameH(x, t);
    if (h < 0.35) continue;
    const seed = 1 + Math.round(hh(Math.round(x * 7)) * 6);
    const u = q((t * 2.3 + x * 0.37) % 1, 30);
    const z = FIRE_Z + (hh(Math.round(x * 13), 2) - 0.5) * 3.2;
    out.fx.push({ key: `flame|${u}|${seed}`, cw: 300, ch: 600, draw: (p) => fxFlame(p, u, seed), x, y: 0.06, z,
      w: 1.0 + h * 0.11, h: h * 0.68, rot: (hh(Math.round(x * 5), 3) - 0.5) * 0.18, col: FLAME_COL, base: true });
    if (hh(Math.round(x * 3), 4) > 0.45) { // smoke column puff above the taller flames
      const su = q((t * 0.55 + x * 0.11) % 1, 30);
      out.fx.push({ key: `smokebig|${su}`, cw: 400, ch: 400, draw: (p) => fxSmokeBig(p, su), x, y: 0.5 + h * 0.55 + su * 4.5, z: z - 0.5, w: 3.2 + su * 5, h: 3.2 + su * 5, soft: true, rot: su * 0.8 });
    }
  }
  // ignition burst
  if (t >= IGNITE - 0.04 && t < IGNITE + 0.55) {
    const u = q((t - IGNITE + 0.04) / 0.59, 30);
    out.fx.push({ key: `burst|${u}`, cw: 500, ch: 500, draw: (p) => fxBurst(p, u), x: IGN[0], y: 1.0, z: IGN[2], w: 5 + u * 7, h: 5 + u * 7, col: "x3,2.2,1.2" });
  }
};
const sparkFx = (t: number, st: RiverState, out: Stage) => {
  if (!st.sparks) return;
  for (let k = 0; k < 10; k++) {
    const u = q((t * 2.6 + k * 0.173) % 1, 40);
    const x = TRESTLE_X + (hh(k, 1) - 0.5) * 2.4 + u * 1.6;
    const y = (TRESTLE_Y - 0.4) - u * (TRESTLE_Y - 0.7);
    const z = st.train - 6.2 + (hh(k, 2) - 0.5) * 2.2;
    out.fx.push({ key: `spark|${u}`, cw: 120, ch: 120, draw: (p) => fxSpark(p, u), x, y, z, w: 0.5, h: 0.5, col: "x3.2,2.3,0.9" });
  }
};
const trainPuffs = (t: number, st: RiverState, out: Stage) => {
  if (t <= TRAIN_T0 || t >= TRAIN_T1) return;
  for (let k = 0; k < 4; k++) {
    const u = q((t * 0.85 + k * 0.27) % 1, 30);
    out.fx.push({ key: `puff|${u}`, cw: 400, ch: 400, draw: (p) => fxPuff(p, u), x: TRESTLE_X + (hh(k) - 0.5) * 0.6, y: TRESTLE_Y + 4.7 + u * 3.6, z: st.train - 6.4 + u * 2.5,
      w: 0.9 + u * 1.9, h: 0.9 + u * 1.9, soft: true });
  }
};
const hoseFx = (t: number, st: RiverState, out: Stage) => {
  if (st.fire <= 0.05) return;
  const spread = fireSpread(t);
  for (const [tx, k] of [[IGN[0] - spread * 0.45, 0], [IGN[0] + spread * 0.35, 1]] as const) {
    const txc = Math.max(FIRE_X0 + 2, Math.min(FIRE_X1 - 2, tx));
    const mx = (BOAT[0] + txc) / 2, mz = (BOAT[2] + FIRE_Z) / 2;
    const dist = Math.hypot(BOAT[0] - txc, BOAT[2] - FIRE_Z);
    const u = q((t * 1.5 + k * 0.5) % 1, 30);
    out.fx.push({ key: `foam|${u}|${k}`, cw: 700, ch: 700, draw: (p) => fxFoam(p, u), x: mx, z: mz,
      w: dist * 0.5, h: dist * 0.3, y: 0.8 + dist * 0.1, rot: (k ? -1 : 1) * -0.12, col: "#d8ecfa", base: true });
    // foam burst where the jet lands on the fire
    const iu = q((t * 2.2 + k) % 1, 30);
    out.fx.push({ key: `foamhit|${iu}|${k}`, cw: 700, ch: 700, draw: (p) => fxFoam(p, Math.min(1, 0.75 + iu * 0.25)), x: txc, y: 0.9 + iu * 1.0, z: FIRE_Z, w: 2.2, h: 1.5, rot: Math.PI * 0.5 + iu, col: "#ffffff", base: true });
  }
};
const fishFx = (t: number, out: Stage) => {
  for (let k = 0; k < 3; k++) {
    const u = q((t * 0.42 + k * 0.33) % 1, 40);
    out.fx.push({ key: `fish|${u}`, cw: 400, ch: 400, draw: (p) => fxFish(p, u), x: kayakX(t) - 4 + k * 3.1 + u * 1.5, y: 0.12, z: 1.2 + k * 1.4, w: 0.85, h: 0.85, rot: 0.1 * Math.sin(u * 9 + k) });
  }
};
const flotsam = (t: number, out: Stage) => {
  const items: [number, number, "plank" | "drum"][] = [[-14, -7, "plank"], [-6.5, -1, "drum"], [2.5, -8, "plank"], [8, 3, "drum"]];
  items.forEach(([x, z, kind], i) => {
    const bob = 0.03 * Math.sin(t * 1.9 + i * 1.7), r = 0.3 * Math.sin(t * 1.1 + i) + i;
    if (kind === "plank") out.fx.push({ key: `plank${q(bob, 60)}`, cw: 320, ch: 110, draw: fxPlank, x, y: 0.1 + bob, z, w: 1.5, h: 0.52, rot: r });
    else out.fx.push({ key: `drum${q(bob, 60)}`, cw: 260, ch: 240, draw: fxDrum, x, y: 0.14 + bob, z, w: 0.62, h: 0.57, rot: r });
    out.fx.push({ key: `ring${q(((t * 0.4 + i * 0.3) % 1), 30)}`, cw: 600, ch: 600, draw: (p) => fxRing(p, q(((t * 0.4 + i * 0.3) % 1), 30)), x, y: 0.03, z, w: 1.6, h: 1.6, flat: true });
  });
};

/** stars circling a dazed onlooker's head (the eruption gag, shot 6) */
const starsFx = (t: number, out: Stage) => {
  const u = q((t * 0.8) % 1, 30);
  out.fx.push({ key: `stars|${u}`, cw: 420, ch: 210, draw: (p) => fxStars(p, u), x: 22.5, y: D0 + 2.6, z: 33.6, w: 0.8, h: 0.4 });
};

/** small flames on the pan in the kitchen (stove top at 400.38, 1.19, -8.02), from the analogy beat on */
const panFire = (t: number, out: Stage) => {
  const env = clamp01((t - 32.2) / 1.2) * clamp01((41.8 - t) / 1.5);
  if (env <= 0.02) return;
  for (let k = 0; k < 3; k++) {
    const u = q((t * 2.6 + k * 0.31) % 1, 30);
    const h = (0.5 + 0.4 * Math.sin(t * 7 + k * 2)) * env;
    out.fx.push({ key: `panflame|${u}|${k}`, cw: 300, ch: 600, draw: (p) => fxFlame(p, u, k + 2), x: 400.38 + (hh(k) - 0.5) * 0.3, y: 1.19, z: -8.02 + (hh(k, 2) - 0.5) * 0.3,
      w: 0.34 + h * 0.12, h: Math.max(0.25, h * 0.6), rot: (hh(k, 3) - 0.5) * 0.2, col: FLAME_COL, base: true });
  }
};

// ---------------- stage ----------------
/** everything with a face (or a flame) in shot `id` at time t */
export const stage = (id: number, t: number, st: RiverState, cam: CamInfo): Stage => {
  const out: Stage = { places: [], fx: [] };
  const s = SHOTS[id - 1];
  LNAME = s.light;
  findSun(cam, SUN);
  const f = t * FPS;
  switch (s.crowd) {
    case "quay":
      if (id === 2) { // riverfront street: far-bank crowd + workers by the factory
        quayCrowd(cam, t, out, -1, 20, -30, 26, (i) => (i % 4 === 3 ? "nervous" : i % 2 ? "neutral" : "stern"));
        workers(cam, t, out, 4, -34, -22, "neutral");
      } else if (id === 4) { // train crossing: far-bank onlookers
        quayCrowd(cam, t, out, -1, 12, -18, 14, () => "neutral");
      } else if (id === 11) { // golden riverfront after
        quayCrowd(cam, t, out, 1, 10, -8, 22, (i) => (["smile", "grin", "laugh", "smile_closed"] as Expr[])[i % 4], true);
        quayCrowd(cam, t, out, -1, 8, -20, 16, (i) => (["smile", "grin", "smile"] as Expr[])[i % 3]);
      }
      break;
    case "shock": // the eruption: near-foreground onlookers (shock) + far bank
      quayCrowd(cam, t, out, 1, 3, 20, 26, () => (t > 22.95 ? "relief" : "shock"));
      quayCrowd(cam, t, out, -1, 10, -16, 12, () => (t > 22.95 ? "relief_open" : "shock"));
      starsFx(t, out);
      break;
    case "fire": // burning river + fireboat: far-bank watchers, two firefighters on the boat
      quayCrowd(cam, t, out, -1, 8, -14, 12, () => "shock");
      for (const [dx, i] of [[-0.9, 71], [0.8, 72]] as const) {
        out.places.push(person(cam, { i, o: FIREFIGHTER, okey: "ff" }, BOAT[0] + dx, 1.05 + 0.05 * Math.sin(t * 1.7 + i), BOAT[2] - 0.6,
          { side: false, mirror: false }, { mode: "stand", expr: "stern", blink: lidAt(t, i) }, {}));
      }
      break;
    case "photo":
      photographer(cam, t, f, out);
      quayCrowd(cam, t, out, -1, 6, -10, 8, () => "nervous");
      break;
    case "sign": {
      quayCrowd(cam, t, out, 1, 2, 7, 9.5, (i) => (i ? "smile" : "grin"));
      break;
    }
    case "kayak":
      kayaker(cam, t, out);
      if (id === 14) quayCrowd(cam, t, out, -1, 8, -16, 10, (i) => (["smile", "grin", "laugh"] as Expr[])[i % 3], true);
      break;
    default:
      break;
  }
  if (id <= 5) flotsam(t, out);
  if (id <= 8) { fireFx(t, st, out); sparkFx(t, st, out); }
  if (id <= 6) trainPuffs(t, st, out);
  if (id >= 6 && id <= 8) hoseFx(t, st, out);
  if (id === 13) fishFx(t, out);
  if (id === 9 || id === 10) panFire(t, out); // the greasy pan catches (the analogy beat)
  return out;
};

export { FPS };
