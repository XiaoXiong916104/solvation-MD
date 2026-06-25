# GROMACS package

This package contains the original GROMACS reference workflow and the compact 100 ps result used for comparison with LAMMPS.

## System

- Water: `SOL`, 1044 molecules.
- Zinc ions: `ZN`, 18 ions.
- Triflate/OTF anions: topology residue name `BFAF`, 36 molecules.
- Total atoms: 3438.
- Starting box target: 5.0 x 5.0 x 5.0 nm.
- Force field: `gromos54a7.ff` plus OTF parameters in `toppar/OTF.itp`.

## Original workflow logic

1. `00_packmol`: build the initial water/Zn/OTF coordinates.
   - Packmol uses Angstrom.
   - The intended initial box is 50 A, equal to 5.0 nm in GROMACS.
   - `water_Zn_OTF_5nm.inp` defines the packing numbers and box.

2. `01_gromacs_workflow`: prepare and run GROMACS.
   - `topol.top` includes the force field and the molecular counts.
   - `minimization.mdp` prepares energy minimization.
   - `equilibration_1ns.mdp` prepares NPT equilibration.
   - `production_100ps_test.mdp` prepares the short 100 ps production test.
   - `production_60ns.mdp` is the planned full production setting.
   - `run_gromacs_pipeline.sh` runs the workflow in order.

3. `02_analysis`: first analysis script.
   - `analyze_rdf.sh` is prepared for RDF-style analysis.

4. `03_results/production_test_100ps`: selected final 100 ps output.
   - `production_test.gro`: final structure.
   - `production_test.xtc`: compressed trajectory.
   - `production_test.tpr`: topology-aware run input.
   - `production_test.log`: production log.

## Manual run sequence

Energy minimization:

```bash
gmx grompp -f minimization.mdp -c initial_water_Zn_OTF_5nm.gro -r initial_water_Zn_OTF_5nm.gro -o minimization.tpr -p topol.top -maxwarn 3
gmx mdrun -v -deffnm minimization -pin off -ntmpi 1 -ntomp 8
```

Equilibration:

```bash
gmx grompp -f equilibration_1ns.mdp -c minimization.gro -r minimization.gro -o equilibration.tpr -p topol.top -maxwarn 3
gmx mdrun -v -deffnm equilibration -pin off -ntmpi 1 -ntomp 8
```

100 ps production test:

```bash
gmx grompp -f production_100ps_test.mdp -c equilibration.gro -r equilibration.gro -t equilibration.cpt -o production_test.tpr -p topol.top -maxwarn 3
gmx mdrun -v -deffnm production_test -s production_test.tpr -pin off -ntmpi 1 -ntomp 8
```

## 100 ps result summary

From `production_test.log`:

- Timestep: 0.001 ps.
- Steps: 100000.
- Simulated time: 100 ps.
- Thermostat: Nose-Hoover at 300 K.
- Barostat: Parrinello-Rahman, isotropic, 1 bar.
- Long-range electrostatics: PME.
- Average temperature: 299.823 K.
- Average pressure: -17.8026 bar.
- Performance: 32.886 ns/day.

The final `production_test.gro` box is 3.30179 x 3.30179 x 3.30179 nm.