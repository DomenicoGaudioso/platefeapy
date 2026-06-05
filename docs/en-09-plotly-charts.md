---
layout: default
title: "09 - Plotly Charts"
parent: English
nav_order: 9
---

# 09 - Plotly Charts

platefeapy provides 6 interactive visualization functions based on Plotly.

## Installation

```bash
pip install platefeapy[plot]
```

## Available functions

### plot_mesh(m, show_node_ids=True)

2D mesh visualization with node IDs:

```python
from platefeapy.plotting import plot_mesh
fig = plot_mesh(m)
fig.show()
```

### plot_deformed(result, scale=1.0, n=21)

3D deformed shape with color-coded displacement:

```python
from platefeapy.plotting import plot_deformed
plot_deformed(res, scale=100).show()
```

The deformed shape is rendered as a point cloud with element edges. The `scale`
parameter amplifies the displacement for visualization.

### plot_contour(result, component="Mx", n=11, title=None, show_isolines=True)

2D contour map of a field component:

```python
from platefeapy.plotting import plot_contour

# Bending moment Mx
plot_contour(res, "Mx").show()

# More/fewer separation lines between contour bands
plot_contour(res, "Mx", n_isolines=12).show()

# Bending moment My
plot_contour(res, "My").show()

# Twisting moment Mxy
plot_contour(res, "Mxy").show()

# Shear forces
plot_contour(res, "Qx").show()
plot_contour(res, "Qy").show()

# Transverse displacement
plot_contour(res, "w").show()
```

Available components: `Mx`, `My`, `Mxy`, `Qx`, `Qy`, `w`.

The contour is rendered as a scatter plot with color-coded values at `n×n`
points per element. Iso-lines are drawn over the same sampled element
triangulation to show the separation between value bands.

### plot_supports(model)

Constrained nodes and active DOFs:

```python
from platefeapy.plotting import plot_supports
plot_supports(m).show()
```

### plot_reactions(result, scale=1.0)

Support reactions at constrained nodes:

```python
from platefeapy.plotting import plot_reactions
plot_reactions(res).show()
```

Reactions are displayed as triangle markers with force values.

### plot_mode(modal_result, i=0, scale=1.0, n=21)

3D mode shape visualization:

```python
from platefeapy.plotting import plot_mode

# First mode
plot_mode(mr, i=0, scale=100).show()

# Second mode
plot_mode(mr, i=1, scale=100).show()
```

The mode shape is rendered as a point cloud with the natural frequency and
period in the title.

## Saving figures

```python
fig = plot_contour(res, "Mx")
fig.write_html("moment_Mx.html", include_plotlyjs="cdn")
fig.write_image("moment_Mx.png", width=1200, height=800)  # requires kaleido
```

## Complete example

```python
from platefeapy import Model, Material, ShellSection
from platefeapy.plotting import plot_mesh, plot_deformed, plot_contour

# Create model
m = Model()
# ... add nodes, elements, loads ...
res = m.solve()

# Visualize
plot_mesh(m).show()
plot_deformed(res, scale=100).show()
plot_contour(res, "Mx").show()
plot_contour(res, "My").show()
plot_contour(res, "w").show()
```

## Color maps

All contour plots use the `RdYlBu` colorscale:
- **Red**: positive values (or high magnitude)
- **Blue**: negative values (or low magnitude)
- **Yellow/white**: near zero

The colorbar shows the value range with units.
