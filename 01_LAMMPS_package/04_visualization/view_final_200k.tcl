# VMD2-safe loader for final 200k NPT trajectory converted to XYZ.
mol new "C:/Users/xiong/Desktop/solvation MD/MD simulation/LAMMPS_submission_package/04_visualization/vmd_safe_npt_final_200k.xyz" type xyz waitfor all
mol delrep 0 top
mol representation VDW 0.45 16
mol color Name
mol selection all
mol material Opaque
mol addrep top
mol representation VDW 1.05 24
mol color ColorID 4
mol selection "name Zn"
mol material Opaque
mol addrep top
animate goto last
display projection Orthographic
display depthcue off
axes location Off
color Display Background white
puts "Loaded final 200k NPT XYZ frames: [molinfo top get numframes]"
