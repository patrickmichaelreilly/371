# Solo works — status log

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
