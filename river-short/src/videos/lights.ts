// Light presets per time of day / weather. The sun is CAMERA-RELATIVE and frozen per shot (world.ts update()).
// az = degrees from the shot camera's forward axis (0 = sun straight ahead = backlight, +90 = screen right,
// 180 = behind camera), el = elevation. lit/shade/lift are LINEAR RGB multipliers for shade.ts (may exceed 1).
type C3 = [number, number, number];
export type LightPreset = {
  az: number; el: number;
  lit: C3; shade: C3; lift: C3; lambert: number; sideK: number; term: number;
  charTint: C3; charShade: number; charGrad: number; bodyGrad: number; sideTint: C3;
  blob: C3; actorShadow: boolean;
  top: string; hor: string; skyCurve: C3; fog: string; fogNear: number; fogFar: number; sunDisc: string;
  sunCol: string; sunI: number; sky: string; ground: string; hemiI: number;
  bias: number; normalBias: number;
};
export const LIGHTS: Record<"day" | "golden" | "smoke", LightPreset> = {
  day: {
    az: 75, el: 48,
    lit: [1.58, 1.5, 1.33], shade: [0.3, 0.29, 0.36], lift: [0.05, 0.06, 0.11], lambert: 0.35, sideK: 0.84, term: 0.2,
    charTint: [1.0, 0.94, 0.92], charShade: 0.86, charGrad: 0.07, bodyGrad: 0.2, sideTint: [0.92, 0.90, 0.96],
    blob: [0.62, 0.58, 0.58], actorShadow: false,
    top: "#3e7fd2", hor: "#b8d0ec", skyCurve: [0.0, 0.5, 0.6], fog: "#b8d0ec", fogNear: 25, fogFar: 300, sunDisc: "#000000",
    sunCol: "#fff3e0", sunI: 2.8, sky: "#dcecff", ground: "#b49a78", hemiI: 0.55,
    bias: -0.00025, normalBias: 0.015,
  },
  golden: {
    az: 6, el: 7,
    lit: [1.5, 0.68, 0.24], shade: [0.15, 0.15, 0.3], lift: [0.04, 0.06, 0.17], lambert: 0.35, sideK: 0.82, term: 0.07,
    charTint: [1.0, 0.78, 0.56], charShade: 0.88, charGrad: 0.1, bodyGrad: 0.25, sideTint: [0.85, 0.80, 0.95],
    blob: [0.75, 0.74, 0.9], actorShadow: true,
    top: "#6a4f8c", hor: "#ffd08a", skyCurve: [0.05, 0.6, 1.0], fog: "#efb489", fogNear: 50, fogFar: 380, sunDisc: "#ffcf9e",
    sunCol: "#ffab5e", sunI: 5.5, sky: "#d8b0b8", ground: "#8a6a60", hemiI: 0.5,
    bias: -0.0006, normalBias: 0.03,
  },
  // the fire shots: hazy smoke-filled afternoon, sun low and diffused, warm-grey air
  smoke: {
    az: 40, el: 20,
    lit: [1.34, 1.12, 0.92], shade: [0.34, 0.31, 0.44], lift: [0.07, 0.05, 0.1], lambert: 0.4, sideK: 0.9, term: 0.3,
    charTint: [1.0, 0.9, 0.82], charShade: 0.88, charGrad: 0.08, bodyGrad: 0.22, sideTint: [0.9, 0.86, 0.98],
    blob: [0.6, 0.56, 0.66], actorShadow: false,
    top: "#5d6478", hor: "#d9b294", skyCurve: [0.0, 0.45, 0.55], fog: "#cfae90", fogNear: 18, fogFar: 240, sunDisc: "#000000",
    sunCol: "#ffd9b0", sunI: 1.9, sky: "#e8d4c4", ground: "#8a7460", hemiI: 0.6,
    bias: -0.0004, normalBias: 0.02,
  },
};

/** world-only look per light (sky stops by elevation in degrees, river colours, cloud palette). */
export type WorldLook = {
  sky: { c: string[]; e: number[] };
  water: { near: string; mid: string; far: string; crest: string; trough: string; glint: string; shade: C3 };
  bounce: C3;
  sat: number;
  cloud: { lit: string; mid: string; shade: string };
};
export const LOOK: Record<"day" | "golden" | "smoke", WorldLook> = {
  day: {
    sky: { c: ["#b8d0ec", "#9cbfea", "#6a9fe0", "#4f8cdb", "#3373cc"], e: [0, 3, 8, 16, 40] },
    water: { near: "#1b93a6", mid: "#167fb2", far: "#1a5596", crest: "#7ddfe8", trough: "#0e4a80", glint: "#ffffff", shade: [0.5, 0.56, 0.72] },
    cloud: { lit: "#fbf8f1", mid: "#e1e5f3", shade: "#c3cbe9" },
    bounce: [0, 0, 0],
    sat: 1.08,
  },
  golden: {
    sky: { c: ["#ffc47c", "#f7ae78", "#e8967c", "#c4848e", "#8a6f8a"], e: [0, 4, 10, 20, 40] },
    water: { near: "#1e3a6e", mid: "#355f96", far: "#d4a48e", crest: "#d9a088", trough: "#16294f", glint: "#ffe2b0", shade: [0.42, 0.46, 0.72] },
    cloud: { lit: "#ffd2a8", mid: "#f2a08f", shade: "#a98fc4" },
    bounce: [0.04, 0.02, 0.0],
    sat: 1.1,
  },
  // smoky: the river is dark and oily, the sky a hot hazy grey-peach
  smoke: {
    sky: { c: ["#e0b795", "#d3ac8f", "#a89383", "#7d7c8e", "#5d6478"], e: [0, 3, 9, 18, 40] },
    water: { near: "#232a38", mid: "#1c2231", far: "#4a4a58", crest: "#7a6248", trough: "#0b0d14", glint: "#ffb36b", shade: [0.42, 0.42, 0.6] },
    cloud: { lit: "#e8cdb4", mid: "#c9b2a0", shade: "#9a8f96" },
    bounce: [0.03, 0.015, 0.0],
    sat: 0.92,
  },
};
