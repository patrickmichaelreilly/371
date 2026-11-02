# Solo works for 371 — handoff spec

Add Bach's violin Sonatas & Partitas (BWV 1001–1006) and cello Suites
(BWV 1007–1012) to the 371 app as a **listen-and-read library**: engraved
score, playback with a moving highlight, no analysis game. Conform to the
existing stack: music21 builds MusicXML, the app renders it client-side with
Verovio WASM, data ships as gzipped JSON bundles.

There is no answer key for these works, so `events` is always `[]` and the
analysis UI is hidden for them. Chorale behaviour must not change at all.

## Rules (read twice)

1. Work on branch `solo-works`. Never commit to `main`.
2. Work **one phase at a time**. At the end of each phase: run the gate,
   paste its raw output into `docs/solo/STATUS.md`, commit with the message
   `[P<n> DONE] <summary>`, push, then **stop and wait**. Start the next
   phase only when told "continue P<n+1>".
3. Never edit: `chorales/` (any file), `pipeline/build_chorale.py`,
   `pipeline/build_corpus.py`, `pipeline/check_solo.py`,
   `docs/solo/chorales.sha256`. The gate checks this.
4. Never write that a check passed unless its raw output, pasted in
   STATUS.md, says PASS. A partial result is reported as partial.
5. If the same error happens 3 times, or a rule here seems impossible,
   write `BLOCKED: <reason + evidence>` at the top of STATUS.md, commit,
   push, stop.
6. Small diffs. No refactors of existing code. No new dependencies beyond
   those named here.
7. Commit early inside a phase (`[P<n>] <what>`) so progress is visible.
8. At the start of every phase, re-read this file and STATUS.md.

## Environment

    python3 -m venv .venv
    .venv/bin/pip install music21 verovio==6.2.1
    # verovio 6.2.1 is pinned: it must match vendor/verovio-toolkit-wasm.js (6.2.0)

Gate: `.venv/bin/python pipeline/check_solo.py [--phase 0]` — exit 0 = PASS.
Verovio prints `[Warning] Insufficient space to draw mixed beam` lines; they
are harmless.

## Phase 0 — sources and inventory

Goal: every movement of all 12 works as a kern file under
`data/solo/kern/{violin,cello}/`, plus `docs/solo/INVENTORY.md`.

Source: KernScores (Craig Sapp, CCARH). The directories are believed to be
`users/craig/classical/bach/violin` and `users/craig/classical/bach/cello`.
Believed URL forms (verify; adjust if needed):

    https://kern.humdrum.org/cgi-bin/ksbrowse?l=users/craig/classical/bach/cello
    https://kern.humdrum.org/cgi-bin/ksdata?l=users/craig/classical/bach/cello&file=bwv1007-01.krn&f=kern

Known file naming: violin `sonata1-4.krn`, `partita1-2.krn` (work-movement);
cello `bwv1007-01.krn`. A partial mirror exists at
github.com/automata/ana-music under `corpus/classical/users/craig/classical/bach/`
(fallback only).

Every downloaded file must start with Humdrum content containing `**kern`.
An HTML error page saved as .krn is the classic failure; the gate catches it.

INVENTORY.md: one table row per file: path, BWV, movement number, movement
name (from the table below, NOT from the file header), bytes, source URL.
List anything missing. Do not substitute other sources (no LilyPond
conversion). If any work is incomplete, record it and stop; the reviewer
decides.

Gate: `check_solo.py --phase 0` must PASS.

Subagents: allowed. At most 2 at once (one local GPU): one fetches violin,
one fetches cello. Each returns its file list; you write INVENTORY.md and
commit.

## Partial source set (added after P0 attempt 1)

KernScores returned 503 site-wide during P0, and every mirror found holds
the same 28-file subset. Decision: proceed with the files we have. Run the
gate as `check_solo.py --allow-partial` in P1–P3; missing movements are
then warnings, and every other check still fails hard. When KernScores is
reachable again, re-run P0's fetch for the missing files, rebuild with
build_solo.py, and run the gate WITHOUT --allow-partial.

Never use files headed `Extracted Monophonic Melody` (e.g. the MCCC set in
lexngu/cmme-jupyter): their chords and double stops are stripped.

## Phase 1 — bundles (REVISED after review; supersedes the first P1)

Review of the first P1 found the music21 kern→MusicXML route damages the
score: every slur is dropped, Humdrum spine splits become stray multi-bar
beams (bwv1004-1, bars 1–8) and padded voices. Verovio's own Humdrum import
renders the same files correctly. The vendored JS toolkit cannot read
Humdrum (it is built without it), but it reads MEI. So bundles now carry
MEI produced by the pinned **Python** Verovio from the kern source.

Rework `pipeline/build_solo.py` (keep its identity tables, ids, index logic):
1. `tk = verovio.toolkit(); tk.loadData(kern_text); mei = tk.getMEI()`.
   Ignore `ExpansionMap::Expand ... label-A` and "expansion cannot be
   generated" warnings: they are harmless.
2. `parts[].notes` come from Verovio, not music21: load the MEI into a
   fresh toolkit, take `renderToTimemap()` (a JSON string in Python 6.2.1;
   it may be a list in other versions — handle both). For each id in an
   entry's `on`, offset = that qstamp; dur = qstamp of the entry whose
   `off` contains the id, minus offset; midi =
   `getMIDIValuesForElement(id)["pitch"]`. This makes parts and the app's
   timemap one timeline.
3. Bundle fields: as before, but `mei` replaces `musicxml` (no `musicxml`
   key at all), plus `sourceFile` = path relative to `data/solo/kern/`
   (e.g. `violin/partita1-2.krn`).
4. music21 is no longer used to build bundles. Do not strip or expand
   repeats; Verovio handles the kern's own repeat structure.

Gate (updated `check_solo.py`, still not yours to edit): full run with
`--allow-partial` must PASS. It now checks the MEI loads and renders, that
the timemap's note count is within 3% of an independent music21 count of the
kern source, that slurs in the source render, and that `parts` matches the
timemap exactly.

## Phase 2 — listen mode in the app

All changes in `index.html`. Chorale paths stay byte-for-byte equivalent in
behaviour.

1. Picker: after loading `chorales/index.json`, also load `solo/index.json`
   and append two `<optgroup>`s: "Violin — Sonatas & Partitas" and
   "Cello Suites". Option values are `s:<id>`; option text
   `BWV 1002 · Allemanda`. Chorale options unchanged.
2. Loading `s:<id>` fetches `solo/<id>.json.gz` with the existing
   decompression helper. Remember the last selection the same way chorales do.
3. When `kind==="solo"`: hide the answer slots, palette, grading and
   progress UI. Render `DATA.mei` (not musicxml) with the existing Verovio
   toolkit, but with page
   layout (systems wrapping, vertical scroll) instead of the chorale's
   single horizontal system; movements run 30–250 bars.
4. Playback for solo uses **only the Verovio timemap**
   (`tk.renderToTimemap()` returns an ARRAY in the JS toolkit). For each
   note id in `on`: start = its qstamp, end = the qstamp where it appears
   in `off`, pitch = `tk.getMIDIValuesForElement(id).pitch`. Do not use
   `parts[].notes` offsets for timing: Verovio qstamps drift from music21
   offsets by up to a bar wherever there is a pickup or partial measure
   (measured: partita1-2 ends at qstamp 99.25 vs music21 95.25).
   Reuse the existing scheduler, voice and tempo slider.
5. Highlight: while a note sounds, add a class to its element (`#<id>`) and
   colour it; auto-scroll to keep the sounding system in view. Tapping a
   note starts playback from it.
6. Smoke test `tests/smoke_solo.mjs` (Playwright, `npx playwright`), serving
   the repo with `python3 -m http.server`. Must print PASS/FAIL per assertion:
   - chorale 1 loads, shows its answer slots, no console errors;
   - `s:bwv1002-2` (Double), `s:bwv1004-4` (Giga), `s:bwv1007-1` each load with
     an SVG, no console errors, and after 2 s of playback at least one note
     is highlighted;
   - switching back to chorale 1 restores slots and palette.

Gate: `check_solo.py` PASS **and** the smoke test output, both pasted.
Subagents: not allowed (one file, sequential edits).

## Phase 3 — offline, docs, wrap-up

1. `sw.js`: cache `solo/*.json.gz` cache-first like chorale bundles; add
   `solo/index.json` to the precache.
2. SPEC.md: add pitfalls 10–12 (expansion labels vs expandRepeats; qstamp
   vs music21 offset drift; kern header metadata unreliable) and a Status
   entry for this work. README: one paragraph + attribution (KernScores,
   Craig Sapp / CCARH).
3. STATUS.md: final summary: bundles built, failures, what to review.

Gate: `check_solo.py` PASS + smoke test PASS, pasted.

## Movement names (movementNo = file order)

| BWV | Movements |
|---|---|
| 1001 | Adagio · Fuga · Siciliana · Presto |
| 1002 | Allemanda · Double · Corrente · Double (Presto) · Sarabande · Double · Tempo di Borea · Double |
| 1003 | Grave · Fuga · Andante · Allegro |
| 1004 | Allemanda · Corrente · Sarabanda · Giga · Ciaccona |
| 1005 | Adagio · Fuga · Largo · Allegro assai |
| 1006 | Preludio · Loure · Gavotte en Rondeau · Menuet I · Menuet II · Bourrée · Gigue |
| 1007–1012 | Prélude · Allemande · Courante · Sarabande · (galanterie pair) · Gigue |

Galanterie pairs: 1007/1008 Menuet I & II; 1009/1010 Bourrée I & II;
1011/1012 Gavotte I & II. If the kern source splits a pair into two files,
each file is its own movement (so a suite can have 7).

## STATUS.md format

    ## P<n> — <date>
    Done: <bullets>
    Not done / known issues: <bullets>
    Gate output:
    ```
    <raw output>
    ```
    Waiting for review.
