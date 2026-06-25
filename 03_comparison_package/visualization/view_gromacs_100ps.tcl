# VMD script: GROMACS 100 ps reference trajectory.
# Use in VMD Tk Console:
# source ".../03_comparison_package/visualization/view_gromacs_100ps.tcl"

set script_dir [file dirname [info script]]
set repo_dir [file normalize [file join $script_dir ".." ".."]]
set gmx_dir [file join $repo_dir "02_GROMACS_package" "03_results" "production_test_100ps"]
set gmx_gro [file join $gmx_dir "production_test.gro"]
set gmx_xtc [file join $gmx_dir "production_test.xtc"]

mol delete all
mol new $gmx_gro type gro waitfor all
mol addfile $gmx_xtc type xtc waitfor all
mol rename top "GROMACS production test 100 ps"
mol delrep 0 top

mol representation Lines 1.0
mol color Name
mol selection "resname SOL"
mol material Opaque
mol addrep top

mol representation VDW 1.45 32
mol color ColorID 10
mol selection "resname ZN or name ZN"
mol material Opaque
mol addrep top

mol representation Licorice 0.12 16 12
mol color Name
mol selection "resname BFAF"
mol material Opaque
mol addrep top

mol representation Licorice 0.18 16 12
mol color Name
mol selection "same residue as within 3.5 of (resname ZN or name ZN)"
mol material Opaque
mol addrep top

package require pbctools
pbc box -color white -width 2
axes location LowerLeft
color Display Background black
display projection Orthographic
display depthcue off
display resetview
scale by 1.25