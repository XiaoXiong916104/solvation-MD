# Solvation MD: LAMMPS, GROMACS, and Comparison Packages

This repository is organized into three independent packages for submission.

## 1. `01_LAMMPS_package`

LAMMPS reproduction package. It contains LAMMPS input files, Python/PowerShell run scripts, final NVT/NPT outputs, thermodynamic plots, and LAMMPS-only visualization files.

Main result:

- Final NPT step: 200000
- Final temperature: 303.39 K
- Final density: 1.1728 g/cm3
- Final cubic box length: about 32.9868 A / 3.29868 nm
- Final trajectory frames: 101

## 2. `02_GROMACS_package`

GROMACS reference package. It contains the original Packmol/GROMACS workflow logic, force-field/topology files, MDP files, scripts, selected minimization/equilibration files, and the 100 ps production-test result.

Important parts:

- `00_packmol`: initial molecular packing files.
- `01_gromacs_workflow`: MDP files, topology, force-field files, run scripts, and selected intermediate outputs.
- `02_analysis`: analysis script.
- `03_results/production_test_100ps`: compact GROMACS 100 ps output used for comparison.

## 3. `03_comparison_package`

Comparison and reporting package. It contains the Chinese report and VMD scripts for viewing LAMMPS and GROMACS in a matched visual style.

Recommended files:

- `PROJECT_REPORT_CN.md`: project report comparing LAMMPS and GROMACS.
- `visualization/view_lammps_gromacs_style_wrapped.tcl`: corrected LAMMPS VMD view.
- `visualization/view_gromacs_100ps.tcl`: GROMACS reference VMD view.
- `visualization/view_compare_gromacs_lammps.tcl`: load both for comparison.

## Short conclusion

The two workflows describe the same water/Zn/OTF system and give very similar final box sizes. The main practical difference is visualization/topology handling: GROMACS files such as TPR/GRO/XTC carry topology information more naturally into VMD, while LAMMPS dump files mainly store coordinates and require extra conversion/topology handling for clean bond display.