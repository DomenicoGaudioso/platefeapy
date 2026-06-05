---
layout: default
title: "01 - Installazione"
parent: Italiano
nav_order: 1
---

# 01 - Installazione

## Requisiti

- Python >= 3.9
- numpy >= 1.24
- scipy >= 1.10
- gmsh >= 4.12 per le mesh dei casi studio generate con Gmsh

## Installazione

### Da sorgente (sviluppo)

```bash
git clone https://github.com/DomenicoGaudioso/platefeapy.git
cd platefeapy
pip install -e ".[all]"
```

### Solo dipendenze base

```bash
pip install -e .
```

## Extra

| Extra | Pacchetti | Descrizione |
|-------|-----------|-------------|
| `plot` | plotly, kaleido | Grafici interattivi Plotly |
| `mesh` | gmsh | Generazione mesh con Gmsh |
| `all` | plotly, kaleido, gmsh | Tutto |
| `dev` | plotly, kaleido, gmsh, pytest | Sviluppo + test |

Esempio:

```bash
pip install -e ".[all]"       # tutto
pip install -e ".[plot]"      # solo grafici
pip install -e ".[mesh]"      # solo meshing Gmsh
```

## Verifica installazione

```python
import platefeapy
print(platefeapy.__version__)  # 0.1.0
```

## Esecuzione test

```bash
pip install -e ".[dev]"
python -m pytest tests -q
```

## Risoluzione problemi

### ImportError: plotly non trovato

L'extra `plot` non e' installato. Eseguire:

```bash
pip install -e ".[all]"
```

### ImportError: gmsh non trovato

L'extra `mesh` non e' installato. Eseguire:

```bash
pip install -e ".[mesh]"
```
