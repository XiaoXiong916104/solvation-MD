# LAMMPS 文件中文阅读指南

## 1. 先看哪几个文件

建议按这个顺序读：

1. `README.md`
   - 看体系组成、最终步数、最终温度/密度/压力、文件夹用途。
2. `02_run_scripts/in.minimize`
   - 看最初结构如何做能量最小化。
3. `02_run_scripts/in.safe_nvt_26ps`
   - 看如何从稳定 26 ps 结构做 NVT 稳温。
4. `02_run_scripts/in.safe_npt_26ps`
   - 看最终 NPT 如何慢慢调体积和密度。
5. `01_input_files/pair_coeffs.in`
   - 看 LJ 参数，也就是不同 atom type 之间的 epsilon/sigma。
6. `03_output_files/final_200k/FINAL_STATUS.txt`
   - 看最终运行是否成功，以及最终温度、压力、密度。

## 2. LAMMPS 输入脚本怎么读

LAMMPS 输入脚本基本按“设置 -> 读入结构 -> 设置力场 -> 运行 -> 写出结果”的顺序写。

核心关键词：

- `units real`：使用 real 单位，时间 fs，长度 Angstrom，能量 kcal/mol，压力 atm。
- `atom_style full`：原子带 molecule id、atom type、电荷和坐标，适合水/离子/有机阴离子体系。
- `boundary p p p`：三维周期性边界。
- `read_data ...data`：读入结构和拓扑。
- `include pair_coeffs.in`：读入 LJ 非键参数。
- `pair_style lj/cut/coul/long 12.0`：LJ 截断 12 A，电荷长程相互作用单独处理。
- `kspace_style pppm 1.0e-4`：用 PPPM 处理长程库仑。
- `fix shake`：约束水分子的键长和角度。
- `fix nvt`：恒粒子数、恒体积、恒温。
- `fix npt`：恒粒子数、恒压、恒温，盒子体积会变。
- `thermo_style`：控制 log 中输出哪些热力学量。
- `dump`：输出轨迹。
- `write_data`：保存最后结构。

## 3. 这个体系的工作流

实际最终流程是：

1. `solvent_mix_1.data`
   - 初始转换结构。
2. `in.minimize`
   - 能量最小化，得到 `solvent_mix_1.minimized.data`。
3. `solvent_mix_1_26ps.data`
   - 选择一个已经稳定到 26 ps 的结构作为更安全起点。
4. `in.safe_nvt_26ps`
   - 做 10 ps NVT 稳温，得到 `solvent_mix_1_26ps_nvt.data`。
5. `in.safe_npt_26ps`
   - 做 100 ps 慢 NPT，得到最终结构 `solvent_mix_1_26ps_npt_100ps.data`。

## 4. 最重要的物理判断

- 温度：最终约 303 K，接近 300 K 目标。
- 密度：最终约 1.1728 g/cm3，是判断短程平衡更有用的指标。
- 压力：最终瞬时压力约 244 atm，但小盒子液体的瞬时压力波动很大，不应该只看最后一行压力判断失败。
- 能量：看势能 `pe` 是否整体稳定，不应持续漂移或突然爆炸。
- 轨迹：看分子有没有飞散、盒子有没有异常塌缩、水分子几何是否稳定。

## 5. 报告里可以怎么说

LAMMPS was used as the molecular dynamics engine. Python scripts were used for format conversion, run automation, archiving, and post-processing. The final workflow used energy minimization, NVT stabilization from a stable 26 ps structure, and slow NPT equilibration to 200000 steps. The final system reached approximately 303 K with a density of 1.1728 g/cm3.
