# VMD visualization files

This folder contains the cleaned visualization files used for the report comparison.

## Recommended files

- `lammps_final_200k_gromacs_style_wrapped.gro`: corrected LAMMPS final frame for VMD. Atom type mapping was corrected from the LAMMPS data file: type 3 is Zn.
- `view_lammps_gromacs_style_wrapped.tcl`: VMD script for the corrected LAMMPS final frame.
- `view_gromacs_100ps.tcl`: VMD script for the GROMACS 100 ps reference trajectory stored in `02_GROMACS_package/03_results/production_test_100ps`.
- `view_compare_gromacs_lammps.tcl`: loads both systems into VMD for manual comparison.

## How to open

Open VMD, then in `Extensions -> Tk Console` run one of these:

```tcl
source "<repository>/03_comparison_package/visualization/view_lammps_gromacs_style_wrapped.tcl"
```

```tcl
source "<repository>/03_comparison_package/visualization/view_gromacs_100ps.tcl"
```

The display uses black background, white PBC box, water as lines, Zn as cyan VDW spheres, OTF/BFAF as licorice, and the Zn solvation shell as thicker licorice.

## Important note

The early PDB trial files were removed because VMD can misread 4-character residue names such as `BFAF` and can guess incorrect bonds when topology is absent. The corrected report view uses GRO format instead.