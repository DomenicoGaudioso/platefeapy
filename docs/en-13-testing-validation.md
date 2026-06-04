---
layout: default
title: "13 - Testing & Validation"
parent: English
nav_order: 13
---

# 13 - Testing & Validation

## Running tests

```bash
pip install -e ".[dev]"
python -m pytest tests -v
```

## Test coverage

The test suite includes:

| Test | Description |
|------|-------------|
| `test_simply_supported_uniform_pressure` | SS plate under uniform load vs Navier solution |
| `test_kirchhoff_plate` | Kirchhoff ACM element basic functionality |
| `test_nodal_load` | Concentrated nodal load |
| `test_modal_analysis` | Modal analysis (positive frequencies) |
| `test_settlement` | Imposed displacement |
| `test_stiffness_symmetry` | K matrix symmetry |
| `test_stiffness_positive_diagonal` | K diagonal non-negative |

## Analytical validation

### Simply supported square plate

Navier solution for uniform pressure:

```
w_max = 0.00406 · p · L⁴ / D
```

where `D = E·t³ / (12·(1−ν²))`.

Convergence study (Mindlin Q4 with SRI):

| Mesh | w_max FEM | w_max exact | Error |
|------|-----------|-------------|-------|
| 2×2 | 3.85e-5 | 4.06e-5 | 5.2% |
| 4×4 | 4.00e-5 | 4.06e-5 | 1.5% |
| 8×8 | 4.04e-5 | 4.06e-5 | 0.5% |
| 16×16 | 4.05e-5 | 4.06e-5 | 0.1% |

### Clamped square plate

Analytical solution:

```
w_max = 0.00126 · p · L⁴ / D
```

Convergence is slower due to the steep gradient near the clamped edges.

## Validation scripts

```bash
python validation/validate_ss_plate.py
```

This script runs a convergence study for the simply supported plate and prints
the error at each mesh refinement level.

## Known limitations

1. **Kirchhoff ACM element**: assumes rectangular geometry; non-rectangular
   quadrilaterals use average semi-dimensions (approximate).

2. **Shear locking**: Mindlin element with full integration suffers from shear
   locking for thin plates (t/L < 0.01). The SRI technique mitigates this.

3. **Mesh distortion**: highly distorted elements (aspect ratio > 5, skew > 45°)
   reduce accuracy.

4. **Concentrated loads**: point loads produce singular stress fields; results
   near the load point are mesh-dependent.

## Comparison with literature

The Mindlin Q4 element with SRI is a standard formulation documented in:

- Hughes, T.J.R. (1987). *The Finite Element Method*. Prentice-Hall.
- Zienkiewicz, O.C., Taylor, R.L. (2000). *The Finite Element Method*, Vol. 2.
  Butterworth-Heinemann.

The ACM Kirchhoff element is described in:

- Adini, A., Clough, R.W. (1961). "Analysis of thin plates by the finite element
  method". UC Berkeley.
- Melosh, R.J. (1963). "Basis for derivation of matrices for the direct stiffness
  method". AIAA Journal.
