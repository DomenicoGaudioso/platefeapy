---
layout: default
title: "03 - Structural Model"
parent: English
nav_order: 3
---

# 03 - Structural Model

## Nodes

Each node has 3 degrees of freedom (DOFs): `[w, theta_x, theta_y]`.

```python
m.add_node(id, x, y)   # id = integer identifier, coordinates in meters
```

Example:
```python
m.add_node(1, 0, 0)    # origin
m.add_node(2, 5, 0)    # 5 m along X
m.add_node(3, 5, 3)    # 5 m in X, 3 m in Y
m.add_node(4, 0, 3)    # corner
```

## Materials

```python
mat = Material(E=210e9, nu=0.3, alpha=1.2e-5)   # steel
mat = Material(E=30e9, nu=0.2, alpha=1.0e-5)       # concrete
```

| Parameter | Description | Default |
|-----------|-------------|---------|
| `E` | Young's modulus [Pa] | required |
| `nu` | Poisson's ratio | 0.3 |
| `alpha` | Thermal expansion coefficient [1/°C] | 0.0 |
| `G` | Shear modulus [Pa] | computed from E and nu |
| `rho` | Density [kg/m³] | 0.0 |

## Sections

```python
sec = ShellSection(t=0.01)              # 10 mm plate
sec = ShellSection(t=0.20, kappa=5/6)   # 200 mm with shear correction
```

| Parameter | Description | Default |
|-----------|-------------|---------|
| `t` | Plate thickness [m] | required |
| `kappa` | Shear correction factor | 5/6 |

### Derived properties

```python
D = sec.D_bending(E, nu)     # flexural rigidity: E·t³/(12·(1−ν²))
Ds = sec.D_shear(G)           # shear rigidity: κ·G·t
C = sec.D_membrane(E, nu)    # membrane rigidity: E·t/(1−ν²)
```

## Elements

### Adding a plate element

```python
m.add_plate(id, [n1, n2, n3, n4], material, section, theory="mindlin")
```

Nodes must be ordered **counter-clockwise** when viewed from +Z:

```
  4 --- 3
  |     |
  1 --- 2
```

### Element theories

| Theory | Keyword | Description |
|--------|---------|-------------|
| Mindlin-Reissner | `"mindlin"` | Thick plates, shear deformable, SRI integration |
| Kirchhoff-Love | `"kirchhoff"` | Thin plates, ACM element, no shear deformation |

See [Element Types](en-04-element-types.md) for details.

## Supports

```python
m.fix(node)                              # fixed: all 3 DOFs restrained
m.pin(node)                              # simple support: w only
m.support(node, w=True, theta_x=True)    # custom: only specified DOFs
```

| Method | Restrained DOFs | Typical use |
|--------|-----------------|-------------|
| `fix(n)` | w, theta_x, theta_y | Fixed (clamped) edge |
| `pin(n)` | w | Simply supported edge |
| `support(n,...)` | custom | Symmetry, guided edge |

Examples:
```python
# Clamped edge
m.fix(1)

# Simply supported (w=0, rotations free)
m.pin(2)

# Symmetry: w and theta_x fixed, theta_y free
m.support(3, w=True, theta_x=True)

# Guided: rotations fixed, w free
m.support(4, theta_x=True, theta_y=True)
```

## Solution

```python
res = m.solve()                   # dense solver (default)
res = m.solve(sparse=True)        # sparse solver (large models)
res = m.solve(cases=["G", "Q"])    # specific load cases
```

See [Solution](en-07-solution.md) for details.
