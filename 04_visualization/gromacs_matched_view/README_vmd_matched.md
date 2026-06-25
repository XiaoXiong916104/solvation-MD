# GROMACS/LAMMPS matched VMD visualization

This folder contains VMD2 visualization files prepared to compare the GROMACS 100 ps production test and the final LAMMPS 200k NPT result using a similar display style.

## Source trajectories

GROMACS:

- `../production_test_100ps/production_test.gro`
- `../production_test_100ps/production_test.xtc`

LAMMPS:

- `lammps_final_200k_vmd.pdb`
- converted from `LAMMPS_submission_package/03_output_files/final_200k/safe_npt_26ps.lammpstrj`

## VMD scripts

Open VMD2, then in Tk Console run one of these:

```tcl
source "C:/Users/xiong/Desktop/solvation MD/MD simulation/GROMACS_reproduction_water_Zn_OTF_5nm_20260625/results/production_test_100ps_vmd/view_gromacs_100ps.tcl"
```

```tcl
source "C:/Users/xiong/Desktop/solvation MD/MD simulation/GROMACS_reproduction_water_Zn_OTF_5nm_20260625/results/production_test_100ps_vmd/view_lammps_final_matched.tcl"
```

```tcl
source "C:/Users/xiong/Desktop/solvation MD/MD simulation/GROMACS_reproduction_water_Zn_OTF_5nm_20260625/results/production_test_100ps_vmd/view_compare_gromacs_lammps.tcl"
```

## Display style

- Water (`SOL`): transparent CPK
- Zn ions (`ZN`): large VDW spheres
- OTF/BFAF anions (`BFAF`): licorice
- Zn first-shell environment within 2.8 A: highlighted licorice

## Notes

The LAMMPS trajectory was converted to multi-model PDB instead of plain XYZ so that VMD selections such as `resname SOL`, `resname ZN`, and `resname BFAF` work correctly. This makes it easier to match the GROMACS visualization style.
