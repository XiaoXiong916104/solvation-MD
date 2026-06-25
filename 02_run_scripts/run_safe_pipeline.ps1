$ErrorActionPreference = 'Stop'
$work = 'C:\Users\xiong\Desktop\solvation MD\MD simulation\sol_mix_1\lammps_model'
$lmp = 'C:\Users\xiong\AppData\Local\LAMMPS 64-bit 22Jul2025 with Python\bin\lmp.exe'
Set-Location -Path $work
"START safe pipeline: $(Get-Date)" | Set-Content -Path (Join-Path $work 'safe_pipeline.status')
& $lmp -in in.safe_nvt_26ps -log safe_nvt_26ps.log
"NVT exit code: $LASTEXITCODE at $(Get-Date)" | Add-Content -Path (Join-Path $work 'safe_pipeline.status')
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& $lmp -in in.safe_npt_26ps -log safe_npt_26ps.log
"NPT exit code: $LASTEXITCODE at $(Get-Date)" | Add-Content -Path (Join-Path $work 'safe_pipeline.status')
exit $LASTEXITCODE
