"""
Generate a concise, vintage 1980s/1990s minimalist scientific diagram summarizing
Section 1.1 ("Arquitetura Computacional e Escolha Tecnológica") of the 2D SWE work.

Key goals:
  - Present the authentic, original-color vector logos of NumPy, JAX, and PyTorch
    clearly for readers unfamiliar with the ecosystem.
  - Summarize ultra-succinctly what each library is designed for, strongly
    emphasizing the adopted dual-implementation choice (NumPy + JAX, 100% manual
    solvers with zero black-box linear solvers) vs. the non-adopted alternative
    (PyTorch, oriented toward imperative Deep Learning).
  - Include a single-line bottom strip showing the 4-stage CPU -> GPU (WSL2)
    validation progression and the 3 fair-benchmarking rules (JIT warm-up,
    block_until_ready(), and float64 precision parity).
  - Strictly preserve the warm cream paper (#FAF8F3), classic booktabs rules,
    90-degree drafting frames, and razor-sharp LaTeX Latin Modern Roman &
    Computer Modern Math typography of Figures 1-9.

Outputs:
  - ../figures/swe_computational_architecture.svg
  - ../figures/swe_computational_architecture.pdf
  - ../figures/swe_computational_architecture.png
"""

import glob
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.patches import Rectangle, Polygon, Circle, FancyArrowPatch
import matplotlib.patheffects as pe

# ---------------------------------------------------------------------------
# 1. Load Authentic LaTeX Latin Modern Roman Fonts & Computer Modern Math
# ---------------------------------------------------------------------------
miktex_lm_paths = glob.glob(
    r"C:\Program Files\MiKTeX_2\fonts\opentype\public\lm\lmroman*.otf"
)
for fp in miktex_lm_paths:
    fm.fontManager.addfont(fp)

plt.rcParams.update({
    "font.family": "Latin Modern Roman",
    "mathtext.fontset": "cm",
    "svg.fonttype": "path",       # Convert all glyphs to exact vector curves
    "pdf.fonttype": 42,           # Embed TrueType/OpenType outlines in PDF
    "axes.unicode_minus": True,
})

# ---------------------------------------------------------------------------
# 2. Vintage 1980s/90s Editorial Palette (Matching Figures 1-9)
# ---------------------------------------------------------------------------
PALETTE = {
    "bg_canvas": "#FAF8F3",       # Warm archival paper cream/ivory
    "panel_adopted": "#FDFCFA",   # Bright clean archival card for NumPy + JAX
    "panel_header": "#E8F1F6",    # Soft ice-blue header tint (from Fig 1 water palette)
    "panel_alt": "#F3EFE8",       # Recessed warm gray-ivory for non-adopted option
    "panel_alt_hdr": "#E7E1D6",   # Muted sand header for non-adopted option
    "ink_primary": "#11161C",     # Deep obsidian ink
    "ink_secondary": "#222B35",   # Crisp charcoal body ink
    "ink_muted": "#5C6773",       # Muted slate ink
    "navy_deep": "#0D3149",       # Deep Prussian navy (primary frame & titles)
    "z_node": "#145374",          # Cerulean navy (connectors & highlights)
    "teal_adi": "#17575A",        # Sea-teal (execution scope tags)
    "terracotta": "#8E321E",      # Venetian terracotta (strict constraints / contrast)
    "amber_sun": "#9C5E14",       # Warm amber (progression arrows)
    "rule_dark": "#283648",       # Heavy booktabs rule
    "rule_light": "#CFC5B7",      # Subtle archival divider rule
    "rule_muted": "#8A949E",      # Dashed border for non-adopted card
}


def crisp_text(ax, x, y, s, color="#11161C", stroke_w=0.15, bg_color=None, pad=0.05, **kwargs):
    """Render razor-sharp LaTeX text with micro self-colored stroke reinforcement."""
    if bg_color is not None:
        kwargs["bbox"] = dict(
            boxstyle=f"square,pad={pad}",
            facecolor=bg_color,
            edgecolor="none",
            alpha=0.96,
        )
    t = ax.text(x, y, s, color=color, **kwargs)
    if stroke_w > 0:
        t.set_path_effects([pe.withStroke(linewidth=stroke_w, foreground=color)])
    return t


def draw_2d_arrow(
    ax, p0, p1, color, lw=1.25, mutation_scale=9.5, arrowstyle="-|>",
    zorder=20, ls="-", connectionstyle="arc3,rad=0.0"
):
    arr = FancyArrowPatch(
        p0, p1,
        arrowstyle=arrowstyle,
        mutation_scale=mutation_scale,
        color=color,
        linewidth=lw,
        linestyle=ls,
        connectionstyle=connectionstyle,
        shrinkA=0,
        shrinkB=0,
        zorder=zorder,
    )
    ax.add_patch(arr)
    return arr


# ---------------------------------------------------------------------------
# 3. Exact Original-Color Vector Reconstructions of Official Library Logos
# ---------------------------------------------------------------------------
def draw_numpy_logo(ax, cx, cy, scale=1.0, zorder=15):
    """
    Draw the official NumPy logo in exact brand colors:
      - Isometric 3D cube:
          * Top face: 2x2 cyan-blue (#4DABCF) diamond tiles
          * Right face: 2x2 cyan-blue (#4DABCF) parallelogram tiles
          * Front-left face: royal-blue (#4D77CF) bold capital 'N'
      - Clean bold sans-serif 'NumPy' wordmark in deep navy (#013243)
    """
    R = 0.56 * scale
    cube_cx = cx - 0.74 * scale
    cube_cy = cy - 0.02 * scale

    u_L = np.array([-np.cos(np.deg2rad(30)), np.sin(np.deg2rad(30))]) * R
    u_R = np.array([np.cos(np.deg2rad(30)), np.sin(np.deg2rad(30))]) * R
    u_D = np.array([0.0, -1.0]) * R
    center = np.array([cube_cx, cube_cy])

    col_cyan = "#4DABCF"
    col_blue = "#4D77CF"
    col_word = "#013243"

    # 1. Top face: 2x2 diamond tiles
    segs_top = [(0.04, 0.46), (0.54, 0.98)]
    for a0, a1 in segs_top:
        for b0, b1 in segs_top:
            pts = [
                center + a0 * u_L + b0 * u_R,
                center + a1 * u_L + b0 * u_R,
                center + a1 * u_L + b1 * u_R,
                center + a0 * u_L + b1 * u_R,
            ]
            ax.add_patch(Polygon(pts, closed=True, facecolor=col_cyan, edgecolor="none", zorder=zorder))

    # 2. Right face: 2x2 parallelogram tiles
    segs_b = [(0.06, 0.48), (0.56, 0.98)]
    segs_c = [(0.06, 0.48), (0.56, 0.98)]
    for b0, b1 in segs_b:
        for c0, c1 in segs_c:
            pts = [
                center + b0 * u_R + c0 * u_D,
                center + b1 * u_R + c0 * u_D,
                center + b1 * u_R + c1 * u_D,
                center + b0 * u_R + c1 * u_D,
            ]
            ax.add_patch(Polygon(pts, closed=True, facecolor=col_cyan, edgecolor="none", zorder=zorder))

    # 3. Front-left face: Isometric capital 'N'
    n_ac = [
        (0.98, 0.98),
        (0.98, 0.06),
        (0.70, 0.06),
        (0.33, 0.58),
        (0.33, 0.06),
        (0.06, 0.06),
        (0.06, 0.98),
        (0.34, 0.98),
        (0.71, 0.46),
        (0.71, 0.98),
    ]
    pts_n = [center + a * u_L + c * u_D for (a, c) in n_ac]
    ax.add_patch(Polygon(pts_n, closed=True, facecolor=col_blue, edgecolor="none", zorder=zorder + 1))

    # 4. 'NumPy' geometric sans-serif wordmark
    ax.text(
        cube_cx + 0.62 * scale, cube_cy - 0.03 * scale,
        "NumPy",
        fontfamily="Segoe UI",
        fontweight="bold",
        fontsize=20.5 * scale,
        color=col_word,
        ha="left",
        va="center",
        zorder=zorder + 2,
    )


# Exact 71 equilateral triangles and 90 isometric cube edges of the official JAX logo
JAX_TRIANGLES = [
    ('U', 0, 9, '#5E97F6'), ('D', 0, 10, '#5E97F6'), ('U', 0, 11, '#EA80FC'),
    ('D', 0, 12, '#EA80FC'), ('U', 0, 13, '#9C27B0'), ('U', 0, 15, '#EA80FC'),
    ('D', 0, 16, '#EA80FC'), ('U', 0, 17, '#9C27B0'), ('U', 1, 8, '#5E97F6'),
    ('D', 1, 9, '#5E97F6'), ('U', 1, 10, '#00796B'), ('D', 1, 11, '#00695C'),
    ('U', 1, 12, '#00695C'), ('D', 1, 13, '#9C27B0'), ('U', 1, 14, '#9C27B0'),
    ('D', 1, 15, '#EA80FC'), ('U', 1, 16, '#9C27B0'), ('D', 1, 17, '#9C27B0'),
    ('U', 2, 7, '#5E97F6'), ('D', 2, 8, '#5E97F6'), ('U', 2, 9, '#00796B'),
    ('D', 2, 10, '#00796B'), ('D', 2, 12, '#00695C'), ('U', 2, 13, '#00695C'),
    ('D', 2, 14, '#9C27B0'), ('U', 2, 15, '#9C27B0'), ('D', 2, 16, '#9C27B0'),
    ('U', 3, 2, '#5E97F6'), ('D', 3, 3, '#5E97F6'), ('U', 3, 4, '#2A56C6'),
    ('U', 3, 6, '#5E97F6'), ('D', 3, 7, '#5E97F6'), ('U', 3, 8, '#26A69A'),
    ('D', 3, 9, '#26A69A'), ('U', 3, 10, '#26A69A'), ('D', 3, 11, '#26A69A'),
    ('U', 3, 12, '#EA80FC'), ('D', 3, 13, '#EA80FC'), ('U', 3, 14, '#9C27B0'),
    ('D', 3, 15, '#9C27B0'), ('U', 3, 16, '#9C27B0'), ('U', 4, 1, '#5E97F6'),
    ('D', 4, 2, '#5E97F6'), ('U', 4, 3, '#5E97F6'), ('D', 4, 4, '#5E97F6'),
    ('U', 4, 5, '#5E97F6'), ('D', 4, 6, '#5E97F6'), ('U', 4, 7, '#00796B'),
    ('D', 4, 8, '#00695C'), ('U', 4, 9, '#00695C'), ('D', 4, 10, '#00695C'),
    ('U', 4, 11, '#EA80FC'), ('D', 4, 12, '#EA80FC'), ('U', 4, 13, '#9C27B0'),
    ('D', 4, 14, '#9C27B0'), ('U', 4, 15, '#00695C'), ('D', 4, 16, '#9C27B0'),
    ('U', 4, 17, '#9C27B0'), ('D', 5, 1, '#2A56C6'), ('U', 5, 2, '#2A56C6'),
    ('D', 5, 3, '#2A56C6'), ('U', 5, 4, '#2A56C6'), ('D', 5, 5, '#2A56C6'),
    ('U', 5, 6, '#2A56C6'), ('D', 5, 7, '#00796B'), ('D', 5, 11, '#6A1B9A'),
    ('U', 5, 12, '#6A1B9A'), ('D', 5, 13, '#9C27B0'), ('D', 5, 15, '#00695C'),
    ('U', 5, 16, '#00695C'), ('D', 5, 17, '#9C27B0'),
]

JAX_DRAWN_EDGES = {
    ((0, 9), (0, 11)), ((0, 9), (1, 8)), ((0, 11), (0, 13)), ((0, 11), (1, 10)),
    ((0, 13), (1, 12)), ((0, 13), (1, 14)), ((0, 15), (0, 17)), ((0, 15), (1, 14)),
    ((0, 17), (1, 16)), ((0, 17), (1, 18)), ((1, 8), (1, 10)), ((1, 8), (2, 7)),
    ((1, 10), (1, 12)), ((1, 10), (2, 9)), ((1, 10), (2, 11)), ((1, 12), (2, 13)),
    ((1, 14), (1, 16)), ((1, 14), (2, 13)), ((1, 14), (2, 15)), ((1, 16), (2, 15)),
    ((1, 16), (2, 17)), ((1, 18), (2, 17)), ((2, 7), (2, 9)), ((2, 7), (3, 6)),
    ((2, 9), (3, 8)), ((2, 9), (3, 10)), ((2, 11), (2, 13)), ((2, 11), (3, 10)),
    ((2, 11), (3, 12)), ((2, 13), (3, 14)), ((2, 15), (3, 14)), ((2, 15), (3, 16)),
    ((2, 17), (3, 16)), ((3, 2), (3, 4)), ((3, 2), (4, 1)), ((3, 4), (4, 3)),
    ((3, 4), (4, 5)), ((3, 6), (3, 8)), ((3, 6), (4, 5)), ((3, 8), (3, 10)),
    ((3, 8), (4, 7)), ((3, 10), (3, 12)), ((3, 10), (4, 9)), ((3, 12), (3, 14)),
    ((3, 12), (4, 11)), ((3, 14), (4, 13)), ((3, 14), (4, 15)), ((3, 16), (4, 15)),
    ((3, 16), (4, 17)), ((4, 1), (4, 3)), ((4, 1), (5, 0)), ((4, 3), (4, 5)),
    ((4, 3), (5, 2)), ((4, 5), (4, 7)), ((4, 5), (5, 4)), ((4, 7), (4, 9)),
    ((4, 7), (5, 6)), ((4, 7), (5, 8)), ((4, 9), (4, 11)), ((4, 9), (5, 10)),
    ((4, 11), (4, 13)), ((4, 11), (5, 10)), ((4, 13), (5, 12)), ((4, 13), (5, 14)),
    ((4, 15), (5, 14)), ((4, 15), (5, 16)), ((4, 17), (5, 16)), ((4, 17), (5, 18)),
    ((5, 0), (5, 2)), ((5, 0), (6, 1)), ((5, 2), (5, 4)), ((5, 2), (6, 3)),
    ((5, 4), (5, 6)), ((5, 4), (6, 5)), ((5, 6), (6, 7)), ((5, 8), (5, 10)),
    ((5, 8), (6, 7)), ((5, 10), (5, 12)), ((5, 10), (6, 11)), ((5, 12), (6, 13)),
    ((5, 14), (5, 16)), ((5, 14), (6, 13)), ((5, 14), (6, 15)), ((5, 16), (6, 17)),
    ((5, 18), (6, 17)), ((6, 1), (6, 3)), ((6, 3), (6, 5)), ((6, 5), (6, 7)),
    ((6, 11), (6, 13)), ((6, 15), (6, 17)),
}


def draw_jax_logo(ax, cx, cy, height=0.98, zorder=15):
    """
    Draw the exact 3D isometric Google JAX logo in its authentic 8-color palette
    (#5E97F6, #2A56C6, #26A69A, #00796B, #00695C, #EA80FC, #9C27B0, #6A1B9A)
    from its exact 6x18 equilateral-triangle lattice.
    """
    hy = height / 6.0
    hx = hy / np.sqrt(3.0)
    w_total = 18.0 * hx
    x0 = cx - 0.5 * w_total
    y_top = cy + 0.5 * height

    def vtx(r, k):
        return (x0 + k * hx, y_top - r * hy)

    edge_counts = {}
    for orient, r, k, col in JAX_TRIANGLES:
        if orient == 'U':
            vs = [(r, k), (r + 1, k - 1), (r + 1, k + 1)]
        else:
            vs = [(r, k - 1), (r, k + 1), (r + 1, k)]
        pts = [vtx(*v) for v in vs]
        ax.add_patch(Polygon(
            pts, closed=True, facecolor=col, edgecolor=col, lw=0.25, zorder=zorder
        ))
        for i in range(3):
            e = tuple(sorted([vs[i], vs[(i + 1) % 3]]))
            edge_counts[e] = edge_counts.get(e, 0) + 1

    # Draw crisp white internal isometric cube creases & subtle clean silhouette hairline
    for e, cnt in edge_counts.items():
        if e in JAX_DRAWN_EDGES:
            p1, p2 = vtx(*e[0]), vtx(*e[1])
            if cnt == 1:
                ax.plot([p1[0], p2[0]], [p1[1], p2[1]],
                        color="#8C96A3", lw=0.45, solid_capstyle="round", zorder=zorder + 2)
            else:
                ax.plot([p1[0], p2[0]], [p1[1], p2[1]],
                        color="#FFFFFF", lw=1.10, solid_capstyle="round", zorder=zorder + 1)


def draw_pytorch_logo(ax, cx, cy, scale=1.0, zorder=15):
    """
    Draw the official PyTorch flame-ring + spark-dot icon in exact PyTorch
    orange-red (#EE4C2C) alongside the clean thin sans-serif 'PyTorch' wordmark.
    """
    R = 0.34 * scale
    r_in = 0.68 * R
    ic_x = cx - 0.78 * scale
    ic_y = cy - 0.06 * scale
    col_flame = "#EE4C2C"
    col_word = "#262626"

    # Circular arc from +45 deg clockwise around bottom (-90 deg) to +135 deg (-225 deg)
    thetas = np.linspace(np.deg2rad(45.0), np.deg2rad(-225.0), 120)
    outer_arc = [(ic_x + R * np.cos(t), ic_y + R * np.sin(t)) for t in thetas]
    inner_arc = [(ic_x + r_in * np.cos(t), ic_y + r_in * np.sin(t)) for t in thetas[::-1]]

    # At theta = 135 deg (-225 deg), tangent continues at +45 deg up-right to x = ic_x
    tip_top = (ic_x, ic_y + R * np.sqrt(2.0))
    tip_bot = (ic_x, ic_y + r_in * np.sqrt(2.0))

    flame_pts = outer_arc + [tip_top, tip_bot] + inner_arc
    ax.add_patch(Polygon(flame_pts, closed=True, facecolor=col_flame, edgecolor="none", zorder=zorder))

    # Spark dot in upper-right opening
    dot_x = ic_x + 0.34 * R
    dot_y = ic_y + 0.88 * R
    ax.add_patch(Circle((dot_x, dot_y), 0.155 * R, facecolor=col_flame, edgecolor="none", zorder=zorder + 1))

    # Clean light geometric sans-serif 'PyTorch' wordmark
    ax.text(
        ic_x + 0.54 * scale, ic_y + 0.04 * scale,
        "PyTorch",
        fontfamily="Segoe UI Light",
        fontsize=20.5 * scale,
        color=col_word,
        ha="left",
        va="center",
        zorder=zorder + 2,
    )


# ---------------------------------------------------------------------------
# 4. Main Figure Assembly (Concise Vintage 1980s/90s Plate)
# ---------------------------------------------------------------------------
def build_figure():
    fig, ax = plt.subplots(figsize=(13.8, 5.45), dpi=300)
    fig.patch.set_facecolor(PALETTE["bg_canvas"])
    ax.set_facecolor(PALETTE["bg_canvas"])

    # =======================================================================
    # ZONE 1 (LEFT, PROMINENT): ESCOLHA ADOTADA — DUPLA IMPLEMENTAÇÃO (NumPy + JAX)
    # =======================================================================
    xL0, xL1 = 0.22, 9.52
    yB0, yB1 = 1.24, 5.25
    wL = xL1 - xL0

    # Main outer drafting box for Adopted Choice
    ax.add_patch(Rectangle(
        (xL0, yB0), wL, yB1 - yB0,
        facecolor=PALETTE["panel_adopted"], edgecolor=PALETTE["navy_deep"],
        lw=1.45, zorder=2
    ))
    # Header band + classic double booktabs rule at top
    h_hdr = 0.50
    ax.add_patch(Rectangle(
        (xL0, yB1 - h_hdr), wL, h_hdr,
        facecolor=PALETTE["panel_header"], edgecolor="none", zorder=3
    ))
    ax.plot([xL0, xL1], [yB1 + 0.055, yB1 + 0.055], color=PALETTE["navy_deep"], lw=1.9, zorder=5)
    ax.plot([xL0, xL1], [yB1 - h_hdr, yB1 - h_hdr], color=PALETTE["navy_deep"], lw=1.05, zorder=5)

    crisp_text(
        ax, xL0 + 0.20, yB1 - 0.5 * h_hdr,
        "ESCOLHA ADOTADA — DUPLA IMPLEMENTAÇÃO (NumPy + JAX)",
        color=PALETTE["navy_deep"], stroke_w=0.20,
        fontsize=9.6, fontweight="bold", ha="left", va="center", zorder=10
    )
    crisp_text(
        ax, xL1 - 0.18, yB1 - 0.5 * h_hdr,
        "Solucionadores 100% manuais (zero caixa-preta)",
        color=PALETTE["terracotta"], stroke_w=0.15,
        fontsize=8.3, fontweight="bold", fontstyle="italic", ha="right", va="center", zorder=10
    )

    # --- Sub-card 1: NumPy (x = 0.42 to 4.42) ---
    xn0, xn1 = 0.42, 4.42
    xc_np = 0.5 * (xn0 + xn1)
    ax.add_patch(Rectangle(
        (xn0, 1.42), xn1 - xn0, 3.15,
        facecolor="#FFFFFF", edgecolor=PALETTE["rule_light"], lw=0.85, zorder=4
    ))

    # Official NumPy Logo
    draw_numpy_logo(ax, xc_np, 4.02, scale=0.92, zorder=15)

    ax.plot([xn0 + 0.18, xn1 - 0.18], [3.44, 3.44], color=PALETTE["rule_light"], lw=0.80, zorder=6)

    crisp_text(
        ax, xc_np, 3.19,
        "NumPy — Referência e Validação",
        color=PALETTE["navy_deep"], stroke_w=0.18,
        fontsize=9.1, fontweight="bold", ha="center", va="center", zorder=10
    )
    crisp_text(
        ax, xc_np, 2.91,
        r"Prototipação em CPU $\cdot$ Precisão dupla ($\mathrm{float64}$)",
        color=PALETTE["teal_adi"], stroke_w=0.14,
        fontsize=8.0, fontstyle="italic", ha="center", va="center", zorder=10
    )

    np_bullets = [
        r"$\bullet\;$ Computação científica em arrays",
        r"$\bullet\;$ Verificação transparente passo a passo",
        r"$\bullet\;$ Gabarito exato de referência numérica",
    ]
    for idx_b, b_txt in enumerate(np_bullets):
        crisp_text(
            ax, xn0 + 0.22, 2.46 - idx_b * 0.37, b_txt,
            color=PALETTE["ink_secondary"], stroke_w=0.14,
            fontsize=8.25, ha="left", va="center", zorder=10
        )

    # --- Central Coupling (+ & Isomorphic API Arrow) (x = 4.42 to 5.26) ---
    xc_link = 4.84
    # Prominent '+' emblem uniting NumPy + JAX
    ax.add_patch(Circle(
        (xc_link, 4.02), 0.21,
        facecolor=PALETTE["panel_header"], edgecolor=PALETTE["navy_deep"], lw=1.15, zorder=12
    ))
    crisp_text(
        ax, xc_link, 4.02, r"$+$",
        color=PALETTE["navy_deep"], stroke_w=0.22,
        fontsize=12.5, fontweight="bold", ha="center", va="center", zorder=14
    )

    # Bidirectional equivalence arrow at lower half
    draw_2d_arrow(
        ax, (xn1 + 0.05, 2.46), (5.26 - 0.05, 2.46),
        color=PALETTE["z_node"], lw=1.30, mutation_scale=8.5, arrowstyle="<|-|>", zorder=14
    )
    crisp_text(
        ax, xc_link, 2.80, "API\nisomórfica",
        color=PALETTE["z_node"], stroke_w=0.14,
        fontsize=7.6, fontweight="bold", ha="center", va="center", linespacing=1.08, zorder=14
    )
    crisp_text(
        ax, xc_link, 2.10, "Validação\ncruzada",
        color=PALETTE["ink_muted"], stroke_w=0.13,
        fontsize=7.5, fontstyle="italic", ha="center", va="center", linespacing=1.08, zorder=14
    )

    # --- Sub-card 2: JAX (x = 5.26 to 9.32) ---
    xj0, xj1 = 5.26, 9.32
    xc_jax = 0.5 * (xj0 + xj1)
    ax.add_patch(Rectangle(
        (xj0, 1.42), xj1 - xj0, 3.15,
        facecolor="#FFFFFF", edgecolor=PALETTE["rule_light"], lw=0.85, zorder=4
    ))

    # Official JAX Isometric 3D Logo centered cleanly in its original form
    draw_jax_logo(ax, xc_jax, 4.01, height=0.92, zorder=15)

    ax.plot([xj0 + 0.18, xj1 - 0.18], [3.44, 3.44], color=PALETTE["rule_light"], lw=0.80, zorder=6)

    crisp_text(
        ax, xc_jax, 3.19,
        "JAX — Compilação e Escala",
        color=PALETTE["navy_deep"], stroke_w=0.18,
        fontsize=9.1, fontweight="bold", ha="center", va="center", zorder=10
    )
    crisp_text(
        ax, xc_jax, 2.91,
        r"Compilação JIT / XLA $\cdot$ CPU e GPU (WSL2)",
        color=PALETTE["teal_adi"], stroke_w=0.14,
        fontsize=8.0, fontstyle="italic", ha="center", va="center", zorder=10
    )

    jax_bullets = [
        r"$\bullet\;$ Funções puras ($A:\mathbb{R}^N \rightarrow \mathbb{R}^N$)",
        r"$\bullet\;$ Métodos Matrix-Free e laços CG compilados",
        r"$\bullet\;$ Transformações composáveis ($\mathrm{jit}$, $\mathrm{vmap}$, $\mathrm{jvp}$)",
    ]
    for idx_b, b_txt in enumerate(jax_bullets):
        crisp_text(
            ax, xj0 + 0.20, 2.46 - idx_b * 0.37, b_txt,
            color=PALETTE["ink_secondary"], stroke_w=0.14,
            fontsize=8.20, ha="left", va="center", zorder=10
        )

    # =======================================================================
    # ZONE 2 (RIGHT, SUBDUED): ALTERNATIVA AVALIADA — NÃO ADOTADA (PyTorch)
    # =======================================================================
    xR0, xR1 = 9.80, 13.58
    wR = xR1 - xR0
    xc_pt = 0.5 * (xR0 + xR1)

    ax.add_patch(Rectangle(
        (xR0, yB0), wR, yB1 - yB0,
        facecolor=PALETTE["panel_alt"], edgecolor=PALETTE["rule_muted"],
        lw=1.10, linestyle=(0, (5, 3)), zorder=2
    ))
    ax.add_patch(Rectangle(
        (xR0 + 0.02, yB1 - h_hdr), wR - 0.04, h_hdr - 0.02,
        facecolor=PALETTE["panel_alt_hdr"], edgecolor="none", zorder=3
    ))
    ax.plot([xR0, xR1], [yB1 - h_hdr, yB1 - h_hdr], color=PALETTE["rule_muted"], lw=0.90, ls="--", zorder=5)

    crisp_text(
        ax, xc_pt, yB1 - 0.5 * h_hdr,
        "ALTERNATIVA NÃO ADOTADA",
        color="#52473B", stroke_w=0.18,
        fontsize=9.2, fontweight="bold", ha="center", va="center", zorder=10
    )

    # Inner subtle card for PyTorch
    xp0, xp1 = xR0 + 0.18, xR1 - 0.18
    ax.add_patch(Rectangle(
        (xp0, 1.42), xp1 - xp0, 3.15,
        facecolor="#FAF8F4", edgecolor=PALETTE["rule_light"], lw=0.80, zorder=4
    ))

    # Official PyTorch Logo
    draw_pytorch_logo(ax, xc_pt, 4.02, scale=0.92, zorder=15)

    ax.plot([xp0 + 0.18, xp1 - 0.18], [3.44, 3.44], color=PALETTE["rule_light"], lw=0.80, zorder=6)

    crisp_text(
        ax, xc_pt, 3.19,
        "PyTorch — Aprendizado Profundo",
        color="#4E4337", stroke_w=0.17,
        fontsize=8.9, fontweight="bold", ha="center", va="center", zorder=10
    )
    crisp_text(
        ax, xc_pt, 2.91,
        r"Treinamento de Redes Neurais $\cdot$ GPU",
        color=PALETTE["ink_muted"], stroke_w=0.13,
        fontsize=8.0, fontstyle="italic", ha="center", va="center", zorder=10
    )

    pt_bullets = [
        r"$\bullet\;$ Paradigma imperativo e estado mutável",
        r"$\bullet\;$ Abstrações voltadas a redes neurais",
        r"$\bullet\;$ Menor afinidade com operadores puros",
    ]
    for idx_b, b_txt in enumerate(pt_bullets):
        crisp_text(
            ax, xp0 + 0.18, 2.46 - idx_b * 0.37, b_txt,
            color=PALETTE["ink_muted"], stroke_w=0.13,
            fontsize=8.15, ha="left", va="center", zorder=10
        )

    # =======================================================================
    # ZONE 3 (BOTTOM BOOKTABS STRIP): PROGRESSÃO EM 4 ETAPAS & PROTOCOLO DE MEDIÇÃO
    # =======================================================================
    yF0, yF1 = 0.18, 0.98
    ax.plot([xL0, xR1], [yF1, yF1], color=PALETTE["rule_dark"], lw=1.15, zorder=8)
    ax.plot([xL0, xR1], [yF0, yF0], color=PALETTE["rule_dark"], lw=1.15, zorder=8)
    ax.add_patch(Rectangle(
        (xL0, yF0), xR1 - xL0, yF1 - yF0,
        facecolor="#F6F3EC", edgecolor="none", zorder=1
    ))

    # Left half of footer: 4-Stage Controlled Progression
    crisp_text(
        ax, xL0 + 0.14, yF1 - 0.22,
        "Progressão Controlada de Validação:",
        color=PALETTE["navy_deep"], stroke_w=0.16,
        fontsize=8.1, fontweight="bold", ha="left", va="center", zorder=10
    )

    steps = [
        (0.98, "1. NumPy (CPU)"),
        (2.75, "2. JAX (CPU)"),
        (4.58, "3. JAX (GPU / WSL2)"),
        (6.68, "4. Comparação Final"),
    ]
    y_st = yF0 + 0.25
    for idx_s, (xs_c, s_lbl) in enumerate(steps):
        crisp_text(
            ax, xs_c, y_st, s_lbl,
            color=PALETTE["ink_primary"], stroke_w=0.15,
            bg_color="#FFFFFF", pad=0.05,
            fontsize=7.85, fontweight="bold", ha="center", va="center", zorder=12
        )
    # Arrows between the 4 step pills
    for (xa, xb) in [(1.68, 2.15), (3.35, 3.74), (5.43, 5.86)]:
        draw_2d_arrow(ax, (xa, y_st), (xb, y_st), color=PALETTE["amber_sun"], lw=1.15, mutation_scale=8.0, zorder=13)

    # Vertical divider inside footer
    ax.plot([7.78, 7.78], [yF0 + 0.12, yF1 - 0.12], color=PALETTE["rule_light"], lw=0.95, zorder=9)

    # Right half of footer: 3 Fair Benchmarking Rules
    crisp_text(
        ax, 7.96, yF1 - 0.22,
        "Rigor no Benchmark (Comparação Justa):",
        color=PALETTE["teal_adi"], stroke_w=0.16,
        fontsize=8.1, fontweight="bold", ha="left", va="center", zorder=10
    )
    crisp_text(
        ax, 7.96, y_st,
        r"$\bullet\;$ Warm-up JIT     $\bullet\;$ Sincronização (block_until_ready)     $\bullet\;$ Isonomia $\mathrm{float64}$",
        color=PALETTE["ink_secondary"], stroke_w=0.14,
        fontsize=7.85, ha="left", va="center", zorder=10
    )

    ax.set_xlim(0.05, 13.75)
    ax.set_ylim(0.05, 5.42)
    ax.set_aspect("equal")
    ax.axis("off")

    plt.tight_layout(pad=0.08)

    out_dir = Path(__file__).resolve().parent.parent / "figures"
    out_dir.mkdir(parents=True, exist_ok=True)

    svg_path = out_dir / "swe_computational_architecture.svg"
    pdf_path = out_dir / "swe_computational_architecture.pdf"
    png_path = out_dir / "swe_computational_architecture.png"

    fig.savefig(svg_path, format="svg", bbox_inches="tight", facecolor=fig.get_facecolor())
    fig.savefig(pdf_path, format="pdf", bbox_inches="tight", facecolor=fig.get_facecolor())
    fig.savefig(png_path, format="png", dpi=300, bbox_inches="tight", facecolor=fig.get_facecolor())
    print(f"Saved: {svg_path}")
    print(f"Saved: {pdf_path}")
    print(f"Saved: {png_path}")


if __name__ == "__main__":
    build_figure()
