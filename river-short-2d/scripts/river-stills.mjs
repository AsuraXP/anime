// QA stills for the 2D short (batched: one browser launch for many frames).
// usage: BROWSER=/path/chrome OPTS='{"gl":"swangle","args":[...]}' node scripts/river-stills.mjs <outPrefix> <f,f,...> [scale]
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
process.env.REMOTION_TMP = process.env.REMOTION_TMP || fs.mkdtempSync(path.join(os.tmpdir(), "remotion-2d-"));
fs.mkdirSync(process.env.REMOTION_TMP, { recursive: true });
process.env.TEMP = process.env.TMP = process.env.REMOTION_TMP;
import { bundle } from "@remotion/bundler";
import { renderStill, selectComposition } from "@remotion/renderer";

const prefix = process.argv[2] ?? "out/qa";
const frames = (process.argv[3] ?? "60").split(",").map(Number);
const scale = Number(process.argv[4] ?? 0.5);
const browserExecutable = process.env.BROWSER || "/tmp/chromium";
const chromiumOptions = process.env.OPTS ? JSON.parse(process.env.OPTS)
  : { gl: "swangle", args: ["--no-sandbox", "--disable-dev-shm-usage", "--enable-unsafe-swiftshader", "--disable-gpu", "--mute-audio"] };

const serveUrl = await bundle({ entryPoint: path.resolve("src/index.ts"), publicDir: path.resolve("public") });
const composition = await selectComposition({ serveUrl, id: process.env.COMP || "Short2D", browserExecutable, chromiumOptions });
console.log("composition", composition.width, composition.height, composition.durationInFrames, "fps", composition.fps);
for (const f of frames) {
  const t0 = Date.now();
  const out = `${prefix}-f${f}.jpg`;
  await renderStill({ composition, serveUrl, frame: f, output: out, imageFormat: "jpeg", jpegQuality: 88, scale, browserExecutable, chromiumOptions, timeoutInMilliseconds: 300000 });
  console.log(`f${f} -> ${out} in`, ((Date.now() - t0) / 1000).toFixed(1) + "s");
}
