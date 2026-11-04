// gpu-check.cjs — print the WebGL UNMASKED_RENDERER string of the browser under given chromium options.
// usage: OPTS_JSON='{"gl":"vulkan","args":[...]}' BROWSER=/path/to/chrome node scripts/gpu-check.cjs
//        (optionally under: xvfb-run -a ... for a headed candidate with "headless": false)
// Output: WEBGL_RENDERER=<string>  (SwiftShader => software rendering, not a real GPU)
const { chromium } = require('playwright');
(async () => {
  const opts = JSON.parse(process.env.OPTS_JSON || '{}');
  const args = (opts.args || []).slice();
  const headless = opts.headless !== false;
  const browser = await chromium.launch({
    executablePath: process.env.BROWSER,
    args,
    headless,
  });
  const page = await browser.newPage();
  const renderer = await page.evaluate(() => {
    const c = document.createElement('canvas');
    const gl = c.getContext('webgl2') || c.getContext('webgl');
    if (!gl) return 'NO-WEBGL';
    const ext = gl.getExtension('WEBGL_debug_renderer_info');
    return ext ? String(gl.getParameter(ext.UNMASKED_RENDERER_WEBGL)) : String(gl.getParameter(gl.RENDERER));
  });
  console.log('WEBGL_RENDERER=' + renderer);
  await browser.close();
})().catch((e) => {
  console.log('WEBGL_RENDERER=ERROR ' + e.message);
});
