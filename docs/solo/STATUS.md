# Solo works — status log

## Setup — 2026-11-02 (prepared in a Claude session)
Done:
- Branch `solo-works`, HANDOFF.md, CLAUDE.md, gate `pipeline/check_solo.py`,
  baseline hashes `docs/solo/chorales.sha256` (356 chorale files + index +
  build_chorale.py + build_corpus.py).
- Gate tested against two sample bundles (partita1-2, bwv1007-01): both
  validate (380/380 and 656/657 timemap note-ons); tampering with
  chorales/index.json is caught.
Next: P0.
