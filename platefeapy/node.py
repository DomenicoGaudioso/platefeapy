"""Nodo della piastra."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class Node:
    """Nodo a 3 gradi di liberta' (w, theta_x, theta_y).

    L'ordine dei gradi di liberta' nodali e':
        [w, theta_x, theta_y]

    dove w e' lo spostamento trasversale (out-of-plane),
    theta_x e' la rotazione attorno all'asse X globale,
    theta_y e' la rotazione attorno all'asse Y globale.
    """

    id: int
    x: float
    y: float

    @property
    def coords(self) -> np.ndarray:
        return np.array([self.x, self.y], dtype=float)
