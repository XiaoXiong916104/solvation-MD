#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   source ~/venvs/gmx/bin/activate
#   source ~/gromacs-2026.2-install/bin/GMXRC
#   cd "/mnt/c/Users/xiong/Desktop/solvation MD/MD simulation/GROMACS_reproduction_water_Zn_OTF_5nm_20260625/01_gromacs"
#   bash run_gromacs_pipeline.sh test
#   bash run_gromacs_pipeline.sh full

mode="${1:-test}"
threads="${GMX_THREADS:-8}"

if ! command -v gmx >/dev/null 2>&1; then
    echo "ERROR: gmx not found. Run: source ~/gromacs-2026.2-install/bin/GMXRC" >&2
    exit 1
fi

run_mdrun() {
    local name="$1"
    gmx mdrun -v -deffnm "$name" -pin off -ntmpi 1 -ntomp "$threads"
}

echo "== Minimization =="
gmx grompp -f minimization.mdp -c initial_water_Zn_OTF_5nm.gro -r initial_water_Zn_OTF_5nm.gro -o minimization.tpr -p topol.top -maxwarn 3
run_mdrun minimization

echo "== Equilibration, 1 ns =="
gmx grompp -f equilibration_1ns.mdp -c minimization.gro -r minimization.gro -o equilibration.tpr -p topol.top -maxwarn 3
run_mdrun equilibration

if [[ "$mode" == "test" ]]; then
    echo "== Production smoke test, 100 ps =="
    gmx grompp -f production_100ps_test.mdp -c equilibration.gro -r equilibration.gro -t equilibration.cpt -o production_test.tpr -p topol.top -maxwarn 3
    gmx mdrun -v -deffnm production_test -s production_test.tpr -pin off -ntmpi 1 -ntomp "$threads"
    echo "Done: test pipeline finished. For full 60 ns run: bash run_gromacs_pipeline.sh full"
elif [[ "$mode" == "full" ]]; then
    echo "== Production, 60 ns =="
    gmx grompp -f production_60ns.mdp -c equilibration.gro -r equilibration.gro -t equilibration.cpt -o production.tpr -p topol.top -maxwarn 3
    run_mdrun production
    echo "Done: full production finished."
else
    echo "ERROR: mode must be 'test' or 'full'." >&2
    exit 2
fi
