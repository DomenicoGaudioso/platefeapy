"""Elementi piastra: Mindlin-Reissner (Q4) e Kirchhoff-Love.

Elemento piastra Q4 di Mindlin-Reissner a 4 nodi con 3 GdL per nodo:
    [w, theta_x, theta_y]

dove:
    w       = spostamento trasversale (out-of-plane, direzione Z)
    theta_x = rotazione attorno all'asse X globale
    theta_y = rotazione attorno all'asse Y globale

Convenzione: la piastra giace nel piano X-Y globale, lo spessore e'
nella direzione Z.

L'elemento Q4 standard soffre di shear locking per piastre sottili;
si usa la tecnica di integrazione ridotta selettiva (SRI):
integrazione completa (2x2) per la parte flessionale,
integrazione ridotta (1x1) per la parte di taglio.
"""

from __future__ import annotations

import numpy as np

from .material import Material
from .node import Node
from .section import ShellSection


class MindlinPlateQ4:
    """Elemento piastra di Mindlin-Reissner quadrilatero a 4 nodi (Q4).

    12 GdL totali: [w1, thx1, thy1, w2, thx2, thy2, w3, thx3, thy3, w4, thx4, thy4]
    """

    n_dof = 12
    n_nodes = 4

    def __init__(
        self,
        id: int,
        nodes: list[Node],
        material: Material,
        section: ShellSection,
    ) -> None:
        if len(nodes) != 4:
            raise ValueError(f"Elemento {id}: servono 4 nodi per Q4.")
        self.id = id
        self.nodes = nodes
        self.material = material
        self.section = section

    @property
    def node_ids(self) -> list[int]:
        return [n.id for n in self.nodes]

    def _coords(self) -> np.ndarray:
        """Coordinate nodali (4, 2)."""
        return np.array([[n.x, n.y] for n in self.nodes], dtype=float)

    @staticmethod
    def _shape_functions(xi: float, eta: float) -> np.ndarray:
        """Funzioni di forma bilineari N1..N4 su [-1,1]^2."""
        return 0.25 * np.array([
            (1 - xi) * (1 - eta),
            (1 + xi) * (1 - eta),
            (1 + xi) * (1 + eta),
            (1 - xi) * (1 + eta),
        ])

    @staticmethod
    def _shape_derivatives(xi: float, eta: float) -> np.ndarray:
        """Derivate delle funzioni di forma rispetto a (xi, eta): shape (2, 4)."""
        dNdxi = 0.25 * np.array([
            -(1 - eta), (1 - eta), (1 + eta), -(1 + eta)
        ])
        dNdeta = 0.25 * np.array([
            -(1 - xi), -(1 + xi), (1 + xi), (1 - xi)
        ])
        return np.vstack([dNdxi, dNdeta])

    def _jacobian(self, xi: float, eta: float) -> tuple[np.ndarray, np.ndarray, float]:
        """Matrice Jacobiana, sua inversa e determinante."""
        coords = self._coords()
        dNdxi_eta = self._shape_derivatives(xi, eta)
        J = dNdxi_eta @ coords
        detJ = float(np.linalg.det(J))
        if abs(detJ) < 1e-30:
            raise ValueError(f"Elemento {self.id}: Jacobiano singolare a xi={xi}, eta={eta}.")
        Jinv = np.linalg.inv(J)
        return J, Jinv, detJ

    def _B_bending(self, xi: float, eta: float) -> np.ndarray:
        """Matrice B_b (3x12) per le curvature: [kappa_x, kappa_y, 2*kappa_xy].

        kappa_x  = d(theta_y)/dx
        kappa_y  = -d(theta_x)/dy
        kappa_xy = (d(theta_y)/dy - d(theta_x)/dx) / 2
        """
        _, Jinv, _ = self._jacobian(xi, eta)
        dNdxi_eta = self._shape_derivatives(xi, eta)
        dNdxy = Jinv @ dNdxi_eta
        dNdx = dNdxy[0, :]
        dNdy = dNdxy[1, :]

        B = np.zeros((3, 12))
        for i in range(4):
            col_w = 3 * i
            col_tx = 3 * i + 1
            col_ty = 3 * i + 2
            B[0, col_ty] = dNdx[i]
            B[1, col_tx] = -dNdy[i]
            B[2, col_ty] = dNdy[i]
            B[2, col_tx] = -dNdx[i]
        return B

    def _B_shear(self, xi: float, eta: float) -> np.ndarray:
        """Matrice B_s (2x12) per le deformazioni di taglio: [gamma_xz, gamma_yz].

        gamma_xz = dw/dx + theta_y
        gamma_yz = dw/dy - theta_x
        """
        _, Jinv, _ = self._jacobian(xi, eta)
        dNdxi_eta = self._shape_derivatives(xi, eta)
        dNdxy = Jinv @ dNdxi_eta
        dNdx = dNdxy[0, :]
        dNdy = dNdxy[1, :]

        N = self._shape_functions(xi, eta)
        Bs = np.zeros((2, 12))
        for i in range(4):
            col_w = 3 * i
            col_tx = 3 * i + 1
            col_ty = 3 * i + 2
            Bs[0, col_w] = dNdx[i]
            Bs[0, col_ty] = N[i]
            Bs[1, col_w] = dNdy[i]
            Bs[1, col_tx] = -N[i]
        return Bs

    def _Db_matrix(self) -> np.ndarray:
        """Matrice costitutiva flessionale 3x3."""
        E = self.material.E
        nu = self.material.nu
        D = self.section.D_bending(E, nu)
        Db = D * np.array([
            [1.0, nu, 0.0],
            [nu, 1.0, 0.0],
            [0.0, 0.0, (1.0 - nu) / 2.0],
        ])
        return Db

    def _Ds_matrix(self) -> np.ndarray:
        """Matrice costitutiva di taglio 2x2."""
        G = self.material.G
        Ds_val = self.section.D_shear(G)
        return Ds_val * np.eye(2)

    def stiffness_local(self) -> np.ndarray:
        """Matrice di rigidezza 12x12 con integrazione ridotta selettiva (SRI).

        Parte flessionale: integrazione completa 2x2.
        Parte di taglio: integrazione ridotta 1x1 (al centro).
        """
        K = np.zeros((12, 12))
        Db = self._Db_matrix()
        Ds = self._Ds_matrix()

        xi_g, eta_g, w_g = _gauss_points_2d(2)
        for xi, eta, w in zip(xi_g, eta_g, w_g):
            Bb = self._B_bending(xi, eta)
            _, _, detJ = self._jacobian(xi, eta)
            K += w * (Bb.T @ Db @ Bb) * abs(detJ)

        B_s = self._B_shear(0.0, 0.0)
        _, _, detJ_s = self._jacobian(0.0, 0.0)
        K += 4.0 * (B_s.T @ Ds @ B_s) * abs(detJ_s)

        return K

    def area(self) -> float:
        """Area dell'elemento (integrazione numerica)."""
        coords = self._coords()
        x, y = coords[:, 0], coords[:, 1]
        return 0.5 * abs(
            (x[0] * y[1] - x[1] * y[0]) +
            (x[1] * y[2] - x[2] * y[1]) +
            (x[2] * y[3] - x[3] * y[2]) +
            (x[3] * y[0] - x[0] * y[3])
        )

    def global_dofs(self, dof_map: dict[int, np.ndarray]) -> np.ndarray:
        """Indici globali dei 12 GdL dell'elemento."""
        return np.concatenate([dof_map[n.id] for n in self.nodes])

    def equivalent_pressure(self, p: float, n_gauss: int = 2) -> np.ndarray:
        """Forze nodali equivalenti per pressione uniforme p (positiva verso +Z).

        f_i = integrale di N_i * p dA
        """
        f = np.zeros(12)
        xi_g, eta_g, w_g = _gauss_points_2d(n_gauss)
        for xi, eta, w in zip(xi_g, eta_g, w_g):
            N = self._shape_functions(xi, eta)
            _, _, detJ = self._jacobian(xi, eta)
            for i in range(4):
                f[3 * i] += w * N[i] * p * abs(detJ)
        return f

    def stress_at(self, xi: float, eta: float, u_elem: np.ndarray) -> dict:
        """Calcola momenti e tagli al punto (xi, eta) dagli spostamenti elementali.

        Restituisce dict con: Mx, My, Mxy, Qx, Qy.
        """
        Bb = self._B_bending(xi, eta)
        Bs = self._B_shear(xi, eta)
        Db = self._Db_matrix()
        Ds = self._Ds_matrix()
        moments = Db @ Bb @ u_elem
        shears = Ds @ Bs @ u_elem
        return {
            "Mx": float(moments[0]),
            "My": float(moments[1]),
            "Mxy": float(moments[2]),
            "Qx": float(shears[0]),
            "Qy": float(shears[1]),
        }


class KirchhoffPlateQ4:
    """Elemento piastra di Kirchhoff (ACM - Adini-Clough-Melosh) a 4 nodi.

    12 GdL totali: [w1, theta_x1, theta_y1, ..., w4, theta_x4, theta_y4]

    Usa il campo di spostamento ACM (incompleto cubico) che evita
    lo shear locking per piastre sottili. Non include deformabilita'
    a taglio (valido per piastre sottili, t/L < 0.05).
    """

    n_dof = 12
    n_nodes = 4

    def __init__(
        self,
        id: int,
        nodes: list[Node],
        material: Material,
        section: ShellSection,
    ) -> None:
        if len(nodes) != 4:
            raise ValueError(f"Elemento {id}: servono 4 nodi per Q4.")
        self.id = id
        self.nodes = nodes
        self.material = material
        self.section = section

    @property
    def node_ids(self) -> list[int]:
        return [n.id for n in self.nodes]

    def _coords(self) -> np.ndarray:
        return np.array([[n.x, n.y] for n in self.nodes], dtype=float)

    def _dims(self) -> tuple[float, float]:
        """Semi-dimensioni a, b per elemento rettangolare (approssimazione)."""
        coords = self._coords()
        a = 0.5 * (abs(coords[1, 0] - coords[0, 0]) + abs(coords[2, 0] - coords[3, 0]))
        b = 0.5 * (abs(coords[3, 1] - coords[0, 1]) + abs(coords[2, 1] - coords[1, 1]))
        return a, b

    def stiffness_local(self) -> np.ndarray:
        """Matrice di rigidezza 12x12 dell'elemento ACM (Kirchhoff).

        Formulazione ACM per piastra rettangolare. Per elementi non
        rettangolari si usa l'approssimazione con le semi-dimensioni medie.
        """
        a, b = self._dims()
        E = self.material.E
        nu = self.material.nu
        t = self.section.t
        D = E * t**3 / (12.0 * (1.0 - nu**2))

        K = np.zeros((12, 12))
        xi_g, eta_g, w_g = _gauss_points_2d(3)
        for xi, eta, w in zip(xi_g, eta_g, w_g):
            B = self._B_acm(xi, eta, a, b)
            Db = D * np.array([
                [1.0, nu, 0.0],
                [nu, 1.0, 0.0],
                [0.0, 0.0, (1.0 - nu) / 2.0],
            ])
            K += w * (B.T @ Db @ B) * a * b
        return K

    def _B_acm(self, xi: float, eta: float, a: float, b: float) -> np.ndarray:
        """Matrice B (3x12) per l'elemento ACM.

        Curvature: [d2w/dx2, d2w/dy2, 2*d2w/dxdy]
        """
        B = np.zeros((3, 12))
        for i in range(4):
            xi_i = [-1, 1, 1, -1][i]
            eta_i = [-1, -1, 1, 1][i]
            x0 = xi_i * xi
            y0 = eta_i * eta

            d2N_dx2_w = 3 * xi_i / (4 * a**2) * (1 + y0) * (-1 + 2 * x0 + xi * xi)
            d2N_dx2_tx = -xi_i * b / (4 * a**2) * (1 + y0) * (-1 + 3 * xi * xi)
            d2N_dx2_ty = -3 * xi_i * a / (4 * a**2) * (1 + y0) * xi * (-1 + xi * xi) / a

            d2N_dy2_w = 3 * eta_i / (4 * b**2) * (1 + x0) * (-1 + 2 * y0 + eta * eta)
            d2N_dy2_tx = -3 * eta_i * b / (4 * b**2) * (1 + x0) * eta * (-1 + eta * eta) / b
            d2N_dy2_ty = -eta_i * a / (4 * b**2) * (1 + x0) * (-1 + 3 * eta * eta)

            d2N_dxdy_w = xi_i * eta_i / (4 * a * b) * (2 * x0 + 2 * y0 - 1 + xi * xi + eta * eta - 3 * xi * xi * eta * eta + 3 * xi * xi * eta * eta)
            d2N_dxdy_tx = -eta_i / (4 * a) * (2 * y0 - 1 + eta * eta + 3 * xi * xi * (1 - eta * eta))
            d2N_dxdy_ty = -xi_i / (4 * b) * (2 * x0 - 1 + xi * xi + 3 * eta * eta * (1 - xi * xi))

            col_w = 3 * i
            col_tx = 3 * i + 1
            col_ty = 3 * i + 2
            B[0, col_w] = d2N_dx2_w
            B[0, col_tx] = d2N_dx2_tx
            B[0, col_ty] = d2N_dx2_ty
            B[1, col_w] = d2N_dy2_w
            B[1, col_tx] = d2N_dy2_tx
            B[1, col_ty] = d2N_dy2_ty
            B[2, col_w] = 2 * d2N_dxdy_w
            B[2, col_tx] = 2 * d2N_dxdy_tx
            B[2, col_ty] = 2 * d2N_dxdy_ty
        return B

    def area(self) -> float:
        coords = self._coords()
        x, y = coords[:, 0], coords[:, 1]
        return 0.5 * abs(
            (x[0] * y[1] - x[1] * y[0]) +
            (x[1] * y[2] - x[2] * y[1]) +
            (x[2] * y[3] - x[3] * y[2]) +
            (x[3] * y[0] - x[0] * y[3])
        )

    def global_dofs(self, dof_map: dict[int, np.ndarray]) -> np.ndarray:
        return np.concatenate([dof_map[n.id] for n in self.nodes])

    def equivalent_pressure(self, p: float, n_gauss: int = 2) -> np.ndarray:
        """Forze nodali equivalenti per pressione uniforme p."""
        a, b = self._dims()
        f = np.zeros(12)
        ab = a * b
        for i in range(4):
            xi_i = [-1, 1, 1, -1][i]
            eta_i = [-1, -1, 1, 1][i]
            f[3 * i] = p * ab / 4.0
            f[3 * i + 1] = -p * ab * b * eta_i / 24.0
            f[3 * i + 2] = p * ab * a * xi_i / 24.0
        return f

    def stress_at(self, xi: float, eta: float, u_elem: np.ndarray) -> dict:
        a, b = self._dims()
        E = self.material.E
        nu = self.material.nu
        t = self.section.t
        D = E * t**3 / (12.0 * (1.0 - nu**2))
        B = self._B_acm(xi, eta, a, b)
        Db = D * np.array([
            [1.0, nu, 0.0],
            [nu, 1.0, 0.0],
            [0.0, 0.0, (1.0 - nu) / 2.0],
        ])
        moments = Db @ B @ u_elem
        return {
            "Mx": float(moments[0]),
            "My": float(moments[1]),
            "Mxy": float(moments[2]),
            "Qx": 0.0,
            "Qy": 0.0,
        }


def _gauss_points_2d(n: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Punti e pesi di Gauss 2D su [-1,1]^2."""
    xi_i, wi = np.polynomial.legendre.leggauss(n)
    eta_j, wj = np.polynomial.legendre.leggauss(n)
    xi = np.repeat(xi_i, n)
    eta = np.tile(eta_j, n)
    w = np.repeat(wi, n) * np.tile(wj, n)
    return xi, eta, w
