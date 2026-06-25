# 目的：一键按顺序运行安全平衡流程：先 NVT，再 NPT。
# 注意：$work 指向原始 LAMMPS 工作目录；如果只在 submission package 里复现，
# 需要先把 01_input_files 和 02_run_scripts 里的必要文件复制到同一个工作目录。

$ErrorActionPreference = 'Stop'

# LAMMPS 实际运行目录。LAMMPS 会在这里寻找 in.safe_nvt_26ps、in.safe_npt_26ps、data、pair_coeffs.in。
$work = 'C:\Users\xiong\Desktop\solvation MD\MD simulation\sol_mix_1\lammps_model'

# 本机 LAMMPS 可执行文件路径。
$lmp = 'C:\Users\xiong\AppData\Local\LAMMPS 64-bit 22Jul2025 with Python\bin\lmp.exe'

Set-Location -Path $work

# 写一个简单状态文件，方便判断流程跑到哪一步。
"START safe pipeline: $(Get-Date)" | Set-Content -Path (Join-Path $work 'safe_pipeline.status')

# 第一步：NVT 稳温，输出 solvent_mix_1_26ps_nvt.data。
& $lmp -in in.safe_nvt_26ps -log safe_nvt_26ps.log
"NVT exit code: $LASTEXITCODE at $(Get-Date)" | Add-Content -Path (Join-Path $work 'safe_pipeline.status')
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

# 第二步：从 NVT 输出结构继续 NPT 慢平衡。
& $lmp -in in.safe_npt_26ps -log safe_npt_26ps.log
"NPT exit code: $LASTEXITCODE at $(Get-Date)" | Add-Content -Path (Join-Path $work 'safe_pipeline.status')
exit $LASTEXITCODE
