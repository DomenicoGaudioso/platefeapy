---
layout: default
title: "01 - Installation"
parent: English
nav_order: 1
---

# 01 - Installation

## Requirements

- Python >= 3.9
- numpy >= 1.24
- scipy >= 1.10
- gmsh >= 4.12 for Gmsh-backed case-study meshes

## Installation

### From source (development)

```bash
git clone https://github.com/DomenicoGaudioso/platefeapy.git
cd platefeapy
pip install -e ".[all]"
```

### Base dependencies only

```bash
pip install -e .
```

## Extras

| Extra | Packages | Description |
|-------|----------|-------------|
| `plot` | plotly, kaleido | Interactive Plotly charts |
| `mesh` | gmsh | Gmsh mesh generation |
| `all` | plotly, kaleido, gmsh | Everything |
| `dev` | plotly, kaleido, gmsh, pytest | Development + tests |

Example:

```bash
pip install -e ".[all]"       # everything
pip install -e ".[plot]"      # charts only
pip install -e ".[mesh]"      # Gmsh meshing only
```

## Verify installation

```python
import platefeapy
print(platefeapy.__version__)  # 0.1.0
```

## Running tests

```bash
pip install -e ".[dev]"
python -m pytest tests -q
```

## Troubleshooting

### ImportError: plotly not found

The `plot` extra is not installed. Run:

```bash
pip install -e ".[all]"
```

### ImportError: gmsh not found

The `mesh` extra is not installed. Run:

```bash
pip install -e ".[mesh]"
```
