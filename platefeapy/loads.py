"""Carichi per piastre: pressione, nodali, termici."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

DOF_NAMES = ["w", "theta_x", "theta_y"]
DOF_INDEX = {name: i for i, name in enumerate(DOF_NAMES)}


@dataclass
class NodalLoad:
    """Forza/momento concentrato applicato a un nodo.

    Convenzione: Fz forza trasversale; Mx, My momenti attorno agli assi X, Y.
    """

    node: int
    Fz: float = 0.0
    Mx: float = 0.0
    My: float = 0.0

    def vector(self) -> np.ndarray:
        return np.array([self.Fz, self.Mx, self.My], float)


@dataclass
class PressureLoad:
    """Pressione uniforme su un elemento piastra.

    Parametri
    ---------
    elem : int
        Id dell'elemento caricato.
    p : float
        Pressione [N/m^2], positiva verso +Z.
    """

    elem: int
    p: float


@dataclass
class PatchLoad:
    """Carico a chiazza (pressione su porzione di elemento).

    Parametri
    ---------
    elem : int
        Id dell'elemento.
    p : float
        Pressione.
    xi_range, eta_range : tuple
        Intervalli nel dominio naturale [-1,1]^2.
    """

    elem: int
    p: float
    xi_range: tuple[float, float] = (-1.0, 1.0)
    eta_range: tuple[float, float] = (-1.0, 1.0)


@dataclass
class ThermalLoad:
    """Carico termico su piastra (gradiente attraverso lo spessore).

    Parametri
    ---------
    elem : int
        Id dell'elemento.
    dT : float
        Differenza di temperatura tra estradosso e intradosso.
        dT > 0 produce curvatura con estradosso in compressione.
    """

    elem: int
    dT: float

    def curvature(self, alpha: float, t: float) -> float:
        """Curvatura termica kappa = alpha * dT / t."""
        return alpha * self.dT / t


@dataclass
class Settlement:
    """Cedimento nodale: spostamento o rotazione imposta.

    Parametri
    ---------
    node : int
        Id del nodo.
    dof : str
        Uno tra 'w', 'theta_x', 'theta_y'.
    value : float
        Valore imposto.
    """

    node: int
    dof: str
    value: float

    def __post_init__(self) -> None:
        self.dof = self.dof.lower()
        if self.dof not in DOF_INDEX:
            raise ValueError(f"dof non valido: {self.dof}")

    @property
    def local_index(self) -> int:
        return DOF_INDEX[self.dof]
