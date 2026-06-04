---
layout: default
title: "05 - Loads"
parent: English
nav_order: 5
---

# 05 - Loads

platefeapy supports all major load types for static analysis of plate structures.

## Pressure loads

Uniform pressure on element surfaces (positive towards +Z):

```python
# Uniform pressure on one element
m.add_pressure(elem, p=-1000.0)       # 1 kPa downward

# Apply to all elements
for eid in m.elements:
    m.add_pressure(eid, p=-5000.0)
```

Pressure is converted to equivalent nodal forces via numerical integration:

```
f_i = ∫ N_i · p dA
```

### Patch load (partial pressure)

```python
# Pressure on a portion of the element (natural coordinates [-1,1]²)
m.add_patch_load(elem, p=-2000.0,
                 xi_range=(-0.5, 0.5),
                 eta_range=(-0.5, 0.5))
```

## Nodal loads

Forces and moments applied directly at nodes (global system):

```python
m.add_nodal_load(node, Fz=-10000, Mx=0, My=500, case="G")
```

| Parameter | Description |
|-----------|-------------|
| `Fz` | Transverse force [N] (positive +Z) |
| `Mx` | Moment about global X [Nm] |
| `My` | Moment about global Y [Nm] |

## Thermal loads

Temperature gradient through the plate thickness:

```python
# Temperature difference between top and bottom surfaces
m.add_thermal_load(elem, dT=30.0)
```

The thermal gradient produces curvature:

```
κ = α · ΔT / t
```

where `α` is the thermal expansion coefficient and `t` is the thickness.
The resulting thermal moment is:

```
M_thermal = D · (1 + ν) · κ
```

This moment is applied as equivalent nodal forces.

## Settlements

Imposed displacements or rotations at nodes:

```python
m.add_settlement(node, "w", -0.005)        # vertical settlement 5 mm
m.add_settlement(node, "theta_x", 0.001)   # imposed rotation
```

The DOF can be: `w`, `theta_x`, `theta_y`.

## Assignment to Load Cases

Each load can have a `case`:

```python
m.add_pressure(1, p=-5000.0, case="G")          # permanent
m.add_nodal_load(5, Fz=-20000, case="Q")         # variable
m.add_thermal_load(2, dT=20.0, case="T")          # thermal

m.load_cases()                    # → ['G', 'Q', 'T']
res = m.solve(cases=["G", "Q"])    # combination
res = m.solve(cases="G")           # single case
res = m.solve()                     # all loads
```

## Combinations with coefficients

```python
res = m.solve(cases={"G": 1.35, "Q": 1.5})        # ULS combination
res = m.solve(cases={"G": 1.0, "Q": 0.3})          # SLS combination
```

All results (displacements, reactions, internal forces) respect the coefficients.

## Illustrated examples

**Simply supported plate under uniform pressure:**

```python
m = Model()
# ... create mesh ...
for eid in m.elements:
    m.add_pressure(eid, p=-1000.0)
for nid in boundary_nodes:
    m.fix(nid, ["w"])
res = m.solve()
```

**Clamped plate with concentrated load:**

```python
m.add_nodal_load(center_node, Fz=-50000.0)
for nid in boundary_nodes:
    m.fix(nid)    # all 3 DOFs
```

See [Usage Examples](en-14-usage-examples.md) for complete scripts.
