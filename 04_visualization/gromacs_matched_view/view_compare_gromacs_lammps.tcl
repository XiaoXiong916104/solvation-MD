# VMD script: load GROMACS reference and LAMMPS final frame as two molecules.
# Toggle molecule visibility in VMD Main to inspect one result at a time.

set script_dir [file dirname [info script]]
set pkg_dir [file normalize [file join $script_dir ".." ".."]]
set lmp_gro [file join $script_dir "lammps_final_200k_gromacs_style_wrapped.gro"]
set gmx_dir [file join $pkg_dir "07_gromacs_reference" "production_test_100ps"]
set gmx_gro [file join $gmx_dir "production_test.gro"]
set gmx_xtc [file join $gmx_dir "production_test.xtc"]

proc add_common_reps {} {
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
}

mol delete all
mol new $gmx_gro type gro waitfor all
mol addfile $gmx_xtc type xtc waitfor all
mol rename top "GROMACS 100 ps reference"
add_common_reps

mol new $lmp_gro type gro waitfor all
mol rename top "LAMMPS final 200k corrected"
add_common_reps

package require pbctools
pbc box -color white -width 2
axes location LowerLeft
color Display Background black
display projection Orthographic
display depthcue off
display resetview