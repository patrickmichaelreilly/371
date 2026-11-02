/* P2 smoke test (HANDOFF Phase 2 step 6).
   Serves the repo with python3 -m http.server and drives the app in
   headless Chromium via Playwright. Prints PASS/FAIL per assertion;
   exits 1 if any assertion failed, 2 on setup problems.

   Run (the repo has no package.json — keep the playwright module outside):
     mkdir -p ~/pw-smoke && cd ~/pw-smoke
     PATH="<dir-with-node>:$PATH" npm i playwright
     PATH="<dir-with-node>:$PATH" npx playwright install chromium
     PATH="<dir-with-node>:$PATH" PW_NODE_MODULES=~/pw-smoke/node_modules \
       node tests/smoke_solo.mjs
*/
import {createRequire} from 'module';
import {spawn} from 'child_process';
import {dirname, resolve, join} from 'path';
import {fileURLToPath} from 'url';

const require = createRequire(import.meta.url);
function loadPlaywright() {
  try { return require('playwright'); } catch (_) {}
  const dir = process.env.PW_NODE_MODULES;
  if (dir) { try { return require(join(dir, 'playwright')); } catch (_) {} }
  console.error('FAIL setup: playwright module not found '
    + '(npm i playwright somewhere, then PW_NODE_MODULES=<dir>/node_modules)');
  process.exit(2);
}
const pw = loadPlaywright();

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const PORT = 8797;
const BASE = `http://127.0.0.1:${PORT}`;

const srv = spawn('python3', ['-m', 'http.server', String(PORT),
                              '--bind', '127.0.0.1', '--directory', ROOT],
                  {stdio: 'ignore'});
process.on('exit', () => srv.kill());

async function waitServer() {
  for (let i = 0; i < 100; i++) {
    try {
      const r = await fetch(`${BASE}/chorales/index.json`);
      if (r.ok) return true;
    } catch (_) {}
    await new Promise(res => setTimeout(res, 200));
  }
  return false;
}

let failed = 0;
function check(name, cond) {
  console.log(`${cond ? 'PASS' : 'FAIL'} ${name}`);
  if (!cond) failed++;
}

const errors = [];
function hearConsole(page) {
  page.on('console', m => {
    /* Verovio engraving warnings ("Insufficient space to draw mixed beam",
       "[Warning] ...") are declared harmless by HANDOFF; only real app
       errors count. */
    if (m.type() === 'error' && !/Insufficient space|\[Warning\]/.test(m.text()))
      errors.push(m.text());
  });
  page.on('pageerror', e => errors.push(String(e)));
}

const browser = await pw.chromium.launch({
  args: ['--autoplay-policy=no-user-gesture-required', '--mute-audio'],
});
try {
  if (!(await waitServer())) {
    console.error('FAIL setup: http.server did not come up on ' + PORT);
    process.exit(2);
  }
  const page = await browser.newPage();
  hearConsole(page);

  /* --- chorale 1: unchanged behaviour --- */
  await page.goto(`${BASE}/index.html`, {waitUntil: 'domcontentloaded'});
  await page.waitForSelector('#slots .slot', {timeout: 30000});
  check('chorale 1 loads with answer slots',
        (await page.locator('#slots .slot').count()) > 0);
  check('chorale 1 selected by default',
        (await page.inputValue('#pick')) === '1');
  check('chorale 1: palette visible', await page.locator('#palette').isVisible());
  check('chorale 1: no console errors', errors.length === 0);
  errors.length = 0;

  /* --- solo movements: load, render, play, highlight --- */
  for (const val of ['s:bwv1002-2', 's:bwv1004-4', 's:bwv1007-1']) {
    await page.selectOption('#pick', val);
    await page.waitForSelector('#staff svg g.note', {timeout: 60000});
    const notes = await page.locator('#staff svg g.note').count();
    check(`${val}: SVG rendered with notes (${notes} note groups)`, notes > 0);
    check(`${val}: slots and palette hidden`,
          (await page.locator('#slots').isHidden())
          && (await page.locator('#palette').isHidden()));
    check(`${val}: no console errors`, errors.length === 0);
    errors.length = 0;

    await page.click('#playbtn');
    await page.waitForTimeout(2000);
    const hl = await page.locator('#staff svg g.playing').count();
    check(`${val}: >=1 note highlighted after 2 s of playback`, hl > 0);
    await page.click('#playbtn');          /* stop */
    await page.waitForTimeout(300);
  }

  /* --- back to chorale 1: game UI restored --- */
  await page.selectOption('#pick', '1');
  await page.waitForSelector('#slots .slot', {timeout: 60000});
  check('back to chorale 1: slots visible and populated',
        await page.locator('#slots').isVisible()
        && (await page.locator('#slots .slot').count()) > 0);
  check('back to chorale 1: palette visible',
        await page.locator('#palette').isVisible());
  check('back to chorale 1: no console errors', errors.length === 0);
} finally {
  await browser.close();
  srv.kill();
}
process.exit(failed ? 1 : 0);