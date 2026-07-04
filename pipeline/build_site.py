#!/usr/bin/env python3
"""
build_site.py -- package built chorales (build/NNN/) into the published
site data: chorales/NNN.json.gz (game_data + the three spacing SVGs, gzipped
for the repo; the app decompresses with DecompressionStream) and
chorales/index.json (picker manifest).

Chorales are included per the Milestone 1 triage: build ok AND >=60%
pitch-verified (see reports/milestone1.md).

Usage:
    python build_site.py [--build build] [--out chorales] [--min-verified 60]
"""
import argparse, gzip, json
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", type=Path, default=Path("build"))
    ap.add_argument("--out", type=Path, default=Path("chorales"))
    ap.add_argument("--min-verified", type=float, default=60.0)
    a = ap.parse_args()

    report = json.loads((a.build / "report.json").read_text())
    a.out.mkdir(exist_ok=True)
    manifest, skipped = [], []
    for r in report["chorales"]:
        if r["status"] != "ok" or r["pct_verified"] < a.min_verified:
            skipped.append(r["riem"])
            continue
        d = a.build / f"{r['riem']:03d}"
        data = json.loads((d / "game_data.json").read_text())
        data["svgs"] = [(d / f"sys{i}.svg").read_text() for i in range(3)]
        blob = gzip.compress(json.dumps(data).encode(), 9)
        (a.out / f"{r['riem']:03d}.json.gz").write_bytes(blob)
        manifest.append({"riem": r["riem"], "title": data["title"],
                         "events": r["events"], "phrases": r["phrases"]})
    (a.out / "index.json").write_text(json.dumps(manifest))
    total = sum(f.stat().st_size for f in a.out.glob("*.json.gz"))
    print(f"{len(manifest)} chorales -> {a.out}/ "
          f"({total // (1 << 20)} MB gzipped), skipped {len(skipped)}: "
          f"{skipped}")


if __name__ == "__main__":
    main()
