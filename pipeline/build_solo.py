#!/usr/bin/env python3
"""
build_solo.py -- data pipeline for the solo-works library (Bach violin
Sonatas & Partitas BWV 1001-1006, cello Suites BWV 1007-1012).

For every movement found under data/solo/kern/{violin,cello}/, produces:
  - solo/<id>.json.gz  bundle: {"id","bwv","set","work","movement",
                       "movementNo","key","kind","source","sourceFile",
                       "mei","parts","events"}
  - solo/index.json    array of {id, bwv, movementNo, movement, work, set},
                       regenerated from the bundles after every run so the
                       index can never disagree with them.

There is no answer key for these works, so `events` is always [] (see
docs/solo/HANDOFF.md). Chorale data is untouched: bundles live in a
separate solo/ directory.

Usage:
    python pipeline/build_solo.py                  # build all movements
    python pipeline/build_solo.py --id bwv1007-4   # rebuild one movement

Requires: pip install verovio==6.2.1. music21 is NOT used here (its
kern->MusicXML route drops every slur and mangles Humdrum spine splits);
the gate uses music21 only as an independent counter of the kern source.

READ docs/solo/HANDOFF.md (Phase 1, revised) BEFORE MODIFYING -- several
steps below exist because of non-obvious Verovio/kern behaviors:
  - bundles carry MEI straight from Verovio's own Humdrum import:
    tk.loadData(kern_text) -> tk.getMEI(). ExpansionMap::Expand
    "Element referenced in @plist not found" warnings are harmless.
    NOTE "An expansion cannot be generated with more than one section"
    is NOT harmless: it marks kerns with *>[A,A,B,B] but no *>norep
    label (bwv1011-03/-04), for which Verovio auto-expands at
    render/timemap time and mints synthetic "-rend2" note ids -- see
    the BLOCKED entry in docs/solo/STATUS.md.
  - repeats are neither stripped nor expanded: Verovio follows the kern's
    own repeat structure.
  - parts[].notes come from that same Verovio timemap, so parts and the
    app's playback share one timeline: offset = the qstamp of the entry
    whose `on` holds the note id; dur = the qstamp of the entry whose
    `off` holds it, minus offset; midi = getMIDIValuesForElement(id).
  - work/key/movement names come from the WORKS table + the HANDOFF
    movement table, NEVER from kern headers (they are wrong in places,
    e.g. partita1-2.krn claims "D Major"); the MEI's own title is
    rewritten from our tables for the same reason.
"""
import argparse, gzip, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "pipeline"))
from check_solo import WORKS  # single source of truth for work titles/keys

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


def tmap(tk):
    r = tk.renderToTimemap()
    return json.loads(r) if isinstance(r, str) else r


def timemap_notes(tk, bid):
    """parts[].notes straight from the toolkit's own timemap -- the exact
    timeline the app plays back (Phase 1 step 2): for each id in an
    entry's `on`, offset = that qstamp; dur = the qstamp of the entry
    whose `off` contains the id, minus offset; midi =
    getMIDIValuesForElement(id)["pitch"]. Exits loudly if an on id has no
    MIDI pitch (e.g. a rest leaking into the timemap)."""
    tm = tmap(tk)
    off_q = {}
    for e in tm:
        for nid in e.get("off") or []:
            off_q.setdefault(nid, float(e["qstamp"]))
    notes = []
    for e in tm:
        q = float(e["qstamp"])
        for nid in e.get("on") or []:
            v = tk.getMIDIValuesForElement(nid)
            pitch = v.get("pitch") if isinstance(v, dict) else None
            if not isinstance(pitch, int) or pitch <= 0:
                sys.exit(f"{bid}: timemap id {nid} has no MIDI pitch "
                         f"(got {v!r}) -- unexpected rest in timemap?")
            notes.append({"offset": q, "dur": off_q.get(nid, q) - q,
                          "midi": int(pitch)})
    return notes


def set_mei_title(mei: str, title: str) -> str:
    """Replace the first header <title> with our table identity (kern
    headers are unreliable). Leaves the MEI untouched if it has no
    <titleStmt>."""
    new, n = re.subn(r"(<titleStmt>\s*<title[^>]*>).*?(</title>)",
                     lambda m: m.group(1) + title + m.group(2),
                     mei, count=1, flags=re.S)
    return new if n else mei


def build_one(kern: Path, out_dir: Path, split: bool):
    """One kern file -> solo/<id>.json.gz. Returns the index entry."""
    bwv, movementNo, setname = kern_id(kern)
    bid = f"bwv{bwv}-{movementNo}"
    work, key = WORKS[bwv][1], WORKS[bwv][2]
    movement = movement_name(bwv, movementNo, split)

    kern_text = kern.read_text()
    tk = verovio.toolkit()
    if not tk.loadData(kern_text):
        sys.exit(f"{bid}: verovio could not load the kern source")
    mei = tk.getMEI()
    if not mei.lstrip().startswith("<?xml"):
        mei = '<?xml version="1.0" encoding="UTF-8"?>\n' + mei
    mei = set_mei_title(mei, f"{work}, {movement}")

    # ---- self-check, mirroring the gate's checks (informational:
    #      pipeline/check_solo.py remains the referee) ----
    chk = verovio.toolkit()
    if not chk.loadData(mei):
        sys.exit(f"{bid}: verovio cannot re-load the generated MEI")
    pages = chk.getPageCount()
    ons = sum(len(e["on"]) for e in tmap(chk) if e.get("on"))
    notes = timemap_notes(chk, bid)
    if len(notes) != ons:
        sys.exit(f"{bid}: parts notes {len(notes)} != timemap note-ons {ons}")
    bad = [n["midi"] for n in notes if not 20 <= n["midi"] <= 108]
    if bad:
        sys.exit(f"{bid}: midi values out of range: {bad[:5]}")
    if "(" in kern_text and 'class="slur' not in chk.renderToSVG(1):
        # same condition as the gate's slur check -- informational only,
        # the gate stays the referee (note: a '(' inside a !!! comment
        # record, e.g. the bibliographic !!!SCA line, trips this heuristic
        # even when the music has no slurs)
        print(f"  WARN {bid}: '(' in kern source but page 1 renders no slur")
    print(f"  {bid:<13} pages={pages:<2} ons={ons}")

    debug_mei = ROOT / "build" / f"_solo_{bid}.mei"
    debug_mei.parent.mkdir(exist_ok=True)
    debug_mei.write_text(mei)

    # Solo works are one staff; all timemap notes go under that one part.
    # Timing comes from the timemap in the app too (single timeline).
    label = re.search(r'<staffDef[^>]*\blabel="([^"]*)"', mei)
    name = {"violin": "Violin", "cello": "Cello"}[setname]
    if label and label.group(1).strip():
        name = label.group(1).strip()
    parts = [{"name": name, "notes": notes}]

    source = (f"KernScores, Craig Sapp / CCARH "
              f"(users/craig/classical/bach/{setname}/{kern.name}); bytes "
              f"via automata/ana-music mirror, Wayback-verified; see "
              f"docs/solo/INVENTORY.md")
    bundle = {"id": bid, "bwv": bwv, "set": setname, "work": work,
              "movement": movement, "movementNo": movementNo, "key": key,
              "kind": "solo", "source": source,
              "sourceFile": f"{setname}/{kern.name}",
              "mei": mei, "parts": parts, "events": []}
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
    ap.add_argument("--id", help="rebuild a single movement, e.g. bwv1007-4")
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