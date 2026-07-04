#!/usr/bin/env python3
"""
build_app.py -- inject a built chorale (build/NNN/) into app/ui_template.html,
producing a self-contained playable HTML file.

Usage:
    python build_app.py <build_dir> [--template app/ui_template.html]
                        [--out app/chorale_analysis.html]
"""
import argparse, json
from pathlib import Path


def build_app(build_dir: Path, template: Path, out: Path):
    html = template.read_text()
    data = json.loads((build_dir / "game_data.json").read_text())
    title = f"Chorale Analysis — Riemenschneider {data['riemenschneider']}"
    html = html.replace("__TITLE__", title)
    for i in range(3):
        html = html.replace(f"__SVG{i}__", (build_dir / f"sys{i}.svg").read_text())
    html = html.replace("__DATA__", json.dumps(data))
    assert "__SVG" not in html and "__DATA__" not in html and "__TITLE__" not in html
    out.write_text(html)
    print(f"{out} ({out.stat().st_size // 1024} KB) <- {build_dir}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("build_dir", type=Path)
    ap.add_argument("--template", type=Path, default=Path("app/ui_template.html"))
    ap.add_argument("--out", type=Path, default=Path("app/chorale_analysis.html"))
    a = ap.parse_args()
    build_app(a.build_dir, a.template, a.out)
