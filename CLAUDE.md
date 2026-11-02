# 371 — agent instructions

Current task: **docs/solo/HANDOFF.md** (solo-works branch). Read it fully
before doing anything, and again at the start of every phase.

- One phase at a time; stop after each `[P<n> DONE]` commit and push, and
  wait for "continue P<n+1>".
- `pipeline/check_solo.py` is the referee. Never edit it, the chorale
  bundles, or the chorale pipeline. Paste raw gate output; never summarize
  a gate you did not see pass.
- Same error 3 times → write BLOCKED in docs/solo/STATUS.md, commit, push, stop.
- Background on the app: SPEC.md (canonical spec and pitfall ledger).
