"""platefeapy - Solutore FEM per piastre (elementi shell).

Libreria didattica/ingegneristica per l'analisi statica e modale di
piastre sottili e spesse con elementi finiti.

Elementi disponibili:
  * MindlinPlateQ4 - piastra di Mindlin-Reissner (spessa), 4 nodi, SRI
  * KirchhoffPlateQ4 - piastra di Kirchhoff-Love (sottile), 4 nodi, ACM

Funzionalita':
  * carichi nodali (forze e momenti)
  * pressione uniforme e a chiazza
  * carichi termici (gradiente attraverso lo spessore)
  * cedimenti nodali
  * analisi modale
  * post-processing (momenti, tagli, spostamenti)
  * visualizzazione Plotly

Esempio minimo:

    from platefeapy import Model, Material, ShellSection

    m = Model()
    m.add_node(1, 0, 0)
    m.add_node(2, 1, 0)
    m.add_node(3, 1, 1)
    m.add_node(4, 0, 1)
    mat = Material(E=210e9, nu=0.3)
    sec = ShellSection(t=0.01)
    m.add_plate(1, [1, 2, 3, 4], mat, sec)
    m.fix(1); m.fix(2); m.fix(3); m.fix(4)
    m.add_pressure(1, p=-1000.0)
    res = m.solve()
    print(res.displacements(1))
"""

from .material import Material
from .section import ShellSection
from .node import Node
from .element import MindlinPlateQ4, KirchhoffPlateQ4
from .loads import (
    NodalLoad, PressureLoad, PatchLoad, ThermalLoad, Settlement,
)
from .model import Model, Result, ModalResult
from . import postprocess

__all__ = [
    "Material",
    "ShellSection",
    "Node",
    "MindlinPlateQ4",
    "KirchhoffPlateQ4",
    "NodalLoad",
    "PressureLoad",
    "PatchLoad",
    "ThermalLoad",
    "Settlement",
    "Model",
    "Result",
    "ModalResult",
    "postprocess",
]

__version__ = "0.1.0"
