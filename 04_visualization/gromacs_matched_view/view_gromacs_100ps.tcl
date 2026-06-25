# VMD2 script: visualize GROMACS 100 ps production test.
# Tk Console:
# source "C:/Users/xiong/Desktop/solvation MD/MD simulation/GROMACS_reproduction_water_Zn_OTF_5nm_20260625/results/production_test_100ps_vmd/view_gromacs_100ps.tcl"

mol new "C:/Users/xiong/Desktop/solvation MD/MD simulation/GROMACS_reproduction_water_Zn_OTF_5nm_20260625/results/production_test_100ps/production_test.gro" type gro waitfor all
mol addfile "C:/Users/xiong/Desktop/solvation MD/MD simulation/GROMACS_reproduction_water_Zn_OTF_5nm_20260625/results/production_test_100ps/production_test.xtc" type xtc waitfor all
mol delrep 0 top

# Water: light transparent small spheres.
mol representation CPK 0.35 0.12 16 12
mol color ColorID 0
mol selection "resname SOL"
mol material Transparent
mol addrep top

# Zn ions: large highlighted spheres.
mol representation VDW 1.05 24
mol color ColorID 4
mol selection "resname ZN or name ZN"
mol material Opaque
mol addrep top

# OTF/BFAF anions.
mol representation Licorice 0.22 16 16
mol color Name
mol selection "resname BFAF or not (resname SOL ZN)"
mol material Opaque
mol addrep top

# Zn first-shell environment.
mol representation Licorice 0.18 12 12
mol color ColorID 1
mol selection "same residue as within 2.8 of (resname ZN or name ZN)"
mol material Opaque
mol addrep top

animate goto last
display projection Orthographic
display depthcue off
axes location Off
color Display Background white
puts "Loaded GROMACS production_test.gro + production_test.xtc; frames: [molinfo top get numframes]"
