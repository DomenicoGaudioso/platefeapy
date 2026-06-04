"""Materiale elastico isotropo per piastre."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Material:
    """Materiale elastico lineare isotropo.

    Parametri
    ---------
    E : float
        Modulo di Young.
    nu : float
        Coefficiente di Poisson.
    alpha : float
        Coefficiente di dilatazione termica lineare (1/grado). Default 0.
    G : float, opzionale
        Modulo di taglio. Se non fornito viene derivato da E e nu come
        G = E / (2 (1 + nu)).
    rho : float
        Densita' di massa.
    name : str
        Etichetta opzionale.
    """

    E: float
    nu: float = 0.3
    alpha: float = 0.0
    G: float | None = None
    rho: float = 0.0
    name: str = ""

    def __post_init__(self) -> None:
        if self.G is None:
            self.G = self.E / (2.0 * (1.0 + self.nu))
