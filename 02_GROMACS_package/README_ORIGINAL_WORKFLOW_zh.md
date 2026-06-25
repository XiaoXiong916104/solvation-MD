# GROMACS reproduction: water + Zn + OTF, 5 nm box

This folder is a cleaned-up reproduction of the original `sol_mix_1` GROMACS project.

## What this system is

- Water: `SOL`, 1044 molecules
- Zinc ions: `ZN`, 18 ions
- OTF/triflate anions: topology name `BFAF`, 36 molecules
- Box: `5.0 x 5.0 x 5.0 nm`
- Force field: copied from the original project, `gromos54a7.ff`
- OTF parameters: copied from the original ATB topology, `toppar/OTF.itp`

Important unit rule:

- Packmol uses Angstrom.
- GROMACS uses nm.
- `50 A = 5.0 nm`.

The original project had a `50 50 50` GRO box in some places, which GROMACS reads as 50 nm and makes PME extremely slow. This cleaned folder uses `5.00000 5.00000 5.00000` nm.

## Folder map

- `00_packmol/`: files for rebuilding the initial PDB box with Packmol.
- `01_gromacs/`: all files needed to run GROMACS.
- `02_analysis/`: first analysis scripts.
- `results/`: place to copy selected final outputs.

## How to run GROMACS

Open Ubuntu/WSL:

```bash
source ~/venvs/gmx/bin/activate
source ~/gromacs-2026.2-install/bin/GMXRC
cd "/mnt/c/Users/xiong/Desktop/solvation MD/MD simulation/GROMACS_reproduction_water_Zn_OTF_5nm_20260625/01_gromacs"
```

First run a short test pipeline:

```bash
bash run_gromacs_pipeline.sh test
```

If minimization, 1 ns equilibration, and 100 ps production test all finish without `Fatal error`, `nan`, or serious `LINCS WARNING`, run the full production:

```bash
bash run_gromacs_pipeline.sh full
```

The full production is 60 ns and can take a long time on CPU-only GROMACS.

## Manual commands

Minimization:

```bash
gmx grompp -f minimization.mdp -c initial_water_Zn_OTF_5nm.gro -r initial_water_Zn_OTF_5nm.gro -o minimization.tpr -p topol.top -maxwarn 3
gmx mdrun -v -deffnm minimization -pin off -ntmpi 1 -ntomp 8
```

Equilibration:

```bash
gmx grompp -f equilibration_1ns.mdp -c minimization.gro -r minimization.gro -o equilibration.tpr -p topol.top -maxwarn 3
gmx mdrun -v -deffnm equilibration -pin off -ntmpi 1 -ntomp 8
```

Production test:

```bash
gmx grompp -f production_100ps_test.mdp -c equilibration.gro -r equilibration.gro -t equilibration.cpt -o production_test.tpr -p topol.top -maxwarn 3
gmx mdrun -v -deffnm production_test -s production_test.tpr -pin off -ntmpi 1 -ntomp 8
```

Full production:

```bash
gmx grompp -f production_60ns.mdp -c equilibration.gro -r equilibration.gro -t equilibration.cpt -o production.tpr -p topol.top -maxwarn 3
gmx mdrun -v -deffnm production -pin off -ntmpi 1 -ntomp 8
```

## Rebuilding the initial structure with Packmol

Windows PowerShell:

```powershell
cd "C:\Users\xiong\Desktop\solvation MD\MD simulation\GROMACS_reproduction_water_Zn_OTF_5nm_20260625\00_packmol"
.\run_packmol_windows.ps1
```

Then convert to GRO in Ubuntu/WSL:

```bash
cd "/mnt/c/Users/xiong/Desktop/solvation MD/MD simulation/GROMACS_reproduction_water_Zn_OTF_5nm_20260625/01_gromacs"
gmx editconf -f ../00_packmol/water_Zn_OTF_5nm.pdb -o initial_water_Zn_OTF_5nm.gro -box 5.0 5.0 5.0
```

## Notes

- `topol.top` is intentionally short: it only includes the molecules actually present in this reproduction.
- The original unused DMSO, EA, ACN, and DMC includes were removed from the clean topology.
- GROMACS warnings about the Berendsen thermostat and GROMOS force fields are expected for this legacy-style reproduction. Do not ignore fatal errors.
