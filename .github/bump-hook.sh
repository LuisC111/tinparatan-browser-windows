#!/bin/bash
# Runs from imputnet's bump-platform action after it checks out
# helium-chromium origin/main and refreshes patches, before it commits.
# origin is this fork (see .gitmodules), not imputnet/helium.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SCRIPT="$ROOT/helium-chromium/tinparatan/substitute_product_name.py"

if [[ ! -f "$SCRIPT" ]]; then
  echo "tinparatan/substitute_product_name.py is not on helium-chromium origin/main." >&2
  echo "Merge https://github.com/LuisC111/tinparatan-browser/pull/1 before bumping." >&2
  exit 1
fi
