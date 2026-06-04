"""Sezione della piastra (spessore e proprieta')."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ShellSection:
    """Proprieta' della sezione di piastra/guscio.

    Parametri
    ---------
    t : float
        Spessore della piastra.
    kappa : float
        Fattore di correzione al taglio (shear correction factor).
        Default 5/6 per piastre di Mindlin-Reissner.
    name : str
        Etichetta opzionale.
    """

    t: float
    kappa: float = 5.0 / 6.0
    name: str = ""

    def D_bending(self, E: float, nu: float) -> float:
        """Rigidezza flessionale D = E t^3 / (12 (1 - nu^2))."""
        return E * self.t**3 / (12.0 * (1.0 - nu**2))

    def D_shear(self, G: float) -> float:
        """Rigidezza al taglio Ds = kappa * G * t."""
        return self.kappa * G * self.t

    def D_membrane(self, E: float, nu: float) -> float:
        """Rigidezza membranale C = E t / (1 - nu^2)."""
        return E * self.t / (1.0 - nu**2)
