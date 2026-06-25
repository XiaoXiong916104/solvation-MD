# LAMMPS Solvation MD Submission Package

This repository contains a cleaned LAMMPS reproduction package for a zinc triflate aqueous solvation model, plus a compact GROMACS 100 ps reference used for comparison.

GitHub repository: https://github.com/XiaoXiong916104/solvation-MD

## Project summary

System composition:

- 1044 SPC/E water molecules
- 18 Zn2+ ions
- 36 OTF/BFAF anions
- 3438 atoms total
- Net charge: 0

Final LAMMPS result:

- Final NPT trajectory step: 200000
- Saved NPT frames: 101
- Final temperature: 303.39 K
- Final pressure: 244.19 atm
- Final density: 1.1728 g/cm3
- Final volume: 35893.8 A^3
- Final cubic box length: about 32.9868 A / 3.29868 nm

GROMACS reference:

- 100 ps production test
- 101 trajectory frames
- Final `production_test.gro` box: 3.30179 x 3.30179 x 3.30179 nm
- Average temperature from log: 299.823 K
- Average pressure from log: -17.8026 bar

## Folder structure

### 01_input_files

LAMMPS input data and parameter files:

- `solvent_mix_1.data`: initial converted LAMMPS data file
- `solvent_mix_1.minimized.data`: minimized structure
- `solvent_mix_1_26ps.data`: stable 26 ps restart structure
- `pair_coeffs.in`: Lennard-Jones pair coefficients converted from GROMACS/ATB parameters

### 02_run_scripts

Scripts for reproducing and understanding the LAMMPS workflow:

- `in.minimize`: energy minimization input
- `in.safe_nvt_26ps`: NVT stabilization input
- `in.safe_npt_26ps`: final slow NPT input
- `convert_gromacs_to_lammps.py`: conversion script
- `run_lammps_from_python.py`: launches LAMMPS from Python with `subprocess`
- `run_lammps_api.py`: controls LAMMPS through the LAMMPS Python API
- `run_safe_pipeline.ps1`: PowerShell NVT -> NPT runner

### 03_output_files/final_200k

Main LAMMPS result folder:

- `safe_npt_26ps.lammpstrj`: final NPT trajectory
- `safe_npt_26ps.log`: final NPT log
- `safe_nvt_26ps.lammpstrj`: NVT stabilization trajectory
- `safe_nvt_26ps.log`: NVT stabilization log
- `solvent_mix_1_26ps_npt_100ps.data`: final LAMMPS structure
- `thermo_final_200k.csv`: extracted final NPT thermodynamic table
- `thermo_final_200k.png`: temperature/density/energy plot
- `FINAL_STATUS.txt`: concise final status summary

### 04_visualization

VMD visualization files.

Recommended corrected LAMMPS view:

```tcl
source "<repository>/04_visualization/gromacs_matched_view/view_lammps_gromacs_style_wrapped.tcl"
```

Recommended GROMACS reference view:

```tcl
source "<repository>/04_visualization/gromacs_matched_view/view_gromacs_100ps.tcl"
```

Important file:

- `04_visualization/gromacs_matched_view/lammps_final_200k_gromacs_style_wrapped.gro`: corrected LAMMPS final-frame VMD file. This fixes the earlier visualization issue by using the correct LAMMPS atom type mapping, especially type 3 = Zn.

### 05_report_assets

Report-ready summary files:

- `PROJECT_REPORT_CN.md`: Chinese project report comparing LAMMPS and GROMACS
- `FINAL_SUMMARY.txt`: concise final LAMMPS summary
- `thermo_final_200k.csv`: final thermodynamic table
- `thermo_final_200k.png`: final thermodynamic plot
- `final_frame_step_200000.xyz`: final snapshot

### 06_notes

Reading and file organization notes:

- `FILE_GUIDE.txt`
- `LAMMPS_READING_GUIDE_CN.md`

### 07_gromacs_reference

Compact GROMACS reference files used for comparison:

- `production_test_100ps/production_test.gro`
- `production_test_100ps/production_test.xtc`
- `production_test_100ps/production_test.tpr`
- `production_test_100ps/production_test.log`
- `README_GROMACS_REFERENCE_CN.md`

## How to reproduce the final LAMMPS run

The final workflow uses the stable 26 ps restart structure, then NVT and slow NPT:

```powershell
cd "<repository>\01_input_files"
```

Copy or reference the scripts from `02_run_scripts`, then run NVT followed by NPT with the installed LAMMPS executable. The Python API runner in `02_run_scripts/run_lammps_api.py` shows how to control LAMMPS directly from Python.

## Notes for grading/reporting

The LAMMPS run completed successfully. The final LAMMPS box length is very close to the GROMACS final box length. Pressure differs between instantaneous values and averages because pressure fluctuates strongly in a small ionic system. The most important practical difference is file format: GROMACS carries topology into VMD more naturally, while LAMMPS requires explicit conversion for clean visualization.