#!/usr/bin/env bash
# Rebuild every article figure (PNG + SVG) in ../
set -euo pipefail
cd "$(dirname "$0")"
scripts=(
  fig01_three_games.py
  fig02_rs.py
  fig03_signals.py
  fig04_toy.py
  fig05_schedules.py
  fig06_bonus_malus.py
  fig07_hirshleifer.py
  fig08_insurance_dag.py
  fig09_dsep.py
  fig10_parametric.py
  fig11_bailout.py
)
for s in "${scripts[@]}"; do
  echo "running $s"
  python3 "$s"
done
echo "done"
