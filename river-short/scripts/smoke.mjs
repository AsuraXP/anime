// Smoke test: bundle a trivial composition and render one still through the sandbox Chromium.
import fs from "node:fs";
process.env.REMOTION_TMP = "/home/user/shorts/remotion-tmp";
fs.mkdirSync(process.env.REMOTION_TMP, { recursive: true });
process.env.TEMP = process.env.TMP = process.env.REMOTION_TMP;
import { bundle } from "@remotion/bundler";
import { renderStill, selectComposition } from "@remotion/renderer";
import path from "node:path";

const browserExecutable = "/tmp/chromium";
const chromiumOptions = {
  gl: "swangle",
  args: ["--no-sandbox", "--disable-dev-shm-usage", "--enable-unsafe-swiftshader", "--disable-gpu", "--no-first-run", "--no-default-browser-check", "--disable-extensions", "--mute-audio"],
};
const serveUrl = await bundle({ entryPoint: path.resolve("src/smoke.tsx"), publicDir: path.resolve("public") });
const composition = await selectComposition({ serveUrl, id: "Smoke", browserExecutable, chromiumOptions });
console.log("composition", composition.width, composition.height, composition.durationInFrames);
const t0 = Date.now();
await renderStill({ composition, serveUrl, frame: 5, output: "out/smoke.jpg", imageFormat: "jpeg", jpegQuality: 88, scale: 0.5, browserExecutable, chromiumOptions, timeoutInMilliseconds: 240000, onBrowserLog: (l) => console.log(`[${l.type}]`, l.text.slice(0, 200)) });
console.log("still rendered in", ((Date.now() - t0) / 1000).toFixed(1) + "s");
