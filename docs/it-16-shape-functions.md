---
layout: default
title: "16 - Funzioni di Forma"
parent: Italiano
nav_order: 16
---

# 16 - Funzioni di Forma

Le funzioni di forma sono il fondamento matematico del metodo degli elementi finiti. Interpolano il campo di spostamenti all'interno di un elemento a partire dai valori nodali.

## Elemento Q4 (Quadrilatero 4 nodi)

L'elemento Q4 utilizza **funzioni di forma bilineari** definite in coordinate naturali (ξ, η) ∈ [-1, 1]².

### Definizioni delle Funzioni di Forma

Per un elemento quadrilatero con nodi numerati in senso antiorario:

```
N₁(ξ,η) = ¼(1-ξ)(1-η)
N₂(ξ,η) = ¼(1+ξ)(1-η)
N₃(ξ,η) = ¼(1+ξ)(1+η)
N₄(ξ,η) = ¼(1-ξ)(1+η)
```

### Proprietà

1. **Partizione dell'unità**: N₁ + N₂ + N₃ + N₄ = 1 ovunque
2. **Delta di Kronecker**: Nᵢ(ξⱼ, ηⱼ) = δᵢⱼ (1 al nodo i, 0 agli altri nodi)
3. **Lineari lungo i bordi**: variano linearmente lungo ogni bordo dell'elemento
4. **Bilineari all'interno**: prodotto di funzioni lineari in ξ e η

### Visualizzazione

![Funzioni di forma Q4](images/shape_functions_Q4.png)
*Mappe di contorno delle quattro funzioni di forma bilineari in coordinate naturali.*

### Interpolazione degli Spostamenti

Lo spostamento trasversale w in qualsiasi punto (ξ, η) è:

```
w(ξ,η) = N₁·w₁ + N₂·w₂ + N₃·w₃ + N₄·w₄
```

Analogamente per le rotazioni θₓ e θᵧ.

### Derivate

Le derivate rispetto alle coordinate naturali sono:

```
∂N₁/∂ξ = -¼(1-η)    ∂N₁/∂η = -¼(1-ξ)
∂N₂/∂ξ = +¼(1-η)    ∂N₂/∂η = -¼(1-ξ)
∂N₃/∂ξ = +¼(1+η)    ∂N₃/∂η = +¼(1-ξ)
∂N₄/∂ξ = -¼(1+η)    ∂N₄/∂η = +¼(1-ξ)
```

Queste sono utilizzate per calcolare la matrice deformazione-spostamento B.

## Mappatura delle Coordinate

Le stesse funzioni di forma mappano dalle coordinate naturali (ξ, η) alle coordinate fisiche (x, y):

```
x(ξ,η) = N₁·x₁ + N₂·x₂ + N₃·x₃ + N₄·x₄
y(ξ,η) = N₁·y₁ + N₂·y₂ + N₃·y₃ + N₄·y₄
```

### Matrice Jacobiana

La matrice Jacobiana J relaciona le derivate in coordinate naturali e fisiche:

```
J = [∂x/∂ξ  ∂y/∂ξ] = Σᵢ [∂Nᵢ/∂ξ · xᵢ   ∂Nᵢ/∂ξ · yᵢ]
    [∂x/∂η  ∂y/∂η]     [∂Nᵢ/∂η · xᵢ   ∂Nᵢ/∂η · yᵢ]
```

Il determinante |J| deve essere positivo ovunque per un elemento valido.

## Integrazione

L'integrazione numerica utilizza la **quadratura di Gauss** in coordinate naturali:

```
∫∫ f(ξ,η) dξ dη ≈ Σᵢ Σⱼ wᵢ·wⱼ·f(ξᵢ, ηⱼ)
```

### Schemi di Integrazione

| Schema | Punti | Accuratezza | Uso |
|--------|-------|-------------|-----|
| 1×1 | 1 | Lineare | Taglio (ridotta) |
| 2×2 | 4 | Cubica | Flessione (completa) |
| 3×3 | 9 | Quintica | Ordine superiore |

### Integrazione Ridotta Selettiva (SRI)

L'elemento piastra di Mindlin utilizza:
- **Gauss 2×2** per la rigidezza flessionale (integrazione completa)
- **Gauss 1×1** per la rigidezza a taglio (integrazione ridotta)

Questo previene il shear locking nelle piastre sottili mantenendo l'accuratezza.

## Implementazione

In platefeapy, le funzioni di forma sono implementate nella classe `MindlinPlateQ4`:

```python
def _shape_functions(self, xi, eta):
    """Funzioni di forma bilineari N1..N4."""
    return np.array([
        0.25 * (1 - xi) * (1 - eta),
        0.25 * (1 + xi) * (1 - eta),
        0.25 * (1 + xi) * (1 + eta),
        0.25 * (1 - xi) * (1 + eta),
    ])
```

La matrice B (deformazione-spostamento) è calcolata utilizzando le derivate delle funzioni di forma e l'inversa dello Jacobiano.

## Riferimenti

- Zienkiewicz, O.C., Taylor, R.L. (2000). *The Finite Element Method*, Vol. 1. Butterworth-Heinemann.
- Hughes, T.J.R. (1987). *The Finite Element Method*. Prentice-Hall.
