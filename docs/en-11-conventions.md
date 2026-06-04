---
layout: default
title: "11 - Conventions"
parent: English
nav_order: 11
---

# 11 - Conventions

## Nodal degrees of freedom

Each node has 3 DOFs in order: `[w, theta_x, theta_y]`

- `w`: transverse displacement (out-of-plane, +Z direction)
- `theta_x`: rotation about global X-axis
- `theta_y`: rotation about global Y-axis

## Plate geometry

- **Plate plane**: X-Y global
- **Thickness**: Z direction (out-of-plane)
- **Positive pressure**: towards +Z (upward)

## Element node ordering

Nodes must be ordered **counter-clockwise** when viewed from +Z:

```
  4 --- 3
  |     |
  1 --- 2
```

## Moment sign convention

- **Mx**: bending moment causing curvature in X-direction (about Y-axis)
- **My**: bending moment causing curvature in Y-direction (about X-axis)
- **Mxy**: twisting moment

Positive moments cause tension on the bottom surface (−Z side).

## Shear force convention

- **Qx**: shear force in X-direction
- **Qy**: shear force in Y-direction

Positive in the positive direction of the corresponding axis.

## Units

The system is **unit-agnostic**: the user chooses units as long as they are consistent.

| Quantity | SI Unit |
|----------|---------|
| Length | m |
| Thickness | m |
| Force | N |
| Pressure | Pa (N/m²) |
| Moment | Nm/m (per unit length) |
| Temperature | °C |
| Density | kg/m³ |

## Natural coordinates

Element integration uses natural coordinates `(ξ, η)` in `[-1, 1]²`:

| Point | ξ | η |
|-------|---|---|
| Node 1 | -1 | -1 |
| Node 2 | +1 | -1 |
| Node 3 | +1 | +1 |
| Node 4 | -1 | +1 |
| Center | 0 | 0 |

## Flexural rigidity

```
D = E · t³ / (12 · (1 − ν²))
```

## Shear rigidity

```
Ds = κ · G · t
```

where `κ = 5/6` is the shear correction factor for Mindlin plates.
