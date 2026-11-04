// QA stills for the river short through the sandbox Chromium.
// usage: node scripts/river-stills.mjs <outPrefix> <f,f,...> [scale] [inputPropsJson]
import fs from "node:fs";
process.env.REMOTION_TMP = "/home/user/shorts/remotion-tmp";
fs.mkdirSync(process.env.REMOTION_TMP, { recursive: true });
process.env.TEMP = process.env.TMP = process.env.REMOTION_TMP;
import { bundle } from "@remotion/bundler";
import { renderStill, selectComposition } from "@remotion/renderer";
import path from "node:path";

const prefix = process.argv[2] ?? "out/river";
const frames = (process.argv[3] ?? "60").split(",").map(Number);
const scale = Number(process.argv[4] ?? 0.5);
const inputProps = process.argv[5] ? JSON.parse(process.argv[5]) : undefined;

const browserExecutable = "/tmp/chromium";
const chromiumOptions = {
  gl: "swangle",
  args: ["--no-sandbox", "--disable-dev-shm-usage", "--enable-unsafe-swiftshader", "--disable-gpu", "--no-first-run", "--no-default-browser-check", "--disable-extensions", "--mute-audio"],
};
const serveUrl = await bundle({ entryPoint: path.resolve("src/index.ts"), publicDir: path.resolve("public") });
const composition = await selectComposition({ serveUrl, id: "RiverShort", browserExecutable, chromiumOptions });
console.log("composition", composition.width, composition.height, composition.durationInFrames, "fps", composition.fps);
for (const f of frames) {
  const t0 = Date.now();
  const out = `${prefix}-f${f}.jpg`;
  await renderStill({ composition, serveUrl, frame: f, output: out, imageFormat: "jpeg", jpegQuality: 88, scale, inputProps, browserExecutable, chromiumOptions, timeoutInMilliseconds: 300000, onBrowserLog: (l) => { if (l.type === "error") console.log(`[${l.type}]`, l.text.slice(0, 300)); } });
  console.log(`f${f} -> ${out} in`, ((Date.now() - t0) / 1000).toFixed(1) + "s");
}
