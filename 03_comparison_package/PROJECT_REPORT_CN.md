# Zn-OTF water solvation MD project report

## 1. Objective

This project compares two molecular dynamics workflows for an aqueous zinc triflate system: a GROMACS reference workflow and a LAMMPS reproduction workflow. The goal is to check whether the LAMMPS model can reproduce the same system scale and provide a usable visualization/report package.

## 2. Package organization

The repository is split into three packages:

- `01_LAMMPS_package`: LAMMPS inputs, run scripts, final outputs, and LAMMPS-only visualization files.
- `02_GROMACS_package`: original GROMACS workflow, Packmol setup, topology/force-field files, MDP files, scripts, and the 100 ps reference result.
- `03_comparison_package`: comparison report and matched VMD visualization scripts.

## 3. System composition

Both workflows describe the same 3438-atom system:

- 1044 SPC/E water molecules, 3132 water atoms.
- 18 Zn2+ ions.
- 36 OTF/BFAF anions, 288 anion atoms.
- Net charge is neutral.

The corrected LAMMPS VMD conversion uses the LAMMPS atom type mapping from the final data file: type 1 water oxygen, type 2 water hydrogen, type 3 zinc, type 4 fluorine, type 5 carbon, type 6 sulfur, and type 7 oxygen in OTF/BFAF.

## 4. GROMACS original workflow

The GROMACS workflow is stored in `02_GROMACS_package`.

1. Initial packing was prepared with Packmol in `00_packmol`.
   - Packmol coordinates use Angstrom.
   - The intended starting box was 50 A, equal to 5.0 nm.
   - Water, Zn, and OTF coordinate templates were packed into one initial structure.

2. GROMACS preparation and simulation files are stored in `01_gromacs_workflow`.
   - `topol.top` defines the molecule types and counts.
   - `gromos54a7.ff` provides the force-field files.
   - `toppar/OTF.itp` provides the OTF/triflate parameters.
   - `minimization.mdp` defines energy minimization.
   - `equilibration_1ns.mdp` defines equilibration.
   - `production_100ps_test.mdp` defines the 100 ps test production.
   - `production_60ns.mdp` is the planned full production setting.

3. The run sequence is minimization -> equilibration -> production test.
   - Minimization removes bad contacts.
   - Equilibration lets the density and box relax under temperature/pressure coupling.
   - The 100 ps production test checks whether the workflow runs stably and produces a trajectory.

4. The selected GROMACS result is stored in `03_results/production_test_100ps`.
   - `production_test.gro`: final structure.
   - `production_test.xtc`: compressed trajectory.
   - `production_test.tpr`: topology-aware input file.
   - `production_test.log`: run log and performance/statistics.

From the GROMACS log, the 100 ps test used a 0.001 ps timestep and 100000 steps. The average temperature was 299.823 K, the average pressure was -17.8026 bar, and the reported performance was 32.886 ns/day. The final `production_test.gro` box length was 3.30179 nm.

## 5. LAMMPS workflow

The LAMMPS workflow is stored in `01_LAMMPS_package`.

1. GROMACS/Packmol-style input information was converted into LAMMPS data and parameter files.
2. The initial structure was minimized.
3. A stable 26 ps restart structure was used to avoid overly fast compression from the raw starting box.
4. NVT stabilization was run for 20000 steps with a 0.5 fs timestep.
5. Slow NPT equilibration was run for 200000 steps with a 0.5 fs timestep.
6. Python was used to extract thermodynamic data and convert trajectory information for VMD.

The final LAMMPS NPT stage reached step 200000 successfully. The NVT and NPT exit codes were both 0. The final NPT stage took about 4 h 54 min, and the safe pipeline including NVT took about 5 h 10 min.

## 6. LAMMPS final result

Final LAMMPS thermo row at step 200000:

- Temperature: 303.39 K.
- Pressure: 244.19 atm.
- Density: 1.1728 g/cm3.
- Volume: 35893.8 A^3.
- Final cubic box length: about 32.9868 A, equal to 3.29868 nm.
- NPT trajectory frames: 101.

The last pressure value is instantaneous. In a small ionic/water box, pressure fluctuates strongly, so density, temperature, volume trend, stable trajectory completion, and absence of dangerous neighbor builds are more meaningful for this short validation.

## 7. LAMMPS and GROMACS comparison

The two workflows are consistent in system composition and final box scale. The GROMACS final box length is 3.30179 nm, and the LAMMPS final box length is about 3.29868 nm. The difference is about 0.00311 nm, or about 0.031 A, which is very small for this short reproduction test.

Important differences:

- GROMACS stores topology-aware files such as `tpr`, `gro`, and `xtc`; VMD can use these to display residues, molecules, and bonds more naturally.
- LAMMPS dump files mainly store atom coordinates, types, charges, and box information; they do not automatically carry all bond/topology/residue information into VMD.
- Therefore, the LAMMPS result needed an extra visualization conversion step. The corrected VMD file uses GRO format and the correct LAMMPS atom type mapping, especially type 3 = Zn.
- GROMACS used a 1 fs timestep for the 100 ps reference test, while the LAMMPS safe workflow used a 0.5 fs timestep.
- GROMACS was faster in this test because it used optimized PME kernels and 8 OpenMP threads. The recorded LAMMPS final run used 1 MPI task x 1 OpenMP thread.

## 8. Visualization

Recommended VMD scripts are stored in `03_comparison_package/visualization`.

LAMMPS final view:

```tcl
source "<repository>/03_comparison_package/visualization/view_lammps_gromacs_style_wrapped.tcl"
```

GROMACS 100 ps reference view:

```tcl
source "<repository>/03_comparison_package/visualization/view_gromacs_100ps.tcl"
```

Matched comparison view:

```tcl
source "<repository>/03_comparison_package/visualization/view_compare_gromacs_lammps.tcl"
```

## 9. Conclusion

The LAMMPS model was built and run successfully. Compared with the GROMACS 100 ps reference, it has the same atom count and a very similar final box size. The main difference is not the physical system itself but the software output format: GROMACS output carries topology into VMD more directly, while LAMMPS output requires conversion and careful atom type mapping before VMD can show the same type of molecular representation.