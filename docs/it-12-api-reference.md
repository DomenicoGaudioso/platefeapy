---
layout: default
title: "12 - Riferimento API"
parent: Italiano
nav_order: 12
---

# 12 - Riferimento API

Riferimento completo di tutte le funzioni pubbliche in **platefeapy**.

Import tipico:

```python
from platefeapy import Model, ShellModel, Material, ShellSection
from platefeapy import postprocess
from platefeapy.plotting import (plot_mesh, plot_deformed, plot_contour,
                                  plot_supports, plot_reactions, plot_mode)
```

---

## Materiali e Sezioni

### `Material(E, nu=0.3, alpha=0.0, G=None, rho=0.0, name="")`
Materiale elastico isotropo. `G` (modulo di taglio) è derivato come
`E/(2(1+nu))` se non fornito. `alpha` = dilatazione termica; `rho` = densità.

### `ShellSection(t, kappa=5/6, name="")`
Proprietà della sezione di piastra.
- `t`: spessore [m]
- `kappa`: fattore di correzione al taglio (default 5/6 per piastre di Mindlin)

Metodi:
- `D_bending(E, nu)` → `E·t³/(12·(1−ν²))`
- `D_shear(G)` → `κ·G·t`
- `D_membrane(E, nu)` → `E·t/(1−ν²)`

---

## Modello

### `Model()`
Contenitore del modello FEM. Attributi: `nodes`, `elements`, `nodal_loads`,
`pressure_loads`, `thermal_loads`, `settlements`.

### `add_node(id, x, y) -> Node`
Aggiunge un nodo (3 GdL: `w, theta_x, theta_y`).

### `add_plate(id, node_ids, materiale, sezione, theory="mindlin") -> MindlinPlateQ4 | KirchhoffPlateQ4`
Elemento piastra quadrilatero (4 nodi).
- `node_ids`: lista di 4 ID nodo (ordine antiorario)
- `theory`: `"mindlin"` (default, SRI) o `"kirchhoff"` (ACM)

### `ShellModel()`
Contenitore per shell Q4 su geometria 3D reale. Ogni nodo ha 6 GdL:
`ux, uy, uz, rx, ry, rz`.

### `ShellModel.add_node(id, x, y, z) -> ShellNode`
Aggiunge un nodo nello spazio 3D, sulla superficie reale della struttura.

### `ShellModel.add_shell(id, node_ids, materiale, sezione) -> ShellQ4`
Aggiunge un elemento shell quadrilatero. L'elemento costruisce una terna locale
dalla geometria 3D, combina membrana e flessione Mindlin e trasforma la
rigidezza nel sistema globale.

### Vincoli
- **`fix(nodo, dofs=None)`** — vincola i GdL elencati; `None` = tutti e 3 (incastro).
- **`pin(nodo)`** — appoggio semplice: vincola solo `w`.
- **`support(nodo, w=False, theta_x=False, theta_y=False)`** — vincolo selettivo.

### `add_settlement(nodo, dof, valore) -> Settlement`
Cedimento (spostamento/rotazione imposta): `dof` ∈ `{w, theta_x, theta_y}`.

---

## Carichi

Tutti i metodi `add_*` accettano `case="..."` (caso di carico, default `"default"`).

### `add_nodal_load(nodo, case="default", Fz=0, Mx=0, My=0) -> NodalLoad`
Forza/momento concentrato a un nodo (sistema globale).

### `add_pressure(elem, p, case="default") -> PressureLoad`
Pressione uniforme sulla superficie dell'elemento [Pa]. Positiva = direzione +Z.

### `add_patch_load(elem, p, xi_range=(-1,1), eta_range=(-1,1), case="default") -> PatchLoad`
Pressione su una porzione dell'elemento (coordinate naturali).

### `add_thermal_load(elem, dT, case="default") -> ThermalLoad`
Gradiente di temperatura attraverso lo spessore [°C]. Produce curvatura `κ = α·ΔT/t`.

---

## Soluzione

### `load_cases() -> list[str]`
Lista ordinata dei casi di carico presenti nei carichi.

### `solve(sparse=False, cases=None) -> Result`
Risolve il sistema.
- `sparse`: `True` usa il solver sparso scipy (modelli grandi).
- `cases`: combinazione di carico —
  - `None` = tutti i carichi (coeff 1);
  - stringa = un singolo caso di carico;
  - lista/set = combinazione (coeff 1 ciascuno);
  - **dict `{case: coefficiente}`** = combinazione con coefficienti moltiplicativi.

### `modal(n_modes=10) -> ModalResult`
Analisi modale: risolve `K φ = ω² M φ`. Richiede `rho > 0` nei materiali.

---

## Risultati

### `ShellResult`
Attributi: `U` (spostamenti globali), `R` (reazioni globali).

- **`displacements(nodo) -> ndarray(6)`**: `[ux, uy, uz, rx, ry, rz]` del nodo.
- **`displacement(nodo, dof) -> float`**: singola componente.
- **`reactions(nodo) -> ndarray(6)`**: `[Fx, Fy, Fz, Mx, My, Mz]` del nodo.

### `Result`
Attributi: `U` (spostamenti globali), `R` (reazioni globali),
`element_forces` (forze d'estremità locali per elemento, 12).

- **`displacements(nodo) -> ndarray(3)`** — `[w, theta_x, theta_y]` del nodo.
- **`displacement(nodo, dof) -> float`** — singola componente.
- **`reactions(nodo) -> ndarray(3)`** — `[Fz, Mx, My]` del nodo.

### `ModalResult`
Attributi: `omega` [rad/s], `freq` [Hz], `period` [s], `phi` (ndof × n_modi).

- **`mode(i) -> ndarray(ndof)`** — vettore i-esima forma modale.
- **`mode_shape(i, nodo) -> ndarray(3)`** — `[w, theta_x, theta_y]` al nodo.

---

## Post-processing (`platefeapy.postprocess`)

### `element_stresses(result, elem_id, n=5) -> dict`
Tensioni in `n×n` punti di Gauss. Restituisce `{x, y, Mx, My, Mxy, Qx, Qy}`.

### `element_displacements(result, elem_id, n=11) -> dict`
Spostamenti in `n×n` punti. Restituisce `{x, y, w}`.

### `deformed_shape(result, scale=1.0, n=11) -> dict`
Coordinate deformate per tutti gli elementi. Restituisce `{elem_id: {x, y, w}}`.

### `principal_moments(Mx, My, Mxy) -> tuple[float, float, float]`
Momenti principali e angolo: `(M1, M2, alpha)`.

---

## Visualizzazione (`platefeapy.plotting`)

Richiede l'extra `plot` (`plotly`, `kaleido`). Ogni funzione restituisce un
`plotly.graph_objects.Figure`.

- **`plot_mesh(model, show_node_ids=True)`** — mesh 2D con ID nodi.
- **`plot_deformed(result, scale=1.0, n=21)`** — forma deformata 3D.
- **`plot_contour(result, component="Mx", n=11, show_isolines=True)`** — mappa a colori 2D con iso-linee.
- **`plot_supports(model)`** — nodi vincolati e gradi di liberta' attivi.
- **`plot_reactions(result, scale=1.0)`** — reazioni vincolari.
- **`plot_mode(modal_result, i=0, scale=1.0, n=21)`** — i-esima forma modale.
