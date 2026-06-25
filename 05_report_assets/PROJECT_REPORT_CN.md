# Zn-OTF water solvation MD project report

## 1. Objective

This project builds and tests a molecular dynamics model for an aqueous zinc triflate system. The target system contains water, Zn2+ ions, and OTF/BFAF anions. The main task was to reproduce the GROMACS-style solvation model in LAMMPS, run a stable short MD workflow, and prepare files that can be inspected in VMD.

## 2. System composition

Both the LAMMPS result and the GROMACS reference contain 3438 atoms:

- 1044 SPC/E water molecules, 3132 water atoms
- 18 Zn2+ ions
- 36 OTF/BFAF anions, 288 anion atoms
- Total charge is neutral

The corrected VMD file uses the LAMMPS atom type mapping from the final data file: type 1 water oxygen, type 2 water hydrogen, type 3 zinc, type 4 fluorine, type 5 carbon, type 6 sulfur, and type 7 oxygen in OTF/BFAF.

## 3. LAMMPS workflow

The LAMMPS workflow was organized as:

1. Convert the initial GROMACS/Packmol-style model into LAMMPS data and parameter files.
2. Minimize the initial structure.
3. Use a stable 26 ps restart structure to avoid overly fast compression from the raw starting box.
4. Run NVT stabilization for 20000 steps with a 0.5 fs timestep.
5. Run slow NPT equilibration for 200000 steps with a 0.5 fs timestep.
6. Export the final LAMMPS data file, trajectory, thermo table, plot, and VMD visualization files.

The final LAMMPS NPT stage reached step 200000 successfully. The NVT and NPT exit codes were both 0. The final LAMMPS stage ran from 07:21:34 to 12:16:00 on 2026-06-25, about 4 h 54 min. Including NVT, the safe pipeline took about 5 h 10 min.

## 4. LAMMPS final result

Main final outputs are stored in 3_output_files/final_200k.

Final LAMMPS thermo row at step 200000:

- Temperature: 303.39 K
- Pressure: 244.19 atm
- Density: 1.1728 g/cm3
- Volume: 35893.8 A^3
- Final cubic box length: about 32.9868 A, equal to 3.29868 nm
- NPT trajectory frames: 101

The instantaneous pressure is not expected to be exactly 1 atm in such a small ionic liquid/water box because pressure fluctuates strongly. Temperature, density, volume trend, and lack of dangerous neighbor builds are more useful indicators for this short validation run.

## 5. GROMACS reference result

The GROMACS 100 ps reference files are stored in 7_gromacs_reference/production_test_100ps.

From production_test.log:

- dt = 0.001 ps
- 
steps = 100000
- simulated time: 100 ps
- thermostat: Nose-Hoover, 300 K
- barostat: Parrinello-Rahman, isotropic, 1 bar
- long-range electrostatics: PME
- trajectory frames: 101
- average temperature: 299.823 K
- average pressure: -17.8026 bar
- reported performance: 32.886 ns/day

From the final production_test.gro, the final box is 3.30179 x 3.30179 x 3.30179 nm, close to the LAMMPS final box of 3.29868 nm.

## 6. LAMMPS and GROMACS comparison

The two simulations are consistent in system composition and final box scale. The final cubic box lengths differ by only about 0.00311 nm, roughly 0.031 A. This indicates that the LAMMPS workflow reproduced the overall density/box size of the GROMACS reference reasonably well for a short test.

Important differences:

- GROMACS stores topology-aware files such as 	pr, gro, and xtc, so VMD can often display molecules and bonds more cleanly.
- LAMMPS dump files mainly store atom coordinates, types, charges, and box information. They do not automatically carry all topology and residue naming information into VMD.
- Because of this, direct LAMMPS-to-VMD visualization can look wrong if VMD guesses bonds or if PDB formatting is used with 4-character residue names such as BFAF.
- The corrected LAMMPS VMD view therefore uses GRO format with explicit atom/residue names and molecule-wrapped coordinates.
- LAMMPS used a 0.5 fs timestep for the final safe workflow, while the GROMACS reference used 1 fs. LAMMPS therefore used more integration steps for a comparable physical time.
- Performance is not directly comparable because GROMACS used 8 OpenMP threads and optimized PME kernels, while the recorded LAMMPS final run used 1 MPI task x 1 OpenMP thread and was much slower.

## 7. Visualization method

The recommended LAMMPS visualization script is:

`	cl
source "<repository>/04_visualization/gromacs_matched_view/view_lammps_gromacs_style_wrapped.tcl"
`

The recommended GROMACS visualization script is:

`	cl
source "<repository>/04_visualization/gromacs_matched_view/view_gromacs_100ps.tcl"
`

The VMD representation is matched between the two systems as much as possible: water as lines, Zn as cyan VDW spheres, OTF/BFAF as licorice, and local Zn solvation shells as thicker licorice.

## 8. Conclusion

The LAMMPS model was built and run successfully. The final LAMMPS structure has the same atom count and very similar final cubic box length to the GROMACS 100 ps reference. The largest practical difference encountered was visualization: GROMACS files carry topology information more naturally into VMD, while LAMMPS output needs explicit conversion and careful atom type mapping. After correcting the Zn atom type and using GRO instead of PDB, the LAMMPS result can be visualized in a GROMACS-like way and is suitable for reporting as a short reproduction/validation run.
