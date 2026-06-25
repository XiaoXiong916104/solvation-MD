# GROMACS reference files

This folder stores the compact GROMACS 100 ps reference result used to compare against the LAMMPS reproduction.

Files:

- production_test.gro: final GROMACS structure, 3438 atoms, final box 3.30179 x 3.30179 x 3.30179 nm.
- production_test.xtc: compressed GROMACS trajectory, 101 frames.
- production_test.tpr: portable GROMACS run input, useful for topology-aware visualization.
- production_test.log: GROMACS run log.

Key log values:

- dt = 0.001 ps
- 
steps = 100000
- simulated time = 100 ps
- average temperature = 299.823 K
- average pressure = -17.8026 bar over this short test
- performance = 32.886 ns/day on 1 MPI rank with 8 OpenMP threads

These files are kept as a reference only. The LAMMPS production files are in 3_output_files/final_200k.
