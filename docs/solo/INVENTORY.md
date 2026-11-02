# Solo works — kern inventory (Phase 0)

**Status: PARTIAL SET.** 28 of ~75 movement files obtained. KernScores
(kern.humdrum.org) returned 503 site-wide for the whole domain during P0 —
the domain now fronts the Polish Music Heritage project (`website-polish-scores`
in Craig Sapp's repos) and `git.humdrum.org` is unreachable — so the canonical
download URLs are dead. Every file below was fetched from the documented
fallback mirror `automata/ana-music` and **verified byte-identical (28/28,
`diff` on full contents)** against the Wayback Machine's identity captures of
the original `kern.humdrum.org/cgi-bin/ksdata` responses (Sept 2025), so the
bytes are KernScores bytes, not mirror edits.

Canonical source: KernScores, Craig Sapp / CCARH,
`users/craig/classical/bach/{violin,cello}`. Canonical URL form (currently 503):

    https://kern.humdrum.org/cgi-bin/ksdata?l=users/craig/classical/bach/<set>&file=<file>&f=kern

`<M>` in the table = the mirror base URL:

    https://raw.githubusercontent.com/automata/ana-music/master/corpus/classical/users/craig/classical/bach

Movement names and movementNo come from the HANDOFF table (movementNo = file
order), **not** from kern `!!!` headers (spec: headers unreliable).
For the two suites the source splits into 7 files (1007, 1010) the galanterie
pair occupies movements 5–6, matching the files' own `!!!OMD` headers
(Menuet I/II, Bourrée I/II).

## Present files (28)

| Path | BWV | Mov. no | Movement | Bytes | Source URL | Wayback ts |
|---|---|---|---|---|---|---|
| `violin/sonata1-4.krn` | 1001 | 4 | Presto | 6358 | `<M>/violin/sonata1-4.krn` | 20250910135256 |
| `violin/partita1-2.krn` | 1002 | 2 | Double | 3404 | `<M>/violin/partita1-2.krn` | 20250910022231 |
| `violin/partita1-3.krn` | 1002 | 3 | Corrente | 3203 | `<M>/violin/partita1-3.krn` | 20250916162243 |
| `violin/partita1-4.krn` | 1002 | 4 | Double (Presto) | 7274 | `<M>/violin/partita1-4.krn` | 20250914184027 |
| `violin/partita1-6.krn` | 1002 | 6 | Double | 2132 | `<M>/violin/partita1-6.krn` | 20250910074051 |
| `violin/partita1-8.krn` | 1002 | 8 | Double | 3754 | `<M>/violin/partita1-8.krn` | 20250918072152 |
| `violin/sonata2-4.krn` | 1003 | 4 | Allegro | 9914 | `<M>/violin/sonata2-4.krn` | 20250918133129 |
| `violin/partita2-1.krn` | 1004 | 1 | Allemanda | 4300 | `<M>/violin/partita2-1.krn` | 20250914055022 |
| `violin/partita2-4.krn` | 1004 | 4 | Giga | 6444 | `<M>/violin/partita2-4.krn` | 20250912020942 |
| `violin/sonata3-4.krn` | 1005 | 4 | Allegro assai | 11651 | `<M>/violin/sonata3-4.krn` | 20250917053634 |
| `violin/partita3-6.krn` | 1006 | 6 | Bourrée | 2928 | `<M>/violin/partita3-6.krn` | 20250910215317 |
| `violin/partita3-7.krn` | 1006 | 7 | Gigue | 2667 | `<M>/violin/partita3-7.krn` | 20250916230034 |
| `cello/bwv1007-01.krn` | 1007 | 1 | Prélude | 5042 | `<M>/cello/bwv1007-01.krn` | 20250911010025 |
| `cello/bwv1007-02.krn` | 1007 | 2 | Allemande | 3821 | `<M>/cello/bwv1007-02.krn` | 20250908131447 |
| `cello/bwv1007-03.krn` | 1007 | 3 | Courante | 3098 | `<M>/cello/bwv1007-03.krn` | 20250919173006 |
| `cello/bwv1007-04.krn` | 1007 | 4 | Sarabande | 1665 | `<M>/cello/bwv1007-04.krn` | 20250911034025 |
| `cello/bwv1007-05.krn` | 1007 | 5 | Menuet I | 1320 | `<M>/cello/bwv1007-05.krn` | 20250912232751 |
| `cello/bwv1007-06.krn` | 1007 | 6 | Menuet II | 1267 | `<M>/cello/bwv1007-06.krn` | 20250909233700 |
| `cello/bwv1007-07.krn` | 1007 | 7 | Gigue | 1820 | `<M>/cello/bwv1007-07.krn` | 20250910193141 |
| `cello/bwv1010-01.krn` | 1010 | 1 | Prélude | 5764 | `<M>/cello/bwv1010-01.krn` | 20250920052651 |
| `cello/bwv1010-02.krn` | 1010 | 2 | Allemande | 4294 | `<M>/cello/bwv1010-02.krn` | 20250908172246 |
| `cello/bwv1010-03.krn` | 1010 | 3 | Courante | 3756 | `<M>/cello/bwv1010-03.krn` | 20250916133637 |
| `cello/bwv1010-04.krn` | 1010 | 4 | Sarabande | 2430 | `<M>/cello/bwv1010-04.krn` | 20250916003642 |
| `cello/bwv1010-05.krn` | 1010 | 5 | Bourrée I | 3210 | `<M>/cello/bwv1010-05.krn` | 20250912175249 |
| `cello/bwv1010-06.krn` | 1010 | 6 | Bourrée II | 1012 | `<M>/cello/bwv1010-06.krn` | 20250911030815 |
| `cello/bwv1010-07.krn` | 1010 | 7 | Gigue | 3498 | `<M>/cello/bwv1010-07.krn` | 20250909150952 |
| `cello/bwv1011-03.krn` | 1011 | 3 | Courante | 2489 | `<M>/cello/bwv1011-03.krn` | 20250910044705 |
| `cello/bwv1011-04.krn` | 1011 | 4 | Sarabande | 1141 | `<M>/cello/bwv1011-04.krn` | 20250914002505 |

## Missing movements (~47 files)

Blocked by the KernScores outage; re-run the P0 fetch when the site is
reachable, rebuild bundles, and run the gate **without** `--allow-partial`
(HANDOFF, "Partial source set").

| BWV | Work | Have | Missing files (movement) |
|---|---|---|---|
| 1001 | Sonata No. 1 in G minor | 1/4 | `sonata1-1.krn` (Adagio), `sonata1-2.krn` (Fuga), `sonata1-3.krn` (Siciliana) |
| 1002 | Partita No. 1 in B minor | 5/8 | `partita1-1.krn` (Allemanda), `partita1-5.krn` (Sarabande), `partita1-7.krn` (Tempo di Borea) |
| 1003 | Sonata No. 2 in A minor | 1/4 | `sonata2-1.krn` (Grave), `sonata2-2.krn` (Fuga), `sonata2-3.krn` (Andante) |
| 1004 | Partita No. 2 in D minor | 2/5 | `partita2-2.krn` (Corrente), `partita2-3.krn` (Sarabanda), `partita2-5.krn` (Ciaccona) |
| 1005 | Sonata No. 3 in C major | 1/4 | `sonata3-1.krn` (Adagio), `sonata3-2.krn` (Fuga), `sonata3-3.krn` (Largo) |
| 1006 | Partita No. 3 in E major | 2/7 | `partita3-1.krn` (Preludio), `partita3-2.krn` (Loure), `partita3-3.krn` (Gavotte en Rondeau), `partita3-4.krn` (Menuet I), `partita3-5.krn` (Menuet II) |
| 1008 | Suite No. 2 in D minor | 0/6+ | `bwv1008-01.krn` … `bwv1008-06/07.krn` — all |
| 1009 | Suite No. 3 in C major | 0/6+ | `bwv1009-01.krn` … `bwv1009-06/07.krn` — all |
| 1011 | Suite No. 5 in C minor | 2/6 | `bwv1011-01.krn` (Prélude), `bwv1011-02.krn` (Allemande), `bwv1011-05.krn` (Gavotte I), `bwv1011-06.krn` (Gavotte II), `bwv1011-07.krn` (Gigue, if pair split) |
| 1012 | Suite No. 6 in D major | 0/6+ | `bwv1012-01.krn` … `bwv1012-06/07.krn` — all |

Complete works: **BWV 1007 (7/7)** and **BWV 1010 (7/7)**. Suites 1008/1009/1012
were never seen in any capture, so their exact file count (6, or 7 with a split
galanterie pair) is unknown; "~75" above assumes the 6-file form except where
splits are proven.

## Search exhausted — evidence

- `kern.humdrum.org`: HTTP 503 + maintenance page for every path probed
  (browse CGI, data CGI, root); `http://` 301s to the same. Not transient.
- `git.humdrum.org`: connection failed (no listener).
- `craigsapp` GitHub (full repo list): no repo contains the solo works;
  `bach-370-chorales` and `bach-musical-offering` are different repertoires.
- `automata/ana-music`: full recursive git tree (2,207 paths, not truncated)
  contains exactly the 28 files above — nothing more.
- Wayback Machine CDX (prefix + domain-wide, all URL forms): captures exist
  **only** for the 28 files above; zero captures for any missing filename.
- Not used, per spec: IMSLP/PDF, LilyPond conversion, and the
  `Extracted Monophonic Melody` MCCC set (`lexngu/cmme-jupyter`) — chords and
  double stops are stripped there, which breaks this library's chordal
  playback.

