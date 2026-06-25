from __future__ import annotations

import math
import re
from collections import OrderedDict
from dataclasses import dataclass
from pathlib import Path


BASE = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent

GRO = BASE / "solvent_mix_1.gro"
TOP = BASE / "topol_solvent_mix_5.top"
FFNB = BASE / "gromos54a7.ff" / "ffnonbonded.itp"
OTF = BASE / "toppar" / "OTF.itp"

KJ_TO_KCAL = 1.0 / 4.184


@dataclass(frozen=True)
class Atom:
    atom_type: str
    atom_name: str
    charge: float
    mass: float


@dataclass
class MoleculeTemplate:
    name: str
    atoms: list[Atom]
    bonds: list[tuple[int, int, int, float, float]]
    angles: list[tuple[int, int, int, int, float, float]]
    dihedrals: list[tuple[int, int, int, int, int, float, float, int]]


def strip_comment(line: str) -> str:
    return line.split(";", 1)[0].strip()


def section_name(line: str) -> str | None:
    match = re.match(r"\[\s*([^\]]+?)\s*\]", line)
    return match.group(1).strip() if match else None


def parse_molecule_counts(path: Path) -> OrderedDict[str, int]:
    counts: OrderedDict[str, int] = OrderedDict()
    in_molecules = False
    for raw in path.read_text().splitlines():
        sec = section_name(raw)
        if sec:
            in_molecules = sec == "molecules"
            continue
        if not in_molecules:
            continue
        line = strip_comment(raw)
        if not line:
            continue
        parts = line.split()
        if len(parts) >= 2:
            counts[parts[0]] = int(parts[1])
    return counts


def parse_gro(path: Path) -> tuple[list[dict], tuple[float, float, float]]:
    lines = path.read_text().splitlines()
    natoms = int(lines[1].strip())
    atoms = []
    for raw in lines[2 : 2 + natoms]:
        atoms.append(
            {
                "resid": int(raw[0:5]),
                "resname": raw[5:10].strip(),
                "atomname": raw[10:15].strip(),
                "atomnr": int(raw[15:20]),
                "x_nm": float(raw[20:28]),
                "y_nm": float(raw[28:36]),
                "z_nm": float(raw[36:44]),
            }
        )
    box_values = tuple(float(x) for x in lines[2 + natoms].split()[:3])
    return atoms, box_values


def parse_nonbonded(path: Path) -> tuple[dict[str, tuple[float, float]], dict[tuple[str, str], tuple[float, float]]]:
    atomtypes: dict[str, tuple[float, float]] = {}
    nonbond_params: dict[tuple[str, str], tuple[float, float]] = {}
    section = None
    for raw in path.read_text().splitlines():
        sec = section_name(raw)
        if sec:
            section = sec
            continue
        line = strip_comment(raw)
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if section == "atomtypes" and len(parts) >= 7:
            name = parts[0]
            c6 = float(parts[-2])
            c12 = float(parts[-1])
            atomtypes[name] = (c6, c12)
        elif section == "nonbond_params" and len(parts) >= 5:
            a, b = parts[0], parts[1]
            c6 = float(parts[-2])
            c12 = float(parts[-1])
            nonbond_params[tuple(sorted((a, b)))] = (c6, c12)
    return atomtypes, nonbond_params


def parse_otf(path: Path) -> MoleculeTemplate:
    atoms: list[Atom] = []
    bonds: list[tuple[int, int, int, float, float]] = []
    angles: list[tuple[int, int, int, int, float, float]] = []
    dihedrals: list[tuple[int, int, int, int, int, float, float, int]] = []
    section = None
    for raw in path.read_text().splitlines():
        sec = section_name(raw)
        if sec:
            section = sec
            continue
        line = strip_comment(raw)
        if not line:
            continue
        parts = line.split()
        if section == "atoms" and len(parts) >= 8:
            atoms.append(Atom(parts[1], parts[4], float(parts[6]), float(parts[7])))
        elif section == "bonds" and len(parts) >= 5:
            bonds.append((int(parts[0]), int(parts[1]), int(parts[2]), float(parts[3]), float(parts[4])))
        elif section == "angles" and len(parts) >= 6:
            angles.append((int(parts[0]), int(parts[1]), int(parts[2]), int(parts[3]), float(parts[4]), float(parts[5])))
        elif section == "dihedrals" and len(parts) >= 8:
            dihedrals.append(
                (
                    int(parts[0]),
                    int(parts[1]),
                    int(parts[2]),
                    int(parts[3]),
                    int(parts[4]),
                    float(parts[5]),
                    float(parts[6]),
                    int(parts[7]),
                )
            )
    return MoleculeTemplate("BFAF", atoms, bonds, angles, dihedrals)


def water_template() -> MoleculeTemplate:
    atoms = [
        Atom("OW", "OW", -0.8476, 15.9994),
        Atom("H", "HW1", 0.4238, 1.0080),
        Atom("H", "HW2", 0.4238, 1.0080),
    ]
    # Flexible SPC/E parameters from gromos54a7.ff/spce.itp, useful for minimization
    # and compatible with fix shake during dynamics.
    bonds = [(1, 2, 1, 0.1000, 345000.0), (1, 3, 1, 0.1000, 345000.0)]
    angles = [(2, 1, 3, 1, 109.47, 383.0)]
    return MoleculeTemplate("SOL", atoms, bonds, angles, [])


def zinc_template() -> MoleculeTemplate:
    return MoleculeTemplate("ZN", [Atom("ZN2+", "ZN", 2.0, 65.37)], [], [], [])


def lj_from_c6_c12(c6: float, c12: float) -> tuple[float, float]:
    if c6 == 0.0 or c12 == 0.0:
        return 0.0, 1.0
    sigma_nm = (c12 / c6) ** (1.0 / 6.0)
    epsilon_kj = (c6 * c6) / (4.0 * c12)
    return epsilon_kj * KJ_TO_KCAL, sigma_nm * 10.0


def get_pair_c6_c12(
    a: str,
    b: str,
    atomtypes: dict[str, tuple[float, float]],
    nonbond_params: dict[tuple[str, str], tuple[float, float]],
) -> tuple[float, float]:
    key = tuple(sorted((a, b)))
    if key in nonbond_params:
        return nonbond_params[key]
    c6a, c12a = atomtypes[a]
    c6b, c12b = atomtypes[b]
    return math.sqrt(c6a * c6b), math.sqrt(c12a * c12b)


def bond_coeff(bond: tuple[int, int, int, float, float]) -> tuple[float, float]:
    _, _, funct, r0_nm, k = bond
    r0_ang = r0_nm * 10.0
    if funct == 1:
        kval = 0.5 * k * KJ_TO_KCAL / 100.0
    elif funct == 2:
        kval = k * r0_nm * r0_nm * KJ_TO_KCAL / 100.0
    else:
        raise ValueError(f"Unsupported bond function {funct}")
    return kval, r0_ang


def angle_coeff(angle: tuple[int, int, int, int, float, float]) -> tuple[float, float]:
    _, _, _, funct, theta_deg, k = angle
    if funct == 1:
        kval = 0.5 * k * KJ_TO_KCAL
    elif funct == 2:
        kval = 0.5 * k * (math.sin(math.radians(theta_deg)) ** 2) * KJ_TO_KCAL
    else:
        raise ValueError(f"Unsupported angle function {funct}")
    return kval, theta_deg


def dihedral_coeff(dihedral: tuple[int, int, int, int, int, float, float, int]) -> tuple[float, int, int]:
    _, _, _, _, funct, phase, k, mult = dihedral
    if funct != 1:
        raise ValueError(f"Unsupported dihedral function {funct}")
    phase_norm = phase % 360.0
    if abs(phase_norm) < 1.0e-6:
        sign = 1
    elif abs(phase_norm - 180.0) < 1.0e-6:
        sign = -1
    else:
        raise ValueError(f"Only 0/180 degree periodic dihedrals can be converted to dihedral_style harmonic: {phase}")
    return k * KJ_TO_KCAL, sign, mult


def main() -> None:
    counts = parse_molecule_counts(TOP)
    gro_atoms, box_values = parse_gro(GRO)
    atomtypes, nonbond_params = parse_nonbonded(FFNB)

    templates = {
        "SOL": water_template(),
        "ZN": zinc_template(),
        "BFAF": parse_otf(OTF),
    }

    expected_atoms = sum(len(templates[name].atoms) * count for name, count in counts.items())
    if expected_atoms != len(gro_atoms):
        raise ValueError(f"Topology expects {expected_atoms} atoms but GRO contains {len(gro_atoms)}")

    max_coord_nm = max(max(atom["x_nm"], atom["y_nm"], atom["z_nm"]) for atom in gro_atoms)
    # Packmol used a 50 A cube. VMD wrote GRO coordinates in nm but kept the box as 50,
    # so values much larger than coordinates are treated as Angstrom box lengths.
    if min(box_values) > 2.0 * max_coord_nm:
        box_ang = box_values
    else:
        box_ang = tuple(v * 10.0 for v in box_values)

    type_ids: OrderedDict[str, int] = OrderedDict()
    atom_type_masses: dict[str, float] = {}
    for name in counts:
        for atom in templates[name].atoms:
            if atom.atom_type not in type_ids:
                type_ids[atom.atom_type] = len(type_ids) + 1
                atom_type_masses[atom.atom_type] = atom.mass

    bond_type_ids: OrderedDict[tuple[float, float], int] = OrderedDict()
    angle_type_ids: OrderedDict[tuple[float, float], int] = OrderedDict()
    dihedral_type_ids: OrderedDict[tuple[float, int, int], int] = OrderedDict()

    lmp_atoms = []
    lmp_bonds = []
    lmp_angles = []
    lmp_dihedrals = []
    gro_index = 0
    atom_id = 1
    mol_id = 1
    bond_id = 1
    angle_id = 1
    dihedral_id = 1
    water_bond_types = set()
    water_angle_types = set()

    for mol_name, count in counts.items():
        tmpl = templates[mol_name]
        for _ in range(count):
            start_atom_id = atom_id
            for atom in tmpl.atoms:
                gro = gro_atoms[gro_index]
                if gro["resname"] != mol_name or gro["atomname"] != atom.atom_name:
                    raise ValueError(
                        f"Atom order mismatch at GRO atom {gro_index + 1}: "
                        f"expected {mol_name}:{atom.atom_name}, got {gro['resname']}:{gro['atomname']}"
                    )
                lmp_atoms.append(
                    (
                        atom_id,
                        mol_id,
                        type_ids[atom.atom_type],
                        atom.charge,
                        gro["x_nm"] * 10.0,
                        gro["y_nm"] * 10.0,
                        gro["z_nm"] * 10.0,
                    )
                )
                atom_id += 1
                gro_index += 1

            for bond in tmpl.bonds:
                coeff = bond_coeff(bond)
                if coeff not in bond_type_ids:
                    bond_type_ids[coeff] = len(bond_type_ids) + 1
                btype = bond_type_ids[coeff]
                if mol_name == "SOL":
                    water_bond_types.add(btype)
                lmp_bonds.append((bond_id, btype, start_atom_id + bond[0] - 1, start_atom_id + bond[1] - 1))
                bond_id += 1

            for angle in tmpl.angles:
                coeff = angle_coeff(angle)
                if coeff not in angle_type_ids:
                    angle_type_ids[coeff] = len(angle_type_ids) + 1
                atype = angle_type_ids[coeff]
                if mol_name == "SOL":
                    water_angle_types.add(atype)
                lmp_angles.append(
                    (angle_id, atype, start_atom_id + angle[0] - 1, start_atom_id + angle[1] - 1, start_atom_id + angle[2] - 1)
                )
                angle_id += 1

            for dihedral in tmpl.dihedrals:
                coeff = dihedral_coeff(dihedral)
                if coeff not in dihedral_type_ids:
                    dihedral_type_ids[coeff] = len(dihedral_type_ids) + 1
                dtype = dihedral_type_ids[coeff]
                lmp_dihedrals.append(
                    (
                        dihedral_id,
                        dtype,
                        start_atom_id + dihedral[0] - 1,
                        start_atom_id + dihedral[1] - 1,
                        start_atom_id + dihedral[2] - 1,
                        start_atom_id + dihedral[3] - 1,
                    )
                )
                dihedral_id += 1
            mol_id += 1

    data_path = OUT / "solvent_mix_1.data"
    with data_path.open("w", newline="\n") as fh:
        fh.write("LAMMPS data for solvent_mix_1 converted from GROMACS/ATB topology\n\n")
        fh.write(f"{len(lmp_atoms)} atoms\n")
        fh.write(f"{len(lmp_bonds)} bonds\n")
        fh.write(f"{len(lmp_angles)} angles\n")
        fh.write(f"{len(lmp_dihedrals)} dihedrals\n")
        fh.write("0 impropers\n\n")
        fh.write(f"{len(type_ids)} atom types\n")
        fh.write(f"{len(bond_type_ids)} bond types\n")
        fh.write(f"{len(angle_type_ids)} angle types\n")
        fh.write(f"{len(dihedral_type_ids)} dihedral types\n")
        fh.write("0 improper types\n\n")
        fh.write(f"0.0 {box_ang[0]:.8f} xlo xhi\n")
        fh.write(f"0.0 {box_ang[1]:.8f} ylo yhi\n")
        fh.write(f"0.0 {box_ang[2]:.8f} zlo zhi\n\n")

        fh.write("Masses\n\n")
        for name, idx in type_ids.items():
            fh.write(f"{idx:4d} {atom_type_masses[name]:12.6f} # {name}\n")

        fh.write("\nBond Coeffs # harmonic\n\n")
        for coeff, idx in bond_type_ids.items():
            k, r0 = coeff
            fh.write(f"{idx:4d} {k:16.8f} {r0:12.6f}\n")

        fh.write("\nAngle Coeffs # harmonic\n\n")
        for coeff, idx in angle_type_ids.items():
            k, theta = coeff
            fh.write(f"{idx:4d} {k:16.8f} {theta:12.6f}\n")

        fh.write("\nDihedral Coeffs # harmonic\n\n")
        for coeff, idx in dihedral_type_ids.items():
            k, sign, mult = coeff
            fh.write(f"{idx:4d} {k:16.8f} {sign:4d} {mult:4d}\n")

        fh.write("\nAtoms # full\n\n")
        for rec in lmp_atoms:
            fh.write(f"{rec[0]:6d} {rec[1]:6d} {rec[2]:4d} {rec[3]:12.6f} {rec[4]:12.6f} {rec[5]:12.6f} {rec[6]:12.6f}\n")

        fh.write("\nBonds\n\n")
        for rec in lmp_bonds:
            fh.write(f"{rec[0]:6d} {rec[1]:4d} {rec[2]:6d} {rec[3]:6d}\n")

        fh.write("\nAngles\n\n")
        for rec in lmp_angles:
            fh.write(f"{rec[0]:6d} {rec[1]:4d} {rec[2]:6d} {rec[3]:6d} {rec[4]:6d}\n")

        fh.write("\nDihedrals\n\n")
        for rec in lmp_dihedrals:
            fh.write(f"{rec[0]:6d} {rec[1]:4d} {rec[2]:6d} {rec[3]:6d} {rec[4]:6d} {rec[5]:6d}\n")

    pair_lines = []
    used_types = list(type_ids.keys())
    for i, ai in enumerate(used_types):
        for j, aj in enumerate(used_types[i:], start=i):
            c6, c12 = get_pair_c6_c12(ai, aj, atomtypes, nonbond_params)
            eps, sigma = lj_from_c6_c12(c6, c12)
            pair_lines.append((type_ids[ai], type_ids[aj], eps, sigma, ai, aj))

    pair_file = OUT / "pair_coeffs.in"
    with pair_file.open("w", newline="\n") as fh:
        fh.write("# Pair coefficients converted from GROMOS C6/C12 to LAMMPS real-unit LJ epsilon/sigma.\n")
        for i, j, eps, sigma, ai, aj in pair_lines:
            fh.write(f"pair_coeff {i:2d} {j:2d} {eps:14.8f} {sigma:12.8f} # {ai}-{aj}\n")

    in_min = OUT / "in.minimize"
    in_min.write_text(
        "\n".join(
            [
                "units real",
                "atom_style full",
                "boundary p p p",
                "",
                "bond_style harmonic",
                "angle_style harmonic",
                "dihedral_style harmonic",
                "special_bonds lj/coul 0.0 0.0 1.0",
                "",
                "pair_style lj/cut/coul/long 12.0",
                "kspace_style pppm 1.0e-4",
                "read_data solvent_mix_1.data",
                "include pair_coeffs.in",
                "",
                "variable run_steps index 100000",
                "",
                "neighbor 2.0 bin",
                "neigh_modify delay 0 every 1 check yes",
                "",
                "thermo 100",
                "thermo_style custom step temp pe etotal press density",
                "min_style cg",
                "minimize 1.0e-4 1.0e-6 1000 10000",
                "write_data solvent_mix_1.minimized.data",
                "",
            ]
        ),
        newline="\n",
    )

    shake_bonds = " ".join(str(x) for x in sorted(water_bond_types))
    shake_angles = " ".join(str(x) for x in sorted(water_angle_types))
    in_npt = OUT / "in.equil_npt"
    in_npt.write_text(
        "\n".join(
            [
                "units real",
                "atom_style full",
                "boundary p p p",
                "",
                "bond_style harmonic",
                "angle_style harmonic",
                "dihedral_style harmonic",
                "special_bonds lj/coul 0.0 0.0 1.0",
                "",
                "pair_style lj/cut/coul/long 12.0",
                "kspace_style pppm 1.0e-4",
                "read_data solvent_mix_1.minimized.data",
                "include pair_coeffs.in",
                "",
                "neighbor 2.0 bin",
                "neigh_modify delay 0 every 1 check yes",
                "",
                "velocity all create 300.0 4928459 mom yes rot yes dist gaussian",
                f"fix water all shake 1.0e-4 20 0 b {shake_bonds} a {shake_angles}",
                "fix ensemble all npt temp 300.0 300.0 100.0 iso 1.0 1.0 1000.0",
                "",
                "timestep 1.0",
                "thermo 1000",
                "thermo_style custom step temp press pe etotal density vol",
                "dump traj all custom 1000 solvent_mix_1.lammpstrj id mol type q x y z",
                "run ${run_steps}",
                "",
                "write_data solvent_mix_1.equil.data",
                "",
            ]
        ),
        newline="\n",
    )

    readme = OUT / "README_LAMMPS.md"
    readme.write_text(
        "\n".join(
            [
                "# LAMMPS model for solvent_mix_1",
                "",
                "Generated from `../solvent_mix_1.gro`, `../topol_solvent_mix_5.top`, `../gromos54a7.ff`, and `../toppar/OTF.itp`.",
                "",
                "The active composition in the topology is:",
                "",
                "- 1044 SPC/E water molecules (`SOL`)",
                "- 18 zinc ions (`ZN`, +2)",
                "- 36 triflate/OTF anions (`BFAF`, -1)",
                "",
                "Files:",
                "",
                "- `solvent_mix_1.data`: LAMMPS full-style topology and coordinates",
                "- `pair_coeffs.in`: LJ pair coefficients converted from GROMOS C6/C12 parameters",
                "- `in.minimize`: energy minimization input",
                "- `in.equil_npt`: short 300 K / 1 atm NPT equilibration input; run `in.minimize` first",
                "",
                "Run from this directory with, for example:",
                "",
                "```bash",
                "lmp -in in.minimize",
                "lmp -in in.equil_npt",
                "```",
                "",
                "Notes:",
                "",
                "- The Packmol input defines a 50 A cubic box. The GRO coordinates are in nm, but its box line is `50 50 50`; the generated LAMMPS data therefore uses a 50 A box and coordinates converted to Angstrom.",
                "- GROMOS G96 bonds/angles are represented by harmonic small-displacement equivalents. Water uses flexible SPC/E coefficients for minimization and SHAKE during dynamics.",
                "- Nonbonded interactions use `lj/cut/coul/long 12.0` with PPPM, matching the 1.2 nm GROMACS cutoff.",
                "",
            ]
        ),
        newline="\n",
    )

    print(f"Wrote {data_path}")
    print(f"Wrote {pair_file}")
    print(f"Wrote {in_min}")
    print(f"Wrote {in_npt}")
    print(f"Wrote {readme}")
    print(f"Atoms: {len(lmp_atoms)}, bonds: {len(lmp_bonds)}, angles: {len(lmp_angles)}, dihedrals: {len(lmp_dihedrals)}")
    print(f"Box: {box_ang[0]:.3f} x {box_ang[1]:.3f} x {box_ang[2]:.3f} A")


if __name__ == "__main__":
    main()
