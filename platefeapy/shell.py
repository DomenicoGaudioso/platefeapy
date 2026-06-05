"""Elementi shell Q4 su geometria 3D reale.

Questo modulo affianca il solutore piastra piano esistente. Usa nodi 3D con
6 gradi di liberta' globali per nodo:
    [ux, uy, uz, rx, ry, rz]

Ogni elemento Q4 costruisce una terna locale dalla geometria reale, combina una
membrana bilineare in tensione piana con la flessione Mindlin gia' disponibile
e trasforma la rigidezza in coordinate globali.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .element import MindlinPlateQ4
from .material import Material
from .node import Node
from .section import ShellSection


SHELL_DOF_NAMES = ["ux", "uy", "uz", "rx", "ry", "rz"]
SHELL_DOF_INDEX = {name: i for i, name in enumerate(SHELL_DOF_NAMES)}


@dataclass
class ShellNode:
    id: int
    x: float
    y: float
    z: float

    @property
    def coords(self) -> np.ndarray:
        return np.array([self.x, self.y, self.z], dtype=float)


@dataclass
class ShellResult:
    model: "ShellModel"
    U: np.ndarray
    R: np.ndarray

    def displacements(self, node: int) -> np.ndarray:
        return self.U[self.model.dof_map[node]]

    def reactions(self, node: int) -> np.ndarray:
        return self.R[self.model.dof_map[node]]

    def displacement(self, node: int, dof: str) -> float:
        return float(self.U[self.model.dof_map[node][SHELL_DOF_INDEX[dof.lower()]]])


class ShellQ4:
    n_nodes = 4
    n_dof = 24

    def __init__(self, id: int, nodes: list[ShellNode],
                 material: Material, section: ShellSection) -> None:
        if len(nodes) != 4:
            raise ValueError(f"Elemento shell {id}: servono 4 nodi.")
        self.id = id
        self.nodes = nodes
        self.material = material
        self.section = section

    @property
    def node_ids(self) -> list[int]:
        return [n.id for n in self.nodes]

    def _coords3d(self) -> np.ndarray:
        return np.array([n.coords for n in self.nodes], dtype=float)

    def _basis(self) -> tuple[np.ndarray, np.ndarray]:
        c = self._coords3d()
        e1 = c[1] - c[0]
        e1 /= np.linalg.norm(e1)
        diag_a = c[2] - c[0]
        diag_b = c[3] - c[1]
        e3 = np.cross(diag_a, diag_b)
        nrm = np.linalg.norm(e3)
        if nrm < 1e-12:
            raise ValueError(f"Elemento shell {self.id}: normale degenere.")
        e3 /= nrm
        e2 = np.cross(e3, e1)
        e2 /= np.linalg.norm(e2)
        basis = np.column_stack([e1, e2, e3])
        origin = c.mean(axis=0)
        return basis, origin

    def _coords2d(self) -> np.ndarray:
        basis, origin = self._basis()
        rel = self._coords3d() - origin
        local = rel @ basis
        return local[:, :2]

    @staticmethod
    def _shape_derivatives(xi: float, eta: float) -> np.ndarray:
        dNdxi = 0.25 * np.array([
            -(1 - eta), (1 - eta), (1 + eta), -(1 + eta)
        ])
        dNdeta = 0.25 * np.array([
            -(1 - xi), -(1 + xi), (1 + xi), (1 - xi)
        ])
        return np.vstack([dNdxi, dNdeta])

    def _membrane_stiffness_local(self) -> np.ndarray:
        coords = self._coords2d()
        E = self.material.E
        nu = self.material.nu
        t = self.section.t
        D = E / (1.0 - nu ** 2) * np.array([
            [1.0, nu, 0.0],
            [nu, 1.0, 0.0],
            [0.0, 0.0, (1.0 - nu) / 2.0],
        ])
        K = np.zeros((8, 8))
        g = 1.0 / np.sqrt(3.0)
        for xi in (-g, g):
            for eta in (-g, g):
                dN = self._shape_derivatives(xi, eta)
                J = dN @ coords
                detJ = float(np.linalg.det(J))
                if abs(detJ) < 1e-14:
                    raise ValueError(f"Elemento shell {self.id}: Jacobiano membrana singolare.")
                dNxy = np.linalg.inv(J) @ dN
                B = np.zeros((3, 8))
                for a in range(4):
                    B[0, 2 * a] = dNxy[0, a]
                    B[1, 2 * a + 1] = dNxy[1, a]
                    B[2, 2 * a] = dNxy[1, a]
                    B[2, 2 * a + 1] = dNxy[0, a]
                K += B.T @ D @ B * t * abs(detJ)
        return K

    def _plate_stiffness_local(self) -> np.ndarray:
        coords = self._coords2d()
        nodes = [Node(i + 1, float(x), float(y)) for i, (x, y) in enumerate(coords)]
        plate = MindlinPlateQ4(self.id, nodes, self.material, self.section)
        return plate.stiffness_local()

    def stiffness_local(self) -> np.ndarray:
        K = np.zeros((24, 24))
        Km = self._membrane_stiffness_local()
        Kb = self._plate_stiffness_local()
        for a in range(4):
            for b in range(4):
                # Membrana: local u,v.
                K[6*a:6*a+2, 6*b:6*b+2] += Km[2*a:2*a+2, 2*b:2*b+2]
                # Flessione Mindlin: local w, rx, ry.
                map_a = [6*a + 2, 6*a + 3, 6*a + 4]
                map_b = [6*b + 2, 6*b + 3, 6*b + 4]
                K[np.ix_(map_a, map_b)] += Kb[3*a:3*a+3, 3*b:3*b+3]
        # Piccola rigidezza drilling per evitare singolarita' su rz.
        diag_ref = max(float(np.max(np.diag(K))), 1.0)
        for a in range(4):
            K[6*a + 5, 6*a + 5] += diag_ref * 1e-8
        return K

    def _transform(self) -> np.ndarray:
        basis, _ = self._basis()
        block = basis.T
        T = np.zeros((24, 24))
        for a in range(4):
            T[6*a:6*a+3, 6*a:6*a+3] = block
            T[6*a+3:6*a+6, 6*a+3:6*a+6] = block
        return T

    def stiffness_global(self) -> np.ndarray:
        T = self._transform()
        return T.T @ self.stiffness_local() @ T

    def global_dofs(self, dof_map: dict[int, np.ndarray]) -> np.ndarray:
        return np.concatenate([dof_map[n.id] for n in self.nodes])

    def area(self) -> float:
        c = self._coords3d()
        return (
            0.5 * np.linalg.norm(np.cross(c[1] - c[0], c[2] - c[0]))
            + 0.5 * np.linalg.norm(np.cross(c[2] - c[0], c[3] - c[0]))
        )

    def equivalent_pressure_global(self, p: float) -> np.ndarray:
        basis, _ = self._basis()
        normal = basis[:, 2]
        nodal = p * self.area() / 4.0 * normal
        f = np.zeros(24)
        for a in range(4):
            f[6*a:6*a+3] = nodal
        return f


class ShellModel:
    def __init__(self) -> None:
        self.nodes: dict[int, ShellNode] = {}
        self.elements: dict[int, ShellQ4] = {}
        self.pressures: list[tuple[int, float]] = []
        self.nodal_loads: list[tuple[int, np.ndarray]] = []
        self._prescribed: dict[int, float] = {}
        self._dof_map: dict[int, np.ndarray] | None = None

    def add_node(self, id: int, x: float, y: float, z: float) -> ShellNode:
        node = ShellNode(id, x, y, z)
        self.nodes[id] = node
        self._dof_map = None
        return node

    def add_shell(self, id: int, node_ids: list[int],
                  material: Material, section: ShellSection) -> ShellQ4:
        el = ShellQ4(id, [self.nodes[nid] for nid in node_ids], material, section)
        self.elements[id] = el
        return el

    @property
    def dof_map(self) -> dict[int, np.ndarray]:
        if self._dof_map is None:
            self._dof_map = {
                nid: np.arange(6 * i, 6 * i + 6)
                for i, nid in enumerate(sorted(self.nodes))
            }
        return self._dof_map

    @property
    def ndof(self) -> int:
        return 6 * len(self.nodes)

    def fix(self, node: int, dofs: list[str] | None = None) -> None:
        names = SHELL_DOF_NAMES if dofs is None else [d.lower() for d in dofs]
        for name in names:
            self._prescribed[self.dof_map[node][SHELL_DOF_INDEX[name]]] = 0.0

    def add_pressure(self, elem: int, p: float) -> None:
        self.pressures.append((elem, p))

    def add_nodal_load(self, node: int, **comps: float) -> None:
        f = np.zeros(6)
        for name, value in comps.items():
            f[SHELL_DOF_INDEX[name.lower()]] = float(value)
        self.nodal_loads.append((node, f))

    def assemble_stiffness(self) -> np.ndarray:
        K = np.zeros((self.ndof, self.ndof))
        for el in self.elements.values():
            ed = el.global_dofs(self.dof_map)
            K[np.ix_(ed, ed)] += el.stiffness_global()
        return K

    def assemble_loads(self) -> np.ndarray:
        F = np.zeros(self.ndof)
        for nid, f in self.nodal_loads:
            F[self.dof_map[nid]] += f
        for eid, p in self.pressures:
            el = self.elements[eid]
            F[el.global_dofs(self.dof_map)] += el.equivalent_pressure_global(p)
        return F

    def solve(self) -> ShellResult:
        K = self.assemble_stiffness()
        F = self.assemble_loads()
        p_idx = np.array(sorted(self._prescribed), dtype=int)
        if p_idx.size == 0:
            raise ValueError("Nessun vincolo: struttura labile.")
        free = np.array([i for i in range(self.ndof) if i not in self._prescribed], dtype=int)
        U = np.zeros(self.ndof)
        U[p_idx] = [self._prescribed[i] for i in p_idx]
        rhs = F[free] - K[np.ix_(free, p_idx)] @ U[p_idx]
        U[free] = np.linalg.solve(K[np.ix_(free, free)], rhs)
        R = K @ U - F
        R[free] = 0.0
        return ShellResult(self, U, R)
