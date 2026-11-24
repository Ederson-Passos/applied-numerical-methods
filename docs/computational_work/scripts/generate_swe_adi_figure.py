"""
Generate an Edward Tufte-inspired vector scientific illustration comparing
(1) Pillar A: 2D Coupled Pentadiagonal System vs. (2) Pillar C: Casulli's
Alternating Direction Implicit (ADI) Decomposition into 1D Tridiagonal Systems
for the 2D Shallow Water Equations (2D SWE), following Casulli (1990).

Spacious two-panel side-by-side comparative layout on warm archival paper (#FCFBF7),
matching Figures 5 and 6's exact aesthetic, color palette, and razor-sharp LaTeX
Latin Modern Roman & Computer Modern Math typography (self-colored micro-stroke
reinforcement). Maximally visual ("falar muito com pouco texto"):

Left Panel:
  1. Pilar A — Esquema 2D Acoplado (Matriz Pentadiagonal de Banda Larga):
     - Left: 2D Spatial Grid (n=4 columns x m=4 rows) with the 5-point cross (+)
       stencil at (i, j) simultaneously coupling all 4 neighbors: West (i-1, j),
       East (i+1, j), South (i, j-1), and North (i, j+1) at t_{k+1}.
     - Right: Schematic N x N Pentadiagonal Matrix (16 x 16 for 4x4 grid) showing:
         * Main diagonal (center i, j)
         * Adjacent sub/super-diagonals at distance +-1 (West/East neighbors)
         * Distant sub/super-diagonals at bandwidth distance +-n (South/North neighbors)
         * Shaded band of width 2n+1 showing where direct Gaussian elimination
           suffers from zero fill-in ("preenchimento de zeros"), requiring iterative
           solvers.

Right Panel:
  2. Pilar C — Decomposição por Direções Alternadas (ADI em 2 Meios-Passos):
     - Top (Nível 1: t_k -> t_{k+1/2} — Varredura Implícita em x):
         * 2D Grid split into m independent horizontal strips (rows), with 3-point
           horizontal stencils (West-Center-East: i-1, i, i+1) and y frozen at t_k.
         * Visual stack of m independent n x n Tridiagonal Matrices (3 compact
           diagonals, zero bandwidth gap, zero fill-in).
     - Bottom (Nível 2: t_{k+1/2} -> t_{k+1} — Varredura Implícita em y):
         * 2D Grid split into n independent vertical strips (columns), with 3-point
           vertical stencils (South-Center-North: j-1, j, j+1) and x frozen at t_{k+1/2}.
         * Visual stack of n independent m x m Tridiagonal Matrices (3 compact
           diagonals).
     - Bottom synthesis badge: Algoritmo de Thomas: Resolução Direta e Exata,
       Custo Linear O(N) (zero fill-in) e Naturalmente Vetorizável/Paralelizável.

Outputs:
  - ../figures/swe_adi_vs_pentadiagonal.svg (vector SVG with embedded glyph paths)
  - ../figures/swe_adi_vs_pentadiagonal.pdf (vector PDF for LaTeX publication)
  - ../figures/swe_adi_vs_pentadiagonal.png (high-resolution raster preview)
"""

import glob
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.patches import Rectangle, FancyArrowPatch, Polygon
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
# 2. High-Contrast Typography & Edward Tufte Muted Cartographic Palette
# ---------------------------------------------------------------------------
PALETTE = {
    "bg_canvas": "#FCFBF7",       # Warm archival paper ivory
    "ink_primary": "#11161C",     # Deep, razor-sharp obsidian ink for titles & math
    "ink_secondary": "#222B35",   # Crisp dark charcoal for explanatory body text
    "ink_muted": "#687380",       # Clean slate gray for leader lines & grid axes
    "rule_light": "#D6CFC4",      # Subtle divider rule
    "cell_bg": "#F3EFEA",         # Subtle archival cell interior
    "cell_focus": "#E8F1F6",      # Highlighted central cell / strip
    "cell_alert": "#F9EBEB",      # Soft terracotta tint for fill-in band / warning
    "cell_teal": "#E6F2F0",       # Soft sea-teal tint for y-sweep vertical strips
    "cell_border": "#4A5968",     # Crisp cell boundary
    "z_node": "#145374",          # Deep cerulean for main diagonal & center node (i,j)
    "u_node": "#8E321E",          # Deep Venetian terracotta for x-coupling (West/East)
    "v_node": "#17575A",          # Deep sea-teal for y-coupling (South/North)
    "amber_sub": "#B06D1E",       # Warm ochre/amber for fill-in / bandwidth highlight
    "mat_bg": "#FAF7F2",          # Matrix canvas background
}


def crisp_text(ax, x, y, s, color="#11161C", stroke_w=0.16, bg_pill=None, pad=0.14, **kwargs):
    """
    Render razor-sharp LaTeX text by reinforcing ultra-thin Computer Modern
    hairlines with a micro self-colored stroke (no blurry halo!).
    """
    if bg_pill is not None:
        kwargs["bbox"] = dict(
            boxstyle=f"round,pad={pad}",
            facecolor=bg_pill,
            edgecolor="none",
            alpha=0.92,
        )
    t = ax.text(x, y, s, color=color, **kwargs)
    if stroke_w > 0:
        t.set_path_effects([pe.withStroke(linewidth=stroke_w, foreground=color)])
    return t


def draw_2d_arrow(
    ax, p0, p1, color, lw=1.4, mutation_scale=11.5, arrowstyle="-|>",
    zorder=20, ls="-", alpha=1.0, connectionstyle="arc3,rad=0.0"
):
    arr = FancyArrowPatch(
        p0, p1,
        arrowstyle=arrowstyle,
        mutation_scale=mutation_scale,
        color=color,
        linewidth=lw,
        linestyle=ls,
        alpha=alpha,
        connectionstyle=connectionstyle,
        shrinkA=0,
        shrinkB=0,
        zorder=zorder,
    )
    ax.add_patch(arr)
    return arr


def draw_tridiag_matrix_stack(
    ax, x0, y0, size, n_dim, count_stack, diag_col, off_col,
    stack_dx=0.18, stack_dy=0.16, zorder_base=10
):
    """
    Draw a visual stack of independent n_dim x n_dim Tridiagonal Matrices
    with crisp square entries for the 3 diagonals (main + sub + super).
    """
    cell_s = size / n_dim
    # Draw back-to-front in the stack
    for s_idx in range(count_stack - 1, -1, -1):
        xs = x0 + s_idx * stack_dx
        ys = y0 + s_idx * stack_dy
        zb = zorder_base + (count_stack - s_idx) * 3
        alpha_card = 1.0 if s_idx == 0 else (0.72 if s_idx == 1 else 0.48)

        # Matrix square background
        ax.add_patch(Rectangle(
            (xs, ys), size, size,
            facecolor=PALETTE["mat_bg"] if s_idx == 0 else "#EFECE6",
            edgecolor=PALETTE["cell_border"],
            linewidth=1.25 if s_idx == 0 else 0.85,
            alpha=alpha_card, zorder=zb
        ))

        if s_idx == 0:
            # Subtle internal matrix grid lines on front matrix
            for k in range(1, n_dim):
                ax.plot([xs + k * cell_s, xs + k * cell_s], [ys, ys + size],
                        color=PALETTE["rule_light"], lw=0.45, zorder=zb + 1)
                ax.plot([xs, xs + size], [ys + k * cell_s, ys + k * cell_s],
                        color=PALETTE["rule_light"], lw=0.45, zorder=zb + 1)

            # Populate 3 diagonals (row r from 0..n_dim-1 top-to-bottom)
            for r in range(n_dim):
                for c in range(n_dim):
                    if abs(r - c) <= 1:
                        cx = xs + c * cell_s
                        cy = ys + (n_dim - 1 - r) * cell_s
                        col = diag_col if r == c else off_col
                        pad_m = 0.08 * cell_s
                        ax.add_patch(Rectangle(
                            (cx + pad_m, cy + pad_m),
                            cell_s - 2 * pad_m, cell_s - 2 * pad_m,
                            facecolor=col, edgecolor="none",
                            alpha=0.92, zorder=zb + 2
                        ))


def build_figure():
    fig, ax = plt.subplots(figsize=(15.6, 9.1), dpi=300)
    fig.patch.set_facecolor(PALETTE["bg_canvas"])
    ax.set_facecolor(PALETTE["bg_canvas"])

    # Vertical dashed divider separating Left Panel (Pilar A) and Right Panel (Pilar C - ADI)
    ax.plot([-0.35, -0.35], [-4.75, 4.45], color=PALETTE["rule_light"], lw=0.95, ls="--", zorder=3)

    # =======================================================================
    # LEFT PANEL: PILAR A — 2D COUPLED PENTADIAGONAL SYSTEM
    # =======================================================================
    xc_L = -4.65

    crisp_text(
        ax, xc_L, 4.25,
        r"1. Pilar A — Esquema 2D Acoplado: Estêncil em Cruz e Matriz Pentadiagonal",
        color=PALETTE["u_node"], stroke_w=0.20,
        fontsize=10.8, fontweight="bold", ha="center", va="bottom", zorder=28
    )
    crisp_text(
        ax, xc_L, 4.00,
        r"Acopla simultaneamente $x$ e $y$ em $t_{k+1}$ $\;\Longrightarrow\;$ 1 sistema global $N \times N$ de banda larga ($N = m\cdot n$)",
        color=PALETTE["ink_primary"], stroke_w=0.15,
        fontsize=9.1, ha="center", va="top", zorder=28
    )

    # -----------------------------------------------------------------------
    # Left Top: 2D Grid (n=4 x m=4) with 5-Point Cross (+) Stencil
    # -----------------------------------------------------------------------
    gx_L = -7.95
    gy_L = 0.45
    nc_L, mc_L = 4, 4
    cs_L = 0.68  # cell size

    crisp_text(
        ax, gx_L + 2 * cs_L, gy_L + 4 * cs_L + 0.34,
        r"Malha 2D ($n \times m$) com Estêncil 5-Pontos (+)",
        color=PALETTE["ink_primary"], stroke_w=0.17,
        fontsize=9.2, fontweight="bold", ha="center", va="bottom", zorder=25
    )

    # Stencil center at (col=1, row=2) -> (i, j)
    ic_st, jc_st = 1, 2
    stencil_cells = {
        (ic_st, jc_st): ("center", PALETTE["cell_focus"]),
        (ic_st - 1, jc_st): ("x_nb", "#F9E9E4"),
        (ic_st + 1, jc_st): ("x_nb", "#F9E9E4"),
        (ic_st, jc_st - 1): ("y_nb", PALETTE["cell_teal"]),
        (ic_st, jc_st + 1): ("y_nb", PALETTE["cell_teal"]),
    }

    for ix in range(nc_L):
        for iy in range(mc_L):
            x_c = gx_L + ix * cs_L
            y_c = gy_L + iy * cs_L
            if (ix, iy) in stencil_cells:
                kind, fc = stencil_cells[(ix, iy)]
                ec = PALETTE["z_node"] if kind == "center" else (
                    PALETTE["u_node"] if kind == "x_nb" else PALETTE["v_node"]
                )
                lw = 1.65
                zo = 8
            else:
                fc = PALETTE["cell_bg"]
                ec = PALETTE["cell_border"]
                lw = 0.85
                zo = 4
            ax.add_patch(Rectangle(
                (x_c, y_c), cs_L, cs_L,
                facecolor=fc, edgecolor=ec, linewidth=lw, zorder=zo
            ))

    # Center coordinates of the 5 stencil cells
    def cell_center_L(ix, iy):
        return (gx_L + (ix + 0.5) * cs_L, gy_L + (iy + 0.5) * cs_L)

    P_c = cell_center_L(ic_st, jc_st)
    P_w = cell_center_L(ic_st - 1, jc_st)
    P_e = cell_center_L(ic_st + 1, jc_st)
    P_s = cell_center_L(ic_st, jc_st - 1)
    P_n = cell_center_L(ic_st, jc_st + 1)

    # Cross (+) coupling arrows
    draw_2d_arrow(ax, P_c, P_w, color=PALETTE["u_node"], lw=2.1, mutation_scale=10.5, arrowstyle="<|-|>", zorder=18)
    draw_2d_arrow(ax, P_c, P_e, color=PALETTE["u_node"], lw=2.1, mutation_scale=10.5, arrowstyle="<|-|>", zorder=18)
    draw_2d_arrow(ax, P_c, P_s, color=PALETTE["v_node"], lw=2.1, mutation_scale=10.5, arrowstyle="<|-|>", zorder=18)
    draw_2d_arrow(ax, P_c, P_n, color=PALETTE["v_node"], lw=2.1, mutation_scale=10.5, arrowstyle="<|-|>", zorder=18)

    # Node dots
    ax.plot(*P_c, marker="o", markersize=7.5, markerfacecolor=PALETTE["z_node"],
            markeredgecolor="white", markeredgewidth=1.1, zorder=22)
    for pt in [P_w, P_e]:
        ax.plot(*pt, marker="s", markersize=6.2, markerfacecolor=PALETTE["u_node"],
                markeredgecolor="white", markeredgewidth=1.0, zorder=22)
    for pt in [P_s, P_n]:
        ax.plot(*pt, marker="D", markersize=6.0, markerfacecolor=PALETTE["v_node"],
                markeredgecolor="white", markeredgewidth=1.0, zorder=22)

    # Column and row index labels around the 4x4 grid
    col_lbls = [r"$i-1$", r"$i$", r"$i+1$", r"$i+2$"]
    row_lbls = [r"$j-2$", r"$j-1$", r"$j$", r"$j+1$"]
    for ix in range(nc_L):
        crisp_text(
            ax, gx_L + (ix + 0.5) * cs_L, gy_L - 0.12, col_lbls[ix],
            color=PALETTE["ink_secondary"], stroke_w=0.14,
            fontsize=8.2, fontweight="bold", ha="center", va="top", zorder=15
        )
    for iy in range(mc_L):
        crisp_text(
            ax, gx_L - 0.12, gy_L + (iy + 0.5) * cs_L, row_lbls[iy],
            color=PALETTE["ink_secondary"], stroke_w=0.14,
            fontsize=8.2, fontweight="bold", ha="right", va="center", zorder=15
        )

    # Brief explanation below the 2D cross grid
    crisp_text(
        ax, gx_L + 2 * cs_L, gy_L - 0.52,
        "Vizinhos Leste/Oeste ($\\pm 1$ na matriz)\n"
        "e Norte/Sul ($\\pm n$ na matriz)\n"
        "acoplados ao mesmo tempo.",
        color=PALETTE["ink_secondary"], stroke_w=0.13,
        fontsize=8.1, fontstyle="italic", ha="center", va="top", linespacing=1.22, zorder=20
    )

    # -----------------------------------------------------------------------
    # Left Right-Side: Schematic 16x16 Pentadiagonal Matrix (4x4 Grid)
    # -----------------------------------------------------------------------
    mx_L = -4.55
    my_L = 0.05
    msize_L = 3.20
    N_mat = 16       # 4x4 grid -> 16x16 matrix
    n_bw = 4         # bandwidth offset n = 4
    mc_s = msize_L / N_mat

    crisp_text(
        ax, mx_L + 0.5 * msize_L, my_L + msize_L + 0.25,
        r"Matriz Pentadiagonal $A$ ($N \times N$)",
        color=PALETTE["ink_primary"], stroke_w=0.17,
        fontsize=9.2, fontweight="bold", ha="center", va="bottom", zorder=25
    )

    # Matrix outer box
    ax.add_patch(Rectangle(
        (mx_L, my_L), msize_L, msize_L,
        facecolor=PALETTE["mat_bg"], edgecolor=PALETTE["cell_border"],
        linewidth=1.35, zorder=6
    ))

    # Draw 4x4 block dividers (each block is 4x4)
    for b in range(1, 4):
        pos_b = b * 4 * mc_s
        ax.plot([mx_L + pos_b, mx_L + pos_b], [my_L, my_L + msize_L],
                color=PALETTE["rule_light"], lw=0.70, ls=":", zorder=7)
        ax.plot([mx_L, mx_L + msize_L], [my_L + pos_b, my_L + pos_b],
                color=PALETTE["rule_light"], lw=0.70, ls=":", zorder=7)

    # Populate Pentadiagonal entries + Fill-in zeros inside the band
    for r in range(N_mat):
        for c in range(N_mat):
            cx = mx_L + c * mc_s
            cy = my_L + (N_mat - 1 - r) * mc_s
            pad_e = 0.06 * mc_s

            if r == c:
                # Main diagonal: Center (i, j)
                ax.add_patch(Rectangle(
                    (cx + pad_e, cy + pad_e), mc_s - 2 * pad_e, mc_s - 2 * pad_e,
                    facecolor=PALETTE["z_node"], edgecolor="none", zorder=12
                ))
            elif (c == r + 1 and (r + 1) % n_bw != 0) or (c == r - 1 and r % n_bw != 0):
                # Immediate West/East neighbors (+-1)
                ax.add_patch(Rectangle(
                    (cx + pad_e, cy + pad_e), mc_s - 2 * pad_e, mc_s - 2 * pad_e,
                    facecolor=PALETTE["u_node"], edgecolor="none", zorder=11
                ))
            elif abs(r - c) == n_bw:
                # Distant North/South neighbors (+-n)
                ax.add_patch(Rectangle(
                    (cx + pad_e, cy + pad_e), mc_s - 2 * pad_e, mc_s - 2 * pad_e,
                    facecolor=PALETTE["v_node"], edgecolor="none", zorder=11
                ))
            elif abs(r - c) < n_bw:
                # Zero entries inside the band that suffer from Gaussian Elimination fill-in!
                ax.add_patch(Rectangle(
                    (cx + pad_e, cy + pad_e), mc_s - 2 * pad_e, mc_s - 2 * pad_e,
                    facecolor="#F2CFC2", edgecolor="none", alpha=0.80, zorder=8
                ))

    # Bandwidth bracket on top-right of the matrix showing distance n
    r_demo = 2
    c_diag = r_demo
    c_far = r_demo + n_bw
    x_diag_c = mx_L + (c_diag + 0.5) * mc_s
    x_far_c = mx_L + (c_far + 0.5) * mc_s
    y_row_demo = my_L + (N_mat - 1 - r_demo + 0.5) * mc_s

    # Bracket below the matrix showing bandwidth n
    y_bw_brk = my_L - 0.20
    x_bw_0 = mx_L + 5.5 * mc_s
    x_bw_1 = mx_L + (5.5 + n_bw) * mc_s
    draw_2d_arrow(
        ax, (x_bw_0, y_bw_brk), (x_bw_1, y_bw_brk),
        color=PALETTE["v_node"], lw=1.2, mutation_scale=8.5, arrowstyle="<|-|>", zorder=20
    )
    crisp_text(
        ax, 0.5 * (x_bw_0 + x_bw_1), y_bw_brk - 0.08,
        r"Banda larga de distância $n$" + "\n" + r"(vizinhos Norte/Sul afastados)",
        color=PALETTE["v_node"], stroke_w=0.15,
        fontsize=8.1, fontweight="bold", ha="center", va="top", linespacing=1.16, zorder=22
    )

    # Callout pointing to the fill-in band inside the matrix
    p_fill_target = (mx_L + 9.5 * mc_s, my_L + (N_mat - 1 - 7.0) * mc_s)
    p_fill_text = (mx_L + msize_L - 0.05, my_L + msize_L - 0.35)
    draw_2d_arrow(
        ax, (p_fill_text[0] - 0.65, p_fill_text[1] - 0.35), p_fill_target,
        color=PALETTE["u_node"], lw=1.1, mutation_scale=9,
        connectionstyle="arc3,rad=-0.15", zorder=23
    )
    crisp_text(
        ax, mx_L + msize_L - 0.05, my_L + msize_L - 0.10,
        "Zeros dentro da banda\nsofreriam fill-in na\neliminação direta!",
        color=PALETTE["u_node"], stroke_w=0.15, bg_pill=PALETTE["cell_alert"], pad=0.10,
        fontsize=7.9, fontweight="bold", ha="right", va="top", linespacing=1.15, zorder=24
    )

    # -----------------------------------------------------------------------
    # Left Bottom: Legend of the 5 Diagonals & Consequence Badge
    # -----------------------------------------------------------------------
    y_leg_L = -1.65
    ax.plot([-8.45, -0.75], [-1.30, -1.30], color=PALETTE["rule_light"], lw=0.80, zorder=5)

    crisp_text(
        ax, xc_L, -1.48,
        r"Estrutura das 5 Diagonais de $A\,\mathbf{z}^{k+1} = \mathbf{b}$ e Custo de Resolução",
        color=PALETTE["ink_primary"], stroke_w=0.18,
        fontsize=9.5, fontweight="bold", ha="center", va="top", zorder=25
    )

    # 4 legend items for the matrix structure
    leg_items_L = [
        (PALETTE["z_node"], "Diagonal principal:", r"célula central $z_{i,j}^{k+1}$ ($>0$, dominante)"),
        (PALETTE["u_node"], r"2 diagonais adjacentes ($\pm 1$):", r"vizinhos Leste/Oeste ($z_{i\pm 1, j}^{k+1}$)"),
        (PALETTE["v_node"], r"2 diagonais afastadas ($\pm n$):", r"vizinhos Norte/Sul ($z_{i, j\pm 1}^{k+1}$)"),
        ("#E5B3A3", "Faixa interna (fill-in):", "zeros preenchidos se usar Gauss direto"),
    ]

    for idx_l, (col_l, tit_l, desc_l) in enumerate(leg_items_L):
        yl = -2.00 - idx_l * 0.45
        ax.add_patch(Rectangle(
            (-8.15, yl - 0.11), 0.24, 0.22,
            facecolor=col_l, edgecolor=PALETTE["cell_border"], linewidth=0.7, zorder=20
        ))
        crisp_text(
            ax, -7.78, yl, tit_l,
            color=PALETTE["ink_primary"], stroke_w=0.16,
            fontsize=8.6, fontweight="bold", ha="left", va="center", zorder=22
        )
        crisp_text(
            ax, -4.85, yl, desc_l,
            color=PALETTE["ink_secondary"], stroke_w=0.13,
            fontsize=8.5, ha="left", va="center", zorder=22
        )

    # Bottom summary pill for Left Panel
    crisp_text(
        ax, xc_L, -4.15,
        r"Na prática, usa Métodos Iterativos (ex.: Gradiente Conjugado Pré-condicionado / SOR)" + "\n"
        + r"Vantagem: preserva simetria 2D plena mesmo para $\Delta t$ muito grande",
        color=PALETTE["u_node"], stroke_w=0.16, bg_pill=PALETTE["cell_alert"], pad=0.18,
        fontsize=8.6, fontweight="bold", ha="center", va="center", linespacing=1.24, zorder=25
    )

    # =======================================================================
    # RIGHT PANEL: PILAR C — ADI (2 SEQUENTIAL HALF-STEPS -> TRIDIAGONAL)
    # =======================================================================
    xc_R = 4.65

    crisp_text(
        ax, xc_R, 4.25,
        r"2. Pilar C — Variante ADI: Decomposição em Sistemas Tridiagonais 1D",
        color=PALETTE["z_node"], stroke_w=0.20,
        fontsize=10.8, fontweight="bold", ha="center", va="bottom", zorder=28
    )
    crisp_text(
        ax, xc_R, 4.00,
        r"Divide $\Delta t$ em 2 meios-passos ($\Delta t/2$) $\;\Longrightarrow\;$ desacopla linhas e colunas em matrizes de 3 diagonais",
        color=PALETTE["ink_primary"], stroke_w=0.15,
        fontsize=9.1, ha="center", va="top", zorder=28
    )

    # -----------------------------------------------------------------------
    # Right Top: NÍVEL 1 (t_k -> t_{k+1/2} — Varredura Implícita em x)
    # -----------------------------------------------------------------------
    crisp_text(
        ax, 0.15, 3.42,
        r"Nível 1 ($t_k \rightarrow t_{k+1/2}$ — Varredura em $x$): $u^{k+1/2},\, z^{k+1/2}$ implícitos; direção $y$ explícita ($t_k$)",
        color=PALETTE["u_node"], stroke_w=0.18,
        fontsize=9.4, fontweight="bold", ha="left", va="bottom", zorder=26
    )

    # 2D Grid split into m=4 independent horizontal strips (rows)
    gx_R1 = 0.45
    gy_R1 = 0.62
    cs_R = 0.62
    row_gap = 0.09  # visual separation between independent horizontal rows!

    row_tints = ["#F9E9E4", "#F4DCD4", "#F9E9E4", "#F4DCD4"]
    for iy in range(4):
        y_strip = gy_R1 + iy * (cs_R + row_gap)
        # Draw each horizontal row as an independent strip
        for ix in range(4):
            x_c = gx_R1 + ix * cs_R
            ax.add_patch(Rectangle(
                (x_c, y_strip), cs_R, cs_R,
                facecolor=row_tints[iy], edgecolor=PALETTE["u_node"],
                linewidth=1.1, zorder=6
            ))
        # Draw 1D horizontal stencil arrows (left-center-right) along each row
        yc_s = y_strip + 0.5 * cs_R
        for ix in range(4):
            xc_s = gx_R1 + (ix + 0.5) * cs_R
            ax.plot(xc_s, yc_s, marker="o", markersize=4.8,
                    markerfacecolor=PALETTE["z_node"], markeredgecolor="white",
                    markeredgewidth=0.8, zorder=14)
            if ix < 3:
                xc_next = gx_R1 + (ix + 1.5) * cs_R
                draw_2d_arrow(
                    ax, (xc_s + 0.08, yc_s), (xc_next - 0.08, yc_s),
                    color=PALETTE["u_node"], lw=1.45, mutation_scale=8.0,
                    arrowstyle="<|-|>", zorder=12
                )
        # Row label on the left
        crisp_text(
            ax, gx_R1 - 0.12, yc_s, rf"Linha $j_{iy+1}$",
            color=PALETTE["u_node"], stroke_w=0.14,
            fontsize=7.9, fontweight="bold", ha="right", va="center", zorder=15
        )

    crisp_text(
        ax, gx_R1 + 2 * cs_R, gy_R1 - 0.14,
        r"$m$ faixas horizontais independentes" + "\n" + r"(acopla só $i-1,\, i,\, i+1$)",
        color=PALETTE["ink_secondary"], stroke_w=0.13,
        fontsize=8.1, fontstyle="italic", ha="center", va="top", linespacing=1.18, zorder=20
    )

    # Arrow from horizontal strips to stack of m Tridiagonal n x n matrices
    draw_2d_arrow(
        ax, (gx_R1 + 4 * cs_R + 0.18, gy_R1 + 1.45),
        (4.15, gy_R1 + 1.45),
        color=PALETTE["u_node"], lw=2.0, mutation_scale=12, zorder=20
    )
    crisp_text(
        ax, 3.60, gy_R1 + 1.62,
        "colapsa em",
        color=PALETTE["u_node"], stroke_w=0.14,
        fontsize=8.0, fontstyle="italic", ha="center", va="bottom", zorder=22
    )

    # Stack of m independent n x n Tridiagonal Matrices (4 x 4 matching n = 4)
    draw_tridiag_matrix_stack(
        ax, x0=4.35, y0=0.72, size=2.15, n_dim=4, count_stack=4,
        diag_col=PALETTE["z_node"], off_col=PALETTE["u_node"],
        stack_dx=0.16, stack_dy=0.14, zorder_base=10
    )

    # Label next to Nível 1 Tridiagonal Stack
    crisp_text(
        ax, 7.12, 2.35,
        r"$m$ Sistemas Tridiagonais" + "\n" + r"independentes ($n \times n$)",
        color=PALETTE["u_node"], stroke_w=0.18,
        fontsize=9.2, fontweight="bold", ha="left", va="center", linespacing=1.20, zorder=25
    )
    crisp_text(
        ax, 7.12, 1.55,
        "• Apenas 3 diagonais compactas:\n"
        "   sub ($-1$), principal ($0$), super ($+1$)\n"
        "• Semibanda mínima ($p = 1$, sem lacunas)\n"
        "• Zero preenchimento (fill-in)\n"
        "• Cada linha $j$ resolvida em paralelo",
        color=PALETTE["ink_secondary"], stroke_w=0.13,
        fontsize=8.1, ha="left", va="center", linespacing=1.26, zorder=25
    )

    # Horizontal divider between Nível 1 and Nível 2
    ax.plot([0.05, 9.55], [-0.08, -0.08], color=PALETTE["rule_light"], lw=0.80, ls=":", zorder=5)

    # -----------------------------------------------------------------------
    # Right Bottom: NÍVEL 2 (t_{k+1/2} -> t_{k+1} — Varredura Implícita em y)
    # -----------------------------------------------------------------------
    crisp_text(
        ax, 0.15, -0.32,
        r"Nível 2 ($t_{k+1/2} \rightarrow t_{k+1}$ — Varredura em $y$): $v^{k+1},\, z^{k+1}$ implícitos; direção $x$ explícita ($t_{k+1/2}$)",
        color=PALETTE["v_node"], stroke_w=0.18,
        fontsize=9.4, fontweight="bold", ha="left", va="top", zorder=26
    )

    # 2D Grid split into n=4 independent vertical strips (columns)
    gx_R2 = 0.45
    gy_R2 = -3.32
    col_gap = 0.09  # visual separation between independent vertical columns!

    col_tints = [PALETTE["cell_teal"], "#D4EAE6", PALETTE["cell_teal"], "#D4EAE6"]
    for ix in range(4):
        x_strip = gx_R2 + ix * (cs_R + col_gap)
        for iy in range(4):
            y_c = gy_R2 + iy * cs_R
            ax.add_patch(Rectangle(
                (x_strip, y_c), cs_R, cs_R,
                facecolor=col_tints[ix], edgecolor=PALETTE["v_node"],
                linewidth=1.1, zorder=6
            ))
        # Draw 1D vertical stencil arrows (bottom-center-top) along each column
        xc_s = x_strip + 0.5 * cs_R
        for iy in range(4):
            yc_s = gy_R2 + (iy + 0.5) * cs_R
            ax.plot(xc_s, yc_s, marker="o", markersize=4.8,
                    markerfacecolor=PALETTE["z_node"], markeredgecolor="white",
                    markeredgewidth=0.8, zorder=14)
            if iy < 3:
                yc_next = gy_R2 + (iy + 1.5) * cs_R
                draw_2d_arrow(
                    ax, (xc_s, yc_s + 0.08), (xc_s, yc_next - 0.08),
                    color=PALETTE["v_node"], lw=1.45, mutation_scale=8.0,
                    arrowstyle="<|-|>", zorder=12
                )
        # Column header on top of each vertical strip
        crisp_text(
            ax, xc_s, gy_R2 + 4 * cs_R + 0.08, rf"Col. $i_{ix+1}$",
            color=PALETTE["v_node"], stroke_w=0.14,
            fontsize=7.7, fontweight="bold", ha="center", va="bottom", zorder=15
        )

    crisp_text(
        ax, gx_R2 + 2 * (cs_R + col_gap) - 0.05, gy_R2 - 0.14,
        r"$n$ faixas verticais independentes" + "\n" + r"(acopla só $j-1,\, j,\, j+1$)",
        color=PALETTE["ink_secondary"], stroke_w=0.13,
        fontsize=8.1, fontstyle="italic", ha="center", va="top", linespacing=1.18, zorder=20
    )

    # Arrow from vertical strips to stack of n Tridiagonal m x m matrices
    draw_2d_arrow(
        ax, (gx_R2 + 4 * cs_R + 3 * col_gap + 0.15, gy_R2 + 1.25),
        (4.15, gy_R2 + 1.25),
        color=PALETTE["v_node"], lw=2.0, mutation_scale=12, zorder=20
    )
    crisp_text(
        ax, 3.65, gy_R2 + 1.42,
        "colapsa em",
        color=PALETTE["v_node"], stroke_w=0.14,
        fontsize=8.0, fontstyle="italic", ha="center", va="bottom", zorder=22
    )

    # Stack of n independent m x m Tridiagonal Matrices (4 x 4 matching m = 4)
    draw_tridiag_matrix_stack(
        ax, x0=4.35, y0=-3.25, size=2.15, n_dim=4, count_stack=4,
        diag_col=PALETTE["z_node"], off_col=PALETTE["v_node"],
        stack_dx=0.16, stack_dy=0.14, zorder_base=10
    )

    # Label next to Nível 2 Tridiagonal Stack
    crisp_text(
        ax, 7.12, -1.65,
        r"$n$ Sistemas Tridiagonais" + "\n" + r"independentes ($m \times m$)",
        color=PALETTE["v_node"], stroke_w=0.18,
        fontsize=9.2, fontweight="bold", ha="left", va="center", linespacing=1.20, zorder=25
    )
    crisp_text(
        ax, 7.12, -2.45,
        "• Mesma estrutura de 3 diagonais:\n"
        "   sub ($-1$), principal ($0$), super ($+1$)\n"
        "• Usa estado intermediário $t_{k+1/2}$\n"
        "• Cada coluna $i$ resolvida em paralelo",
        color=PALETTE["ink_secondary"], stroke_w=0.13,
        fontsize=8.1, ha="left", va="center", linespacing=1.26, zorder=25
    )

    # Bottom Synthesis Badge for Right Panel (Algoritmo de Thomas)
    crisp_text(
        ax, xc_R, -4.15,
        r"Algoritmo de Thomas (Eliminação Direta e Exata em 3 Diagonais): Custo Estritamente Linear $\mathcal{O}(N)$" + "\n"
        + r"Naturalmente vetorizável ($\approx 60\%$ menos tempo de CPU; exige $\Delta t$ moderado para evitar erro de divisão direcional)",
        color=PALETTE["z_node"], stroke_w=0.16, bg_pill=PALETTE["cell_focus"], pad=0.18,
        fontsize=8.6, fontweight="bold", ha="center", va="center", linespacing=1.24, zorder=25
    )

    # Set clean bounds and remove default Matplotlib frame/ticks
    ax.set_xlim(-8.65, 9.75)
    ax.set_ylim(-4.65, 4.65)
    ax.set_aspect("equal")
    ax.axis("off")

    plt.tight_layout(pad=0.12)

    out_dir = Path(__file__).resolve().parent.parent / "figures"
    out_dir.mkdir(parents=True, exist_ok=True)

    svg_path = out_dir / "swe_adi_vs_pentadiagonal.svg"
    pdf_path = out_dir / "swe_adi_vs_pentadiagonal.pdf"
    png_path = out_dir / "swe_adi_vs_pentadiagonal.png"

    fig.savefig(svg_path, format="svg", bbox_inches="tight", facecolor=fig.get_facecolor())
    fig.savefig(pdf_path, format="pdf", bbox_inches="tight", facecolor=fig.get_facecolor())
    fig.savefig(png_path, format="png", dpi=300, bbox_inches="tight", facecolor=fig.get_facecolor())
    print(f"Saved: {svg_path}")
    print(f"Saved: {pdf_path}")
    print(f"Saved: {png_path}")


if __name__ == "__main__":
    build_figure()
