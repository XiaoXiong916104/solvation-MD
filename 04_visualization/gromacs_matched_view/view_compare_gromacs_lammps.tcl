# VMD2 script: load GROMACS and LAMMPS trajectories in the same VMD session for comparison.
# Use Molecule menu to toggle each molecule on/off.
# Tk Console:
# source "C:/Users/xiong/Desktop/solvation MD/MD simulation/GROMACS_reproduction_water_Zn_OTF_5nm_20260625/results/production_test_100ps_vmd/view_compare_gromacs_lammps.tcl"

proc apply_style {mol_id} {
    mol delrep 0 $mol_id
    mol representation CPK 0.35 0.12 16 12
    mol color ColorID 0
    mol selection "resname SOL"
    mol material Transparent
    mol addrep $mol_id

    mol representation VDW 1.05 24
    mol color ColorID 4
    mol selection "resname ZN or name ZN"
    mol material Opaque
    mol addrep $mol_id

    mol representation Licorice 0.22 16 16
    mol color Name
    mol selection "resname BFAF or not (resname SOL ZN)"
    mol material Opaque
    mol addrep $mol_id

    mol representation Licorice 0.18 12 12
    mol color ColorID 1
    mol selection "same residue as within 2.8 of (resname ZN or name ZN)"
    mol material Opaque
    mol addrep $mol_id
}

mol new "C:/Users/xiong/Desktop/solvation MD/MD simulation/GROMACS_reproduction_water_Zn_OTF_5nm_20260625/results/production_test_100ps/production_test.gro" type gro waitfor all
mol addfile "C:/Users/xiong/Desktop/solvation MD/MD simulation/GROMACS_reproduction_water_Zn_OTF_5nm_20260625/results/production_test_100ps/production_test.xtc" type xtc waitfor all
set gmx [molinfo top]
apply_style $gmx
mol rename $gmx "GROMACS_100ps"

mol new "C:/Users/xiong/Desktop/solvation MD/MD simulation/GROMACS_reproduction_water_Zn_OTF_5nm_20260625/results/production_test_100ps_vmd/lammps_final_200k_vmd.pdb" type pdb waitfor all
set lmp [molinfo top]
apply_style $lmp
mol rename $lmp "LAMMPS_final_200k"

animate goto last
display projection Orthographic
display depthcue off
axes location Off
color Display Background white
puts "Loaded comparison molecules: GROMACS molecule id=$gmx, LAMMPS molecule id=$lmp"
puts "Use VMD Main molecule list to show/hide each model."
