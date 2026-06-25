from __future__ import annotations

# 这个脚本的作用：
# 1. 用 Python 一键启动 LAMMPS；
# 2. 自动保存本次运行的日志、轨迹、输入文件和结果文件；
# 3. 从 LAMMPS log 里提取温度、压力、密度、能量，保存成 CSV；
# 4. 生成一个 summary.txt，方便写报告时引用。
#
# 注意：真正做分子动力学计算的是 LAMMPS 的 lmp.exe。
# Python 在这里负责“自动化管理”和“后处理”，不是替代 LAMMPS 算力场。

import csv
import re
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

# WORK 是本项目的 LAMMPS 工作目录。
# 这里面放着 LAMMPS 输入脚本、data 文件、pair_coeffs.in、轨迹和日志。
WORK = Path(r"C:\Users\xiong\Desktop\solvation MD\MD simulation\sol_mix_1\lammps_model")

# LMP 是 LAMMPS 主程序 lmp.exe 的路径。
# Python 后面会通过 subprocess.run(...) 调用这个程序。
LMP = Path(r"C:\Users\xiong\AppData\Local\LAMMPS 64-bit 22Jul2025 with Python\bin\lmp.exe")

# INPUT_SCRIPT 是要运行的 LAMMPS 输入文件。
# 如果以后要跑 NVT，可以改成 "in.safe_nvt_26ps"。
# 如果要跑另一个 LAMMPS 脚本，只需要改这里。
INPUT_SCRIPT = "in.safe_npt_26ps"

# LOG_FILE 是 LAMMPS 这次运行输出的日志文件名。
# LAMMPS 会把温度、压力、能量、密度等信息写进去。
LOG_FILE = "python_launched_safe_npt.log"

# RUN_TAG 用当前时间生成一个唯一标签。
# 这样每次运行都会保存到不同文件夹，不会覆盖之前结果。
RUN_TAG = datetime.now().strftime("%Y%m%d_%H%M%S")

# RUN_DIR 是本次运行的归档目录。
# 例如：python_runs/safe_npt_20260625_103000
RUN_DIR = WORK / "python_runs" / f"safe_npt_{RUN_TAG}"

# 这个正则表达式用于识别 LAMMPS log 里的 thermo 输出行。
# 对应 in.safe_npt_26ps 里的：
# thermo_style custom step temp press pe etotal density vol
# 所以每一行应该包含 7 列：step, temp, press, pe, etotal, density, vol。
THERMO_RE = re.compile(
    r"^\s*(\d+)\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)\s+"
    r"([-+0-9.eE]+)\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)\s*$"
)


def parse_thermo(log_path: Path) -> list[list[float]]:
    """从 LAMMPS log 文件中提取 thermo 数据。

    返回的数据格式类似：
    [
        [step, temperature, pressure, potential_energy, total_energy, density, volume],
        ...
    ]
    """
    rows = []

    # 如果 log 文件还不存在，直接返回空列表，避免程序报错。
    if not log_path.exists():
        return rows

    # 逐行读取 log 文件。errors="ignore" 是为了避免偶尔出现编码问题。
    for line in log_path.read_text(errors="ignore").splitlines():
        match = THERMO_RE.match(line)
        if match:
            # 第 1 列 step 是整数；后面的温度、压力、能量等是浮点数。
            rows.append([int(match.group(1))] + [float(match.group(i)) for i in range(2, 8)])
    return rows


def write_thermo_csv(rows: list[list[float]], csv_path: Path) -> None:
    """把提取出来的 thermo 数据写成 CSV，方便 Excel/Origin/报告画图。"""
    with csv_path.open("w", newline="") as handle:
        writer = csv.writer(handle)

        # CSV 表头。单位按 LAMMPS real units：温度 K，压力 atm，能量 kcal/mol，体积 A^3。
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


def copy_if_exists(name: str, dest_dir: Path) -> None:
    """如果某个结果文件存在，就复制到本次运行的归档目录。"""
    src = WORK / name
    if src.exists():
        shutil.copy2(src, dest_dir / name)


def main() -> None:
    """主流程：检查文件 -> 运行 LAMMPS -> 保存结果 -> 提取摘要。"""

    # 先检查 LAMMPS 主程序是否存在。
    if not LMP.exists():
        raise FileNotFoundError(f"LAMMPS executable not found: {LMP}")

    # 再检查要运行的 LAMMPS 输入脚本是否存在。
    if not (WORK / INPUT_SCRIPT).exists():
        raise FileNotFoundError(f"LAMMPS input not found: {WORK / INPUT_SCRIPT}")

    # 创建本次运行的归档目录。
    # parents=True 表示如果 python_runs 目录不存在，也一起创建。
    RUN_DIR.mkdir(parents=True, exist_ok=True)

    # 保存本次运行的基本信息，方便以后追溯“当时跑了什么命令”。
    (RUN_DIR / "run_metadata.txt").write_text(
        "\n".join(
            [
                f"Run tag: {RUN_TAG}",
                f"Working directory: {WORK}",
                f"LAMMPS executable: {LMP}",
                f"Input script: {INPUT_SCRIPT}",
                f"Log file: {LOG_FILE}",
                "Command:",
                f'"{LMP}" -in {INPUT_SCRIPT} -log {LOG_FILE}',
                "",
            ]
        ),
        encoding="utf-8",
    )

    print(f"Starting LAMMPS run in {WORK}")
    print(f"Archiving run information in {RUN_DIR}")

    # 这里是真正“用 Python 调用 LAMMPS”的地方。
    # 等价于你在 PowerShell 里运行：
    # lmp.exe -in in.safe_npt_26ps -log python_launched_safe_npt.log
    #
    # cwd=WORK：让 LAMMPS 在工作目录里运行，这样它能找到 data 文件和 pair_coeffs.in。
    # stdout=subprocess.PIPE：把屏幕输出抓到 Python，后面保存成 lammps_stdout.txt。
    # stderr=subprocess.STDOUT：把错误输出也合并保存，避免漏掉报错信息。
    result = subprocess.run(
        [str(LMP), "-in", INPUT_SCRIPT, "-log", LOG_FILE],
        cwd=WORK,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    # 保存 LAMMPS 在命令行里的输出。
    (RUN_DIR / "lammps_stdout.txt").write_text(result.stdout, encoding="utf-8", errors="ignore")

    # 保存返回码。0 表示正常结束；非 0 通常表示 LAMMPS 报错退出。
    (RUN_DIR / "return_code.txt").write_text(str(result.returncode), encoding="utf-8")

    # 把关键输入/输出文件复制到归档目录。
    # 注意：文件名要和 LAMMPS 输入脚本里实际写出的名字一致。
    copy_if_exists(LOG_FILE, RUN_DIR)
    copy_if_exists("safe_npt_26ps.lammpstrj", RUN_DIR)
    copy_if_exists("solvent_mix_1_26ps_npt_100ps.data", RUN_DIR)
    copy_if_exists(INPUT_SCRIPT, RUN_DIR)
    copy_if_exists("pair_coeffs.in", RUN_DIR)

    # 从 log 文件提取温度、压力、密度、能量等数据，并写成 CSV。
    rows = parse_thermo(WORK / LOG_FILE)
    write_thermo_csv(rows, RUN_DIR / "thermo.csv")

    # 生成一个简短摘要，方便直接复制进报告或实验记录。
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
        summary = "No thermo rows parsed. Check the LAMMPS log.\n"
    (RUN_DIR / "summary.txt").write_text(summary, encoding="utf-8")
    print(summary)

    # 如果 LAMMPS 返回码不是 0，说明运行没有正常完成。
    # 这里直接停止 Python，并提示去归档目录查看日志。
    if result.returncode != 0:
        raise SystemExit(f"LAMMPS returned non-zero exit code {result.returncode}; see {RUN_DIR}")

    print(f"Done. Results archived in: {RUN_DIR}")


# Python 的标准入口：只有直接运行这个文件时，才会执行 main()。
# 如果将来你在另一个 Python 脚本里 import 这个文件，它不会自动开跑。
if __name__ == "__main__":
    main()
