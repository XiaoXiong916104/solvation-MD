# VMD script: corrected LAMMPS final frame, GROMACS-like style.
# Use in VMD Tk Console:
# source ".../03_comparison_package/visualization/view_lammps_gromacs_style_wrapped.tcl"

set script_dir [file dirname [info script]]
set lmp_gro [file join $script_dir "lammps_final_200k_gromacs_style_wrapped.gro"]

mol delete all
mol new $lmp_gro type gro waitfor all
mol rename top "LAMMPS final 200k, corrected wrapped cube"
mol delrep 0 top

mol representation Lines 1.0
mol color Name
mol selection "resname SOL"
mol material Opaque
mol addrep top

mol representation VDW 1.45 32
mol color ColorID 10
mol selection "name ZN or resname ZN"
mol material Opaque
mol addrep top

mol representation Licorice 0.12 16 12
mol color Name
mol selection "resname BFAF"
mol material Opaque
mol addrep top

mol representation Licorice 0.18 16 12
mol color Name
mol selection "same residue as within 3.5 of (name ZN or resname ZN)"
mol material Opaque
mol addrep top

package require pbctools
pbc set {32.986771 32.986771 32.986771 90 90 90} -all
pbc box -color white -width 2
axes location LowerLeft
color Display Background black
display projection Orthographic
display depthcue off
display resetview
scale by 1.25