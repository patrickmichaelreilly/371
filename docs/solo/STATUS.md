# Solo works — status log

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
