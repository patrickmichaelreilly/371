#!/usr/bin/env python3
"""
build_chorale.py -- data pipeline for the Bach chorale analysis game.

Produces, for one chorale (by Riemenschneider number):
  - three pre-rendered single-system SVGs (spacing levels; medium is default)
  - game JSON: RN answer events (offset, measure, beat, key, figure, MIDI
    voicing, phrase index, per-level notehead element id), per-part note
    data for playback, phrase count, pitch-verification flags.

Usage:
    python build_chorale.py <riem_number> [--wir PATH_TO_WHEN_IN_ROME] [--out DIR]

Requires:
    pip install music21 verovio
    git clone --filter=blob:none --sparse https://github.com/MarkGotham/When-in-Rome.git
    cd When-in-Rome && git sparse-checkout set "Corpus/Early_Choral/Bach,_Johann_Sebastian/Chorales"

READ SPEC.md BEFORE MODIFYING -- several steps below exist because of
non-obvious Verovio/music21 behaviors documented there.
"""
import argparse, json, re, sys
from pathlib import Path

from music21 import corpus, converter, roman, expressions, bar
import verovio

SPACING_LEVELS = [(0.25, 0.55), (0.40, 0.58), (0.90, 0.55)]  # tight/medium/wide
DEFAULT_LEVEL = 1


def load_score(riem: int):
    """Riemenschneider number -> music21 score, repeats stripped.

    Repeats MUST be stripped: Verovio's timemap expands repeats for playback,
    which desynchronizes qstamps from music21 offsets and silently maps
    post-repeat onsets to wrong (earlier) elements. See SPEC.md pitfall 1.
    """
    it = corpus.chorales.Iterator(riem, riem, numberingSystem='riemenschneider',
                                  returnType='stream')
    score = next(iter(it))
    for m in score.recurse().getElementsByClass('Measure'):
        for att in ('leftBarline', 'rightBarline'):
            if isinstance(getattr(m, att), bar.Repeat):
                setattr(m, att, bar.Barline('regular'))
    return score


def render(musicxml_path: str, lin: float, nonlin: float):
    tk = verovio.toolkit()
    tk.setOptions({"breaks": "none", "adjustPageHeight": True,
                   "adjustPageWidth": True, "pageWidth": 60000, "scale": 42,
                   "footer": "none", "header": "none",
                   "spacingLinear": lin, "spacingNonLinear": nonlin})
    tk.loadFile(musicxml_path)
    return tk.renderToSVG(1), tk.renderToTimemap()


def notehead_origin_x(svg: str) -> dict:
    """note-group id -> x of its notehead glyph ORIGIN (left edge, in
    viewBox units, ignoring the page-margin transform).

    Only used to pick the LEFTMOST voice per onset. Never use these raw
    coordinates for on-screen positioning -- the browser must measure the
    .notehead subgroup at runtime instead (SPEC.md pitfalls 2 and 3)."""
    out = {}
    for m in re.finditer(r'<g id="([^"]+)" class="note">', svg):
        hm = re.search(r'class="notehead">\s*<use[^>]*translate\((-?[\d.]+)',
                       svg[m.end():m.end() + 800])
        if hm:
            out[m.group(1)] = float(hm.group(1))
    return out


def build(riem: int, wir_root: Path, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    score = load_score(riem)
    mxl = out_dir / "score.musicxml"
    score.write('musicxml', fp=str(mxl))

    # ---- answer key ----
    ana = wir_root / "Corpus/Early_Choral/Bach,_Johann_Sebastian/Chorales" \
                   / f"{riem:03d}" / "analysis.txt"
    if not ana.exists():
        sys.exit(f"analysis not found: {ana}")
    rntxt = converter.parse(str(ana), format='romanText')
    rns = list(rntxt.flatten().getElementsByClass(roman.RomanNumeral))

    # ---- chordified spans for voicings + pitch verification ----
    spans = [(float(c.offset), float(c.offset + c.quarterLength),
              sorted(p.midi for p in c.pitches))
             for c in score.chordify().flatten().notes]

    def voicing_at(off):
        for s, e, m in spans:
            if s <= off < e:
                return m
        return []

    def pcs_during(start, end):
        pcs = set()
        for s, e, m in spans:
            if s < end and e > start:
                pcs |= {x % 12 for x in m}
        return pcs

    # ---- phrases from soprano fermatas ----
    sop = score.parts[0].flatten().notes
    fends = [float(n.offset + n.quarterLength) for n in sop
             if any(isinstance(x, expressions.Fermata) for x in n.expressions)]

    def phrase_of(off):
        for i, fo in enumerate(fends):
            if off < fo:
                return i
        return max(len(fends) - 1, 0)

    # ---- events ----
    events = []
    for i, rn in enumerate(rns):
        off = round(float(rn.getOffsetInHierarchy(rntxt)), 3)
        nxt = round(float(rns[i + 1].getOffsetInHierarchy(rntxt)), 3) \
            if i + 1 < len(rns) else off + 1.0
        rn_pcs = {p.pitchClass for p in rn.pitches}
        verified = len(rn_pcs - pcs_during(off, nxt)) == 0
        events.append({"offset": off, "measure": rn.measureNumber,
                       "beat": float(rn.beat),
                       "key": rn.key.tonicPitchNameWithCase,
                       "figure": rn.figure, "midi": voicing_at(off),
                       "phrase": phrase_of(off), "verified": verified})

    # ---- render levels; pick leftmost-voice notehead id per onset ----
    noteids, svg_paths = [], []
    for li, (lin, nl) in enumerate(SPACING_LEVELS):
        svg, tm = render(str(mxl), lin, nl)
        nx = notehead_origin_x(svg)
        q2 = {}
        for e in tm:
            if 'on' in e:
                q2.setdefault(round(float(e['qstamp']), 3), []).extend(e['on'])
        ids = []
        for ev in events:
            cands = [(nx[i], i) for i in q2.get(ev["offset"], []) if i in nx]
            if not cands:
                sys.exit(f"riem {riem}: offset {ev['offset']} has no onset in "
                         f"timemap level {li} -- alignment failure, see SPEC.md")
            ids.append(min(cands)[1])
        assert all(svg.count(f'id="{i}"') == 1 for i in ids)
        noteids.append(ids)
        p = out_dir / f"sys{li}.svg"
        p.write_text(svg)
        svg_paths.append(p)

    # ---- per-part note data for playback ----
    parts = []
    for part in score.parts:
        notes = [{"offset": float(n.offset), "dur": float(n.quarterLength),
                  "midi": (n.pitch.midi if n.isNote else None),
                  "fermata": any(isinstance(e, expressions.Fermata)
                                 for e in n.expressions)}
                 for n in part.flatten().notesAndRests]
        parts.append({"name": part.partName, "notes": notes})

    data = {"riemenschneider": riem,
            "title": score.metadata.title or f"Riemenschneider {riem}",
            "numPhrases": len(fends), "defaultLevel": DEFAULT_LEVEL,
            "events": events, "noteids": noteids, "parts": parts,
            "analysisSource": "When in Rome (Gotham et al.), CC BY-SA 4.0"}
    (out_dir / "game_data.json").write_text(json.dumps(data))

    nver = sum(e["verified"] for e in events)
    print(f"riem {riem}: {len(events)} events, {nver} pitch-verified, "
          f"{len(fends)} phrases -> {out_dir}")
    return data


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("riem", type=int)
    ap.add_argument("--wir", type=Path, default=Path("When-in-Rome"))
    ap.add_argument("--out", type=Path, default=None)
    a = ap.parse_args()
    build(a.riem, a.wir, a.out or Path(f"build/{a.riem:03d}"))
