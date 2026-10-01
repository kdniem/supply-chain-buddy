#!/usr/bin/env bash
# Copies the fictional Brightvale fixture files into the run's empty workspace.
# Runs only with `claude plugin eval ... --scaffold`.
set -euo pipefail
SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/resources"
cp "$SRC"/demand_history.csv "$SRC"/item_master.csv .
