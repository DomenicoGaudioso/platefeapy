"""
Genera immagini per la documentazione platefeapy.
"""
import sys
from pathlib import Path

# Aggiungi il path per importare platefeapy
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
import plotly.graph_objects as go

from platefeapy import Model, Material, ShellSection
from platefeapy.plotting import plot_mesh, plot_deformed, plot_contour, plot_mode


def create_simply_supported_plate(n_elements=8):
    """Crea una piastra semplicemente appoggiata con carico uniforme."""
    L = 1.0
    m = Model()
    
    # Nodi
    nid = 1
    for j in range(n_elements + 1):
        for i in range(n_elements + 1):
            m.add_node(nid, i * L / n_elements, j * L / n_elements)
            nid += 1
    
    # Materiale e sezione
    mat = Material(E=210e9, nu=0.3)
    sec = ShellSection(t=0.01)
    
    # Elementi
    eid = 1
    for j in range(n_elements):
        for i in range(n_elements):
            n1 = j * (n_elements + 1) + i + 1
            n2 = n1 + 1
            n3 = n2 + (n_elements + 1)
            n4 = n1 + (n_elements + 1)
            m.add_plate(eid, [n1, n2, n3, n4], mat, sec)
            eid += 1
    
    # Vincoli: semplicemente appoggiata sui bordi
    for j in range(n_elements + 1):
        for i in range(n_elements + 1):
            nid = j * (n_elements + 1) + i + 1
            if i == 0 or i == n_elements or j == 0 or j == n_elements:
                m.fix(nid, ["w"])
    
    # Carico uniforme
    for eid in m.elements:
        m.add_pressure(eid, p=-1000.0)
    
    return m


def create_clamped_plate(n_elements=8):
    """Crea una piastra incastrata con carico uniforme."""
    L = 1.0
    m = Model()
    
    # Nodi
    nid = 1
    for j in range(n_elements + 1):
        for i in range(n_elements + 1):
            m.add_node(nid, i * L / n_elements, j * L / n_elements)
            nid += 1
    
    # Materiale e sezione
    mat = Material(E=210e9, nu=0.3)
    sec = ShellSection(t=0.01)
    
    # Elementi
    eid = 1
    for j in range(n_elements):
        for i in range(n_elements):
            n1 = j * (n_elements + 1) + i + 1
            n2 = n1 + 1
            n3 = n2 + (n_elements + 1)
            n4 = n1 + (n_elements + 1)
            m.add_plate(eid, [n1, n2, n3, n4], mat, sec)
            eid += 1
    
    # Vincoli: incastrata sui bordi
    for j in range(n_elements + 1):
        for i in range(n_elements + 1):
            nid = j * (n_elements + 1) + i + 1
            if i == 0 or i == n_elements or j == 0 or j == n_elements:
                m.fix(nid)
    
    # Carico uniforme
    for eid in m.elements:
        m.add_pressure(eid, p=-1000.0)
    
    return m


def generate_mesh_image(m, filename, title="Mesh"):
    """Genera immagine della mesh."""
    fig = go.Figure()
    
    # Disegna elementi
    for el in m.elements.values():
        coords = el._coords()
        # Chiudi il quadrilatero
        x = list(coords[:, 0]) + [coords[0, 0]]
        y = list(coords[:, 1]) + [coords[0, 1]]
        fig.add_trace(go.Scatter(
            x=x, y=y, mode='lines',
            line=dict(color='black', width=1),
            showlegend=False
        ))
    
    # Disegna nodi
    x_nodes = [n.x for n in m.nodes.values()]
    y_nodes = [n.y for n in m.nodes.values()]
    fig.add_trace(go.Scatter(
        x=x_nodes, y=y_nodes, mode='markers',
        marker=dict(size=5, color='red'),
        showlegend=False
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title="x [m]",
        yaxis_title="y [m]",
        yaxis=dict(scaleanchor="x", scaleratio=1),
        width=800, height=600
    )
    
    fig.write_image(filename, scale=2)
    print(f"Generata: {filename}")


def generate_deformed_image(res, filename, scale=100, title="Deformata"):
    """Genera immagine della deformata."""
    fig = plot_deformed(res, scale=scale)
    fig.update_layout(title=title, width=800, height=600)
    fig.write_image(filename, scale=2)
    print(f"Generata: {filename}")


def generate_stress_image(res, filename, component="Mx", title=None):
    """Genera immagine delle tensioni."""
    if title is None:
        title = f"Tensioni: {component}"
    fig = plot_contour(res, component=component)
    fig.update_layout(title=title, width=800, height=600)
    fig.write_image(filename, scale=2)
    print(f"Generata: {filename}")


def generate_mode_image(mr, mode_idx, filename, scale=100):
    """Genera immagine di una forma modale."""
    fig = plot_mode(mr, i=mode_idx, scale=scale)
    fig.update_layout(width=800, height=600)
    fig.write_image(filename, scale=2)
    print(f"Generata: {filename}")


def generate_shape_functions_image(filename):
    """Genera immagine delle funzioni di forma Q4."""
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # Funzioni di forma bilineari
    def N1(xi, eta): return 0.25 * (1 - xi) * (1 - eta)
    def N2(xi, eta): return 0.25 * (1 + xi) * (1 - eta)
    def N3(xi, eta): return 0.25 * (1 + xi) * (1 + eta)
    def N4(xi, eta): return 0.25 * (1 - xi) * (1 + eta)
    
    xi = np.linspace(-1, 1, 50)
    eta = np.linspace(-1, 1, 50)
    XI, ETA = np.meshgrid(xi, eta)
    
    functions = [N1, N2, N3, N4]
    titles = ["N₁(ξ,η)", "N₂(ξ,η)", "N₃(ξ,η)", "N₄(ξ,η)"]
    
    for idx, (ax, func, title) in enumerate(zip(axes.flat, functions, titles)):
        Z = func(XI, ETA)
        contour = ax.contourf(XI, ETA, Z, levels=20, cmap='viridis')
        ax.contour(XI, ETA, Z, levels=10, colors='black', linewidths=0.5)
        ax.set_xlabel('ξ')
        ax.set_ylabel('η')
        ax.set_title(title)
        ax.set_xlim(-1, 1)
        ax.set_ylim(-1, 1)
        ax.set_aspect('equal')
        plt.colorbar(contour, ax=ax)
    
    plt.tight_layout()
    plt.savefig(filename, dpi=200, bbox_inches='tight')
    plt.close()
    print(f"Generata: {filename}")


def main():
    """Genera tutte le immagini per la documentazione."""
    output_dir = Path(__file__).parent.parent / "docs" / "images"
    output_dir.mkdir(exist_ok=True)
    
    print("Generazione immagini per documentazione platefeapy...")
    print("=" * 60)
    
    # 1. Mesh semplicemente appoggiata
    print("\n1. Piastra semplicemente appoggiata")
    m_ss = create_simply_supported_plate(n_elements=8)
    generate_mesh_image(m_ss, output_dir / "mesh_simply_supported.png", 
                       "Mesh piastra semplicemente appoggiata (8×8)")
    
    # Risolvi
    res_ss = m_ss.solve()
    
    # 2. Deformata semplicemente appoggiata
    generate_deformed_image(res_ss, output_dir / "deformed_simply_supported.png",
                           scale=100, title="Deformata piastra SS (scala 100×)")
    
    # 3. Tensioni Mx
    generate_stress_image(res_ss, output_dir / "stress_Mx_simply_supported.png",
                         component="Mx", title="Momento flettente Mx [Nm/m]")
    
    # 4. Tensioni My
    generate_stress_image(res_ss, output_dir / "stress_My_simply_supported.png",
                         component="My", title="Momento flettente My [Nm/m]")
    
    # 5. Tensioni Mxy
    generate_stress_image(res_ss, output_dir / "stress_Mxy_simply_supported.png",
                         component="Mxy", title="Momento torcente Mxy [Nm/m]")
    
    # 6. Spostamento w
    generate_stress_image(res_ss, output_dir / "displacement_w_simply_supported.png",
                         component="w", title="Spostamento trasversale w [m]")
    
    # 7. Mesh incastrata
    print("\n2. Piastra incastrata")
    m_cl = create_clamped_plate(n_elements=8)
    generate_mesh_image(m_cl, output_dir / "mesh_clamped.png",
                       "Mesh piastra incastrata (8×8)")
    
    # Risolvi
    res_cl = m_cl.solve()
    
    # 8. Deformata incastrata
    generate_deformed_image(res_cl, output_dir / "deformed_clamped.png",
                           scale=100, title="Deformata piastra incastrata (scala 100×)")
    
    # 9. Tensioni Mx incastrata
    generate_stress_image(res_cl, output_dir / "stress_Mx_clamped.png",
                         component="Mx", title="Momento flettente Mx [Nm/m]")
    
    # 10. Analisi modale
    print("\n3. Analisi modale")
    m_modal = create_simply_supported_plate(n_elements=6)
    # Aggiungi densità per analisi modale
    for el in m_modal.elements.values():
        el.material.rho = 7850.0
    
    mr = m_modal.modal(n_modes=6)
    
    for i in range(min(4, len(mr.freq))):
        generate_mode_image(mr, i, output_dir / f"mode_{i+1}.png", scale=100)
    
    # 11. Funzioni di forma
    print("\n4. Funzioni di forma")
    generate_shape_functions_image(output_dir / "shape_functions_Q4.png")
    
    print("\n" + "=" * 60)
    print(f"Generazione completata! Immagini salvate in: {output_dir}")
    print(f"Totale immagini: {len(list(output_dir.glob('*.png')))}")


if __name__ == "__main__":
    main()
