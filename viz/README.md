# VLDB 2027 layout supplement

Figures, tables, and pseudocode only. Numbers on the plots are synthetic.

```bash
cd viz
python3 -m pytest tests -q
python3 -m pipeline.render_exp
python3 -m pipeline.render_mech
python3 -m pipeline.emit_tables
cd tex
TEXINPUTS=./vendor: BSTINPUTS=./vendor: pdflatex main.tex
bibtex main
TEXINPUTS=./vendor: BSTINPUTS=./vendor: pdflatex main.tex
TEXINPUTS=./vendor: BSTINPUTS=./vendor: pdflatex main.tex
```

`tex/vendor` is the unmodified PVLDB Vol. 20 template. Decision notes are in `doc/最终可视化决策.md`.
