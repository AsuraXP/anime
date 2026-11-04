// Shot table for the 2D short. Everything is data: add rows for longer videos (10 min = ~40-60 rows).
// Camera is a 2D transform: (x, y) = world point at viewport center, z = zoom (1 = fit world width), roll = radians.
export const FPS = 30;
export const WORLD = { w: 2400, h: 4266 }; // big stage; viewport pans/zooms through it
export interface Cam { x: number; y: number; z: number; roll: number }
export interface Shot { a: number; b: number; from: Cam; to: Cam; note?: string }

export const SHOTS: Shot[] = [
  { a: 0,   b: 120, from: { x: 700,  y: 2100, z: 1.0,  roll: 0 },    to: { x: 950,  y: 2050, z: 1.25, roll: 0.01 },  note: "wide river, slow push" },
  { a: 120, b: 240, from: { x: 1500, y: 2050, z: 1.3,  roll: -0.01 }, to: { x: 1620, y: 1980, z: 1.8,  roll: 0 },     note: "trestle bridge close" },
  { a: 240, b: 360, from: { x: 1200, y: 2200, z: 1.5,  roll: 0 },    to: { x: 1200, y: 2350, z: 1.0,  roll: 0 },     note: "pull back to wide" },
];
export const TOTAL = SHOTS[SHOTS.length - 1].b; // frames

const ease = (t: number) => t * t * (3 - 2 * t);
export function camAt(f: number): Cam {
  const s = SHOTS.find((s) => f >= s.a && f < s.b) ?? SHOTS[SHOTS.length - 1];
  const t = ease(Math.min(1, Math.max(0, (f - s.a) / Math.max(1, s.b - s.a))));
  return {
    x: s.from.x + (s.to.x - s.from.x) * t,
    y: s.from.y + (s.to.y - s.from.y) * t,
    z: s.from.z + (s.to.z - s.from.z) * t,
    roll: s.from.roll + (s.to.roll - s.from.roll) * t,
  };
}
export const shotAt = (f: number) => SHOTS.findIndex((s) => f >= s.a && f < s.b) + 1;
