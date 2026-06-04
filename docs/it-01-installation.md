---
layout: default
title: "01 - Installazione"
parent: Italiano
nav_order: 1
---

# 01 - Installazione

## Requisiti

- Python ≥ 3.9
- numpy ≥ 1.24
- scipy ≥ 1.10

## Installazione

### Da sorgente (sviluppo)

```bash
git clone https://github.com/DomenicoGaudioso/platefeapy.git
cd platefeapy
pip install -e ".[all]"
```

### Solo dipendenze base (numpy + scipy)

```bash
pip install -e .
```

## Extra

| Extra | Pacchetti | Descrizione |
|-------|-----------|-------------|
| `plot` | plotly, kaleido | Grafici interattivi Plotly |
| `all` | plotly, kaleido | Tutto |
| `dev` | plotly, kaleido, pytest | Sviluppo + test |

Esempio:

```bash
pip install -e ".[all]"       # tutto
pip install -e ".[plot]"      # solo grafici
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

L'extra `plot` non è installato. Eseguire:

```bash
pip install -e ".[all]"
```

### ValueError: Jacobiano singolare

Verificare che i nodi dell'elemento non siano collineari o degeneri. Gli elementi
quadrilaterali richiedono 4 nodi non collineari che formino un quadrilatero valido.
