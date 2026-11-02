#!/usr/bin/env python3
"""
build_solo.py -- data pipeline for the solo-works library (Bach violin
Sonatas & Partitas BWV 1001-1006, cello Suites BWV 1007-1012).

For every movement found under data/solo/kern/{violin,cello}/, produces:
  - solo/<id>.json.gz  bundle: {"id","bwv","set","work","movement",
                       "movementNo","key","kind","source","musicxml",
                       "parts","events"}
  - solo/index.json    array of {id, bwv, movementNo, movement, work, set},
                       regenerated from the bundles after every run so the
                       index can never disagree with them.

There is no answer key for these works, so `events` is always [] (see
docs/solo/HANDOFF.md). Chorale data is untouched: bundles live in a
separate solo/ directory.

Usage:
    python pipeline/build_solo.py                  # build all movements
    python pipeline/build_solo.py --id bwv1007-04  # rebuild one movement

Requires: pip install music21 verovio==6.2.1

READ docs/solo/HANDOFF.md BEFORE MODIFYING -- several steps below exist
because of non-obvious music21/Verovio behaviors:
  - repeats are neutralized WITHOUT expandRepeats(): kern files carry
    Humdrum expansion labels (*>[A,A,B,B]) and music21 raises
    ExpanderException on them; each half plays once (371 pitfall 1).
  - work/key/movement names come from the WORKS table + the HANDOFF
    movement table, NEVER from kern headers (they are wrong in places,
    e.g. partita1-2.krn claims "D Major").
"""
import argparse, gzip, json, re, sys, warnings
from pathlib import Path

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "pipeline"))
from check_solo import WORKS  # single source of truth for work titles/keys

from music21 import converter, bar
import verovio

# violin filename prefix -> BWV (sonata/partita numbering: 1->1, 2->3, 3->5)
VIOLIN_BWV = {"sonata1": 1001, "partita1": 1002, "sonata2": 1003,
              "partita2": 1004, "sonata3": 1005, "partita3": 1006}

# movement names, movementNo = file order (docs/solo/HANDOFF.md table).
# NEVER from kern headers: they are wrong in places.
VIOLIN_MOVEMENTS = {
    1001: ["Adagio", "Fuga", "Siciliana", "Presto"],
    1002: ["Allemanda", "Double", "Corrente", "Double (Presto)",
           "Sarabande", "Double", "Tempo di Borea", "Double"],
    1003: ["Grave", "Fuga", "Andante", "Allegro"],
    1004: ["Allemanda", "Corrente", "Sarabanda", "Giga", "Ciaccona"],
    1005: ["Adagio", "Fuga", "Largo", "Allegro assai"],
    1006: ["Preludio", "Loure", "Gavotte en Rondeau", "Menuet I",
           "Menuet II", "Bourrée", "Gigue"],
}
SUITE_BASE = ["Prélude", "Allemande", "Courante", "Sarabande"]
SUITE_PAIR = {1007: "Menuet", 1008: "Menuet", 1009: "Bourrée",
              1010: "Bourrée", 1011: "Gavotte", 1012: "Gavotte"}

RE_VIOLIN = re.compile(r"^(sonata1|partita1|sonata2|partita2|sonata3|partita3)-(\d+)\.krn$")
RE_CELLO = re.compile(r"^bwv(\d{4})-(\d+)\.krn$")


def kern_id(kern: Path):
    """kern path -> (bwv, movementNo, 'violin'|'cello'). Exits loudly on an
    unrecognized filename: names must come from our tables, never guessed."""
    m = RE_VIOLIN.match(kern.name) if kern.parent.name == "violin" \
        else RE_CELLO.match(kern.name)
    if not m or (kern.parent.name == "cello" and int(m.group(1)) not in WORKS):
        sys.exit(f"unrecognized kern filename (cannot map to BWV/movement): "
                 f"{kern}")
    if kern.parent.name == "violin":
        return VIOLIN_BWV[m.group(1)], int(m.group(2)), "violin"
    return int(m.group(1)), int(m.group(2)), "cello"


def movement_name(bwv: int, movementNo: int, split: bool) -> str:
    """Movement name from the HANDOFF tables. `split`: the source keeps the
    galanterie pair as two files (suite then has 7 movements)."""
    if bwv in VIOLIN_MOVEMENTS:
        tab = VIOLIN_MOVEMENTS[bwv]
        if not 1 <= movementNo <= len(tab):
            sys.exit(f"BWV {bwv}: movementNo {movementNo} outside the "
                     f"HANDOFF table (1..{len(tab)})")
        return tab[movementNo - 1]
    pair = SUITE_PAIR[bwv]
    if 1 <= movementNo <= 4:
        return SUITE_BASE[movementNo - 1]
    if split and movementNo == 5:
        return f"{pair} I"
    if split and movementNo == 6:
        return f"{pair} II"
    if movementNo == (7 if split else 6):
        return "Gigue"
    if movementNo == 5:
        return f"{pair} I & II"  # unsplit galanterie pair
    sys.exit(f"BWV {bwv}: movementNo {movementNo} outside the HANDOFF table")


def strip_repeats(score):
    """Replace every bar.Repeat with a regular barline (371 pitfall 1).
    Do NOT call expandRepeats(): the kern expansion labels (*>[A,A,B,B])
    raise ExpanderException; each half plays once."""
    for m in score.recurse().getElementsByClass("Measure"):
        for att in ("leftBarline", "rightBarline"):
            if isinstance(getattr(m, att), bar.Repeat):
                setattr(m, att, bar.Barline("regular"))


def tmap(tk):
    r = tk.renderToTimemap()
    return json.loads(r) if isinstance(r, str) else r


def build_one(kern: Path, out_dir: Path, split: bool):
    """One kern file -> solo/<id>.json.gz. Returns the index entry."""
    bwv, movementNo, setname = kern_id(kern)
    bid = f"bwv{bwv}-{movementNo}"
    work, key = WORKS[bwv][1], WORKS[bwv][2]
    movement = movement_name(bwv, movementNo, split)

    score = converter.parse(str(kern))
    strip_repeats(score)

    # Correct identity from our tables; kern header titles are unreliable
    # (spec: never use them).
    if score.metadata is not None:
        score.metadata.title = f"{work}, {movement}"

    xml_path = ROOT / "build" / f"_solo_{bid}.musicxml"
    xml_path.parent.mkdir(exist_ok=True)
    score.write("musicxml", fp=str(xml_path))
    xml = xml_path.read_text()

    # ---- self-check, mirroring the gate's arithmetic (informational:
    #      pipeline/check_solo.py remains the referee) ----
    chk = converter.parse(str(xml_path))
    if list(chk.recurse().getElementsByClass(bar.Repeat)):
        sys.exit(f"{bid}: repeat barlines survived in written musicxml")
    pitches = sum(len(n.pitches) for n in chk.recurse().notes
                  if not n.duration.isGrace)
    graces = sum(len(n.pitches) for n in chk.recurse().notes
                 if n.duration.isGrace)
    tk = verovio.toolkit()
    if not tk.loadData(xml):
        sys.exit(f"{bid}: verovio loadData failed")
    pages = tk.getPageCount()
    ons = sum(len(e["on"]) for e in tmap(tk) if e.get("on"))
    if not (pitches <= ons <= pitches + graces):
        sys.exit(f"{bid}: timemap note-ons {ons} vs score pitches {pitches} "
                 f"(+{graces} grace) -- repeats or ties not handled")
    print(f"  {bid:<13} pages={pages:<2} pitches={pitches:<5} "
          f"graces={graces:<3} timemap ons={ons}")

    # ---- parts[].notes from the SAME stripped score; one entry per pitch
    #      of a chord. Rests excluded (no midi); graces included (sounding
    #      pitches). Playback timing in the app comes from the Verovio
    #      timemap, not these offsets (qstamps drift near pickups). ----
    fallback = {"violin": "Violin", "cello": "Cello"}[setname]
    parts = []
    for part in score.parts:
        notes = [{"offset": float(n.offset), "dur": float(n.quarterLength),
                  "midi": int(p.midi)}
                 for n in part.flatten().notes for p in n.pitches]
        parts.append({"name": part.partName or fallback, "notes": notes})

    source = (f"KernScores, Craig Sapp / CCARH "
              f"(users/craig/classical/bach/{setname}/{kern.name}); bytes "
              f"via automata/ana-music mirror, Wayback-verified; see "
              f"docs/solo/INVENTORY.md")
    bundle = {"id": bid, "bwv": bwv, "set": setname, "work": work,
              "movement": movement, "movementNo": movementNo, "key": key,
              "kind": "solo", "source": source, "musicxml": xml,
              "parts": parts, "events": []}
    gz = gzip.compress(json.dumps(bundle).encode("utf-8"), mtime=0)
    (out_dir / f"{bid}.json.gz").write_bytes(gz)
    return {"id": bid, "bwv": bwv, "movementNo": movementNo,
            "movement": movement, "work": work, "set": setname}


def rebuild_index(out_dir: Path):
    """Regenerate solo/index.json from the bundles themselves."""
    idx = []
    for p in sorted(out_dir.glob("*.json.gz")):
        d = json.loads(gzip.decompress(p.read_bytes()))
        idx.append({k: d[k] for k in ("id", "bwv", "movementNo", "movement",
                                      "work", "set")})
    idx.sort(key=lambda e: (e["bwv"], e["movementNo"]))
    (out_dir / "index.json").write_text(json.dumps(idx))
    return idx


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--id", help="rebuild a single movement, e.g. bwv1007-04")
    a = ap.parse_args()
    kern_dir = ROOT / "data/solo/kern"
    kfiles = sorted(kern_dir.glob("*/*.krn"))
    if not kfiles:
        sys.exit(f"no kern files under {kern_dir}")
    # split galanterie pair = the source (mirrored on disk) keeps -07 files
    per_bwv = {}
    for k in kfiles:
        bwv, mov, _ = kern_id(k)
        per_bwv.setdefault(bwv, set()).add(mov)
    out_dir = ROOT / "solo"
    out_dir.mkdir(exist_ok=True)
    if a.id:
        want = [k for k in kfiles if kern_id(k) and
                f"bwv{kern_id(k)[0]}-{kern_id(k)[1]}" == a.id]
        if not want:
            sys.exit(f"--id {a.id}: no such movement under {kern_dir}")
        build_one(want[0], out_dir, split=7 in per_bwv[kern_id(want[0])[0]])
    else:
        print(f"building {len(kfiles)} movements -> {out_dir}/")
        for k in kfiles:
            build_one(k, out_dir, split=7 in per_bwv[kern_id(k)[0]])
    idx = rebuild_index(out_dir)
    print(f"solo/index.json: {len(idx)} entries")


if __name__ == "__main__":
    main()