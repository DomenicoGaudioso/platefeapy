"""Quadratura di Gauss-Legendre per l'integrazione delle forze equivalenti."""

from __future__ import annotations

import numpy as np


def gauss_legendre_2d(nx: int, ny: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Punti e pesi di Gauss-Legendre 2D su [-1,1] x [-1,1].

    Parametri
    ---------
    nx, ny : int
        Numero di punti di Gauss nelle direzioni xi e eta.

    Restituisce
    -----------
    (xi, eta, w) : tuple di ndarray
        Coordinate e pesi nel dominio naturale.
    """
    xi_i, wi = np.polynomial.legendre.leggauss(nx)
    eta_j, wj = np.polynomial.legendre.leggauss(ny)
    xi = np.repeat(xi_i, ny)
    eta = np.tile(eta_j, nx)
    w = np.repeat(wi, ny) * np.tile(wj, nx)
    return xi, eta, w


def gauss_legendre_1d(a: float, b: float, n: int = 4) -> tuple[np.ndarray, np.ndarray]:
    """Punti e pesi di Gauss-Legendre sull'intervallo [a, b]."""
    xi, wi = np.polynomial.legendre.leggauss(n)
    half = 0.5 * (b - a)
    mid = 0.5 * (b + a)
    x = mid + half * xi
    w = half * wi
    return x, w
