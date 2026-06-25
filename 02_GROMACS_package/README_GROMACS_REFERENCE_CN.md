# GROMACS reference result

The compact 100 ps GROMACS reference result is stored in:

`02_GROMACS_package/03_results/production_test_100ps`

Files:

- `production_test.gro`: final GROMACS structure, 3438 atoms, final box 3.30179 x 3.30179 x 3.30179 nm.
- `production_test.xtc`: compressed GROMACS trajectory, 101 frames.
- `production_test.tpr`: topology-aware GROMACS run input, useful for VMD visualization.
- `production_test.log`: GROMACS run log.

Key log values:

- `dt = 0.001 ps`
- `nsteps = 100000`
- simulated time = 100 ps
- average temperature = 299.823 K
- average pressure = -17.8026 bar over this short test
- performance = 32.886 ns/day on 1 MPI rank with 8 OpenMP threads

The original workflow logic and input files are documented in `README_GROMACS_PACKAGE_CN.md`.