#!/usr/bin/env bash
# Copies the fictional Brightvale fixture files into the run's empty workspace (needs --scaffold).
set -euo pipefail
SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/resources"
cp "$SRC"/*.csv .
