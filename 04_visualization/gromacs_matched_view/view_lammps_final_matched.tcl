# Compatibility wrapper.
# The old PDB-based matched view was replaced because VMD guessed bad bonds and missed Zn labels.
source [file join [file dirname [info script]] "view_lammps_gromacs_style_wrapped.tcl"]