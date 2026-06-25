# LAMMPS package

This package contains the LAMMPS reproduction of the water/Zn/OTF solvation system.

## Folder logic

- `01_input_files`: LAMMPS data files and pair coefficients.
- `02_run_scripts`: LAMMPS input scripts plus Python/PowerShell launch scripts.
- `03_output_files/final_200k`: final NVT/NPT outputs and logs.
- `04_visualization`: LAMMPS-only XYZ visualization files.
- `05_report_assets`: LAMMPS summary, thermo table, and thermo plot.
- `06_notes`: Chinese reading guide for the LAMMPS scripts and files.

## Final LAMMPS result

- System: 1044 waters + 18 Zn2+ + 36 OTF/BFAF anions, 3438 atoms total.
- Final NPT step: 200000.
- Final temperature: 303.39 K.
- Final pressure: 244.19 atm, instantaneous value from the last thermo line.
- Final density: 1.1728 g/cm3.
- Final cubic box length: about 32.9868 A.

## Running method

The workflow used a stable 26 ps restart structure, then:

1. NVT stabilization with `in.safe_nvt_26ps`.
2. Slow NPT equilibration with `in.safe_npt_26ps`.
3. Python extraction/conversion for thermo and VMD outputs.

The Python API example is in `02_run_scripts/run_lammps_api.py`.