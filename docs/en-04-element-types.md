---
layout: default
title: "04 - Element Types"
parent: English
nav_order: 4
---

# 04 - Element Types

platefeapy provides two plate element formulations, both quadrilateral with 4 nodes
and 3 DOFs per node (12 DOFs total per element).

## Mindlin-Reissner (MindlinPlateQ4)

**Thick plate** formulation that includes transverse shear deformation.

### Key features

- **Shear deformable**: valid for both thick and thin plates
- **SRI integration** (Selective Reduced Integration): 2×2 Gauss for bending, 1×1 for shear — avoids shear locking in thin plates
- **Bilinear shape functions**: standard Q4 interpolation
- **3 DOFs per node**: `[w, θx, θy]`

### When to use

- General purpose: works for any thickness ratio `t/L`
- Thick plates (`t/L > 0.05`): shear deformation is significant
- Default choice for most applications

### Stiffness matrix

The stiffness is split into bending and shear contributions:

```
K = K_bending (2×2 Gauss) + K_shear (1×1 Gauss)
```

The reduced integration on the shear part prevents the well-known **shear locking**
phenomenon that affects standard Mindlin elements for thin plates.

```python
m.add_plate(id, nodes, mat, sec, theory="mindlin")
```

## Kirchhoff-Love (KirchhoffPlateQ4)

**Thin plate** formulation that neglects transverse shear deformation.

### Key features

- **No shear deformation**: valid only for thin plates (`t/L < 0.05`)
- **ACM element** (Adini-Clough-Melosh): incomplete cubic displacement field
- **No shear locking**: inherently free from the locking problem
- **3 DOFs per node**: `[w, θx, θy]`

### When to use

- Thin plates only (`t/L < 0.05`)
- When shear deformation is negligible
- Slightly faster than Mindlin (no shear integration)

### Limitation

The ACM element assumes a **rectangular** geometry. For non-rectangular
quadrilaterals, the element uses average semi-dimensions as an approximation.

```python
m.add_plate(id, nodes, mat, sec, theory="kirchhoff")
```

## Comparison

| Feature | Mindlin (SRI) | Kirchhoff (ACM) |
|---------|--------------|-----------------|
| Thickness range | Any | Thin only (t/L < 0.05) |
| Shear deformation | Yes | No |
| Shear locking | Avoided by SRI | Not applicable |
| Non-rectangular geometry | Exact | Approximate |
| Integration | 2×2 + 1×1 | 3×3 |
| DOFs per element | 12 | 12 |

## Convergence study

For a simply supported square plate (L=1m, t=10mm, p=1kPa):

| Mesh | Mindlin error | Kirchhoff error |
|------|--------------|-----------------|
| 2×2 | ~15% | ~20% |
| 4×4 | ~5% | ~8% |
| 8×8 | ~1.5% | ~2% |
| 16×16 | ~0.4% | ~0.5% |

Both elements converge to the Navier analytical solution `w = 0.00406·p·L⁴/D`.
