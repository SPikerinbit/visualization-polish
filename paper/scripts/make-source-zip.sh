#!/bin/sh
set -eu
REPO="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="${1:-$REPO/../artifacts/paper-integration-sources.zip}"
mkdir -p "$(dirname "$OUT")"
cd "$REPO"
zip -qr "$OUT" \
  paper/build.sh \
  paper/build-local.sh \
  paper/scripts \
  paper/doc \
  paper/recovery/tables \
  paper/tex \
  doc/label-page-map.md \
  doc/最终可视化决策.md \
  doc/integration-pending-changelog.md \
  -x 'paper/tex/*.aux' 'paper/tex/*.log' 'paper/tex/*.out' \
  -x 'paper/tex/*.bbl' 'paper/tex/*.blg' 'paper/tex/*.fdb_latexmk' 'paper/tex/*.fls' \
  -x 'paper/recovery/tables/**/__pycache__/*' \
  -x 'paper/recovery/tables/.pytest_cache/*'
sha256sum "$OUT"
sha256sum paper/build.sh
echo "wrote $OUT"