# Comparison package

This package contains the report and the matched VMD visualization files for comparing the LAMMPS result and the GROMACS reference.

## Files

- `PROJECT_REPORT_CN.md`: Chinese project report.
- `visualization/lammps_final_200k_gromacs_style_wrapped.gro`: corrected LAMMPS final-frame file for VMD.
- `visualization/view_lammps_gromacs_style_wrapped.tcl`: LAMMPS VMD view.
- `visualization/view_gromacs_100ps.tcl`: GROMACS VMD view.
- `visualization/view_compare_gromacs_lammps.tcl`: loads both systems in VMD.

## VMD usage

Open VMD, then run one of these in `Extensions -> Tk Console`:

```tcl
source "<repository>/03_comparison_package/visualization/view_lammps_gromacs_style_wrapped.tcl"
```

```tcl
source "<repository>/03_comparison_package/visualization/view_gromacs_100ps.tcl"
```

```tcl
source "<repository>/03_comparison_package/visualization/view_compare_gromacs_lammps.tcl"
```

## Main interpretation

The LAMMPS and GROMACS simulations have the same atom count and very similar final box size. GROMACS is easier to visualize directly in VMD because `tpr/gro/xtc` files preserve topology and residue information more naturally. LAMMPS trajectory dumps mostly provide coordinates, so bond display requires conversion plus correct atom/residue mapping.