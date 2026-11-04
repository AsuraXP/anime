// The whole place as one three.js scene: sky, river, banks, the industrial city, the railroad trestle + train,
// the fireboat, the burning oil slick, the kitchen (analogy), the sign, smoke, clouds and the cast.
// update(id, f, camera) poses everything for shot `id` at frame f (pure function of id + f).
import * as THREE from "three";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";
import { staticFile } from "remotion";
import { Batch, V, lam, boxGeo, buildCity, CHIMNEYS, boatGroup, kayakGroup, buildKitchen, kitClone, Ray, Kit } from "./build";
import { ctex, bed, rep, stoneHD, cobbleHD, grassHD, waterNear, waterFar, cloudHD, oilHD, glowHD } from "./paint";
import { Pen, fxNoDump } from "./toon";
import { LIGHTS, LOOK, LightPreset } from "./lights";
import { TONE, CHAR, LFB, twoTone, untone } from "./shade";
import { NOINK } from "./ink";
import { Pool, Actor, Fx, stage } from "./cast";
import { FPS, D0, SHOTS, TRESTLE_X, TRESTLE_Y, IGN, FIRE_Z, FIRE_X0, FIRE_X1, BOAT, SIGN_AT, KITCHEN, IGNITE, OUT, TRAIN_T0, TRAIN_T1, kayakX, riverState, camAt, FOREGROUND, V3, ShotDef } from "./story";

// ---------------- assets ----------------
const KENNEY = ["tree_oak", "tree_default", "tree_detailed", "tree_fat", "tree_cone", "tree-high-round", "tree", "plant_bushLarge", "plant_bushDetailed",
  "plant_bush", "hedge", "flower_redA", "flower_yellowA", "flower_purpleA", "grass_large", "grass", "lily_large", "lantern", "cart", "stall-red",
  "stall-green", "stall-bench", "banner-red", "banner-green", "windmill", "canoe"];
let kitP: Promise<Kit> | null = null;
export const loadKit = () => {
  if (!kitP) {
    const loader = new GLTFLoader();
    kitP = Promise.all(KENNEY.map((n) => loader.loadAsync(staticFile(`river/kenney/${n}.glb`)).then((g) => [n, g.scene] as const).catch(() => [n, null] as const)))
      .then((list) => Object.fromEntries(list.filter((e) => e[1]).map(([n, s]) => [n, s!])) as Kit);
  }
  return kitP;
};

// ---------------- helpers ----------------
const discTex = () => ctex("sunDisc", 128, 128, (g) => {
  const gr = g.createRadialGradient(64, 64, 58, 64, 64, 64); gr.addColorStop(0, "rgba(255,255,255,1)"); gr.addColorStop(1, "rgba(255,255,255,0)");
  g.fillStyle = gr; g.fillRect(0, 0, 128, 128);
});
const haloTex = () => ctex("sunHalo", 256, 256, (g) => {
  const im = g.createImageData(256, 256);
  for (let y = 0; y < 256; y++) for (let x = 0; x < 256; x++) {
    const u = Math.hypot(x - 127.5, y - 127.5) / 128;
    const a = (0.55 * Math.exp(-((u / 0.25) ** 2)) + 0.35 * Math.exp(-((u / 0.6) ** 2))) * (1 - Math.min(1, Math.max(0, (u - 0.8) / 0.2)));
    const i = (y * 256 + x) * 4; im.data[i] = im.data[i + 1] = im.data[i + 2] = 255; im.data[i + 3] = Math.round(255 * Math.min(1, a));
  }
  g.putImageData(im, 0, 0);
});
const smokeTex = () => ctex("smoke", 256, 256, (g) => {
  const p = new Pen(g);
  for (const [x, y, r, c] of [[90, 150, 60, "#8f8d96"], [150, 120, 70, "#a3a1aa"], [170, 165, 55, "#8f8d96"], [120, 100, 50, "#b4b2ba"]] as const) p.ell(x, y, r, r * 0.85, c, 0);
});

/** every lens position of the film looking at its subject (houses there are left out) */
const sightLines = (): Ray[] => {
  const out: Ray[] = [];
  for (const s of SHOTS) for (let f = s.a - 8; f < s.b + 8; f += 2) {
    const c = camAt(s.id, Math.max(0, f)), o = V(...c.pos), look = V(...c.look);
    const fw = look.clone().sub(o), len = fw.length();
    fw.normalize();
    const rt = fw.clone().cross(V(0, 1, 0)).normalize(), up = rt.clone().cross(fw);
    const ty = Math.tan((c.fov * Math.PI) / 360), tx = ty * (9 / 16);
    for (const [sx, sy] of [[0, 0], [-0.6, 0], [0.6, 0], [0, 0.6], [0, -0.4]])
      out.push({ o, d: fw.clone().addScaledVector(rt, sx * tx).addScaledVector(up, sy * ty), len, core: sx === 0 && sy === 0 });
  }
  return out;
};

/** horizontal quad facing up at height y covering x0..x1, z0..z1 */
function quadUp(x0: number, x1: number, z0: number, z1: number, u: number, v: number, y: number) {
  const g = new THREE.BufferGeometry();
  g.setAttribute("position", new THREE.Float32BufferAttribute([x0, y, z1, x1, y, z1, x1, y, z0, x0, y, z1, x1, y, z0, x0, y, z0], 3));
  g.setAttribute("normal", new THREE.Float32BufferAttribute([0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0], 3));
  g.setAttribute("uv", new THREE.Float32BufferAttribute([0, 0, u, 0, u, v, 0, 0, u, v, 0, v], 2));
  return g;
}
/** embankment wall from the river bed to the bank top at z, facing +z (dir 1) or -z (dir -1) */
function wallQuad(x0: number, x1: number, z: number, dir: number) {
  const g = new THREE.BufferGeometry(), y0 = -0.6, y1 = D0;
  g.setAttribute("position", new THREE.Float32BufferAttribute([x0, y0, z, x1, y0, z, x1, y1, z, x0, y0, z, x1, y1, z, x0, y1, z], 3));
  g.setAttribute("normal", new THREE.Float32BufferAttribute(Array(6).fill([0, 0, dir]).flat(), 3));
  const u = Math.abs(x1 - x0) / 4, v = (y1 - y0) / 4;
  g.setAttribute("uv", new THREE.Float32BufferAttribute([0, 0, u, 0, u, v, 0, 0, u, v, 0, v], 2));
  return g;
}

/** the train: loco + 3 cars, local +z behind the loco (it moves toward -z) */
const trainGroup = () => {
  const g = new THREE.Group();
  const loco = lam("loco", () => ({ color: "#2f4a3a" }));
  const cabM = lam("locoCab", () => ({ color: "#26382e" }));
  const iron = lam("locoIron", () => ({ color: "#23262c" }));
  const add = (geo: THREE.BufferGeometry, mat: THREE.Material, x: number, y: number, z: number, rx = 0, ry = 0, rz = 0) => {
    const m = new THREE.Mesh(geo, mat); m.position.set(x, y, z); m.rotation.set(rx, ry, rz); m.castShadow = true; m.receiveShadow = true; g.add(m); return m;
  };
  const box = (w: number, h: number, d: number) => new THREE.BoxGeometry(w, h, d);
  // loco (front at local z = -7)
  add(box(2.6, 2.0, 7), loco, 0, 1.5, -3.5);
  add(box(2.2, 1.3, 2.6), cabM, 0, 3.15, -5.6);
  add(box(2.24, 0.5, 2.64), iron, 0, 2.55, -5.6); // cab roof
  add(box(2.62, 0.7, 0.9), loco, 0, 1.2, -6.9);   // boiler front
  add(new THREE.CylinderGeometry(0.16, 0.2, 1.1, 10), iron, 0, 3.0, -6.4); // chimney
  add(new THREE.CylinderGeometry(0.3, 0.3, 0.5, 10), iron, 0, 2.75, -3.5);  // dome
  const wg = new THREE.CylinderGeometry(0.45, 0.45, 0.18, 14); wg.rotateZ(Math.PI / 2);
  for (const z of [-6.2, -3.5, -0.8]) for (const x of [-0.95, 0.95]) add(wg, iron, x, 0.45, z);
  // cars
  const carCols = ["#5a4632", "#3d4450", "#6a3b2f"];
  [4.5, 12.5, 20.5].forEach((cz, i) => {
    const m = lam("car" + i, () => ({ color: carCols[i] }));
    add(box(2.5, 2.0, 7), m, 0, 1.6, cz);
    add(box(2.55, 0.22, 7.1), iron, 0, 2.7, cz);
    for (const z of [cz - 2.6, cz + 0.2, cz + 2.8]) for (const x of [-0.95, 0.95]) add(wg, iron, x, 0.45, z);
  });
  return g;
};

type Mats = Record<string, THREE.Material>;

export class World {
  root = new THREE.Group();
  private pool = new Pool();
  private actors: Actor[] = [];
  private fxs: Fx[] = [];
  private hemi: THREE.HemisphereLight; private sun: THREE.DirectionalLight;
  private sky: THREE.Mesh; private skyMat: THREE.ShaderMaterial;
  private fog = new THREE.Fog("#bccbec", 25, 420);
  private WU: Record<string, THREE.IUniform>;
  private sunDisc: THREE.Sprite; private sunHalo: THREE.Sprite;
  private sunCache = new Map<number, THREE.Vector3>();
  private cloudMaps: Record<string, THREE.Texture[]>;
  private fgs: { o: THREE.Object3D; a: number; b: number }[] = [];
  private smoke: { m: THREE.Mesh; mat: THREE.MeshLambertMaterial; top: V3; k: number }[] = [];
  private clouds: THREE.Mesh[] = [];
  private oil: THREE.Mesh[] = [];
  private train = trainGroup();
  private boat = boatGroup();
  private kayak: THREE.Group;
  private kitchen = buildKitchen();
  private sign = new THREE.Group();
  private glow: THREE.Sprite;
  private frustum = new THREE.Frustum();
  private m4 = new THREE.Matrix4(); private v = new THREE.Vector3(); private sph = new THREE.Sphere();

  constructor(kit: Kit) {
    const R = this.root, M: Mats = {};
    this.kayak = kayakGroup(kit);
    // ---- sky + light ----
    this.skyMat = new THREE.ShaderMaterial({
      uniforms: { c0: { value: new THREE.Color() }, c1: { value: new THREE.Color() }, c2: { value: new THREE.Color() },
        c3: { value: new THREE.Color() }, c4: { value: new THREE.Color() }, e: { value: new THREE.Vector4() } },
      vertexShader: "varying vec3 vP; void main(){ vP = normalize(position); gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }",
      fragmentShader: `uniform vec3 c0, c1, c2, c3, c4; uniform vec4 e; varying vec3 vP;
        void main(){ float el = asin(clamp(normalize(vP).y, -1.0, 1.0));
          vec3 c = mix(c0, c1, smoothstep(0.0, e.x, el));
          c = mix(c, c2, smoothstep(e.x, e.y, el));
          c = mix(c, c3, smoothstep(e.y, e.z, el));
          c = mix(c, c4, smoothstep(e.z, e.w, el));
          gl_FragColor = vec4(c, 1.0); }`,
      side: THREE.BackSide, depthWrite: false, fog: false,
    });
    this.sky = new THREE.Mesh(new THREE.SphereGeometry(1100, 48, 24), this.skyMat);
    this.sky.renderOrder = -1; this.sky.frustumCulled = false; this.sky.layers.set(NOINK);
    R.add(this.sky);
    this.sunDisc = new THREE.Sprite(new THREE.SpriteMaterial({ map: discTex(), color: new THREE.Color(6.0, 4.4, 2.4), fog: false, depthWrite: false }));
    this.sunHalo = new THREE.Sprite(new THREE.SpriteMaterial({ map: haloTex(), color: new THREE.Color(1, 1, 1), fog: false, depthWrite: false, depthTest: true,
      transparent: true, blending: THREE.AdditiveBlending }));
    this.sunDisc.renderOrder = -0.5; this.sunHalo.renderOrder = 5;
    for (const m of [this.sunDisc, this.sunHalo]) { m.frustumCulled = false; m.layers.set(NOINK); R.add(m); }
    this.hemi = new THREE.HemisphereLight("#cfe6ff", "#6c5c8c", 1.1);
    this.sun = new THREE.DirectionalLight("#fff0d6", 2.6);
    this.sun.castShadow = true;
    this.sun.shadow.mapSize.set(4096, 4096);
    R.add(this.hemi, this.sun, this.sun.target);
    this.cloudMaps = { day: [0, 1, 2, 3].map((k) => cloudHD(k, LOOK.day.cloud)), golden: [0, 1, 2, 3].map((k) => cloudHD(k, LOOK.golden.cloud)), smoke: [0, 1, 2, 3].map((k) => cloudHD(k, LOOK.smoke.cloud)) };
    for (let i = 0; i < 9; i++) {
      const m = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), new THREE.MeshBasicMaterial({ map: this.cloudMaps.day[i % 4], color: new THREE.Color(1.1, 1.1, 1.1), transparent: true, depthWrite: false, fog: false }));
      m.layers.set(NOINK);
      this.clouds.push(m); R.add(m);
    }

    // ---- ground, quays, embankments (static batch) ----
    const b = new Batch();
    M.grass = lam("grassHD", () => ({ map: grassHD() }));
    M.cobble = lam("cobbleHD", () => ({ map: cobbleHD() }));
    M.wall = lam("wallHD", () => ({ map: stoneHD("wallHD", ["#c9bcaa", "#bfb19f", "#d1c5b4", "#b8aa97"], "#958776") }));
    M.cope = lam("copeHD", () => ({ map: stoneHD("copeHD", ["#e6dccd", "#ddd3c3", "#ece4d6", "#d6cbba"], "#aea293") }));
    for (const s of [-1, 1]) {
      const zn = s * 30, zf = s * 900;
      b.add(s < 0 ? quadUp(-900, 900, zf, zn, 450, 217.5, D0) : quadUp(-900, 900, zn, zf, 450, 217.5, D0), M.grass);
      b.add(s < 0 ? quadUp(-160, 160, -36.5, -30, 80, 1.625, D0 + 0.012) : quadUp(-160, 160, 30, 36.5, 80, 1.625, D0 + 0.012), M.cobble);
      b.add(s < 0 ? quadUp(-6, 6, -170, -36.5, 3, 33.375, D0 + 0.012) : quadUp(-6, 6, 36.5, 170, 3, 33.375, D0 + 0.012), M.cobble);
      b.add(s < 0 ? wallQuad(-900, 900, -30, 1) : wallQuad(900, -900, 30, -1), M.wall);
      for (const [x0, x1] of [[-600, -4.6], [4.6, 600]]) b.add(boxGeo(V(x0, D0, s < 0 ? -30.5 : 30), V(x1, D0 + 0.75, s < 0 ? -30 : 30.5), 2), M.cope);
      b.add(boxGeo(V(-600, D0 - 0.05, s < 0 ? -30.6 : 29.4), V(600, D0 + 0.02, s < 0 ? -29.4 : 30.6), 2), M.cope);
    }
    b.add(quadUp(-900, 900, -30, 30, 225, 7.5, -0.6), lam("bed", () => ({ map: bed() })));
    b.build(R);
    buildCity(R, kit, sightLines());

    // water: its own mesh so the ripples can drift (shader from the bridge template)
    const wNear = waterNear(), wFar = waterFar();
    for (const t of [wNear, wFar]) { t.colorSpace = THREE.NoColorSpace; t.anisotropy = 16; t.needsUpdate = true; }
    this.WU = {
      wNearC: { value: new THREE.Color() }, wMidC: { value: new THREE.Color() }, wFarC: { value: new THREE.Color() },
      wCrest: { value: new THREE.Color() }, wTrough: { value: new THREE.Color() }, wGlint: { value: new THREE.Color() },
      wShade: { value: new THREE.Vector3(0.5, 0.56, 0.72) }, wNearTex: { value: wNear }, wFarTex: { value: wFar }, wTime: { value: 0 },
    };
    const waterM = new THREE.MeshLambertMaterial({ color: 0xffffff });
    waterM.onBeforeCompile = (sh) => {
      Object.assign(sh.uniforms, this.WU);
      sh.vertexShader = sh.vertexShader
        .replace("#include <common>", "#include <common>\nvarying vec3 vWP;")
        .replace("#include <project_vertex>", "#include <project_vertex>\nvWP = (modelMatrix * vec4(transformed, 1.0)).xyz;");
      sh.fragmentShader = sh.fragmentShader
        .replace("#include <common>", WATER_DECL)
        .replace("#include <map_fragment>", WATER_COL)
        .replace("#include <lights_fragment_begin>", "float sunVis = 1.0;\n" + LFB)
        .replace("#include <lights_fragment_end>", "#include <lights_fragment_end>\n  reflectedLight.directDiffuse = diffuseColor.rgb * mix(wShade, vec3(1.0), sunVis);\n  reflectedLight.indirectDiffuse = vec3(0.0);");
    };
    waterM.customProgramCacheKey = () => "river1";
    const wm = new THREE.Mesh(quadUp(-900, 900, -30, 30, 1, 1, 0), waterM);
    wm.receiveShadow = true;
    R.add(wm);

    // ---- oil slick patches on the water (shots 1-8) ----
    const oilM = lam("oilHD", () => ({ map: rep(oilHD(), 9, 4) }));
    for (const [x0, x1, z0, z1, y] of [[FIRE_X0 - 8, FIRE_X1 + 6, -26, 2, 0.02], [FIRE_X0, 6, -14, 14, 0.026], [-2, FIRE_X1 + 10, -24, -6, 0.032]] as const) {
      const m = new THREE.Mesh(quadUp(x0, x1, z0, z1, Math.abs(x1 - x0) / 8, Math.abs(z1 - z0) / 4, y), oilM);
      m.receiveShadow = true; this.oil.push(m); R.add(m);
    }
    // fire glow sprite on the water at the ignition point (additive, HDR -> blooms)
    this.glow = new THREE.Sprite(new THREE.SpriteMaterial({ map: glowHD(), color: new THREE.Color(4.5, 1.8, 0.5), fog: false, depthWrite: false, depthTest: false, transparent: true, blending: THREE.AdditiveBlending }));
    this.glow.layers.set(NOINK); this.glow.renderOrder = 4; R.add(this.glow);

    // ---- movable set pieces ----
    this.train.visible = false; R.add(this.train);
    this.boat.visible = false; R.add(this.boat);
    this.kayak.visible = false; R.add(this.kayak);
    this.kitchen.visible = false; R.add(this.kitchen);

    // ---- chimney smoke ----
    const smokeT = smokeTex();
    for (const top of CHIMNEYS) for (let k = 0; k < 6; k++) {
      const mat = new THREE.MeshLambertMaterial({ map: smokeT, transparent: true, depthWrite: false });
      const m = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), mat);
      m.layers.set(NOINK);
      this.smoke.push({ m, mat, top: top as V3, k: k / 6 }); R.add(m);
    }
    // ---- the "no dumping" sign (shots 11-14) ----
    const board = new THREE.Mesh(new THREE.PlaneGeometry(1.5, 1.12), new THREE.MeshBasicMaterial({ map: ctex("signNoDump", 700, 520, (g) => fxNoDump(new Pen(g))), alphaTest: 0.5, color: 0xe6e6e6 }));
    board.layers.set(NOINK);
    board.position.set(SIGN_AT[0], D0 + 1.62, SIGN_AT[2] + 0.04);
    const back = new THREE.Mesh(new THREE.BoxGeometry(1.56, 1.18, 0.06), lam("signWood", () => ({ color: "#7a5a3c" })));
    back.position.set(SIGN_AT[0], D0 + 1.62, SIGN_AT[2] - 0.02);
    this.sign.add(board, back);
    for (const s of [-1, 1]) { const p = new THREE.Mesh(new THREE.BoxGeometry(0.12, 2.15, 0.12), lam("signWood", () => ({ color: "#7a5a3c" }))); p.position.set(SIGN_AT[0] + s * 0.55, D0 + 1.07, SIGN_AT[2]); this.sign.add(p); }
    this.sign.traverse((o) => { o.castShadow = true; o.receiveShadow = true; });
    this.sign.visible = false;
    R.add(this.sign);

    // ---- foreground framing objects ----
    for (const fg of FOREGROUND) {
      const o = kitClone(kit, fg.kit, fg.s ?? 1);
      if (!o) continue;
      o.position.set(...fg.pos); o.rotation.y = fg.yaw ?? 0; o.visible = false;
      this.fgs.push({ o, a: fg.a, b: fg.b }); R.add(o);
    }
  }

  /** camera-relative sun, frozen per shot */
  private shotSun(id: number, s: ShotDef, L: LightPreset) {
    let v = this.sunCache.get(id);
    if (v) return v;
    let fx = 0, fz = 0;
    for (let f = s.a; f < s.b; f += 3) {
      const c = camAt(id, f), x = c.look[0] - c.pos[0], z = c.look[2] - c.pos[2], n = Math.hypot(x, z) || 1;
      fx += x / n; fz += z / n;
    }
    const n = Math.hypot(fx, fz) || 1; fx /= n; fz /= n;
    const az = THREE.MathUtils.degToRad(L.az), el = THREE.MathUtils.degToRad(L.el);
    const hx = fx * Math.cos(az) - fz * Math.sin(az), hz = fz * Math.cos(az) + fx * Math.sin(az);
    v = new THREE.Vector3(hx * Math.cos(el), Math.sin(el), hz * Math.cos(el)).normalize();
    this.sunCache.set(id, v);
    return v;
  }

  private actor(i: number) { while (this.actors.length <= i) this.actors.push(new Actor(this.root)); return this.actors[i]; }
  private fx(i: number) { while (this.fxs.length <= i) this.fxs.push(new Fx(this.root)); return this.fxs[i]; }

  update(id: number, f: number, cam: THREE.PerspectiveCamera, scene: THREE.Scene) {
    const t = f / FPS, s = SHOTS[id - 1], st = riverState(t), L = LIGHTS[s.light];
    // ---- camera ----
    const c = camAt(id, f);
    cam.position.set(...c.pos); cam.up.set(0, 1, 0); cam.lookAt(...c.look); cam.rotateZ(c.roll);
    cam.fov = c.fov; cam.near = 0.2; cam.far = 1500; cam.updateProjectionMatrix(); cam.updateMatrixWorld();
    const focus = V(...c.look), dist = cam.position.distanceTo(focus);
    cam.layers.enable(NOINK);
    // ---- light rig ----
    const K = LOOK[s.light], sunDir = this.shotSun(id, s, L);
    this.hemi.color.set(L.sky); this.hemi.groundColor.set(L.ground); this.hemi.intensity = L.hemiI;
    this.sun.color.set(L.sunCol); this.sun.intensity = L.sunI;
    let Rr = THREE.MathUtils.clamp(dist * 1.15 + 7, 12, 95);
    if (s.light === "golden") Rr = Math.max(Rr, 30);
    this.sun.position.copy(focus).addScaledVector(sunDir, 220); this.sun.target.position.copy(focus);
    const sc = this.sun.shadow.camera;
    sc.left = -Rr; sc.right = Rr; sc.top = Rr; sc.bottom = -Rr; sc.near = 20; sc.far = 480; sc.updateProjectionMatrix();
    this.sun.shadow.bias = L.bias; this.sun.shadow.normalBias = L.normalBias * (Rr / 12);
    TONE.uLitCol.value.set(...L.lit); TONE.uShadeCol.value.set(...L.shade); TONE.uShadeLift.value.set(...L.lift);
    TONE.uLambert.value = L.lambert; TONE.uSideK.value = L.sideK; TONE.uTerm.value = L.term; TONE.uBounce.value.set(...K.bounce); TONE.uSat.value = K.sat;
    CHAR.uCharTint.value.set(...L.charTint); CHAR.uCharShade.value = L.charShade; CHAR.uGrad.value = L.charGrad;
    CHAR.uBodyGrad.value = L.bodyGrad; CHAR.uSideTint.value.set(...L.sideTint);
    // ---- sky, fog, sun, clouds ----
    const su = this.skyMat.uniforms;
    K.sky.c.forEach((h, i) => untone(h, su["c" + i].value));
    const e = K.sky.e.map((deg) => THREE.MathUtils.degToRad(deg));
    su.e.value.set(e[1], e[2], e[3], e[4]);
    this.sky.position.copy(cam.position);
    untone(L.fog, this.fog.color); this.fog.near = L.fogNear; this.fog.far = L.fogFar;
    scene.fog = this.fog; scene.background = null;
    const showSun = s.light === "golden";
    this.sunDisc.visible = this.sunHalo.visible = showSun;
    if (showSun) {
      this.sunDisc.position.copy(cam.position).addScaledVector(sunDir, 900);
      this.sunDisc.scale.setScalar(2 * 900 * Math.tan(THREE.MathUtils.degToRad(1.7)));
      this.sunHalo.position.copy(this.sunDisc.position); this.sunHalo.scale.setScalar(2 * 900 * Math.tan(THREE.MathUtils.degToRad(24)));
      (this.sunHalo.material as THREE.SpriteMaterial).color.set(L.sunDisc).multiplyScalar(1.3);
    }
    for (let i = 0; i < this.clouds.length; i++) { // clouds ride along with the camera (the kitchen set lives at x=400)
      const m = this.clouds[i], mat = m.material as THREE.MeshBasicMaterial;
      const a = (i / this.clouds.length) * Math.PI * 2 + 0.3 + t * 0.004, d = 440 + (i % 3) * 55;
      m.position.set(cam.position.x + Math.cos(a) * d, 100 + (i % 4) * 34, cam.position.z + Math.sin(a) * d);
      const cw = 120 + (i % 4) * 30;
      m.scale.set(cw, cw / 2, 1);
      m.lookAt(cam.position.x, m.position.y, cam.position.z);
      mat.map = this.cloudMaps[s.light][i % 4];
    }
    // ---- river colours ----
    const W = this.WU, wc = K.water;
    untone(wc.near, W.wNearC.value); untone(wc.mid, W.wMidC.value); untone(wc.far, W.wFarC.value);
    untone(wc.crest, W.wCrest.value); untone(wc.trough, W.wTrough.value); untone(wc.glint, W.wGlint.value);
    W.wShade.value.set(...wc.shade); W.wTime.value = t;
    // ---- set visibility per shot ----
    for (const m of this.oil) m.visible = id <= 8;
    const fire = st.fire;
    this.glow.visible = fire > 0.02 && id <= 8;
    if (this.glow.visible) {
      const g = 18 * fire * (0.8 + 0.2 * Math.sin(t * 11));
      this.glow.position.set(IGN[0], 1.2, IGN[2]); this.glow.scale.set(g, g * 0.55, 1);
      (this.glow.material as THREE.SpriteMaterial).opacity = Math.min(1, fire * 1.4);
    }
    this.train.visible = t > TRAIN_T0 - 2.5 && t < TRAIN_T1 + 2.5 && id <= 6;
    if (this.train.visible) this.train.position.set(TRESTLE_X, TRESTLE_Y + 0.28, st.train);
    this.boat.visible = id >= 6 && id <= 8;
    if (this.boat.visible) {
      this.boat.position.set(BOAT[0], 0.06 + 0.05 * Math.sin(t * 1.7), BOAT[2] + 0.4 * Math.sin(t * 0.9));
      this.boat.rotation.z = 0.03 * Math.sin(t * 1.3); this.boat.rotation.y = -0.15;
    }
    this.kayak.visible = id >= 13;
    if (this.kayak.visible) {
      this.kayak.position.set(kayakX(t), 0.1 + 0.04 * Math.sin(t * 2.1), 2.5);
      this.kayak.rotation.z = 0.05 * Math.sin(t * 1.9); this.kayak.rotation.y = 0.5;
    }
    this.kitchen.visible = id === 9 || id === 10;
    this.sign.visible = id >= 11;
    // ---- foreground framing objects ----
    for (const g of this.fgs) g.o.visible = f >= g.a && f < g.b && g.a < s.b && g.b > s.a;
    // ---- chimney smoke ----
    for (const sm of this.smoke) {
      const u = (t * 0.09 + sm.k) % 1, sz = 3 + u * 9;
      sm.m.position.set(sm.top[0] - u * 14 + 2 * Math.sin(t * 0.7 + sm.k * 9), sm.top[1] + u * 12 + u * u * 4, sm.top[2] + u * 3);
      sm.m.scale.set(sz, sz, 1); sm.m.quaternion.copy(cam.quaternion);
      sm.mat.opacity = 0.8 * (1 - u) ** 1.2;
    }
    // ---- cast + effects ----
    const right = V(0, 0, 0).setFromMatrixColumn(cam.matrixWorld, 0);
    const stg = stage(id, t, st, { pos: cam.position, right });
    this.frustum.setFromProjectionMatrix(this.m4.multiplyMatrices(cam.projectionMatrix, cam.matrixWorldInverse));
    const tint = s.light === "golden" ? "#ffcf9e" : "#ffffff";
    let ai = 0;
    const used: Actor[] = [];
    for (const p of stg.places) {
      const sc2 = p.scale ?? 1;
      if (!this.frustum.intersectsSphere(this.sph.set(this.v.set(p.x, p.y + 1.1 * sc2, p.z), 3.5))) continue;
      const a = this.actor(ai++);
      const [w, h, k] = p.size ?? [300, 500, 0.5];
      a.r = this.pool.req(p.key, w, h, k, p.draw);
      a.mesh.visible = true;
      a.mesh.position.set(p.x, p.y, p.z);
      a.mesh.rotation.set(0, p.yaw ?? Math.atan2(cam.position.x - p.x, cam.position.z - p.z), p.roll ?? 0);
      a.mesh.scale.set(p.mirror ? -sc2 : sc2, sc2, sc2);
      if (a.mat.emissiveMap) a.mat.emissive.set(tint);
      a.mesh.castShadow = s.light === "golden" ? true : L.actorShadow;
      used.push(a);
    }
    for (let i = ai; i < this.actors.length; i++) this.actors[i].mesh.visible = false;
    let fi = 0;
    const fused: Fx[] = [];
    for (const p of stg.fx) {
      if (!this.frustum.intersectsSphere(this.sph.set(this.v.set(p.x, p.y, p.z), Math.max(p.w, p.h)))) continue;
      const e = this.fx(fi++);
      e.r = this.pool.req(p.key, p.cw, p.ch, 1, p.draw);
      e.use(!!p.soft);
      e.mesh.visible = true;
      e.mesh.position.set(p.x, p.y, p.z);
      if (p.flat) e.mesh.rotation.set(-Math.PI / 2, 0, p.rot ?? 0);
      else { e.mesh.quaternion.copy(cam.quaternion); e.mesh.rotateZ(p.rot ?? 0); }
      e.mesh.scale.set(p.w, p.h, 1);
      if (p.base && !p.flat) e.mesh.translateY(p.h / 2); // card drawings anchored at their base (flames, jets)
      const cm = e.mesh.material as THREE.MeshBasicMaterial;
      if (p.col && p.col[0] === "x") { const [r, g, b] = p.col.slice(1).split(",").map(Number); cm.color.setRGB(r, g, b); }
      else cm.color.set(p.col ?? "#ffffff");
      fused.push(e);
    }
    for (let i = fi; i < this.fxs.length; i++) this.fxs[i].mesh.visible = false;
    this.pool.flush();
    for (const a of used) a.bind();
    for (const e of fused) e.bind();
    return focus;
  }
}

const WATER_DECL = `#include <common>\nvarying vec3 vWP;\nuniform vec3 wNearC, wMidC, wFarC, wCrest, wTrough, wGlint, wShade;\nuniform sampler2D wNearTex, wFarTex;\nuniform float wTime;`;
const WATER_COL = `
  vec3 wV = vWP - cameraPosition;
  float wd = length(wV);
  float wDep = asin(clamp(-wV.y / wd, 0.0, 1.0));
  float wf = 1.0 - smoothstep(0.0, 0.42, wDep);
  vec3 wc = mix(mix(wNearC, wMidC, smoothstep(0.0, 0.55, wf)), wFarC, smoothstep(0.55, 1.0, wf));
  vec2 wp = vWP.xz + vec2(0.35 * wTime, 0.0);
  vec4 mk = mix(texture2D(wNearTex, wp / 8.0), texture2D(wFarTex, wp / 40.0 + 0.37), smoothstep(25.0, 90.0, wd));
  wc = mix(wc, wTrough, mk.g * 0.6);
  wc = mix(wc, wCrest, mk.r * 0.7);
  wc = mix(wc, wGlint, mk.b * (0.3 + 0.5 * wf));
  diffuseColor.rgb = wc;`;
