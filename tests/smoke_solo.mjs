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
  errors.length = 0;

  /* --- P4: Ctrl+wheel zoom over the chorale score --- */
  const ctrlWheel = dy => page.evaluate(dy => {
    document.getElementById('scroller').dispatchEvent(
      new WheelEvent('wheel', {deltaY: dy, ctrlKey: true,
                               clientX: 400, clientY: 300,
                               bubbles: true, cancelable: true}));
  }, dy);
  const slotXs = () => page.evaluate(() =>
    [...document.querySelectorAll('#slots .slot')].map(s => +s.dataset.x));
  const xsBefore = await slotXs();
  const countBefore = xsBefore.length;
  await ctrlWheel(-240);                    /* one wheel tick: zoom 1 -> 1.12 */
  await page.waitForTimeout(150);           /* inside the commit debounce */
  const tfMid = await page.evaluate(
    () => document.getElementById('staff').style.transform);
  check('P4 chorale: transform preview present mid-gesture',
        /scale/.test(tfMid) && tfMid !== '');
  await page.waitForTimeout(600);           /* debounce 220 ms + re-render */
  const xsAfter = await slotXs();
  check('P4 chorale: slot count unchanged after zoom commit',
        xsAfter.length === countBefore);
  check('P4 chorale: slot x strictly increasing after zoom commit',
        xsAfter.every((x, i) => i === 0 || x > xsAfter[i - 1]));
  const zStored = await page.evaluate(
    () => localStorage.getItem('zoom:chorale'));
  check('P4 chorale: zoom persisted to localStorage (got ' + zStored + ')',
        parseFloat(zStored) > 1 && parseFloat(zStored) <= 3);
  check('P4 chorale: no console errors', errors.length === 0);
  errors.length = 0;

  /* --- P4: zoom persists across reload --- */
  await page.reload({waitUntil: 'domcontentloaded'});
  await page.waitForSelector('#slots .slot', {timeout: 30000});
  const zVar = await page.evaluate(
    () => document.getElementById('staff').style.getPropertyValue('--zoom'));
  check('P4 chorale: zoom restored after reload (--zoom=' + zVar + ')',
        parseFloat(zVar) > 1);
  const xsReload = await slotXs();
  check('P4 chorale: slots strictly increasing after reload',
        xsReload.length === countBefore
        && xsReload.every((x, i) => i === 0 || x > xsReload[i - 1]));
  check('P4 chorale reload: no console errors', errors.length === 0);
  errors.length = 0;

  /* --- P4: spacing slider — preview without Verovio, commit removes it --- */
  const vrvBefore = await page.evaluate(() => window.__vrv || 0);
  await page.evaluate(() => {
    const s = document.getElementById('space');
    s.value = '85';
    s.dispatchEvent(new Event('input', {bubbles: true}));
  });
  const tfSpace = await page.evaluate(
    () => document.getElementById('staff').style.transform);
  const vrvDuring = await page.evaluate(() => window.__vrv || 0);
  check('P4 spacing: input event previews via transform (got "' +
        tfSpace.slice(0, 40) + '")', /scale/.test(tfSpace));
  check('P4 spacing: preview makes zero Verovio calls',
        vrvDuring === vrvBefore);
  await page.evaluate(() => {
    document.getElementById('space').dispatchEvent(
      new Event('change', {bubbles: true}));
  });
  await page.waitForTimeout(700);
  const tfAfter = await page.evaluate(
    () => document.getElementById('staff').style.transform);
  const vrvAfter = await page.evaluate(() => window.__vrv || 0);
  check('P4 spacing: change event commits and removes transform',
        tfAfter === '');
  check('P4 spacing: commit re-rendered via Verovio',
        vrvAfter > vrvDuring);
  const xsSpace = await slotXs();
  check('P4 spacing: slots still strictly increasing after commit',
        xsSpace.length === countBefore
        && xsSpace.every((x, i) => i === 0 || x > xsSpace[i - 1]));
  check('P4 spacing: no console errors', errors.length === 0);
  errors.length = 0;

  /* --- P4: solo zoom during playback — highlight keeps running --- */
  await page.selectOption('#pick', 's:bwv1007-1');
  await page.waitForSelector('#staff svg g.note', {timeout: 60000});
  await page.click('#playbtn');
  await page.waitForTimeout(300);
  await ctrlWheel(-240);
  await ctrlWheel(-240);                    /* zoom 1 -> ~1.25 */
  await page.waitForTimeout(2000);
  const hlSolo = await page.locator('#staff svg g.playing').count();
  const stillOn = await page.evaluate(
    () => document.getElementById('playbtn').classList.contains('on'));
  check('P4 solo: >=1 note highlighted after zoom during playback',
        hlSolo > 0);
  check('P4 solo: playback still running after zoom commit', stillOn);
  await page.click('#playbtn');             /* stop */
  await page.waitForTimeout(300);
  check('P4 solo: no console errors', errors.length === 0);
} finally {
  await browser.close();
  srv.kill();
}
process.exit(failed ? 1 : 0);