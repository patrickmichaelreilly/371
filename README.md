# 371 — Chorale Analysis Game

A mobile game presenting Bach chorales (Riemenschneider 371) one phrase at a
time; the puzzle is Roman-numeral functional analysis entered below the staff.

**Live prototype:** https://patrickmichaelreilly.github.io/371/
(Riemenschneider 1 / BWV 269, hosted on GitHub Pages)

Read `SPEC.md` first — it is the canonical spec and pitfall ledger.

## Building

```sh
python3 -m venv .venv
.venv/bin/pip install music21 verovio

git clone --filter=blob:none --sparse https://github.com/MarkGotham/When-in-Rome.git
cd When-in-Rome && git sparse-checkout set "Corpus/Early_Choral/Bach,_Johann_Sebastian/Chorales" && cd ..

# one chorale
.venv/bin/python pipeline/build_chorale.py 1 --wir When-in-Rome

# full corpus + verification report (Milestone 1)
PYTHONPATH=pipeline .venv/bin/python pipeline/build_corpus.py --jobs 8
# -> build/report.md, build/report.json, build/NNN/{game_data.json,alternatives.json,sys*.svg}

# package the site data (gzipped MusicXML+data bundles + picker manifest)
.venv/bin/python pipeline/build_site.py
# -> chorales/NNN.json.gz, chorales/index.json (committed; served by Pages)
# the app renders client-side with vendor/verovio-toolkit-wasm.js (npm 6.2.0;
# keep in lockstep with the pip verovio used by the pipeline)

# local dev server (the app fetches chorales/ at runtime)
python3 -m http.server 8000   # then open http://localhost:8000/
```

## Attribution

Analyses from [When in Rome](https://github.com/MarkGotham/When-in-Rome)
(Gotham et al.), CC BY-SA 4.0. Scores from the music21 corpus.
