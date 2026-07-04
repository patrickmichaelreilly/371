# Chorale Analysis Game — Handoff Spec

Project: a mobile game presenting Bach chorales (Riemenschneider 371) one
phrase at a time; the puzzle is Roman-numeral functional analysis entered
below the staff. This document is the canonical handoff from the prototyping
session (2026-07-04) to Claude Code development. It is primarily a **pitfall
ledger**: everything in "Hard-won facts" was discovered by hitting the
failure, and re-discovering any of them will cost a session.

## Current state (all verified by running code)

The prototype (`app/chorale_analysis.html`, built from `app/ui_template.html`)
is a self-contained HTML file for Riemenschneider 1 / BWV 269. It renders the
full chorale as one horizontal-scrolling system with 60 answer slots aligned
under chord onsets, a progressive token-builder palette (numeral, quality,
figures, /x secondary, key change) rendering proper stacked theory typography,
press-and-hold drone of Bach's actual voicing per slot (WebAudio), two-attempt
grading with reveal, and a tight/med/wide spacing switcher. Medium spacing is
the locked default. Slot alignment is confirmed correct on desktop and phone.

The pipeline (`pipeline/build_chorale.py`) is parametrized by Riemenschneider
number and reproduces the session's verified output exactly (asserted). It
emits three SVGs plus `game_data.json` containing answer events, per-level
notehead element ids, and per-part note data (offset/duration/MIDI/fermata)
ready for playback. 59/60 events pitch-verify for chorale 1; the one flag is
an incomplete V7 (omitted fifth), i.e. a true musical subtlety, not a bug.

## Data sources

Scores: music21's bundled corpus contains all 371 Riemenschneider chorales
(`corpus.chorales.Iterator`, `numberingSystem='riemenschneider'`).
Answer key: When in Rome meta-corpus (github.com/MarkGotham/When-in-Rome),
directory `Corpus/Early_Choral/Bach,_Johann_Sebastian/Chorales/NNN/`, one
RomanText `analysis.txt` per chorale for all 371, plus a second independent
analysis (`analysis_BCMH.txt`) for 100 of them, plus inline variant readings
(`mNNvar1` lines) and phrase marks (`||`). music21 parses RomanText natively.
License: CC BY-SA 4.0 — fine for a free app with attribution; revisit if
monetizing. Clone sparsely (see script docstring); the full repo is large.

## Hard-won facts — do not relearn these

1. **Verovio's timemap expands repeats.** qstamps after a repeat barline
   desynchronize from music21 offsets AND collide with second-pass qstamps of
   earlier material, silently mapping onsets to wrong elements. Strip all
   `bar.Repeat` barlines from the score before export. `load_score()` does
   this; never remove it.

2. **A Verovio note `<g>`'s bounding box includes its lyric verse and melisma
   extender line.** Centering anything on the note group's bbox drifts right
   by up to a full beat under long extenders. Only ever measure the
   `<g class="notehead">` subgroup.

3. **The notehead `<use>` `translate(x,…)` is the glyph ORIGIN (left edge),
   in viewBox units, nested under a page-margin transform.** Server-side
   coordinate math from it will be wrong on screen. The shipped design:
   server picks WHICH element (leftmost voice per onset, via these origins,
   relative comparison only); the browser measures WHERE
   (`getBoundingClientRect()` of the `.notehead`, center-x). Element ids
   regenerate on every render — never reuse ids across renders or levels.

4. **`spacingLinear` hard-caps at 1.0** and out-of-range values silently fall
   back to the 0.25 default (warning on stderr only). The nonlinear exponent
   dominates perceived width. Locked medium = (0.40, 0.58) ≈ 7.6k px for a
   21-measure chorale.

5. **Verification invariant worth keeping in CI:** for every spacing level,
   slot x-positions must be strictly increasing in event order. This test
   catches every alignment failure mode encountered so far.

6. **~15 When-in-Rome analyses are in a different key than the music21
   score** (edition transposition; e.g. riem 17 score f#, analysis e).
   Figures are key-relative and stay valid; the pipeline detects the
   semitone shift maximizing pitch verification and transposes the analysis
   keys (`transposition` field in game_data.json). Discovered 2026-07-04
   during Milestone 1.

7. **Some analyses mark a harmony on a beat where no voice attacks** (held
   or tied chords, or edition rhythm differences) — no attack means no
   notehead to hang a slot on. The pipeline drops such events but retains
   them in `droppedEvents` (Milestone 3 alternatives seed data). If >20% of
   events are unmatched, the build fails loudly: that means a systematic
   analysis/score desync, not a droppable edge case.

8. **A few When-in-Rome analyses follow a different HARMONIZATION of the
   tune than music21's Riemenschneider numbering** (e.g. riem 170: 8-measure
   analysis in a, 10-measure score in g — no transposition/offset shift
   rescues it). These are upstream data mismatches: riem 43, 179, 333 fail
   the build, and 13 more sit below 60% pitch-verified. All 16 are excluded
   from v1 pending reconciliation; see reports/milestone1.md Triage.

## Milestone 1 — full corpus build

Loop `build_chorale.py` over 1..371 and emit a verification report (per
chorale: event count, % pitch-verified, phrase count, alignment success).
Expect a failure tail, not a clean sweep: known hazards are analysis/score
measure-numbering disagreements in When in Rome, occasional non-SATB textures,
and time-signature variety. Magnitude of the tail is unknown — do not assume;
measure, then triage into (a) pipeline fixes, (b) upstream data issues to
patch locally, (c) chorales to exclude from v1. Also parse and retain the
`mNNvarN` variant readings and the 100 BCMH second analyses: they are the
seed data for grading alternatives.

## Milestone 2 — full-piece playback

All required data already ships in `game_data.json` (`parts[].notes`).
Standard WebAudio lookahead scheduler: a ~25 ms tick schedules notes falling
within the next ~100 ms window at `AudioContext` time; tempo is a
quarter-note-duration multiplier read live so the slider takes effect
mid-playback. Reuse the drone's voice (triangle + octave sine through a
lowpass) per scheduled note with a short envelope. Start/stop, tempo 40–120
qpm. The slot x-mapping doubles as a playhead: interpolate cursor x between
adjacent onset positions by playback time. Optional: multiply fermata note
durations ~1.7x.

## Milestone 3 — grading equivalence engine

Current grading is exact-match after normalization (see `parseFig` /
`sameRN` in the template; the figure regex is verified against all 60
figures of chorale 1 — re-verify against the full corpus vocabulary in
Milestone 1). Needed equivalences, roughly in priority order: V ≈ V7 when
the seventh enters mid-span; tonicization vs. modulation boundary tolerance
(accept either the secondary-function reading or the key-change reading);
variant readings and BCMH disagreements as accepted alternatives; enharmonic
and figure shorthand normalization. Where the two human corpora disagree is
machine-readable evidence of legitimate ambiguity — use it.

## Milestone 4 — mobile shell ("conveyor mode")

Design decision already taken in principle: on mobile, the app owns scrolling
and slot advancement; entry happens in a fixed thumb zone; the drone moves to
a dedicated hold button beside Enter; slots become display-only (which also
dissolves tap-target size constraints). Keep free-navigation mode for review.
Replace pre-rendered SVGs with client-side Verovio (WASM) — this converts the
discrete spacing levels into a true continuous slider and shrinks the payload
by ~500 KB per chorale. Target stack per prior projects: PWA, offline-first;
the whole corpus as JSON should be a few MB.

## Manifest

    pipeline/build_chorale.py   tested; reproduces session output (riem 1)
    app/ui_template.html        template with __SVG0/1/2__ and __DATA__ slots
    app/chorale_analysis.html   built prototype, riem 1, self-contained
    data/game_data.json         riem 1 build output (with parts data)
    data/analysis_001.txt       reference copy of the When-in-Rome source
