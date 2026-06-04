---
layout: default
title: "15 - Web UI"
parent: English
nav_order: 15
---

# 15 - Web UI (Streamlit)

platefeapy includes a Streamlit web application for interactive plate analysis.

## Installation

```bash
pip install platefeapy streamlit plotly
```

## Launch

```bash
streamlit run app.py
```

The app opens in your default browser at `http://localhost:8501`.

## Interface layout

The web UI has three tabs:

### Modello (Model)

Define the plate model through editable tables:

- **Nodi**: node ID, X, Y coordinates
- **Materiali**: material name, E, nu, alpha, rho
- **Sezioni**: section name, thickness t, shear factor kappa
- **Elementi**: element ID, node IDs (N1-N4), material, section, theory
- **Vincoli**: node ID, W, Rx, Ry (boolean checkboxes)
- **Carichi nodali**: node ID, Fz, Mx, My, Case
- **Pressioni**: element ID, pressure p, Case

Click **Applica modifiche** to rebuild the model.

### Analisi (Analysis)

Choose analysis type:

- **Statica**: solve the static problem
- **Modale**: compute natural frequencies and mode shapes

Options:
- Sparse solver (for large models)
- Number of modes (for modal analysis)

### Risultati (Results)

Visualize results:

- **Deformata**: 3D deformed shape with scale factor
- **Contour maps**: Mx, My, Mxy, Qx, Qy, w
- **Nodal displacements**: table of [w, θx, θy] per node
- **Mode shapes**: 3D visualization of each mode
- **Frequency table**: natural frequencies and periods

## Example workflow

1. **Define nodes**: create a 4×4 grid (25 nodes)
2. **Add material**: E=210e9, nu=0.3
3. **Add section**: t=0.01
4. **Create elements**: 16 quadrilateral plates
5. **Apply supports**: simply supported edges (W=1 on boundary)
6. **Apply pressure**: p=-1000 on all elements
7. **Run static analysis**
8. **View results**: deformed shape, moment contours

## Screenshots

The web UI provides:
- Interactive 3D visualization (rotate, zoom, pan)
- Editable tables with add/remove rows
- Real-time model preview
- Export capabilities (planned)

## Limitations

- No Excel import (planned)
- No HDF5 export (planned)
- Limited to the features available in the Python API

## Programmatic access

The web UI uses the same Python API as the library:

```python
from platefeapy import Model, Material, ShellSection

# The web UI builds this model from the tables
m = Model()
# ... add nodes, elements, loads ...
res = m.solve()
```
