#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
chmod +x ./packmol || true
./packmol < water_Zn_OTF_5nm.inp
echo "Packmol wrote water_Zn_OTF_5nm.pdb"
echo "Convert to GRO with:"
echo "  cd ../01_gromacs"
echo "  gmx editconf -f ../00_packmol/water_Zn_OTF_5nm.pdb -o initial_water_Zn_OTF_5nm.gro -box 5.0 5.0 5.0"
