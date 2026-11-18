#!/bin/sh
# Rebuild the framework figure. Does not touch the PVLDB class or the paper.
set -eu
cd "$(dirname "$0")"
pdflatex -interaction=nonstopmode -halt-on-error algo1-framework.tex >/tmp/algo1-framework-build.log
python3 export_views.py
