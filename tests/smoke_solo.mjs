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
    () => document.getElementById('content').style.transform);
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
    () => document.getElementById('content').style.getPropertyValue('--zoom'));
  check('P4 chorale: zoom restored after reload (--zoom=' + zVar + ')',
        parseFloat(zVar) > 1);
  const xsReload = await slotXs();
  check('P4 chorale: slots strictly increasing after reload',
        xsReload.length === countBefore
        && xsReload.every((x, i) => i === 0 || x > xsReload[i - 1]));
  check('P4 chorale reload: no console errors', errors.length === 0);
  errors.length = 0;

  /* --- zoom: blanks stay under their notes; the spacing slider is gone --- */
  check('zoom: spacing slider removed', await page.locator('#space').count() === 0);
  const misalign = () => page.evaluate(() => {
    /* each slot's x vs the centre of the notehead it was assigned to */
    const c = document.getElementById('content').getBoundingClientRect();
    let worst = 0, n = 0;
    for (const s of document.querySelectorAll('#slots .slot')) {
      const x = +s.dataset.x, r = s.getBoundingClientRect();
      worst = Math.max(worst, Math.abs((r.left + r.width / 2 - c.left) - x));
      n++;
    }
    return {worst, n};
  });
  const svgH = () => page.evaluate(() =>
    document.querySelector('#staff svg').getBoundingClientRect().height);
  const h1 = await svgH();
  for (let i = 0; i < 6; i++) await ctrlWheel(-200);
  await page.waitForTimeout(500);
  const h2 = await svgH();
  const zNow = await page.evaluate(() => parseFloat(localStorage.getItem('zoom:chorale')));
  check(`zoom: staff height follows zoom (x${(h2 / h1).toFixed(2)})`, h2 > h1 * 1.5);
  const mz = await misalign();
  check(`zoom: blanks centred under their notes at zoom ${zNow.toFixed(2)} (worst ${mz.worst.toFixed(1)} px)`,
        mz.n > 0 && mz.worst < 2);
  const belowStaff = await page.evaluate(() => {
    const sv = document.querySelector('#staff svg').getBoundingClientRect();
    const sl = document.querySelector('#slots .slot').getBoundingClientRect();
    return sl.top >= sv.bottom - 4;
  });
  check('zoom: answer row sits below the zoomed staff', belowStaff);
  check('zoom: no console errors', errors.length === 0);
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
  const horiz = await page.evaluate(() => {
    const sc = document.getElementById('scroller');
    return {svgs: document.querySelectorAll('#staff > svg').length,
            systems: document.querySelectorAll('#staff svg g.system').length,
            wide: sc.scrollWidth > sc.clientWidth * 2};
  });
  check(`solo: one horizontal system (${horiz.systems} system, ${horiz.svgs} svg)`,
        horiz.svgs === 1 && horiz.systems === 1 && horiz.wide);
  check('P4 solo: no console errors', errors.length === 0);
  errors.length = 0;

  /* --- touch: one finger only scrolls, two fingers zoom --- */
  const tctx = await browser.newContext({viewport: {width: 400, height: 800},
                                         hasTouch: true, isMobile: true});
  const tp = await tctx.newPage();
  tp.on('pageerror', e => errors.push(e.message));
  await tp.goto(`${BASE}/index.html`, {waitUntil: 'domcontentloaded'});
  await tp.waitForSelector('#slots .slot', {timeout: 60000});
  await tp.selectOption('#pick', '1');
  await tp.waitForSelector('#slots .slot', {timeout: 60000});
  const cdp = await tctx.newCDPSession(tp);
  const touch = (type, pts) => cdp.send('Input.dispatchTouchEvent',
    {type, touchPoints: pts.map(([x, y], i) => ({x, y, id: i}))});
  const zOf = () => tp.evaluate(() =>
    parseFloat(document.getElementById('content').style.getPropertyValue('--zoom')) || 1);
  const z0 = await zOf();
  await touch('touchStart', [[200, 200]]);
  for (let i = 1; i <= 8; i++) await touch('touchMove', [[200 - i * 20, 200 + i * 5]]);
  await touch('touchEnd', []);
  await tp.waitForTimeout(300);
  const z1 = await zOf();
  check(`touch: one-finger drag does not zoom (${z0} -> ${z1})`, z1 === z0);
  await touch('touchStart', [[170, 220], [230, 220]]);
  for (let i = 1; i <= 8; i++) await touch('touchMove', [[170 - i * 12, 220], [230 + i * 12, 220]]);
  await touch('touchEnd', []);
  await tp.waitForTimeout(300);
  const z2 = await zOf();
  check(`touch: two-finger pinch zooms (${z1} -> ${z2.toFixed(2)})`, z2 > z1 * 1.5);
  await touch('touchStart', [[200, 200]]);
  for (let i = 1; i <= 8; i++) await touch('touchMove', [[200 - i * 20, 200]]);
  await touch('touchEnd', []);
  await tp.waitForTimeout(300);
  check('touch: one-finger drag after a pinch still does not zoom', await zOf() === z2);
  await tctx.close();
  check('touch: no console errors', errors.length === 0);
} finally {
  await browser.close();
  srv.kill();
}
process.exit(failed ? 1 : 0);