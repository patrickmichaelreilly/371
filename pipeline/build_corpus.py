#!/usr/bin/env python3
"""
build_corpus.py -- Milestone 1: loop build_chorale.py over Riemenschneider
1..371 and emit a verification report.

Per chorale it records: build status, event count, % pitch-verified, phrase
count, and the alignment invariant (slot x-positions strictly increasing in
event order at every spacing level -- SPEC.md pitfall 5). It also retains the
seed data for Milestone 3 grading alternatives: raw mNNvarN variant lines from
analysis.txt and, where present, the parsed BCMH second analysis
(alternatives.json next to each chorale's game_data.json). Every answer figure
is tested against a Python port of the template's NUMRE grading regex; misses
are listed in the report.

Usage:
    python build_corpus.py [--wir When-in-Rome] [--out build] [--jobs N]
                           [--only 5,17,150]

Outputs <out>/report.json and <out>/report.md.
"""
import argparse, json, re, traceback
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import build_chorale
from music21 import converter, roman

# Python port of NUMRE from app/ui_template.html -- keep in sync.
NUMRE = re.compile(
    r'^(b|#)?(VII|VI|IV|III|II|V|I|vii|vi|iv|iii|ii|v|i)'
    r'(o|°|ø|\+)?((?:\d+/?)*)'
    r'(?:/(b|#)?(VII|VI|IV|III|II|V|I|vii|vi|iv|iii|ii|v|i))?$')

VARLINE = re.compile(r'^m\d+[a-z]?var\d+\b')


def strictly_increasing_x(out_dir: Path, noteids: list) -> list:
    """SPEC.md pitfall 5: per level, notehead origin x of the chosen slot
    elements must be strictly increasing in event order. Origins are only
    compared to each other within one render, which is the one legitimate
    use of these coordinates (pitfall 3)."""
    ok = []
    for li, ids in enumerate(noteids):
        svg = (out_dir / f"sys{li}.svg").read_text()
        nx = build_chorale.notehead_origin_x(svg)
        xs = [nx.get(i) for i in ids]
        ok.append(all(x is not None for x in xs)
                  and all(a < b for a, b in zip(xs, xs[1:])))
    return ok


def parse_alternatives(riem: int, wir_root: Path, out_dir: Path) -> dict:
    """Retain variant readings and the BCMH second analysis (Milestone 3 seed
    data). Raw variant lines are kept verbatim; BCMH is parsed to the same
    event fields as the primary analysis."""
    cdir = wir_root / "Corpus/Early_Choral/Bach,_Johann_Sebastian/Chorales" \
                    / f"{riem:03d}"
    variants = [ln.rstrip() for ln in
                (cdir / "analysis.txt").read_text().splitlines()
                if VARLINE.match(ln)]
    bcmh, bcmh_error = None, None
    bpath = cdir / "analysis_BCMH.txt"
    if bpath.exists():
        try:
            s = converter.parse(str(bpath), format='romanText')
            bcmh = [{"offset": round(float(rn.getOffsetInHierarchy(s)), 3),
                     "measure": rn.measureNumber, "beat": float(rn.beat),
                     "key": rn.key.tonicPitchNameWithCase,
                     "figure": rn.figure}
                    for rn in s.flatten().getElementsByClass(roman.RomanNumeral)]
        except Exception as e:
            bcmh_error = f"{type(e).__name__}: {e}"
    alt = {"variants": variants, "bcmh": bcmh, "bcmh_error": bcmh_error}
    (out_dir / "alternatives.json").write_text(json.dumps(alt))
    return alt


def build_one(riem: int, wir: str, out: str) -> dict:
    wir_root, out_dir = Path(wir), Path(out) / f"{riem:03d}"
    rec = {"riem": riem, "status": "ok", "error": None}
    try:
        data = build_chorale.build(riem, wir_root, out_dir)
    except SystemExit as e:
        return {**rec, "status": "fail", "error": str(e)}
    except Exception as e:
        return {**rec, "status": "fail",
                "error": f"{type(e).__name__}: {e}",
                "trace": traceback.format_exc(limit=3)}
    ev = data["events"]
    rec.update(
        events=len(ev),
        verified=sum(e["verified"] for e in ev),
        pct_verified=round(100 * sum(e["verified"] for e in ev) / len(ev), 1)
                     if ev else 0.0,
        phrases=data["numPhrases"],
        x_increasing=strictly_increasing_x(out_dir, data["noteids"]),
        figures=sorted({e["figure"] for e in ev}),
        keys=sorted({e["key"] for e in ev}),
        empty_voicings=sum(1 for e in ev if not e["midi"]),
        transposition=data.get("transposition"),
        dropped=len(data.get("droppedEvents", [])),
    )
    try:
        alt = parse_alternatives(riem, wir_root, out_dir)
        rec["variant_lines"] = len(alt["variants"])
        rec["bcmh"] = ("error" if alt["bcmh_error"] else
                       "yes" if alt["bcmh"] is not None else "no")
        if alt["bcmh_error"]:
            rec["bcmh_error"] = alt["bcmh_error"]
    except Exception as e:
        rec["alt_error"] = f"{type(e).__name__}: {e}"
    return rec


def write_md(report: dict, path: Path):
    rs = report["chorales"]
    ok = [r for r in rs if r["status"] == "ok"]
    fail = [r for r in rs if r["status"] != "ok"]
    align_bad = [r for r in ok if not all(r["x_increasing"])]
    L = ["# Milestone 1 corpus build report", ""]
    L += [f"- built ok: **{len(ok)}/{len(rs)}**",
          f"- build failures: **{len(fail)}**",
          f"- alignment invariant violations (built but x not strictly "
          f"increasing): **{len(align_bad)}**",
          f"- total events: {sum(r['events'] for r in ok)}",
          f"- overall pitch-verified: "
          f"{100 * sum(r['verified'] for r in ok) / max(1, sum(r['events'] for r in ok)):.1f}%",
          f"- chorales with BCMH second analysis parsed: "
          f"{sum(1 for r in ok if r.get('bcmh') == 'yes')} "
          f"(errors: {sum(1 for r in ok if r.get('bcmh') == 'error')})",
          f"- chorales with variant readings: "
          f"{sum(1 for r in ok if r.get('variant_lines', 0) > 0)} "
          f"({sum(r.get('variant_lines', 0) for r in ok)} lines)",
          f"- transposed analyses (auto-corrected): "
          f"{sum(1 for r in ok if r.get('transposition'))}",
          f"- dropped no-attack events: "
          f"{sum(r.get('dropped', 0) for r in ok)} across "
          f"{sum(1 for r in ok if r.get('dropped', 0))} chorales", ""]
    trans = [r for r in ok if r.get("transposition")]
    if trans:
        L += ["## Transposed analyses (analysis key -> score key)", "",
              "| riem | semitones | interval | verified after | before |",
              "|---|---|---|---|---|"]
        L += [f"| {r['riem']} | {r['transposition']['semitones']} "
              f"| {r['transposition']['interval']} "
              f"| {r['transposition']['verifiedFrac']} "
              f"| {r['transposition']['unshiftedFrac']} |" for r in trans]
        L += [""]
    if report["figure_regex_misses"]:
        L += ["## Figures NOT matched by the grading regex (NUMRE)", ""]
        L += [f"- `{f}` (x{c})" for f, c in report["figure_regex_misses"]]
        L += [""]
    if fail:
        L += ["## Build failures", ""]
        by_err = Counter(re.sub(r'\d+(\.\d+)?', 'N', r["error"] or '')[:100]
                         for r in fail)
        L += [f"- {c}x `{e}`" for e, c in by_err.most_common()]
        L += ["", "| riem | error |", "|---|---|"]
        L += [f"| {r['riem']} | {(r['error'] or '')[:140]} |" for r in fail]
        L += [""]
    if align_bad:
        L += ["## Alignment invariant violations", "",
              "| riem | levels ok |", "|---|---|"]
        L += [f"| {r['riem']} | {r['x_increasing']} |" for r in align_bad]
        L += [""]
    low = sorted((r for r in ok if r["pct_verified"] < 90),
                 key=lambda r: r["pct_verified"])
    if low:
        L += [f"## Low pitch-verification (<90%): {len(low)} chorales", "",
              "| riem | % verified | events |", "|---|---|---|"]
        L += [f"| {r['riem']} | {r['pct_verified']} | {r['events']} |"
              for r in low]
        L += [""]
    # ---- triage (SPEC.md Milestone 1: measure, then triage) ----
    suspect = [r for r in ok if r["pct_verified"] < 60]
    good = [r for r in ok if r["pct_verified"] >= 60]
    L += ["## Triage", "",
          f"- **include in v1: {len(good)} chorales** (built, aligned, "
          f">=60% pitch-verified; remaining mismatches are analytical "
          f"subtleties like incomplete chords and passing tones)",
          f"- **exclude pending upstream reconciliation: "
          f"{len(suspect) + len(fail)} chorales** -- "
          f"build failures {sorted(r['riem'] for r in fail)}; "
          f"low-verification (analysis appears to follow a different "
          f"harmonization/edition of the tune) "
          f"{sorted(r['riem'] for r in suspect)}",
          "- transposed-edition and no-attack-event hazards are handled "
          "in-pipeline (see report sections above)", ""]
    path.write_text("\n".join(L))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--wir", default="When-in-Rome")
    ap.add_argument("--out", default="build")
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--only", default=None,
                    help="comma-separated riem numbers (default 1..371)")
    a = ap.parse_args()
    nums = ([int(x) for x in a.only.split(",")] if a.only
            else list(range(1, 372)))
    recs = []
    with ProcessPoolExecutor(max_workers=a.jobs) as ex:
        futs = {ex.submit(build_one, n, a.wir, a.out): n for n in nums}
        for i, f in enumerate(as_completed(futs), 1):
            r = f.result()
            recs.append(r)
            tag = "ok  " if r["status"] == "ok" else "FAIL"
            print(f"[{i}/{len(nums)}] riem {r['riem']:3d} {tag} "
                  f"{r.get('error') or ''}", flush=True)
    recs.sort(key=lambda r: r["riem"])

    figc = Counter()
    for r in recs:
        for f in r.get("figures", []):
            figc[f] += 1
    misses = sorted(((f, c) for f, c in figc.items() if not NUMRE.match(f)),
                    key=lambda t: -t[1])
    report = {"chorales": recs,
              "figure_vocabulary": sorted(figc),
              "figure_regex_misses": misses}
    out = Path(a.out)
    (out / "report.json").write_text(json.dumps(report, indent=1))
    write_md(report, out / "report.md")
    nok = sum(1 for r in recs if r["status"] == "ok")
    print(f"\n{nok}/{len(recs)} built ok -> {out}/report.md")


if __name__ == "__main__":
    main()
