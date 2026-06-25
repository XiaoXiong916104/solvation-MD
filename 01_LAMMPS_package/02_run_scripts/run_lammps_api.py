from __future__ import annotations

# 这个脚本演示“方式 2：Python API 直接控制 LAMMPS”。
#
# 和 subprocess 版本的区别：
# - subprocess 版本：Python 启动 lmp.exe 这个外部程序。
# - API 版本：Python 直接 import lammps，并在 Python 进程里创建 LAMMPS 对象。
#
# 真正做 MD 计算的仍然是 LAMMPS；Python 负责控制它、传入命令、保存结果。

import argparse
import csv
import os
import re
import shutil
from datetime import datetime
from pathlib import Path

from lammps import lammps

# 项目的 LAMMPS 工作目录。输入文件、data 文件、pair_coeffs.in 都在这里。
WORK = Path(r"C:\Users\xiong\Desktop\solvation MD\MD simulation\sol_mix_1\lammps_model")

# LAMMPS log 中 thermo 行的格式。
# 对应输入脚本中的：thermo_style custom step temp press pe etotal density vol
THERMO_RE = re.compile(
    r"^\s*(\d+)\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)\s+"
    r"([-+0-9.eE]+)\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)\s*$"
)

# 常见的 LAMMPS 输出文件。运行结束后会尽量复制到归档目录。
KNOWN_OUTPUTS = [
    "safe_nvt_26ps.lammpstrj",
    "safe_npt_26ps.lammpstrj",
    "solvent_mix_1_26ps_nvt.data",
    "solvent_mix_1_26ps_npt_100ps.data",
]


def parse_args() -> argparse.Namespace:
    """读取命令行参数。

    示例：
    python run_lammps_api.py --input in.safe_nvt_26ps
    python run_lammps_api.py --input in.safe_npt_26ps --tag test_npt
    """
    parser = argparse.ArgumentParser(description="Run LAMMPS through the Python API.")
    parser.add_argument("--input", default="in.safe_npt_26ps", help="LAMMPS input script filename")
    parser.add_argument("--tag", default=None, help="Optional run tag used in the archive folder name")
    parser.add_argument("--screen", action="store_true", help="Also print LAMMPS screen output in the terminal")
    return parser.parse_args()


def parse_thermo(log_path: Path) -> list[list[float]]:
    """从 LAMMPS log 文件提取 step/temp/press/energy/density/volume。"""
    rows = []
    if not log_path.exists():
        return rows
    for line in log_path.read_text(errors="ignore").splitlines():
        match = THERMO_RE.match(line)
        if match:
            rows.append([int(match.group(1))] + [float(match.group(i)) for i in range(2, 8)])
    return rows


def write_thermo_csv(rows: list[list[float]], path: Path) -> None:
    """把 thermo 数据写成 CSV，便于 Excel、Origin 或 Python 画图。"""
    with path.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "step",
                "temperature_K",
                "pressure_atm",
                "potential_energy_kcal_mol",
                "total_energy_kcal_mol",
                "density_g_cm3",
                "volume_A3",
            ]
        )
        writer.writerows(rows)


def copy_if_exists(src: Path, dest_dir: Path) -> None:
    """如果文件存在，就复制到归档目录。"""
    if src.exists():
        shutil.copy2(src, dest_dir / src.name)


def run_lammps_api(input_script: str, run_dir: Path, screen: bool) -> int:
    """用 Python API 直接创建 LAMMPS 对象并执行输入脚本。

    核心就是三步：
    1. lmp = lammps(...)
    2. lmp.file("in.xxx")
    3. lmp.close()
    """
    log_file = run_dir / "api_lammps.log"
    screen_file = run_dir / "api_screen.log"

    # cmdargs 相当于传给 lmp.exe 的命令行参数。
    # -log 指定 LAMMPS log 文件。
    # -screen none 表示不在终端刷大量输出；如果 --screen，则同时保存 screen 输出。
    cmdargs = ["-log", str(log_file)]
    if screen:
        cmdargs += ["-screen", str(screen_file)]
    else:
        cmdargs += ["-screen", "none"]

    # LAMMPS 输入脚本里的 read_data/include 通常使用相对路径，
    # 所以运行前切换到 WORK 目录，确保它能找到 data 和 pair_coeffs.in。
    old_cwd = Path.cwd()
    os.chdir(WORK)
    try:
        lmp = lammps(cmdargs=cmdargs)
        try:
            # 这里就是 API 调用的关键：让 LAMMPS 执行输入脚本。
            lmp.file(input_script)
        finally:
            lmp.close()
    finally:
        os.chdir(old_cwd)

    return 0


def main() -> None:
    args = parse_args()
    input_path = WORK / args.input
    if not input_path.exists():
        raise FileNotFoundError(f"LAMMPS input script not found: {input_path}")

    run_tag = args.tag or f"api_{input_path.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    run_dir = WORK / "python_api_runs" / run_tag
    run_dir.mkdir(parents=True, exist_ok=True)

    # 保存本次 API 运行的元信息，方便写报告或复现实验。
    (run_dir / "api_run_metadata.txt").write_text(
        "\n".join(
            [
                "LAMMPS Python API run",
                f"Working directory: {WORK}",
                f"Input script: {input_path.name}",
                f"Archive directory: {run_dir}",
                f"Screen output enabled: {args.screen}",
                "Python call:",
                "from lammps import lammps",
                "lmp = lammps(cmdargs=[...])",
                f"lmp.file({input_path.name!r})",
                "lmp.close()",
                "",
            ]
        ),
        encoding="utf-8",
    )

    # 先复制输入脚本和 pair_coeffs，记录“这次到底用什么参数跑的”。
    copy_if_exists(input_path, run_dir)
    copy_if_exists(WORK / "pair_coeffs.in", run_dir)

    # 保护已有结果：LAMMPS dump/data 文件可能会被同名新运行覆盖。
    # 因此 API 开跑前，先把工作目录中已有的关键输出备份到 pre_existing_outputs。
    pre_existing_dir = run_dir / "pre_existing_outputs"
    pre_existing_dir.mkdir(exist_ok=True)
    for name in KNOWN_OUTPUTS + ["safe_npt_26ps.log", "safe_nvt_26ps.log"]:
        copy_if_exists(WORK / name, pre_existing_dir)

    print(f"Running LAMMPS through Python API: {input_path.name}")
    print(f"Archive directory: {run_dir}")

    try:
        return_code = run_lammps_api(input_path.name, run_dir, args.screen)
    except Exception as exc:
        # 如果 LAMMPS API 报错，把错误信息保存下来。
        (run_dir / "api_error.txt").write_text(repr(exc), encoding="utf-8")
        raise

    (run_dir / "return_code.txt").write_text(str(return_code), encoding="utf-8")

    # 把常见输出复制进归档目录。
    # 注意：如果输入脚本改了输出文件名，也要把新文件名加到 KNOWN_OUTPUTS。
    for name in KNOWN_OUTPUTS:
        copy_if_exists(WORK / name, run_dir)

    # 从 API 运行产生的 log 中提取 thermo 数据。
    rows = parse_thermo(run_dir / "api_lammps.log")
    write_thermo_csv(rows, run_dir / "thermo.csv")

    if rows:
        last = rows[-1]
        summary = (
            f"Last thermo step: {last[0]}\n"
            f"Temperature: {last[1]:.3f} K\n"
            f"Pressure: {last[2]:.3f} atm\n"
            f"Potential energy: {last[3]:.3f} kcal/mol\n"
            f"Total energy: {last[4]:.3f} kcal/mol\n"
            f"Density: {last[5]:.6f} g/cm3\n"
            f"Volume: {last[6]:.3f} A^3\n"
        )
    else:
        summary = "No thermo rows parsed. Check api_lammps.log.\n"
    (run_dir / "summary.txt").write_text(summary, encoding="utf-8")
    print(summary)
    print(f"Done. API run archived in: {run_dir}")


if __name__ == "__main__":
    main()
