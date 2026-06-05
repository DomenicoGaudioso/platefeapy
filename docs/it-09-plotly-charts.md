---
layout: default
title: "09 - Grafici Plotly"
parent: Italiano
nav_order: 9
---

# 09 - Grafici Plotly

platefeapy fornisce 5 funzioni di visualizzazione interattiva basate su Plotly.

## Installazione

```bash
pip install platefeapy[plot]
```

## Funzioni disponibili

### plot_mesh(m, show_node_ids=True)

Visualizzazione 2D della mesh con ID dei nodi:

```python
from platefeapy.plotting import plot_mesh
fig = plot_mesh(m)
fig.show()
```

### plot_deformed(result, scale=1.0, n=21)

Forma deformata 3D con spostamento codificato a colori:

```python
from platefeapy.plotting import plot_deformed
plot_deformed(res, scale=100).show()
```

La forma deformata è resa come nuvola di punti con bordi degli elementi. Il
parametro `scale` amplifica lo spostamento per la visualizzazione.

### plot_contour(result, component="Mx", n=11, title=None, show_isolines=True)

Mappa a colori 2D di una componente del campo:

```python
from platefeapy.plotting import plot_contour

# Momento flettente Mx
plot_contour(res, "Mx").show()

# Piu' o meno linee di separazione tra fasce di valore
plot_contour(res, "Mx", n_isolines=12).show()

# Momento flettente My
plot_contour(res, "My").show()

# Momento torcente Mxy
plot_contour(res, "Mxy").show()

# Forze di taglio
plot_contour(res, "Qx").show()
plot_contour(res, "Qy").show()

# Spostamento trasversale
plot_contour(res, "w").show()
```

Componenti disponibili: `Mx`, `My`, `Mxy`, `Qx`, `Qy`, `w`.

La mappa usa valori colorati su `n×n` punti per elemento. Le iso-linee sono
disegnate sulla stessa triangolazione campionata per evidenziare la
separazione tra fasce di valore.

### plot_reactions(result, scale=1.0)

Reazioni vincolari ai nodi vincolati:

```python
from platefeapy.plotting import plot_reactions
plot_reactions(res).show()
```

### plot_mode(modal_result, i=0, scale=1.0, n=21)

Visualizzazione 3D della forma modale:

```python
from platefeapy.plotting import plot_mode

# Primo modo
plot_mode(mr, i=0, scale=100).show()

# Secondo modo
plot_mode(mr, i=1, scale=100).show()
```

## Salvataggio figure

```python
fig = plot_contour(res, "Mx")
fig.write_html("momento_Mx.html", include_plotlyjs="cdn")
fig.write_image("momento_Mx.png", width=1200, height=800)  # richiede kaleido
```

## Esempio completo

```python
from platefeapy import Model, Material, ShellSection
from platefeapy.plotting import plot_mesh, plot_deformed, plot_contour

# Creare modello
m = Model()
# ... aggiungere nodi, elementi, carichi ...
res = m.solve()

# Visualizzare
plot_mesh(m).show()
plot_deformed(res, scale=100).show()
plot_contour(res, "Mx").show()
plot_contour(res, "My").show()
plot_contour(res, "w").show()
```

## Mappe di colore

Tutti i grafici a contorno usano la scala di colori `RdYlBu`:
- **Rosso**: valori positivi (o alta intensità)
- **Blu**: valori negativi (o bassa intensità)
- **Giallo/bianco**: vicino allo zero

La barra dei colori mostra l'intervallo di valori con le unità.
