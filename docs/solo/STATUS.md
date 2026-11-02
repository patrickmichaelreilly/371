# Solo works — status log

## Owner review after first deploy — 2026-11-02 (Claude session)
Changed per owner: solo renders as the chorale's single horizontal system
(page layout dropped); zoom replaces the spacing slider (spacing fixed at
the medium anchor); zoom is one CSS-only control on #content, so staff,
answer row and slot boxes scale together and blanks stay under their notes
(no Verovio call on zoom); touch pinch uses the live touch list, fixing
one-finger drags that zoomed (stale pointers from fingers lifted outside
the score); the P4 commit() collided with the game's own commit(), so it
is now zoomCommit(); the __vrv test hook is removed. Smoke test updated:
40/40, including blank alignment at zoom 3 (0.0 px), one horizontal
system for solo, and CDP touch tests (one finger scrolls, two zoom).

## P4 — 2026-11-02
Done:
- **Two-stage zoom + spacing in index.html, both corpora.** While the
  gesture runs, a CSS `transform` on `#staff` previews immediately —
  zero Verovio calls (asserted via a `window.__vrv` counter wrapped
  around the toolkit entry points in `toolkit()`; no behaviour change).
  On gesture end the transform is removed, Verovio re-renders once
  (`redoLayout` — ids stable per P2), and the scroll position is
  restored so the musical point under the gesture anchor stays put
  (chorale: same relative x of the svg re-anchored under the pinch
  midpoint / wheel cursor; solo: scrollTop kept, width is fixed).
- **Zoom inputs:** two-pointer pinch on the score area via Pointer
  Events (midpoint tracked live as the fingers move); desktop
  Ctrl/Cmd + wheel over the score (trackpad pinch arrives the same
  way), `preventDefault` ONLY when ctrl/meta held, debounced 220 ms
  for the commit (wheel has no end event). Clamped 0.5×–3×.
- **Zoom application per corpus:** chorale = CSS height factor
  (`--zoom` var on `#staff`, svg keeps `height:calc(min(46vh,300px)*var(--zoom,1))`,
  width auto) + one `renderScore(false)` re-render to re-derive ids;
  solo = real re-wrap, `pageWidth` divides by zoom inside
  `soloOptions()` (on-screen staff px ≈ staffPx·zoom). Persisted per
  corpus as `zoom:chorale` / `zoom:solo` in localStorage, try/catch,
  restored via `loadZoom()` in `setup()`/`setupSolo()`.
- **Viewport meta relaxed** (`maximum-scale=1, user-scalable=no`
  dropped — it fights two-pointer pinch; iOS Safari ignores
  user-scalable anyway, but Android honoured it). `touch-action:
  pan-x pan-y` on `#scroller` in both modes so the browser's page
  zoom doesn't take over the score; page zoom untouched elsewhere.
- **Spacing slider moved onto the same path:** preview on `input`
  (scaleX, ratio of the piecewise-linear anchor proxies, CSS only),
  commit on `change` (pointerup/keyup) — the 160 ms debounce timer is
  gone. Solo commit restores scrollTop; chorale commit centres the
  selected slot (as before) or keeps the relative scroll fraction.
- **Invariants held:** after any commit the chorale slots are
  re-measured (`renderScore`/`layout`) — strictly increasing asserted
  in the smoke test after zoom commit, after reload, and after a
  spacing commit; playback was zoomed mid-flight in solo in the smoke
  test (highlight keeps running, playbtn stays on); chorale commits
  re-derive `chosenIds` from the new svg+timemap so the playhead
  cursor and grading keep working; zoom gestures never call
  `stopPlayback` and never touch PLAY_NOTES/anchor times.
- Smoke test additions in `tests/smoke_solo.mjs`: 17 new assertions
  (36 total, all PASS, exit 0 — raw output below). Real two-finger
  touch pinch **cannot be exercised headless** (Playwright can send
  the Pointer Events but not a genuine browser gesture pipeline);
  **owner to check pinch on a phone** — the wheel path, which shares
  the whole preview/commit engine, is fully covered.

Not done / known issues:
- PARTIAL SET as in P0–P3: gate run with `--allow-partial`; the 10
  coverage warnings are the expected ones.
- During a pinch preview the slot overlay and cursor stay at layout
  positions (they live outside the transformed `#staff`), so they can
  drift from the previewed staff until the commit lands — visual
  only, self-corrects at commit.
- Wheel-zoom commit is debounced 220 ms (wheel has no end event);
  pinch commits immediately on lifting the second finger.

Gate output (raw, `check_solo.py --allow-partial`, exit code 0):
```
== check_solo.py phase>=1
ok   chorale bundles, chorales/index.json, build_chorale.py, build_corpus.py unchanged
ok   28 kern files under data/solo/kern/
     bwv1001-4      pages=2  timemap=812
     bwv1002-2      pages=1  timemap=380
     bwv1002-3      pages=2  timemap=476
     bwv1002-4      pages=2  timemap=955
     bwv1002-6      pages=1  timemap=299
     bwv1002-8      pages=2  timemap=554
     bwv1003-4      pages=2  timemap=1021
     bwv1004-1      pages=2  timemap=547
     bwv1004-4      pages=2  timemap=910
     bwv1005-4      pages=3  timemap=1196
     bwv1006-6      pages=1  timemap=275
     bwv1006-7      pages=1  timemap=333
     bwv1007-1      pages=2  timemap=657
     bwv1007-2      pages=1  timemap=474
     bwv1007-3      pages=1  timemap=371
     bwv1007-4      pages=1  timemap=157
     bwv1007-5      pages=1  timemap=134
     bwv1007-6      pages=1  timemap=130
     bwv1007-7      pages=1  timemap=213
     bwv1010-1      pages=2  timemap=822
     bwv1010-2      pages=1  timemap=535
     bwv1010-3      pages=2  timemap=468
     bwv1010-4      pages=1  timemap=215
     bwv1010-5      pages=1  timemap=408
     bwv1010-6      pages=1  timemap=69
     bwv1010-7      pages=2  timemap=476
     bwv1011-3      pages=1  timemap=265
     bwv1011-4      pages=1  timemap=108
warn BWV 1001: 1 movements bundled, expected >= 4
warn BWV 1002: 5 movements bundled, expected >= 8
warn BWV 1003: 1 movements bundled, expected >= 4
warn BWV 1004: 2 movements bundled, expected >= 5
warn BWV 1005: 1 movements bundled, expected >= 4
warn BWV 1006: 2 movements bundled, expected >= 7
warn BWV 1008: 0 movements bundled, expected >= 6
warn BWV 1009: 0 movements bundled, expected >= 6
warn BWV 1011: 2 movements bundled, expected >= 6
warn BWV 1012: 0 movements bundled, expected >= 6
     PARTIAL SET: coverage warnings above are expected until KernScores is reachable; see docs/solo/INVENTORY.md
ok   28 solo bundles valid
== PASS  (0 failures, 10 warnings)
```

Smoke test output (raw, `node tests/smoke_solo.mjs`, exit code 0):
```
PASS chorale 1 loads with answer slots
PASS chorale 1 selected by default
PASS chorale 1: palette visible
PASS chorale 1: no console errors
PASS s:bwv1002-2: SVG rendered with notes (380 note groups)
PASS s:bwv1002-2: slots and palette hidden
PASS s:bwv1002-2: no console errors
PASS s:bwv1002-2: >=1 note highlighted after 2 s of playback
PASS s:bwv1004-4: SVG rendered with notes (910 note groups)
PASS s:bwv1004-4: slots and palette hidden
PASS s:bwv1004-4: no console errors
PASS s:bwv1004-4: >=1 note highlighted after 2 s of playback
PASS s:bwv1007-1: SVG rendered with notes (657 note groups)
PASS s:bwv1007-1: slots and palette hidden
PASS s:bwv1007-1: no console errors
PASS s:bwv1007-1: >=1 note highlighted after 2 s of playback
PASS back to chorale 1: slots visible and populated
PASS back to chorale 1: palette visible
PASS back to chorale 1: no console errors
PASS P4 chorale: transform preview present mid-gesture
PASS P4 chorale: slot count unchanged after zoom commit
PASS P4 chorale: slot x strictly increasing after zoom commit
PASS P4 chorale: zoom persisted to localStorage (got 1.12)
PASS P4 chorale: no console errors
PASS P4 chorale: zoom restored after reload (--zoom=1.12)
PASS P4 chorale: slots strictly increasing after reload
PASS P4 chorale reload: no console errors
PASS P4 spacing: input event previews via transform (got "translate(-544.7px, 0px) scale(1.33571, ")
PASS P4 spacing: preview makes zero Verovio calls
PASS P4 spacing: change event commits and removes transform
PASS P4 spacing: commit re-rendered via Verovio
PASS P4 spacing: slots still strictly increasing after commit
PASS P4 spacing: no console errors
PASS P4 solo: >=1 note highlighted after zoom during playback
PASS P4 solo: playback still running after zoom commit
PASS P4 solo: no console errors
```

Waiting for review.

## Review of P2 + P3 — 2026-11-02 (Claude session)
Verdict: **P2 and P3 accepted.** Gate PASS and smoke 19/19 reproduced
independently; screenshots checked on desktop and phone width. P2 found and
fixed the stale `end` field in soloRaf itself. P3's decision to keep the
service-worker VERSION (so visited chorale bundles aren't wiped) is right.
Owner decisions recorded in HANDOFF ("Decisions"): scordatura = sounding
pitch. New work: **Phase 4, pinch zoom and live spacing for both
corpora.** Owner notes from the review, for later: phone staff size is small
(pinch zoom addresses it); score headers show kern-derived labels
("Violoncello", "Prelude").

## P3 — 2026-11-02

Final summary of the whole solo-works effort:

- **Bundles built:** 28 of ~75 movements, from the 28-file partial kern set
  (P0). Violin: bwv1001-4; 1002-2/3/4/6/8; 1003-4; 1004-1/4; 1005-4;
  1006-6/7. Cello: 1007-1…7 (Suite 1 complete); 1010-1…7 (Suite 4
  complete); 1011-3/4. Every bundle: MEI straight from Python Verovio
  6.2.1's Humdrum import, `parts[].notes` derived from that same toolkit's
  timemap (parts count == timemap note-ons, one timeline), `events: []`,
  identity from the WORKS/HANDOFF tables, `sourceFile` recorded.
- **Failures over the course of the work:** first P1 (music21 kern→MusicXML
  route) was rejected in review — it dropped every slur and truncated at
  mid-file spine splits (bwv1002-8 shipped without bars 21–70); redone per
  the revised Phase 1. The P1 redo then hit 6 gate failures, written up as
  BLOCKED with evidence; 4 were gate bugs (raw-text slur grep matching a
  `!!!SCA:` comment; page-1-only slur check; music21 as "independent"
  counter) and 2 were real data gaps (bwv1011-03/04 lacked `*>norep`,
  so Verovio expanded repeats into `-rend2` ids) — the reviewer fixed the
  gate and made the canon edits, and the gate has passed on every run since.
  No failures remain open.
- **What to review:** the sw.js delta (below), SPEC.md pitfalls 10–12 +
  solo Status entry, README paragraph + attribution, the two rebuilt
  scordatura bundles bwv1011-3/4 (canon `*>norep[A,B]` edit documented in
  INVENTORY.md), and docs/solo/INVENTORY.md's missing-movement list for the
  rebuild when KernScores returns.

Done:
- `sw.js`: `solo/index.json` added to the SHELL precache (install-time
  `addAll`). Solo movement bundles needed no new handler: the existing
  `.json.gz` branch is extension-based and already served
  `solo/<id>.json.gz` cache-first from DATA_CACHE exactly like chorale
  bundles — comments updated to say so honestly ("chorale + solo movement
  bundles"; shell comment mentions both picker lists). No chorale behaviour
  change: same caches, same handlers, VERSION still `v1` (deliberate: a
  bump would delete the data cache and discard every visited chorale
  bundle; unchanged VERSION means the new SW byte-diff triggers
  reinstall and `addAll` merges `solo/index.json` into the existing
  SHELL cache). `node --check sw.js` passes.
- SPEC.md: pitfalls 10–12 added per HANDOFF — 10 expansion labels vs
  `expandRepeats()` (music21 never; Verovio's ExpansionMap auto-expands
  `*>[A,A,B,B]` without `*>norep` into `-rend2` replays, gate bans `rend`
  ids, ExpansionMap warnings harmless), 11 Verovio qstamps ≠ music21
  offsets (pickup drift, partita1-2 99.25 vs 95.25; one timeline per
  pipeline; `getMIDIValuesForElement` returns `{}` until
  `renderToTimemap()` has run), 12 kern `!!!` headers unreliable for
  identity (`!!!SCA:` stray-paren false positive included). Plus a
  solo-library entry in the Status section.
- README.md: one paragraph on the listen-and-read library (what it is,
  partial set with pointer to INVENTORY.md, build/gate scripts) and an
  Attribution line: KernScores, Craig Sapp / CCARH.
- Final gates both run fresh on this tree (raw outputs below):
  `check_solo.py --allow-partial` exit 0, smoke test exit 0.

Not done / known issues:
- PARTIAL SET as in P0–P2: KernScores still unreachable; gate run with
  `--allow-partial` and the 10 coverage warnings are the expected ones.
  When it returns: re-run the P0 fetch for the missing files, rebuild with
  `build_solo.py`, run the gate WITHOUT `--allow-partial`.
- Test tooling still lives outside the repo (as in P2; commands documented
  in `tests/smoke_solo.mjs`).

Gate output (raw, `check_solo.py --allow-partial`, exit code 0):
```
== check_solo.py phase>=1
ok   chorale bundles, chorales/index.json, build_chorale.py, build_corpus.py unchanged
ok   28 kern files under data/solo/kern/
     bwv1001-4      pages=2  timemap=812
     bwv1002-2      pages=1  timemap=380
     bwv1002-3      pages=2  timemap=476
     bwv1002-4      pages=2  timemap=955
     bwv1002-6      pages=1  timemap=299
     bwv1002-8      pages=2  timemap=554
     bwv1003-4      pages=2  timemap=1021
     bwv1004-1      pages=2  timemap=547
     bwv1004-4      pages=2  timemap=910
     bwv1005-4      pages=3  timemap=1196
     bwv1006-6      pages=1  timemap=275
     bwv1006-7      pages=1  timemap=333
     bwv1007-1      pages=2  timemap=657
     bwv1007-2      pages=1  timemap=474
     bwv1007-3      pages=1  timemap=371
     bwv1007-4      pages=1  timemap=157
     bwv1007-5      pages=1  timemap=134
     bwv1007-6      pages=1  timemap=130
     bwv1007-7      pages=1  timemap=213
     bwv1010-1      pages=2  timemap=822
     bwv1010-2      pages=1  timemap=535
     bwv1010-3      pages=2  timemap=468
     bwv1010-4      pages=1  timemap=215
     bwv1010-5      pages=1  timemap=408
     bwv1010-6      pages=1  timemap=69
     bwv1010-7      pages=2  timemap=476
     bwv1011-3      pages=1  timemap=265
     bwv1011-4      pages=1  timemap=108
warn BWV 1001: 1 movements bundled, expected >= 4
warn BWV 1002: 5 movements bundled, expected >= 8
warn BWV 1003: 1 movements bundled, expected >= 4
warn BWV 1004: 2 movements bundled, expected >= 5
warn BWV 1005: 1 movements bundled, expected >= 4
warn BWV 1006: 2 movements bundled, expected >= 7
warn BWV 1008: 0 movements bundled, expected >= 6
warn BWV 1009: 0 movements bundled, expected >= 6
warn BWV 1011: 2 movements bundled, expected >= 6
warn BWV 1012: 0 movements bundled, expected >= 6
     PARTIAL SET: coverage warnings above are expected until KernScores is reachable; see docs/solo/INVENTORY.md
ok   28 solo bundles valid
== PASS  (0 failures, 10 warnings)
```

Smoke test output (raw, `node tests/smoke_solo.mjs`, exit code 0):
```
PASS chorale 1 loads with answer slots
PASS chorale 1 selected by default
PASS chorale 1: palette visible
PASS chorale 1: no console errors
PASS s:bwv1002-2: SVG rendered with notes (380 note groups)
PASS s:bwv1002-2: slots and palette hidden
PASS s:bwv1002-2: no console errors
PASS s:bwv1002-2: >=1 note highlighted after 2 s of playback
PASS s:bwv1004-4: SVG rendered with notes (910 note groups)
PASS s:bwv1004-4: slots and palette hidden
PASS s:bwv1004-4: no console errors
PASS s:bwv1004-4: >=1 note highlighted after 2 s of playback
PASS s:bwv1007-1: SVG rendered with notes (657 note groups)
PASS s:bwv1007-1: slots and palette hidden
PASS s:bwv1007-1: no console errors
PASS s:bwv1007-1: >=1 note highlighted after 2 s of playback
PASS back to chorale 1: slots visible and populated
PASS back to chorale 1: palette visible
PASS back to chorale 1: no console errors
```

Waiting for review.

## P2 — 2026-11-02
Done:
- `index.html` picker: after `chorales/index.json`, also loads
  `solo/index.json` and appends two `<optgroup>`s — "Violin — Sonatas &
  Partitas" (12 options) and "Cello Suites" (16); values `s:<id>`, text
  `BWV 1002 · Allemanda` format. Chorale options unchanged (355 direct
  options, same restore path).
- Loading `s:<id>` fetches `solo/<id>.json.gz` through the existing
  decompression helper (now path-parametrised; chorale call site passes
  the same URL as before). Last selection persisted in `lastsel` on every
  load (chorales also keep writing `riem` exactly as before) and restored
  on startup — verified across reload in Chromium.
- `kind==="solo"` (`body.solo` CSS): answer slots, palette, progress and
  reset hidden; Key shown from the bundle's WORKS-table key (case decides
  major/minor, e.g. "E♭ major"); `DATA.mei` rendered with the existing
  toolkit using page layout — `breaks:'auto'`, systems wrap at pageWidth,
  pages stacked, vertical scroll. Staff size adapts to container width
  (pageWidth = 127·W/staffPx; constant measured in Verovio 6.2.x).
- Playback uses **only the Verovio timemap** (`tk.renderToTimemap()`,
  an array in the JS toolkit): start = the entry qstamp whose `on` holds
  the id, end = the qstamp where it appears in `off`, pitch =
  `tk.getMIDIValuesForElement(id).pitch`. parts[].notes offsets are not
  used for timing. No fermata dilation (identity perf map). The existing
  25 ms lookahead scheduler, voice, tempo slider, play/stop are reused.
  Gotcha found and handled: `getMIDIValuesForElement` returns `{}` until
  `renderToTimemap()` has run (verified in 6.2.1) — the build order in
  `buildSoloPlayback()` respects that; comment in code.
- Highlight: `g.playing` class while a note sounds (colour --red, verified
  rgb(169,50,38) on the notehead/stem in a zoomed screenshot); auto-scroll
  keeps the sounding system in view (deadband, no per-frame jitter);
  tapping a notehead starts playback from that note (drag-scroll guarded
  by a 10 px travel check).
- Spacing slider works in solo too (redoLayout; note ids verified stable
  across redoLayout in 6.2.1, so highlight/playback data stays valid).
- `tests/smoke_solo.mjs` (Playwright headless Chromium + `python3 -m
  http.server`): all assertions PASS, exit 0 — raw output below.
- Beyond the mandated assertions: all 28 movements loaded in headless
  Chromium — every one renders an SVG with zero console errors; playback
  highlight probed on 6 (incl. bwv1007-4 with its grace notes and the
  bwv1011-3/4 scordatura pair — bwv1011-3 shows 265 notes, i.e. repeats
  NOT expanded, matching the P1 canon edit); chorale playback cursor and
  spacing slider regression-checked; screenshots inspected (wrapped
  systems with measure numbers, no horizontal scroll).

Not done / known issues:
- PARTIAL SET as in P0/P1 (KernScores still unreachable): gate run with
  `--allow-partial`; the 10 coverage warnings are the expected ones.
- Test tooling lives outside the repo (node tarball in ~/nodedist,
  playwright module in ~/pw-smoke; no package.json added here) —
  `tests/smoke_solo.mjs` header documents the exact commands.
- If `solo/index.json` is unavailable the picker silently falls back to
  chorale-only (console.warn, no user-facing error).

Gate output (raw, `check_solo.py --allow-partial`, exit code 0):
```
== check_solo.py phase>=1
ok   chorale bundles, chorales/index.json, build_chorale.py, build_corpus.py unchanged
ok   28 kern files under data/solo/kern/
     bwv1001-4      pages=2  timemap=812
     bwv1002-2      pages=1  timemap=380
     bwv1002-3      pages=2  timemap=476
     bwv1002-4      pages=2  timemap=955
     bwv1002-6      pages=1  timemap=299
     bwv1002-8      pages=2  timemap=554
     bwv1003-4      pages=2  timemap=1021
     bwv1004-1      pages=2  timemap=547
     bwv1004-4      pages=2  timemap=910
     bwv1005-4      pages=3  timemap=1196
     bwv1006-6      pages=1  timemap=275
     bwv1006-7      pages=1  timemap=333
     bwv1007-1      pages=2  timemap=657
     bwv1007-2      pages=1  timemap=474
     bwv1007-3      pages=1  timemap=371
     bwv1007-4      pages=1  timemap=157
     bwv1007-5      pages=1  timemap=134
     bwv1007-6      pages=1  timemap=130
     bwv1007-7      pages=1  timemap=213
     bwv1010-1      pages=2  timemap=822
     bwv1010-2      pages=1  timemap=535
     bwv1010-3      pages=2  timemap=468
     bwv1010-4      pages=1  timemap=215
     bwv1010-5      pages=1  timemap=408
     bwv1010-6      pages=1  timemap=69
     bwv1010-7      pages=2  timemap=476
     bwv1011-3      pages=1  timemap=265
     bwv1011-4      pages=1  timemap=108
warn BWV 1001: 1 movements bundled, expected >= 4
warn BWV 1002: 5 movements bundled, expected >= 8
warn BWV 1003: 1 movements bundled, expected >= 4
warn BWV 1004: 2 movements bundled, expected >= 5
warn BWV 1005: 1 movements bundled, expected >= 4
warn BWV 1006: 2 movements bundled, expected >= 7
warn BWV 1008: 0 movements bundled, expected >= 6
warn BWV 1009: 0 movements bundled, expected >= 6
warn BWV 1011: 2 movements bundled, expected >= 6
warn BWV 1012: 0 movements bundled, expected >= 6
     PARTIAL SET: coverage warnings above are expected until KernScores is reachable; see docs/solo/INVENTORY.md
ok   28 solo bundles valid
== PASS  (0 failures, 10 warnings)
```

Smoke test output (raw, `node tests/smoke_solo.mjs`, exit code 0):
```
PASS chorale 1 loads with answer slots
PASS chorale 1 selected by default
PASS chorale 1: palette visible
PASS chorale 1: no console errors
PASS s:bwv1002-2: SVG rendered with notes (380 note groups)
PASS s:bwv1002-2: slots and palette hidden
PASS s:bwv1002-2: no console errors
PASS s:bwv1002-2: >=1 note highlighted after 2 s of playback
PASS s:bwv1004-4: SVG rendered with notes (910 note groups)
PASS s:bwv1004-4: slots and palette hidden
PASS s:bwv1004-4: no console errors
PASS s:bwv1004-4: >=1 note highlighted after 2 s of playback
PASS s:bwv1007-1: SVG rendered with notes (657 note groups)
PASS s:bwv1007-1: slots and palette hidden
PASS s:bwv1007-1: no console errors
PASS s:bwv1007-1: >=1 note highlighted after 2 s of playback
PASS back to chorale 1: slots visible and populated
PASS back to chorale 1: palette visible
PASS back to chorale 1: no console errors
```

Waiting for review.

## Review of P1 redo — 2026-11-02 (Claude session)
Verdict: **P1 accepted.** The BLOCKED call was correct and well evidenced;
all five diagnoses were reproduced independently. The gate was wrong, not
the bundles:
- its "independent" count used music21, which truncates kern at mid-file
  spine splits (partita1-8: 24 of 70 bars). The first P1 shipped that
  truncated movement; this redo is the first correct build of it;
- its slur check grepped raw text (matched a `!!!SCA:` comment) and looked
  at page 1 only.
Fixes (by the reviewer): the gate now counts attacks and slur starts with a
direct kern tokenizer, compares slurs in the MEI itself, fails on Verovio
repeat expansion (`rend` ids), and silences Verovio's log. Canon edit:
`*>norep[A,B]` added to bwv1011-03/04 (see INVENTORY.md, "Canon edits");
those two bundles were rebuilt with `build_solo.py --id`.
Gate (`--allow-partial`): PASS, 0 failures, 10 expected coverage warnings.
Next: P2. Highlight logic need not handle `rend` ids any more; the gate
forbids them.

## BLOCKED — 2026-11-02 (P1 redo, revised Phase 1)

BLOCKED: with bundles built exactly per the revised Phase 1 (MEI straight
from Python Verovio 6.2.1's Humdrum import, `parts` from that same
toolkit's `renderToTimemap()`), the gate's `--allow-partial` full run
cannot PASS on honest data. The gate is the referee and not mine to edit,
so per HANDOFF rule 5 I am stopping. The 6 failures decompose into five
root causes, each verified directly (not inferred):

1. **Slur-check false positive 1 — a comment record.** `bwv1011-03`: the
   only `(` in the file is line 9, the `!!!SCA:` bibliographic record
   ("… Bach-Werke-Verzeichnis (Schmieder)"). The music spines contain
   zero slur marks, so the score correctly renders none — but the gate
   tests raw file text: `"(" in src.read_text()`.
2. **Slur-check false positive 2 — pagination.** `bwv1002-04`: 12 real,
   properly paired slur marks; Verovio imports all 12 (`<slur startid=…>
   endid=…>` in the MEI) and renders all 12 — on page 2 (page 1 count 0,
   page 2 count 12, verified). The gate checks only `renderToSVG(1)`.
   (Separately, the check's literal `'class="slur'` can never appear in
   an honest Verovio MEI: `getMEI()` serializes slurs as
   `<slur xml:id="…" startid="#note-…">` with no `class` attribute; and
   since every SVG draws `<g id="…" class="note">` for all 28 bundles,
   matching on raw bundle JSON text would be cosmetic gaming, which I
   did not do.)
3. **music21 truncates the kern at mid-file spine splits.** `bwv1002-08`
   (`partita1-8.krn`): 70 bars; a `*^` split lands at bar 21 (line 200).
   music21 parses only 24 measures / 184 notes — bars 21–70 silently
   dropped. Verovio imports all 70 bars / 554 notes (MEI has 70
   `<measure>`; the split section plainly exists in the kern). The old
   music21-route P1 shipped this movement missing bars 21–70 entirely.
   No honest MEI can bring Verovio's 554 within 3% of music21's 184.
   (13 of the 28 kerns contain `*^` splits; partita1-8 is the worst
   truncation, but the mechanism is systemic in music21's Humdrum
   parser.)
4. **Verovio auto-expands repeats when the kern lacks `*>norep`.**
   `bwv1011-03` / `bwv1011-04` (Suite 5 Courante / Sarabande — exactly
   the two scordatura files): their kerns carry `*>[A,A,B,B]` but NOT
   the `*>norep[A,B]` label that all 25 other repeated kerns carry.
   Verovio then expands the repeat structure at render/timemap time: the
   timemap lists every notated note twice, the second pass under
   synthetic `-rend2` ids (bwv1011-04: 108 written notes → 216 ons, all
   216 ids unique, rend2 entries starting at q=24 with the first note
   replayed; bwv1011-03: 265 → 530). music21 counts the unexpanded score
   (263 / 108). Bisected: removing the `<expansion>` element from the
   MEI removes all rend2 ids (216 → 108) — but that would also change
   playback semantics (repeats not played) and hand-edit Verovio's own
   output, a decision for review, not something to slip in.
   P2 consequence as currently written: the JS toolkit will produce the
   same rend2 ids for these two movements, so highlight logic must
   tolerate timemap ids absent from the SVG.
5. **Grace notes count in the timemap.** `bwv1007-04`: 11 grace notes;
   the gate's independent music21 count excludes graces (146) while the
   timemap includes them (157); tolerance is 3% + 5 → 155.4 < 157.
   Defensible on both sides — listed for completeness; causes 1–4 are
   the hard blockers (cause 3 alone makes a PASS impossible).

The rebuilt bundles themselves are, as far as verifiable, correct per the
revised Phase 1: all 28 MEIs load and render in Verovio 6.2.1, slurs
import wherever the music has them, `parts` mirrors the toolkit timemap
exactly (one timeline), identity fields all come from our tables.
Raw gate output (exit 1) is in the P1 redo section below.

## P1 (redo) — 2026-11-02
Done:
- `pipeline/build_solo.py` rewritten per the revised Phase 1: no music21,
  no repeat stripping. `tk.loadData(kern_text)` → `tk.getMEI()` (a
  `<?xml`-declared MEI; prepended only if absent); identity tables, ids,
  `--id` rebuild, and index regeneration kept as reviewed. Bundle fields
  per REQ: `sourceFile` (path relative to `data/solo/kern/`), `mei`
  replaces `musicxml` (no `musicxml` key anywhere).
- `parts[].notes` from the Verovio timemap of a fresh toolkit load of the
  generated MEI: offset = qstamp of the entry whose `on` holds the id,
  dur = off-qstamp − offset, midi = `getMIDIValuesForElement(id)["pitch"]`
  (loud exit if an on-id has no pitch). 28/28 bundles: parts count ==
  timemap note-ons exactly.
- MEI header `<title>` rewritten from the WORKS/HANDOFF tables (kern
  headers unreliable, per spec).
- Per-movement self-check (informational only): MEI re-loads, pages ≥ 1,
  count/midi sanity, plus the gate's exact slur heuristic as a warning —
  which flagged exactly the two files the gate then failed (bwv1011-3,
  bwv1002-4).
- 28 bundles rebuilt + `solo/index.json` regenerated (28 entries,
  unchanged content).

Not done / known issues:
- BLOCKED — see the section at the top. Gate run: FAIL (6 failures,
  10 warnings), exit 1. The 10 warnings are the expected partial-set
  coverage ones.

Gate output (raw, `check_solo.py --allow-partial`, exit code 1):
```
[Warning] An expansion cannot be generated with more than one section
[Warning] ExpansionMap::Expand: Element referenced in @plist not found: label-A
[Warning] ExpansionMap::Expand: Element referenced in @plist not found: label-A
[Warning] ExpansionMap::Expand: Element referenced in @plist not found: label-B
[Warning] ExpansionMap::Expand: Element referenced in @plist not found: label-B
[Warning] ExpansionMap::Expand: Element referenced in @plist not found: label-A
[Warning] ExpansionMap::Expand: Element referenced in @plist not found: label-A
[Warning] ExpansionMap::Expand: Element referenced in @plist not found: label-B
[Warning] ExpansionMap::Expand: Element referenced in @plist not found: label-B
[Warning] ExpansionMap::Expand: Element referenced in @plist not found: label-A
[Warning] ExpansionMap::Expand: Element referenced in @plist not found: label-A
[Warning] ExpansionMap::Expand: Element referenced in @plist not found: label-B
[Warning] ExpansionMap::Expand: Element referenced in @plist not found: label-B
[Warning] ExpansionMap::Expand: Element referenced in @plist not found: label-A
[Warning] ExpansionMap::Expand: Element referenced in @plist not found: label-A1
[Warning] ExpansionMap::Expand: Element referenced in @plist not found: label-A
[Warning] ExpansionMap::Expand: Element referenced in @plist not found: label-A2
[Warning] ExpansionMap::Expand: Element referenced in @plist not found: label-B
[Warning] ExpansionMap::Expand: Element referenced in @plist not found: label-B1
[Warning] ExpansionMap::Expand: Element referenced in @plist not found: label-B
[Warning] ExpansionMap::Expand: Element referenced in @plist not found: label-B2
[Warning] Insufficient space to draw mixed beam, starting at 'note-L244F1'. Drawing 'below' instead.
[Warning] Insufficient space to draw mixed beam, starting at 'note-L248F1'. Drawing 'below' instead.
[Warning] Insufficient space to draw mixed beam, starting at 'note-L398F1'. Drawing 'below' instead.
[Warning] Insufficient space to draw mixed beam, starting at 'note-L515F1'. Drawing 'below' instead.
[Warning] Insufficient space to draw mixed beam, starting at 'note-L244F1'. Drawing 'below' instead.
[Warning] Insufficient space to draw mixed beam, starting at 'note-L248F1'. Drawing 'below' instead.
[Warning] Insufficient space to draw mixed beam, starting at 'note-L398F1'. Drawing 'below' instead.
[Warning] Insufficient space to draw mixed beam, starting at 'note-L515F1'. Drawing 'below' instead.
[Warning] Insufficient space to draw mixed beam, starting at 'note-L244F1'. Drawing 'below' instead.
[Warning] Insufficient space to draw mixed beam, starting at 'note-L248F1'. Drawing 'below' instead.
[Warning] Insufficient space to draw mixed beam, starting at 'note-L398F1'. Drawing 'below' instead.
[Warning] Insufficient space to draw mixed beam, starting at 'note-L515F1'. Drawing 'below' instead.
[Warning] Insufficient space to draw mixed beam, starting at 'note-L244F1'. Drawing 'below' instead.
[Warning] Insufficient space to draw mixed beam, starting at 'note-L248F1'. Drawing 'below' instead.
[Warning] Insufficient space to draw mixed beam, starting at 'note-L398F1'. Drawing 'below' instead.
[Warning] Insufficient space to draw mixed beam, starting at 'note-L244F1'. Drawing 'below' instead.
[Warning] Insufficient space to draw mixed beam, starting at 'note-L248F1'. Drawing 'below' instead.
[Warning] Insufficient space to draw mixed beam, starting at 'note-L398F1'. Drawing 'below' instead.
[Warning] Insufficient space to draw mixed beam, starting at 'note-L244F1'. Drawing 'below' instead.
[Warning] Insufficient space to draw mixed beam, starting at 'note-L248F1'. Drawing 'below' instead.
[Warning] Insufficient space to draw mixed beam, starting at 'note-L398F1'. Drawing 'below' instead.
[Warning] Insufficient space to draw mixed beam, starting at 'note-L244F1'. Drawing 'below' instead.
[Warning] Insufficient space to draw mixed beam, starting at 'note-L248F1'. Drawing 'below' instead.
[Warning] Insufficient space to draw mixed beam, starting at 'note-L398F1'. Drawing 'below' instead.
[Warning] Insufficient space to draw mixed beam, starting at 'note-L244F1'. Drawing 'below' instead.
[Warning] Insufficient space to draw mixed beam, starting at 'note-L248F1'. Drawing 'below' instead.
[Warning] Insufficient space to draw mixed beam, starting at 'note-L398F1'. Drawing 'below' instead.
[Warning] ExpansionMap::Expand: Element referenced in @plist not found: label-A
[Warning] ExpansionMap::Expand: Element referenced in @plist not found: label-A
[Warning] ExpansionMap::Expand: Element referenced in @plist not found: label-B
[Warning] ExpansionMap::Expand: Element referenced in @plist not found: label-B
[Warning] Insufficient space to draw mixed beam, starting at 'note-L244F1'. Drawing 'below' instead.
[Warning] Insufficient space to draw mixed beam, starting at 'note-L248F1'. Drawing 'below' instead.
[Warning] Insufficient space to draw mixed beam, starting at 'note-L398F1'. Drawing 'below' instead.
[Warning] Insufficient space to draw mixed beam, starting at 'note-L515F1'. Drawing 'below' instead.
[Warning] ExpansionMap::Expand: Element referenced in @plist not found: label-A
[Warning] ExpansionMap::Expand: Element referenced in @plist not found: label-A
[Warning] ExpansionMap::Expand: Element referenced in @plist not found: label-B
[Warning] ExpansionMap::Expand: Element referenced in @plist not found: label-B
[Warning] ExpansionMap::Expand: Element referenced in @plist not found: label-A
[Warning] ExpansionMap::Expand: Element referenced in @plist not found: label-A
[Warning] ExpansionMap::Expand: Element referenced in @plist not found: label-B
[Warning] ExpansionMap::Expand: Element referenced in @plist not found: label-B
[Warning] ExpansionMap::Expand: Element referenced in @plist not found: label-A
[Warning] ExpansionMap::Expand: Element referenced in @plist not found: label-A
[Warning] ExpansionMap::Expand: Element referenced in @plist not found: label-B
[Warning] ExpansionMap::Expand: Element referenced in @plist not found: label-B
[Warning] ExpansionMap::Expand: Element referenced in @plist not found: label-A
[Warning] ExpansionMap::Expand: Element referenced in @plist not found: label-A
[Warning] ExpansionMap::Expand: Element referenced in @plist not found: label-B
[Warning] ExpansionMap::Expand: Element referenced in @plist not found: label-B
[Warning] ExpansionMap::Expand: Element referenced in @plist not found: label-A
[Warning] ExpansionMap::Expand: Element referenced in @plist not found: label-A
[Warning] ExpansionMap::Expand: Element referenced in @plist not found: label-B
[Warning] ExpansionMap::Expand: Element referenced in @plist not found: label-B
[Warning] ExpansionMap::Expand: Element referenced in @plist not found: label-A
[Warning] ExpansionMap::Expand: Element referenced in @plist not found: label-A
[Warning] ExpansionMap::Expand: Element referenced in @plist not found: label-B
[Warning] ExpansionMap::Expand: Element referenced in @plist not found: label-B
[Warning] ExpansionMap::Expand: Element referenced in @plist not found: label-A
[Warning] ExpansionMap::Expand: Element referenced in @plist not found: label-A
[Warning] ExpansionMap::Expand: Element referenced in @plist not found: label-B
[Warning] ExpansionMap::Expand: Element referenced in @plist not found: label-B
[Warning] ExpansionMap::Expand: Element referenced in @plist not found: label-A
[Warning] ExpansionMap::Expand: Element referenced in @plist not found: label-A
[Warning] ExpansionMap::Expand: Element referenced in @plist not found: label-B
[Warning] ExpansionMap::Expand: Element referenced in @plist not found: label-B
[Warning] ExpansionMap::Expand: Element referenced in @plist not found: label-A
[Warning] ExpansionMap::Expand: Element referenced in @plist not found: label-A
[Warning] ExpansionMap::Expand: Element referenced in @plist not found: label-B
[Warning] ExpansionMap::Expand: Element referenced in @plist not found: label-B
[Warning] ExpansionMap::Expand: Element referenced in @plist not found: label-A
[Warning] ExpansionMap::Expand: Element referenced in @plist not found: label-A
[Warning] ExpansionMap::Expand: Element referenced in @plist not found: label-B
[Warning] ExpansionMap::Expand: Element referenced in @plist not found: label-B
[Warning] ExpansionMap::Expand: Element referenced in @plist not found: label-A
[Warning] ExpansionMap::Expand: Element referenced in @plist not found: label-A
[Warning] ExpansionMap::Expand: Element referenced in @plist not found: label-B
[Warning] ExpansionMap::Expand: Element referenced in @plist not found: label-B
[Warning] ExpansionMap::Expand: Element referenced in @plist not found: label-A
[Warning] ExpansionMap::Expand: Element referenced in @plist not found: label-A
[Warning] ExpansionMap::Expand: Element referenced in @plist not found: label-B
[Warning] ExpansionMap::Expand: Element referenced in @plist not found: label-B
[Warning] ExpansionMap::Expand: Element referenced in @plist not found: label-A
[Warning] ExpansionMap::Expand: Element referenced in @plist not found: label-A
[Warning] ExpansionMap::Expand: Element referenced in @plist not found: label-B
[Warning] ExpansionMap::Expand: Element referenced in @plist not found: label-B
[Warning] ExpansionMap::Expand: Element referenced in @plist not found: label-A
[Warning] ExpansionMap::Expand: Element referenced in @plist not found: label-A
[Warning] ExpansionMap::Expand: Element referenced in @plist not found: label-B
[Warning] ExpansionMap::Expand: Element referenced in @plist not found: label-B
[Warning] ExpansionMap::Expand: Element referenced in @plist not found: label-A
[Warning] ExpansionMap::Expand: Element referenced in @plist not found: label-A
[Warning] ExpansionMap::Expand: Element referenced in @plist not found: label-B
[Warning] ExpansionMap::Expand: Element referenced in @plist not found: label-B
[Warning] ExpansionMap::Expand: Element referenced in @plist not found: label-A
[Warning] ExpansionMap::Expand: Element referenced in @plist not found: label-A
[Warning] ExpansionMap::Expand: Element referenced in @plist not found: label-B
[Warning] ExpansionMap::Expand: Element referenced in @plist not found: label-B
[Warning] ExpansionMap::Expand: Element referenced in @plist not found: label-A
[Warning] ExpansionMap::Expand: Element referenced in @plist not found: label-A
[Warning] ExpansionMap::Expand: Element referenced in @plist not found: label-B
[Warning] ExpansionMap::Expand: Element referenced in @plist not found: label-B
[Warning] ExpansionMap::Expand: Element referenced in @plist not found: label-A
[Warning] ExpansionMap::Expand: Element referenced in @plist not found: label-A
[Warning] ExpansionMap::Expand: Element referenced in @plist not found: label-B
[Warning] ExpansionMap::Expand: Element referenced in @plist not found: label-B
== check_solo.py phase>=1
ok   chorale bundles, chorales/index.json, build_chorale.py, build_corpus.py unchanged
ok   28 kern files under data/solo/kern/
     bwv1001-4      pages=2  timemap=812
     bwv1002-2      pages=1  timemap=380
     bwv1002-3      pages=2  timemap=476
FAIL bwv1002-4: source has slurs but page 1 renders none
     bwv1002-4      pages=2  timemap=955
     bwv1002-6      pages=1  timemap=299
FAIL bwv1002-8: timemap note-ons 554 vs kern pitches 184 (more than 3% apart -- notes lost or duplicated)
     bwv1002-8      pages=2  timemap=554
     bwv1003-4      pages=2  timemap=1021
     bwv1004-1      pages=2  timemap=547
     bwv1004-4      pages=2  timemap=910
     bwv1005-4      pages=3  timemap=1196
     bwv1006-6      pages=1  timemap=275
     bwv1006-7      pages=1  timemap=333
     bwv1007-1      pages=2  timemap=657
     bwv1007-2      pages=1  timemap=474
     bwv1007-3      pages=1  timemap=371
FAIL bwv1007-4: timemap note-ons 157 vs kern pitches 146 (more than 3% apart -- notes lost or duplicated)
     bwv1007-4      pages=1  timemap=157
     bwv1007-5      pages=1  timemap=134
     bwv1007-6      pages=1  timemap=130
     bwv1007-7      pages=1  timemap=213
     bwv1010-1      pages=2  timemap=822
     bwv1010-2      pages=1  timemap=535
     bwv1010-3      pages=2  timemap=468
     bwv1010-4      pages=1  timemap=215
     bwv1010-5      pages=1  timemap=408
     bwv1010-6      pages=1  timemap=69
     bwv1010-7      pages=2  timemap=476
FAIL bwv1011-3: timemap note-ons 530 vs kern pitches 263 (more than 3% apart -- notes lost or duplicated)
FAIL bwv1011-3: source has slurs but page 1 renders none
     bwv1011-3      pages=1  timemap=530
FAIL bwv1011-4: timemap note-ons 216 vs kern pitches 108 (more than 3% apart -- notes lost or duplicated)
     bwv1011-4      pages=1  timemap=216
warn BWV 1001: 1 movements bundled, expected >= 4
warn BWV 1002: 5 movements bundled, expected >= 8
warn BWV 1003: 1 movements bundled, expected >= 4
warn BWV 1004: 2 movements bundled, expected >= 5
warn BWV 1005: 1 movements bundled, expected >= 4
warn BWV 1006: 2 movements bundled, expected >= 7
warn BWV 1008: 0 movements bundled, expected >= 6
warn BWV 1009: 0 movements bundled, expected >= 6
warn BWV 1011: 2 movements bundled, expected >= 6
warn BWV 1012: 0 movements bundled, expected >= 6
     PARTIAL SET: coverage warnings above are expected until KernScores is reachable; see docs/solo/INVENTORY.md
== FAIL  (6 failures, 10 warnings)
```

## Review of P1 — 2026-11-02 (Claude session)
Verdict: **redo P1 per the revised Phase 1 in HANDOFF.md.** The first P1
followed the spec and passed the gate; the spec was wrong. Rendering the
bundles showed music21's kern→MusicXML conversion drops all slurs and turns
spine splits into stray beams. Gate and HANDOFF are updated: bundles ship
MEI from Python Verovio's Humdrum import. The current solo/*.json.gz will
FAIL the updated gate until rebuilt.

## P1 — 2026-11-02
Done:
- `pipeline/build_solo.py`: parses each kern (music21), replaces every
  `bar.Repeat` with a regular barline WITHOUT `expandRepeats()` (371
  pitfall 1; the files carry Humdrum expansion labels `*>[A,A,B,B]` which
  music21's Expander rejects), writes MusicXML, extracts `parts[].notes`
  (offset/dur/midi; one entry per chord pitch, rests excluded) from the
  same stripped score, and writes `solo/<id>.json.gz`
  (id = `bwv<bwv>-<movementNo>`, no zero pad). `work`/`key` are imported
  from the WORKS table in check_solo.py; movement names come from the
  HANDOFF table; kern headers are never used for identity (bundle title
  metadata is set from our tables instead).
- 28 bundles + `solo/index.json` (28 entries: id, bwv, movementNo,
  movement, work, set — sorted by BWV then movementNo; the index is
  regenerated from the bundles on every build so the two cannot disagree).
- `build_solo.py` self-check per movement (informational only; the gate
  stays the referee): reparse the written MusicXML → no `bar.Repeat`;
  Verovio timemap note-ons within [pitches, pitches+graces].
- Gate run with `--allow-partial`: PASS, exit code 0 captured directly,
  0 failures. Only warnings are the 10 expected partial-coverage ones.

Not done / known issues:
- PARTIAL SET as in P0 (KernScores still unreachable; ~47 movements
  missing — see INVENTORY.md): gate run with `--allow-partial`, bundles
  exist only for the 28 P0 files.
- Verovio prints harmless import warnings for a few bundles (raw output
  below): `Unsupported bar-style 'heavy-light'` ×2 (music21's
  final-barline style; Verovio ignores it) and `There are 1 ties left
  open` ×2 (dangling tie start in music21's kern→MusicXML export,
  bwv1011-3/bwv1011-4; both pass the timemap check at exactly
  ons == pitches). No bundle failed.
- bwv1007-4 / bwv1011-3: timemap ons slightly exceed the ORIGINAL
  kern-parse pitch count (grace-note and spine-split artifacts of the
  kern→MusicXML round trip). The gate counts on the round-tripped XML,
  where both agree exactly (147+11=158 and 269=269). Raw output below.

Gate output:
```
[Warning] MusicXML import: Unsupported bar-style 'heavy-light'
[Warning] Insufficient space to draw mixed beam, starting at 'r1uj4ucl'. Drawing 'below' instead.
[Warning] Insufficient space to draw mixed beam, starting at 'r1uj4ucl'. Drawing 'below' instead.
[Warning] Insufficient space to draw mixed beam, starting at 'r1uj4ucl'. Drawing 'below' instead.
[Warning] Insufficient space to draw mixed beam, starting at 'r1uj4ucl'. Drawing 'below' instead.
[Warning] Insufficient space to draw mixed beam, starting at 'r1uj4ucl'. Drawing 'below' instead.
[Warning] Insufficient space to draw mixed beam, starting at 'r1uj4ucl'. Drawing 'below' instead.
[Warning] Insufficient space to draw mixed beam, starting at 'edd47f8'. Drawing 'above' instead.
[Warning] Insufficient space to draw mixed beam, starting at 'ztydfbr'. Drawing 'below' instead.
[Warning] Insufficient space to draw mixed beam, starting at 'ztydfbr'. Drawing 'below' instead.
[Warning] Insufficient space to draw mixed beam, starting at 'ztydfbr'. Drawing 'below' instead.
[Warning] Insufficient space to draw mixed beam, starting at 'ztydfbr'. Drawing 'below' instead.
[Warning] Insufficient space to draw mixed beam, starting at 'edd47f8'. Drawing 'above' instead.
[Warning] Insufficient space to draw mixed beam, starting at 'ztydfbr'. Drawing 'below' instead.
[Warning] Insufficient space to draw mixed beam, starting at 'ztydfbr'. Drawing 'below' instead.
[Warning] MusicXML import: Unsupported bar-style 'heavy-light'
[Warning] Insufficient space to draw mixed beam, starting at 'n98x70h'. Drawing 'above' instead.
[Warning] Insufficient space to draw mixed beam, starting at 'n98x70h'. Drawing 'above' instead.
[Warning] Insufficient space to draw mixed beam, starting at 'n98x70h'. Drawing 'above' instead.
[Warning] Insufficient space to draw mixed beam, starting at 'n98x70h'. Drawing 'above' instead.
[Warning] Insufficient space to draw mixed beam, starting at 'n98x70h'. Drawing 'above' instead.
[Warning] Insufficient space to draw mixed beam, starting at 'n98x70h'. Drawing 'above' instead.
[Warning] MusicXML import: There are 1 ties left open
[Warning] MusicXML import: There are 1 ties left open
== check_solo.py phase>=1
ok   chorale bundles, chorales/index.json, build_chorale.py, build_corpus.py unchanged
ok   28 kern files under data/solo/kern/
     bwv1001-4      pages=2  notes=803   timemap=803
     bwv1002-2      pages=1  notes=380   timemap=380
     bwv1002-3      pages=1  notes=474   timemap=474
     bwv1002-4      pages=2  notes=955   timemap=955
     bwv1002-6      pages=1  notes=299   timemap=299
     bwv1002-8      pages=1  notes=184   timemap=184
     bwv1003-4      pages=2  notes=1021  timemap=1021
     bwv1004-1      pages=1  notes=540   timemap=540
     bwv1004-4      pages=2  notes=910   timemap=910
     bwv1005-4      pages=3  notes=1196  timemap=1196
     bwv1006-6      pages=1  notes=275   timemap=275
     bwv1006-7      pages=1  notes=333   timemap=333
     bwv1007-1      pages=2  notes=656   timemap=657
     bwv1007-2      pages=1  notes=469   timemap=474
     bwv1007-3      pages=1  notes=371   timemap=371
     bwv1007-4      pages=1  notes=147   timemap=158
     bwv1007-5      pages=1  notes=133   timemap=134
     bwv1007-6      pages=1  notes=126   timemap=130
     bwv1007-7      pages=1  notes=212   timemap=213
     bwv1010-1      pages=2  notes=822   timemap=822
     bwv1010-2      pages=2  notes=535   timemap=535
     bwv1010-3      pages=2  notes=465   timemap=468
     bwv1010-4      pages=1  notes=213   timemap=215
     bwv1010-5      pages=1  notes=408   timemap=408
     bwv1010-6      pages=1  notes=69    timemap=69
     bwv1010-7      pages=2  notes=476   timemap=476
     bwv1011-3      pages=1  notes=269   timemap=269
     bwv1011-4      pages=1  notes=108   timemap=108
warn BWV 1001: 1 movements bundled, expected >= 4
warn BWV 1002: 5 movements bundled, expected >= 8
warn BWV 1003: 1 movements bundled, expected >= 4
warn BWV 1004: 2 movements bundled, expected >= 5
warn BWV 1005: 1 movements bundled, expected >= 4
warn BWV 1006: 2 movements bundled, expected >= 7
warn BWV 1008: 0 movements bundled, expected >= 6
warn BWV 1009: 0 movements bundled, expected >= 6
warn BWV 1011: 2 movements bundled, expected >= 6
warn BWV 1012: 0 movements bundled, expected >= 6
     PARTIAL SET: coverage warnings above are expected until KernScores is reachable; see docs/solo/INVENTORY.md
ok   28 solo bundles valid
== PASS  (0 failures, 10 warnings)
```
(exit code 0, captured directly with the warnings unfiltered)

Waiting for review.

## P0 — 2026-11-02
Done:
- 28 kern files under `data/solo/kern/{violin,cello}/`: 12 violin + 16 cello
  (BWV 1007 and 1010 complete at 7/7 each; 1001–1006 and 1011 partial; 1008,
  1009, 1012 empty). Breakdown, per-file bytes, source URLs, and the missing
  list: `docs/solo/INVENTORY.md`.
- Provenance: KernScores itself is 503 site-wide (domain now fronts the
  Polish-scores project; not transient). Bytes fetched from the documented
  fallback mirror `automata/ana-music`, then **all 28 verified byte-identical
  to Wayback's identity captures of the original kern.humdrum.org ksdata
  responses** (Sept 2025 timestamps in INVENTORY.md). Movement names/movementNo
  from the HANDOFF table, not kern headers.
- Search-exhausted evidence in INVENTORY.md (dead domain, craigsapp repo list,
  ana-music full tree = same 28 files, Wayback CDX zero hits for ~47 missing
  filenames, MCCC monophonic set not used per spec).

Not done / known issues:
- PARTIAL SET per HANDOFF "Partial source set": ~47 of ~75 movements missing
  (details in INVENTORY.md). P1–P3 will run the gate with `--allow-partial`.
- No subagents used for fetching: 28 small downloads done inline (allowed —
  spec says "at most 2").

Gate output:
```
== check_solo.py phase>=0
ok   chorale bundles, chorales/index.json, build_chorale.py, build_corpus.py unchanged
ok   28 kern files under data/solo/kern/
== PASS  (0 failures, 0 warnings)
```
Waiting for review.

## Setup — 2026-11-02 (prepared in a Claude session)
Done:
- Branch `solo-works`, HANDOFF.md, CLAUDE.md, gate `pipeline/check_solo.py`,
  baseline hashes `docs/solo/chorales.sha256` (356 chorale files + index +
  build_chorale.py + build_corpus.py).
- Gate tested against two sample bundles (partita1-2, bwv1007-01): both
  validate (380/380 and 656/657 timemap note-ons); tampering with
  chorales/index.json is caught.
Next: P0.
