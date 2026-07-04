# Milestone 1 corpus build report

- built ok: **368/371**
- build failures: **3**
- alignment invariant violations (built but x not strictly increasing): **0**
- total events: 20768
- overall pitch-verified: 90.3%
- chorales with BCMH second analysis parsed: 99 (errors: 0)
- chorales with variant readings: 165 (286 lines)
- transposed analyses (auto-corrected): 15
- dropped no-attack events: 94 across 40 chorales

## Transposed analyses (analysis key -> score key)

| riem | semitones | interval | verified after | before |
|---|---|---|---|---|
| 14 | 7 | P4 | 0.898 | 0.068 |
| 17 | 2 | M2 | 1.0 | 0.0 |
| 22 | 2 | M2 | 0.839 | 0.0 |
| 25 | 1 | A1 | 0.941 | 0.0 |
| 38 | 4 | M3 | 0.86 | 0.0 |
| 64 | 3 | m3 | 0.94 | 0.0 |
| 67 | 3 | m3 | 0.907 | 0.037 |
| 69 | 3 | m3 | 0.92 | 0.0 |
| 71 | 3 | m3 | 0.958 | 0.028 |
| 76 | 2 | M2 | 0.968 | 0.0 |
| 89 | 10 | M2 | 0.962 | 0.0 |
| 125 | 2 | M2 | 0.872 | 0.0 |
| 191 | 3 | M6 | 1.0 | 0.025 |
| 215 | 2 | M2 | 0.948 | 0.0 |
| 309 | 11 | m2 | 0.882 | 0.0 |

## Figures NOT matched by the grading regex (NUMRE)

- `IVmaj7` (x44)
- `IVmaj6/5` (x41)
- `VImaj7` (x20)
- `Imaj7` (x15)
- `IVmaj2` (x14)
- `Imaj6/5` (x6)
- `VImaj2` (x4)
- `N` (x3)
- `N6` (x3)
- `III+maj7` (x3)
- `Imaj2` (x3)
- `IIImaj7` (x2)
- `bVIImaj7` (x1)
- `It6` (x1)
- `V6/5/V/III` (x1)
- `Fr4/3` (x1)
- `Imaj4/3` (x1)
- `It6/ii` (x1)
- `V9[b9]` (x1)
- `V/V/III` (x1)
- `V2/V/III` (x1)
- `Ger6/5` (x1)

## Build failures

- 2x `riem N: N/N analysis events have no attack in the score -- systematic desync`
- 1x `riem N: offset N has no onset in timemap level N -- alignment failure, see SPEC.md`

| riem | error |
|---|---|
| 43 | riem 43: offset 20.0 has no onset in timemap level 0 -- alignment failure, see SPEC.md |
| 179 | riem 179: 46/76 analysis events have no attack in the score -- systematic desync |
| 333 | riem 333: 28/64 analysis events have no attack in the score -- systematic desync |

## Low pitch-verification (<90%): 117 chorales

| riem | % verified | events |
|---|---|---|
| 170 | 7.9 | 38 |
| 11 | 29.5 | 88 |
| 55 | 31.0 | 42 |
| 121 | 34.0 | 47 |
| 344 | 38.8 | 49 |
| 368 | 39.1 | 46 |
| 107 | 40.2 | 82 |
| 46 | 40.9 | 44 |
| 272 | 42.2 | 45 |
| 184 | 49.0 | 51 |
| 327 | 50.8 | 59 |
| 261 | 51.0 | 49 |
| 279 | 55.6 | 36 |
| 305 | 64.2 | 53 |
| 338 | 68.4 | 38 |
| 153 | 77.8 | 45 |
| 283 | 77.9 | 77 |
| 326 | 80.9 | 47 |
| 130 | 81.0 | 21 |
| 152 | 81.2 | 64 |
| 220 | 82.1 | 84 |
| 276 | 82.6 | 46 |
| 123 | 82.7 | 52 |
| 9 | 82.8 | 58 |
| 243 | 82.8 | 58 |
| 361 | 82.8 | 58 |
| 290 | 83.0 | 53 |
| 342 | 83.0 | 47 |
| 77 | 83.3 | 60 |
| 241 | 83.3 | 138 |
| 133 | 83.6 | 171 |
| 84 | 83.8 | 74 |
| 22 | 83.9 | 56 |
| 335 | 84.0 | 50 |
| 343 | 84.1 | 63 |
| 100 | 84.2 | 57 |
| 126 | 84.2 | 57 |
| 316 | 84.2 | 38 |
| 163 | 84.3 | 51 |
| 339 | 84.4 | 45 |
| 320 | 84.6 | 26 |
| 311 | 85.1 | 47 |
| 60 | 85.4 | 41 |
| 202 | 85.4 | 96 |
| 203 | 85.5 | 55 |
| 360 | 85.5 | 62 |
| 250 | 85.9 | 64 |
| 18 | 86.0 | 50 |
| 38 | 86.0 | 50 |
| 75 | 86.0 | 50 |
| 354 | 86.0 | 50 |
| 39 | 86.2 | 65 |
| 111 | 86.3 | 51 |
| 49 | 86.7 | 60 |
| 128 | 86.7 | 60 |
| 185 | 86.7 | 45 |
| 246 | 87.0 | 69 |
| 319 | 87.0 | 77 |
| 362 | 87.0 | 46 |
| 125 | 87.2 | 47 |
| 235 | 87.2 | 78 |
| 120 | 87.3 | 55 |
| 349 | 87.3 | 55 |
| 296 | 87.4 | 87 |
| 318 | 87.5 | 56 |
| 359 | 87.5 | 72 |
| 366 | 87.5 | 48 |
| 36 | 87.7 | 57 |
| 143 | 87.7 | 73 |
| 182 | 87.7 | 57 |
| 216 | 87.7 | 65 |
| 285 | 87.8 | 49 |
| 219 | 88.0 | 50 |
| 54 | 88.1 | 42 |
| 364 | 88.1 | 59 |
| 28 | 88.2 | 34 |
| 309 | 88.2 | 76 |
| 5 | 88.3 | 77 |
| 116 | 88.3 | 111 |
| 370 | 88.3 | 60 |
| 188 | 88.4 | 43 |
| 95 | 88.5 | 52 |
| 162 | 88.5 | 61 |
| 212 | 88.5 | 61 |
| 331 | 88.5 | 52 |
| 358 | 88.5 | 52 |
| 6 | 88.6 | 35 |
| 274 | 88.7 | 53 |
| 289 | 88.7 | 53 |
| 345 | 88.7 | 53 |
| 207 | 88.9 | 45 |
| 265 | 88.9 | 63 |
| 266 | 88.9 | 54 |
| 227 | 89.0 | 82 |
| 33 | 89.1 | 46 |
| 96 | 89.1 | 55 |
| 164 | 89.1 | 55 |
| 350 | 89.1 | 46 |
| 346 | 89.2 | 65 |
| 144 | 89.3 | 56 |
| 99 | 89.4 | 47 |
| 109 | 89.4 | 66 |
| 337 | 89.4 | 66 |
| 2 | 89.5 | 57 |
| 157 | 89.5 | 38 |
| 168 | 89.5 | 38 |
| 314 | 89.5 | 57 |
| 65 | 89.6 | 48 |
| 134 | 89.7 | 58 |
| 155 | 89.7 | 58 |
| 192 | 89.7 | 39 |
| 242 | 89.7 | 58 |
| 271 | 89.7 | 58 |
| 277 | 89.7 | 97 |
| 357 | 89.7 | 58 |
| 14 | 89.8 | 59 |
| 23 | 89.8 | 49 |

## Triage

- **include in v1: 355 chorales** (built, aligned, >=60% pitch-verified; remaining mismatches are analytical subtleties like incomplete chords and passing tones)
- **exclude pending upstream reconciliation: 16 chorales** -- build failures [43, 179, 333]; low-verification (analysis appears to follow a different harmonization/edition of the tune) [11, 46, 55, 107, 121, 170, 184, 261, 272, 279, 327, 344, 368]
- transposed-edition and no-attack-event hazards are handled in-pipeline (see report sections above)
