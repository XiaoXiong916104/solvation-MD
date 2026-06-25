# LAMMPS Solvation MD Submission Package

## 1. Project summary

This package contains the final LAMMPS molecular dynamics files for a zinc triflate aqueous solvation system.

System composition:

- 1044 SPC/E water molecules
- 18 Zn2+ ions
- 36 OTF/BFAF anions
- Net charge: 0

Final production/equilibration result:

- Final NPT trajectory step: 200000
- Number of saved NPT frames: 101
- Final temperature: 303.39 K
- Final pressure: 244.19 atm
- Final density: 1.1728 g/cm3
- Final volume: 35893.8 A^3

The pressure is not exactly 1 atm because instantaneous pressure fluctuates strongly in a small liquid simulation box. Density and temperature are more useful for judging equilibration over this short run.

## 2. Folder structure

### 01_input_files

Input and intermediate LAMMPS data files.

- `solvent_mix_1.data`: initial converted LAMMPS data file
- `solvent_mix_1.minimized.data`: minimized initial structure
- `solvent_mix_1_26ps.data`: stable 26 ps restart structure used for safer equilibration
- `pair_coeffs.in`: Lennard-Jones pair coefficients converted from GROMOS/ATB parameters

### 02_run_scripts

Scripts required to reproduce or understand the workflow.

- `in.minimize`: LAMMPS energy minimization input
- `in.safe_nvt_26ps`: NVT stabilization input
- `in.safe_npt_26ps`: final slow NPT input
- `convert_gromacs_to_lammps.py`: converts GROMACS/Packmol files to LAMMPS data/input files
- `run_lammps_from_python.py`: launches LAMMPS from Python using `subprocess`
- `run_lammps_api.py`: controls LAMMPS directly through the LAMMPS Python API
- `run_safe_pipeline.ps1`: PowerShell script used to run NVT followed by NPT

### 03_output_files/final_200k

Final LAMMPS output files. This is the main result folder.

- `safe_npt_26ps.lammpstrj`: final NPT LAMMPS trajectory
- `safe_npt_26ps.log`: final NPT LAMMPS log
- `safe_nvt_26ps.lammpstrj`: NVT stabilization trajectory
- `safe_nvt_26ps.log`: NVT stabilization log
- `solvent_mix_1_26ps_npt_100ps.data`: final structure after NPT
- `solvent_mix_1_26ps_nvt.data`: structure after NVT stabilization
- `thermo_final_200k.csv`: extracted final NPT thermodynamic data
- `thermo_final_200k.png`: temperature, density, and potential energy plots
- `FINAL_STATUS.txt`: concise final status summary

### 04_visualization

VMD2-compatible visualization files.

- `vmd_safe_npt_final_200k.xyz`: final trajectory converted from LAMMPS dump to XYZ for VMD2
- `final_frame_step_200000.xyz`: final frame only
- `view_final_200k.tcl`: VMD2 script for loading and displaying the final trajectory

To visualize in VMD2 Tk Console:

```tcl
source "C:/Users/xiong/Desktop/solvation MD/MD simulation/LAMMPS_submission_package/04_visualization/view_final_200k.tcl"
```

If loading manually, open:

```text
04_visualization/vmd_safe_npt_final_200k.xyz
```

Then change the representation from `Lines` to `VDW` or `CPK` if needed.

### 05_report_assets

Files prepared for report writing.

- `FINAL_SUMMARY.txt`: concise final simulation summary
- `thermo_final_200k.csv`: final thermodynamic table
- `thermo_final_200k.png`: final thermodynamic plot
- `final_frame_step_200000.xyz`: final structure snapshot

### 06_notes

Additional notes about file organization.

## 3. Simulation workflow

The overall workflow was:

1. Packmol/GROMACS coordinate and topology files were used as the starting model.
2. Python converted the GROMACS/ATB force-field information into LAMMPS data and input files.
3. LAMMPS energy minimization was performed.
4. Direct NPT equilibration from the initial low-density box compressed too quickly and was not used as the final workflow.
5. A stable 26 ps structure was selected as a safer restart point.
6. LAMMPS NVT stabilization was performed from this restart structure.
7. LAMMPS slow NPT equilibration was then performed to 200000 steps.
8. Python extracted thermodynamic data and converted the LAMMPS trajectory to XYZ for VMD2 visualization.

## 4. How to reproduce the final run

Open PowerShell and run:

```powershell
cd "C:\Users\xiong\Desktop\solvation MD\MD simulation\LAMMPS_submission_package\01_input_files"
```

The scripts are stored separately in `02_run_scripts`. For a clean rerun, copy the needed input files and run scripts into one working directory, then run:

```powershell
lmp -in in.safe_nvt_26ps -log safe_nvt_26ps.log
lmp -in in.safe_npt_26ps -log safe_npt_26ps.log
```

The LAMMPS executable used on this computer was:

```text
C:\Users\xiong\AppData\Local\LAMMPS 64-bit 22Jul2025 with Python\bin\lmp.exe
```

## 5. Role of Python and LAMMPS

LAMMPS performed the molecular dynamics calculation. Python was used for:

- converting model/topology information to LAMMPS format
- launching or controlling LAMMPS runs
- archiving output files
- extracting thermodynamic data from logs
- converting trajectories for VMD2 visualization

The molecular dynamics engine itself was LAMMPS.

## 6. Suggested report wording

Molecular dynamics simulations were performed using LAMMPS. Python scripts were used to convert the initial Packmol/GROMACS model to LAMMPS format, control simulation execution, archive output files, and post-process thermodynamic data. The final system contained 1044 water molecules, 18 Zn2+ ions, and 36 OTF/BFAF anions. After energy minimization, a stable intermediate structure was equilibrated using NVT followed by slow NPT. The final NPT run reached 200000 steps and produced a final density of 1.1728 g/cm3 at approximately 303 K. The trajectory was converted to XYZ format and visualized using VMD2.
