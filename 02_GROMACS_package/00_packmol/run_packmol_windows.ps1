# Run from Windows PowerShell in this folder:
#   .\run_packmol_windows.ps1

$ErrorActionPreference = "Stop"
Push-Location $PSScriptRoot
try {
    .\packmol.exe < .\water_Zn_OTF_5nm.inp
    Write-Host "Packmol wrote water_Zn_OTF_5nm.pdb"
    Write-Host "Next, in Ubuntu/WSL, convert it with:"
    Write-Host "  cd '/mnt/c/Users/xiong/Desktop/solvation MD/MD simulation/GROMACS_reproduction_water_Zn_OTF_5nm_20260625/01_gromacs'"
    Write-Host "  gmx editconf -f ../00_packmol/water_Zn_OTF_5nm.pdb -o initial_water_Zn_OTF_5nm.gro -box 5.0 5.0 5.0"
}
finally {
    Pop-Location
}
