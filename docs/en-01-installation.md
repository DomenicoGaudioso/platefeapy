---
layout: default
title: "01 - Installation"
parent: English
nav_order: 1
---

# 01 - Installation

## Requirements

- Python ≥ 3.9
- numpy ≥ 1.24
- scipy ≥ 1.10

## Installation

### From source (development)

```bash
git clone https://github.com/DomenicoGaudioso/platefeapy.git
cd platefeapy
pip install -e ".[all]"
```

### Base dependencies only (numpy + scipy)

```bash
pip install -e .
```

## Extras

| Extra | Packages | Description |
|-------|----------|-------------|
| `plot` | plotly, kaleido | Interactive Plotly charts |
| `all` | plotly, kaleido | Everything |
| `dev` | plotly, kaleido, pytest | Development + tests |

Example:

```bash
pip install -e ".[all]"       # everything
pip install -e ".[plot]"      # charts only
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

### ValueError: Jacobiano singolare

Check that element nodes are not collinear or degenerate. Quadrilateral elements
require 4 non-collinear nodes forming a valid quadrilateral.
