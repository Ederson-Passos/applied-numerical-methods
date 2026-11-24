"""
Generate an Edward Tufte-inspired vector scientific illustration of Casulli's
Staggered Spatial Finite Difference Grid (Arakawa C-grid) and why it eliminates
spurious pressure/elevation checkerboard oscillations in the 2D Shallow Water
Equations (2D SWE), following Casulli (1990).

Spacious two-panel comparative layout on warm archival paper (#FCFBF7), without
internal top titles or header bars, featuring razor-sharp LaTeX Latin Modern
Roman & Computer Modern Math typography (self-colored micro-stroke reinforcement).

Left Panel:
  1. Malha Colocalizada (no centro da célula) e Oscilação Espúria:
     - 1D cross-section of a 2*dx sawtooth/checkerboard free-surface wave
       (alto -> baixo -> alto -> baixo) across cells i-1, i, i+1, i+2.
     - Colocated stencil (z_{i+1} - z_{i-1}) / (2*dx) skips cell i and reads
       identical elevations z_{i-1} = z_{i+1}, yielding dz/dx = 0 ("ponto cego"
       to the sawtooth wave).
     - Below: 2D colocated cells showing (u, v, z) stored together at centers.

Right Panel:
  2. Malha Espacial Escalonada de Casulli (Eliminação do Ponto Cego):
     - Same sawtooth free-surface wave across cells i, i+1, but with u_{i+1/2, j}
       located at the vertical face x_{i+1/2} directly between cell centers i
       and i+1.
     - Staggered stencil (z_{i+1, j} - z_{i, j}) / dx uses immediately adjacent
       cells, detecting the exact steep slope != 0 and eliminating any blind spot.
     - Below: Detailed 2D staggered grid (cell (i, j) and neighbors) showing:
         * z_{i, j} at the cell center (x_i, y_j)
         * u_{i-1/2, j} and u_{i+1/2, j} at the left and right vertical faces
         * v_{i, j-1/2} and v_{i, j+1/2} at the bottom and top horizontal faces
         * Control volume dimensions dx and dy and compact gradient coupling.

Outputs:
  - ../figures/swe_staggered_grid.svg (vector SVG with embedded glyph paths)
  - ../figures/swe_staggered_grid.pdf (vector PDF for LaTeX publication)
  - ../figures/swe_staggered_grid.png (high-resolution raster preview)
"""

import glob
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.patches import Rectangle, FancyArrowPatch
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
    "water_high": "#A9CFE5",      # High water column fill (crista)
    "water_low": "#D6EAF5",       # Low water column fill (vale)
    "water_edge": "#1E4966",      # Crisp structural water edge
    "cell_bg": "#F3EFEA",         # Subtle archival cell interior
    "cell_focus": "#E8F1F6",      # Highlighted central cell (i, j)
    "cell_border": "#4A5968",     # Crisp cell boundary
    "z_node": "#145374",          # Deep cerulean for elevation z_{i,j} at center
    "u_node": "#8E321E",          # Deep Venetian terracotta for horizontal velocity u_{i+1/2,j}
    "v_node": "#17575A",          # Deep sea-teal for vertical velocity v_{i,j+1/2}
    "spurious_red": "#8E321E",    # Venetian terracotta for blind spot / error alert
    "valid_teal": "#145374",      # Cerulean/teal for staggered compact coupling
    "bed_fill": "#D8CEC0",        # Seabed base strip
    "bed_edge": "#5E4F41",        # Seabed line
}


def crisp_text(ax, x, y, s, color="#11161C", stroke_w=0.16, bg_pill=None, pad=0.16, **kwargs):
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


def build_figure():
    fig, ax = plt.subplots(figsize=(15.6, 9.1), dpi=300)
    fig.patch.set_facecolor(PALETTE["bg_canvas"])
    ax.set_facecolor(PALETTE["bg_canvas"])

    # Vertical dashed divider separating Left Panel (Colocated) and Right Panel (Staggered)
    ax.plot([0.0, 0.0], [-4.85, 4.55], color=PALETTE["rule_light"], lw=0.95, ls="--", zorder=3)

    # =======================================================================
    # LEFT PANEL: COLOCATED GRID & SPURIOUS CHECKERBOARD OSCILLATION
    # =======================================================================
    xc_L = -4.55

    # Panel 1 Title & Mathematical Subtitle
    crisp_text(
        ax, xc_L, 4.42,
        r"1. Malha Colocalizada (No Centro): Ponto Cego e Oscilação Espúria",
        color=PALETTE["spurious_red"], stroke_w=0.20,
        fontsize=11.0, fontweight="bold", ha="center", va="bottom", zorder=28
    )
    crisp_text(
        ax, xc_L, 4.18,
        r"Variáveis $(u, v, z)$ no mesmo ponto $\;\Longrightarrow\;$ derivada central pula a célula $i$: $\;\left(\dfrac{\partial z}{\partial x}\right)_i \approx \dfrac{z_{i+1} - z_{i-1}}{2\Delta x}$",
        color=PALETTE["ink_primary"], stroke_w=0.15,
        fontsize=9.3, ha="center", va="top", zorder=28
    )

    # -----------------------------------------------------------------------
    # Left Top: 1D Sawtooth Wave Cross-Section (Cells i-1, i, i+1, i+2)
    # -----------------------------------------------------------------------
    x0_L = -8.15
    dx_L = 1.80
    y_base_L = 0.55
    y_mean_L = 1.60
    dz_amp = 0.44  # alternating +dz_amp (alto) and -dz_amp (baixo)

    # Cell index labels and elevations:
    # i-1: ALTO (+dz), i: BAIXO (-dz), i+1: ALTO (+dz), i+2: BAIXO (-dz)
    cell_labels_L = [r"$i - 1$", r"$i$", r"$i + 1$", r"$i + 2$"]
    state_labels_L = ["Alto", "Baixo", "Alto", "Baixo"]
    z_offsets_L = [+dz_amp, -dz_amp, +dz_amp, -dz_amp]

    # Seabed strip at y_base_L
    ax.add_patch(Rectangle(
        (x0_L - 0.15, y_base_L - 0.16), 4 * dx_L + 0.30, 0.16,
        facecolor=PALETTE["bed_fill"], edgecolor="none", zorder=4
    ))
    ax.plot(
        [x0_L - 0.15, x0_L + 4 * dx_L + 0.15], [y_base_L, y_base_L],
        color=PALETTE["bed_edge"], lw=1.25, zorder=8
    )

    # Mean reference level dashed line
    ax.plot(
        [x0_L - 0.25, x0_L + 4 * dx_L + 0.25], [y_mean_L, y_mean_L],
        color=PALETTE["ink_muted"], lw=0.75, ls=":", zorder=6
    )
    crisp_text(
        ax, x0_L - 0.28, y_mean_L, r"$z = 0$",
        color=PALETTE["ink_muted"], stroke_w=0.12,
        fontsize=8.3, ha="right", va="center", zorder=15
    )

    centers_x_L = []
    centers_y_L = []

    for k in range(4):
        xl = x0_L + k * dx_L
        xr = xl + dx_L
        xc = 0.5 * (xl + xr)
        zk = y_mean_L + z_offsets_L[k]
        centers_x_L.append(xc)
        centers_y_L.append(zk)

        fill_col = PALETTE["water_high"] if z_offsets_L[k] > 0 else PALETTE["water_low"]

        # Water column rectangle for cell k
        ax.add_patch(Rectangle(
            (xl, y_base_L), dx_L, zk - y_base_L,
            facecolor=fill_col, edgecolor="none", alpha=0.82, zorder=5
        ))
        # Top water surface segment
        ax.plot([xl, xr], [zk, zk], color=PALETTE["water_edge"], lw=2.0, zorder=10)

        # Vertical cell face lines
        ax.plot([xl, xl], [y_base_L, y_mean_L + dz_amp + 0.28],
                color=PALETTE["cell_border"], lw=0.95, ls="--", zorder=9)

        # Cell center node (colocated u, v, z)
        ax.plot(xc, zk, marker="o", markersize=6.8,
                markerfacecolor=PALETTE["z_node"], markeredgecolor="white",
                markeredgewidth=1.1, zorder=16)

        # Label "Célula ... (Alto/Baixo)" cleanly near bottom of each column
        crisp_text(
            ax, xc, y_base_L + 0.08,
            f"Célula {cell_labels_L[k]} ({state_labels_L[k]})",
            color=PALETTE["ink_secondary"], stroke_w=0.13,
            fontsize=8.1, ha="center", va="bottom", zorder=14
        )

    # Final right vertical cell boundary
    ax.plot([x0_L + 4 * dx_L, x0_L + 4 * dx_L], [y_base_L, y_mean_L + dz_amp + 0.28],
            color=PALETTE["cell_border"], lw=0.95, ls="--", zorder=9)

    # Dashed sawtooth wave profile connecting the cell centers ("serrilhado falso 2*dx")
    ax.plot(
        centers_x_L, centers_y_L,
        color=PALETTE["spurious_red"], lw=1.6, ls="--", zorder=14
    )

    # Node labels z_{i-1}, z_i, z_{i+1}, z_{i+2} placed with zero collision
    crisp_text(
        ax, centers_x_L[0], centers_y_L[0] + 0.12,
        r"$z_{i-1} = +z_0$",
        color=PALETTE["z_node"], stroke_w=0.17, bg_pill=PALETTE["bg_canvas"], pad=0.10,
        fontsize=8.9, fontweight="bold", ha="center", va="bottom", zorder=20
    )
    crisp_text(
        ax, centers_x_L[1], centers_y_L[1] + 0.13,
        r"$z_i = -z_0$ (ignorado!)",
        color=PALETTE["spurious_red"], stroke_w=0.16, bg_pill=PALETTE["bg_canvas"], pad=0.10,
        fontsize=8.4, fontweight="bold", ha="center", va="bottom", zorder=20
    )
    crisp_text(
        ax, centers_x_L[2], centers_y_L[2] + 0.12,
        r"$z_{i+1} = +z_0$",
        color=PALETTE["z_node"], stroke_w=0.17, bg_pill=PALETTE["bg_canvas"], pad=0.10,
        fontsize=8.9, fontweight="bold", ha="center", va="bottom", zorder=20
    )
    crisp_text(
        ax, centers_x_L[3], centers_y_L[3] + 0.13,
        r"$z_{i+2} = -z_0$",
        color=PALETTE["z_node"], stroke_w=0.15, bg_pill=PALETTE["bg_canvas"], pad=0.10,
        fontsize=8.5, ha="center", va="bottom", zorder=20
    )

    # Gentle arch connecting i-1 and i+1 showing the blind spot over cell i
    draw_2d_arrow(
        ax, (centers_x_L[0], centers_y_L[0] + 0.42),
        (centers_x_L[2], centers_y_L[2] + 0.42),
        color=PALETTE["spurious_red"], lw=1.6, mutation_scale=11,
        arrowstyle="<|-|>", connectionstyle="arc3,rad=-0.16", zorder=22
    )

    # Zero-slope line between z_{i-1} and z_{i+1}
    ax.plot(
        [centers_x_L[0], centers_x_L[2]],
        [centers_y_L[0], centers_y_L[2]],
        color=PALETTE["spurious_red"], lw=1.35, ls=":", zorder=15
    )

    crisp_text(
        ax, centers_x_L[1], 3.16,
        r"Pula a célula $i$: $\;z_{i+1} = z_{i-1} \;\Longrightarrow\; \dfrac{z_{i+1} - z_{i-1}}{2\Delta x} = 0$",
        color=PALETTE["spurious_red"], stroke_w=0.18, bg_pill="#F9EFEA",
        fontsize=9.1, fontweight="bold", ha="center", va="bottom", zorder=25
    )
    crisp_text(
        ax, centers_x_L[1], 2.86,
        r"(Ponto cego: o esquema enxerga água plana e não corrige o serrilhado falso)",
        color=PALETTE["ink_secondary"], stroke_w=0.13,
        fontsize=8.3, fontstyle="italic", ha="center", va="bottom", zorder=25
    )

    # 2*dx bracket at bottom of 1D wave
    y_brk_L = y_base_L - 0.30
    draw_2d_arrow(
        ax, (centers_x_L[0], y_brk_L), (centers_x_L[2], y_brk_L),
        color=PALETTE["ink_muted"], lw=1.0, mutation_scale=9, arrowstyle="<|-|>", zorder=15
    )
    crisp_text(
        ax, centers_x_L[1], y_brk_L - 0.08,
        r"Estêncil largo de $2\Delta x$ entre vizinhos $i-1$ e $i+1$",
        color=PALETTE["ink_muted"], stroke_w=0.13, bg_pill=PALETTE["bg_canvas"],
        fontsize=8.3, fontstyle="italic", ha="center", va="top", zorder=18
    )

    # -----------------------------------------------------------------------
    # Left Bottom: 2D Colocated Grid Cells (Showing u, v, z at the same point)
    # -----------------------------------------------------------------------
    crisp_text(
        ax, xc_L, -0.35,
        r"Vista em Planta 2D — Malha Colocalizada: $(u, v, z)$ armazenados juntos no centro",
        color=PALETTE["ink_primary"], stroke_w=0.18,
        fontsize=9.8, fontweight="bold", ha="center", va="bottom", zorder=25
    )

    g_x0_L = -7.65
    g_y0_L = -3.45
    g_dx_L = 2.05
    g_dy_L = 1.95

    col_titles_2d = [r"Célula $(i-1, j)$", r"Célula $(i, j)$", r"Célula $(i+1, j)$"]
    col_var_labels = [
        r"$(u, v, z)_{i-1, j}$",
        r"$(u, v, z)_{i, j}$",
        r"$(u, v, z)_{i+1, j}$",
    ]

    for k in range(3):
        xl = g_x0_L + k * g_dx_L
        xc = xl + 0.5 * g_dx_L
        yc = g_y0_L + 0.5 * g_dy_L

        bg_c = "#F7E9E4" if k == 1 else PALETTE["cell_bg"]
        ax.add_patch(Rectangle(
            (xl, g_y0_L), g_dx_L, g_dy_L,
            facecolor=bg_c, edgecolor=PALETTE["cell_border"],
            linewidth=1.25, zorder=5
        ))

        # Cell header
        crisp_text(
            ax, xc, g_y0_L + g_dy_L - 0.16,
            col_titles_2d[k],
            color=PALETTE["ink_muted"], stroke_w=0.13,
            fontsize=8.3, ha="center", va="top", zorder=14
        )

        # Colocated center marker (circle + u arrow + v arrow all from the center)
        ax.plot(xc, yc, marker="o", markersize=7.2,
                markerfacecolor=PALETTE["z_node"], markeredgecolor="white",
                markeredgewidth=1.1, zorder=18)

        # u arrow starting at center
        draw_2d_arrow(
            ax, (xc, yc), (xc + 0.52, yc),
            color=PALETTE["u_node"], lw=1.6, mutation_scale=10, zorder=17
        )
        # v arrow starting at center
        draw_2d_arrow(
            ax, (xc, yc), (xc, yc + 0.48),
            color=PALETTE["v_node"], lw=1.6, mutation_scale=10, zorder=17
        )

        # Label (u, v, z) below center
        crisp_text(
            ax, xc, yc - 0.24,
            col_var_labels[k],
            color=PALETTE["ink_primary"], stroke_w=0.16, bg_pill=bg_c,
            fontsize=8.8, fontweight="bold", ha="center", va="top", zorder=19
        )

        # Highlight empty faces
        if k < 2:
            xf = xl + g_dx_L
            crisp_text(
                ax, xf, yc + 0.28,
                "face sem\nvariável",
                color=PALETTE["ink_muted"], stroke_w=0.11, bg_pill=PALETTE["bg_canvas"],
                fontsize=7.5, fontstyle="italic", ha="center", va="center", zorder=16
            )

    # Arch on 2D grid showing gradient skipping cell (i, j)
    xc_0 = g_x0_L + 0.5 * g_dx_L
    xc_1 = g_x0_L + 1.5 * g_dx_L
    xc_2 = g_x0_L + 2.5 * g_dx_L

    draw_2d_arrow(
        ax, (xc_0, g_y0_L - 0.08), (xc_2, g_y0_L - 0.08),
        color=PALETTE["spurious_red"], lw=1.5, mutation_scale=10.5,
        arrowstyle="<|-|>", connectionstyle="arc3,rad=0.22", zorder=22
    )
    crisp_text(
        ax, xc_1, g_y0_L - 0.62,
        r"Para calcular $\dfrac{\partial z}{\partial x}$ no centro $i$, usa $z_{i+1}$ e $z_{i-1}$: desacopla células vizinhas",
        color=PALETTE["spurious_red"], stroke_w=0.16,
        fontsize=8.8, fontweight="bold", ha="center", va="top", zorder=25
    )

    # =======================================================================
    # RIGHT PANEL: CASULLI'S STAGGERED GRID (ARAKAWA C-GRID)
    # =======================================================================
    xc_R = 4.65

    # Panel 2 Title & Mathematical Subtitle
    crisp_text(
        ax, xc_R, 4.42,
        r"2. Malha Espacial Escalonada de Casulli: Eliminação do Ponto Cego",
        color=PALETTE["valid_teal"], stroke_w=0.20,
        fontsize=11.0, fontweight="bold", ha="center", va="bottom", zorder=28
    )
    crisp_text(
        ax, xc_R, 4.18,
        r"$z_{i,j}$ no centro e $u_{i+1/2,j}$ na face vertical $\;\Longrightarrow\;$ usa células adjacentes: $\;\left(\dfrac{\partial z}{\partial x}\right)_{i+1/2, j} \approx \dfrac{z_{i+1, j} - z_{i, j}}{\Delta x}$",
        color=PALETTE["ink_primary"], stroke_w=0.15,
        fontsize=9.3, ha="center", va="top", zorder=28
    )

    # -----------------------------------------------------------------------
    # Right Top: 1D Sawtooth Wave Detection on Staggered Grid
    # -----------------------------------------------------------------------
    x0_R = 1.05
    dx_R = 1.80
    y_base_R = 0.55
    y_mean_R = 1.60

    # Same alternating wave so the reader sees why staggered catches it immediately!
    ax.add_patch(Rectangle(
        (x0_R - 0.15, y_base_R - 0.16), 4 * dx_R + 0.30, 0.16,
        facecolor=PALETTE["bed_fill"], edgecolor="none", zorder=4
    ))
    ax.plot(
        [x0_R - 0.15, x0_R + 4 * dx_R + 0.15], [y_base_R, y_base_R],
        color=PALETTE["bed_edge"], lw=1.25, zorder=8
    )
    ax.plot(
        [x0_R - 0.25, x0_R + 4 * dx_R + 0.25], [y_mean_R, y_mean_R],
        color=PALETTE["ink_muted"], lw=0.75, ls=":", zorder=6
    )

    centers_x_R = []
    centers_y_R = []

    for k in range(4):
        xl = x0_R + k * dx_R
        xr = xl + dx_R
        xc = 0.5 * (xl + xr)
        zk = y_mean_R + z_offsets_L[k]
        centers_x_R.append(xc)
        centers_y_R.append(zk)

        fill_col = PALETTE["water_high"] if z_offsets_L[k] > 0 else PALETTE["water_low"]

        ax.add_patch(Rectangle(
            (xl, y_base_R), dx_R, zk - y_base_R,
            facecolor=fill_col, edgecolor="none", alpha=0.82, zorder=5
        ))
        ax.plot([xl, xr], [zk, zk], color=PALETTE["water_edge"], lw=2.0, zorder=10)

        # Vertical cell face lines (active velocity faces!)
        ax.plot([xl, xl], [y_base_R, y_mean_R + dz_amp + 0.28],
                color=PALETTE["cell_border"], lw=1.15, ls="-", zorder=9)

        # Cell center z_{i,j} marker
        ax.plot(xc, zk, marker="o", markersize=6.8,
                markerfacecolor=PALETTE["z_node"], markeredgecolor="white",
                markeredgewidth=1.1, zorder=16)

        crisp_text(
            ax, xc, y_base_R + 0.08,
            f"Célula {cell_labels_L[k]} ({state_labels_L[k]})",
            color=PALETTE["ink_secondary"], stroke_w=0.13,
            fontsize=8.1, ha="center", va="bottom", zorder=14
        )

    ax.plot([x0_R + 4 * dx_R, x0_R + 4 * dx_R], [y_base_R, y_mean_R + dz_amp + 0.28],
            color=PALETTE["cell_border"], lw=1.15, ls="-", zorder=9)

    # Staggered velocity nodes u at the vertical faces between centers!
    for kf in range(3):
        xf = x0_R + (kf + 1) * dx_R
        yf = y_mean_R
        # Draw horizontal velocity vector u on the vertical face
        dir_sign = 1 if kf == 0 or kf == 2 else -1
        draw_2d_arrow(
            ax, (xf - 0.24 * dir_sign, yf), (xf + 0.28 * dir_sign, yf),
            color=PALETTE["u_node"], lw=2.1, mutation_scale=11.5, zorder=21
        )
        ax.plot(xf, yf, marker="s", markersize=5.2,
                markerfacecolor=PALETTE["u_node"], markeredgecolor="white",
                markeredgewidth=0.9, zorder=22)

    # Highlight the adjacent gradient across face i + 1/2 (between cell i and cell i+1)
    xf_mid = x0_R + 2 * dx_R
    ax.plot(
        [centers_x_R[1], centers_x_R[2]],
        [centers_y_R[1], centers_y_R[2]],
        color=PALETTE["u_node"], lw=2.2, ls="-", zorder=18
    )

    # Node labels z_{i-1,j}, z_{i,j}, z_{i+1,j}, z_{i+2,j} placed above water surface with zero collision
    crisp_text(
        ax, centers_x_R[0], centers_y_R[0] + 0.12,
        r"$z_{i-1, j}$",
        color=PALETTE["z_node"], stroke_w=0.16, bg_pill=PALETTE["bg_canvas"], pad=0.10,
        fontsize=8.8, fontweight="bold", ha="center", va="bottom", zorder=20
    )
    crisp_text(
        ax, centers_x_R[1] - 0.15, centers_y_R[1] + 0.12,
        r"$z_{i, j} = -z_0$",
        color=PALETTE["z_node"], stroke_w=0.17, bg_pill=PALETTE["bg_canvas"], pad=0.10,
        fontsize=8.6, fontweight="bold", ha="center", va="bottom", zorder=20
    )
    crisp_text(
        ax, centers_x_R[2] + 0.10, centers_y_R[2] + 0.12,
        r"$z_{i+1, j} = +z_0$",
        color=PALETTE["z_node"], stroke_w=0.17, bg_pill=PALETTE["bg_canvas"], pad=0.10,
        fontsize=8.8, fontweight="bold", ha="center", va="bottom", zorder=20
    )
    crisp_text(
        ax, centers_x_R[3], centers_y_R[3] + 0.12,
        r"$z_{i+2, j}$",
        color=PALETTE["z_node"], stroke_w=0.16, bg_pill=PALETTE["bg_canvas"], pad=0.10,
        fontsize=8.8, ha="center", va="bottom", zorder=20
    )

    # Label for u_{i+1/2, j} right at the vertical face between i and i+1
    crisp_text(
        ax, xf_mid + 0.12, y_mean_R - 0.18,
        r"$u_{i+1/2, j}$" + "\n(na face vertical)",
        color=PALETTE["u_node"], stroke_w=0.16, bg_pill=PALETTE["bg_canvas"], pad=0.10,
        fontsize=8.2, fontweight="bold", ha="left", va="top", linespacing=1.12, zorder=24
    )

    # Compact arch connecting adjacent cells i and i+1 (clear of the z_{i+1,j} label)
    draw_2d_arrow(
        ax, (centers_x_R[1], centers_y_R[1] + 0.45),
        (centers_x_R[2] - 0.25, centers_y_R[2] + 0.34),
        color=PALETTE["valid_teal"], lw=1.7, mutation_scale=11,
        arrowstyle="<|-|>", connectionstyle="arc3,rad=-0.22", zorder=22
    )

    crisp_text(
        ax, xf_mid, 3.16,
        r"Células adjacentes ($i$ e $i+1$): $\;\dfrac{z_{i+1, j} - z_{i, j}}{\Delta x} = \dfrac{2z_0}{\Delta x} \neq 0$",
        color=PALETTE["valid_teal"], stroke_w=0.18, bg_pill="#E8F1F6",
        fontsize=9.1, fontweight="bold", ha="center", va="bottom", zorder=25
    )
    crisp_text(
        ax, xf_mid, 2.86,
        r"(Inclinação real detectada na face $i+1/2$: aciona força restauradora e elimina ponto cego)",
        color=PALETTE["ink_secondary"], stroke_w=0.13,
        fontsize=8.3, fontstyle="italic", ha="center", va="bottom", zorder=25
    )

    # 1*dx bracket at bottom of 1D staggered wave
    draw_2d_arrow(
        ax, (centers_x_R[1], y_brk_L), (centers_x_R[2], y_brk_L),
        color=PALETTE["valid_teal"], lw=1.1, mutation_scale=9, arrowstyle="<|-|>", zorder=15
    )
    crisp_text(
        ax, xf_mid, y_brk_L - 0.08,
        r"Estêncil compacto de $1\Delta x$ centrado na face $x_{i+1/2}$",
        color=PALETTE["valid_teal"], stroke_w=0.14, bg_pill=PALETTE["bg_canvas"],
        fontsize=8.3, fontweight="bold", ha="center", va="top", zorder=18
    )

    # -----------------------------------------------------------------------
    # Right Bottom: Detailed 2D Staggered Grid (Casulli Arakawa C-Grid)
    # -----------------------------------------------------------------------
    crisp_text(
        ax, xc_R, -0.35,
        r"Vista em Planta 2D — Malha Espacial Escalonada de Casulli (Célula $(i, j)$ e Faces Adjacentes)",
        color=PALETTE["ink_primary"], stroke_w=0.18,
        fontsize=9.8, fontweight="bold", ha="center", va="bottom", zorder=25
    )

    # Draw a central main cell (i, j) flanked by adjacent cells (i-1, j), (i+1, j), (i, j+1), (i, j-1)
    cx_main = 3.25
    cy_main = -2.55
    W_cell = 2.45
    H_cell = 2.05

    xL_m = cx_main - 0.5 * W_cell
    xR_m = cx_main + 0.5 * W_cell
    yB_m = cy_main - 0.5 * H_cell
    yT_m = cy_main + 0.5 * H_cell

    # Neighboring ghost/context cells (left: i-1,j; right: i+1,j; top: i,j+1; bottom: i,j-1)
    W_nb = 1.60
    H_nb = 0.72

    # Left neighbor (i-1, j)
    ax.add_patch(Rectangle(
        (xL_m - W_nb, yB_m), W_nb, H_cell,
        facecolor=PALETTE["cell_bg"], edgecolor=PALETTE["cell_border"],
        linewidth=0.95, linestyle="--", alpha=0.85, zorder=4
    ))
    # Right neighbor (i+1, j)
    ax.add_patch(Rectangle(
        (xR_m, yB_m), W_nb, H_cell,
        facecolor=PALETTE["cell_bg"], edgecolor=PALETTE["cell_border"],
        linewidth=0.95, linestyle="--", alpha=0.85, zorder=4
    ))
    # Top neighbor (i, j+1)
    ax.add_patch(Rectangle(
        (xL_m, yT_m), W_cell, H_nb,
        facecolor=PALETTE["cell_bg"], edgecolor=PALETTE["cell_border"],
        linewidth=0.95, linestyle="--", alpha=0.85, zorder=4
    ))
    # Bottom neighbor (i, j-1)
    ax.add_patch(Rectangle(
        (xL_m, yB_m - H_nb), W_cell, H_nb,
        facecolor=PALETTE["cell_bg"], edgecolor=PALETTE["cell_border"],
        linewidth=0.95, linestyle="--", alpha=0.85, zorder=4
    ))

    # Central cell (i, j)
    ax.add_patch(Rectangle(
        (xL_m, yB_m), W_cell, H_cell,
        facecolor=PALETTE["cell_focus"], edgecolor=PALETTE["water_edge"],
        linewidth=1.85, zorder=6
    ))

    # Subtle internal crosshair linking centers
    ax.plot([xL_m - 0.65 * W_nb, xR_m + 0.65 * W_nb], [cy_main, cy_main],
            color=PALETTE["ink_muted"], lw=0.75, ls=":", zorder=7)
    ax.plot([cx_main, cx_main], [yB_m - 0.65 * H_nb, yT_m + 0.65 * H_nb],
            color=PALETTE["ink_muted"], lw=0.75, ls=":", zorder=7)

    # 1. Elevation node z_{i, j} at center of cell (i, j)
    ax.plot(cx_main, cy_main, marker="o", markersize=8.5,
            markerfacecolor=PALETTE["z_node"], markeredgecolor="white",
            markeredgewidth=1.3, zorder=20)
    crisp_text(
        ax, cx_main, cy_main + 0.16,
        r"$z_{i, j}$",
        color=PALETTE["z_node"], stroke_w=0.20, bg_pill=PALETTE["cell_focus"],
        fontsize=10.8, fontweight="bold", ha="center", va="bottom", zorder=22
    )
    crisp_text(
        ax, cx_main, cy_main - 0.16,
        "(centro da célula)",
        color=PALETTE["ink_secondary"], stroke_w=0.13, bg_pill=PALETTE["cell_focus"],
        fontsize=8.2, fontstyle="italic", ha="center", va="top", zorder=22
    )

    # Neighboring z centers: z_{i-1, j}, z_{i+1, j}, z_{i, j+1}, z_{i, j-1}
    xc_left_nb = xL_m - 0.55 * W_nb
    xc_right_nb = xR_m + 0.55 * W_nb
    yc_top_nb = yT_m + 0.52 * H_nb
    yc_bot_nb = yB_m - 0.52 * H_nb

    for (nx, ny) in [
        (xc_left_nb, cy_main),
        (xc_right_nb, cy_main),
        (cx_main, yc_top_nb),
        (cx_main, yc_bot_nb),
    ]:
        ax.plot(nx, ny, marker="o", markersize=6.5,
                markerfacecolor=PALETTE["z_node"], markeredgecolor="white",
                markeredgewidth=1.0, alpha=0.90, zorder=18)

    crisp_text(
        ax, xc_left_nb, cy_main + 0.14, r"$z_{i-1, j}$",
        color=PALETTE["z_node"], stroke_w=0.16, bg_pill=PALETTE["cell_bg"],
        fontsize=9.2, fontweight="bold", ha="center", va="bottom", zorder=20
    )
    crisp_text(
        ax, xc_right_nb, cy_main + 0.14, r"$z_{i+1, j}$",
        color=PALETTE["z_node"], stroke_w=0.16, bg_pill=PALETTE["cell_bg"],
        fontsize=9.2, fontweight="bold", ha="center", va="bottom", zorder=20
    )
    crisp_text(
        ax, cx_main + 0.16, yc_top_nb, r"$z_{i, j+1}$",
        color=PALETTE["z_node"], stroke_w=0.16, bg_pill=PALETTE["cell_bg"],
        fontsize=8.8, fontweight="bold", ha="left", va="center", zorder=20
    )
    crisp_text(
        ax, cx_main + 0.16, yc_bot_nb, r"$z_{i, j-1}$",
        color=PALETTE["z_node"], stroke_w=0.16, bg_pill=PALETTE["cell_bg"],
        fontsize=8.8, fontweight="bold", ha="left", va="center", zorder=20
    )

    # 2. Horizontal velocity nodes u_{i-1/2, j} and u_{i+1/2, j} on left & right VERTICAL faces
    for (xf_u, u_lbl) in [
        (xL_m, r"$u_{i-1/2, j}$"),
        (xR_m, r"$u_{i+1/2, j}$"),
    ]:
        draw_2d_arrow(
            ax, (xf_u - 0.34, cy_main), (xf_u + 0.38, cy_main),
            color=PALETTE["u_node"], lw=2.3, mutation_scale=12.5, zorder=23
        )
        ax.plot(xf_u, cy_main, marker="s", markersize=6.0,
                markerfacecolor=PALETTE["u_node"], markeredgecolor="white",
                markeredgewidth=1.0, zorder=24)
        crisp_text(
            ax, xf_u, cy_main + 0.24, u_lbl,
            color=PALETTE["u_node"], stroke_w=0.18, bg_pill=PALETTE["bg_canvas"], pad=0.12,
            fontsize=9.6, fontweight="bold", ha="center", va="bottom", zorder=25
        )
        crisp_text(
            ax, xf_u, cy_main - 0.24, "face vertical",
            color=PALETTE["u_node"], stroke_w=0.12, bg_pill=PALETTE["bg_canvas"], pad=0.08,
            fontsize=7.6, fontstyle="italic", ha="center", va="top", zorder=25
        )

    # 3. Vertical velocity nodes v_{i, j-1/2} and v_{i, j+1/2} on bottom & top HORIZONTAL faces
    for (yf_v, v_lbl) in [
        (yT_m, r"$v_{i, j+1/2}$"),
        (yB_m, r"$v_{i, j-1/2}$"),
    ]:
        draw_2d_arrow(
            ax, (cx_main, yf_v - 0.28), (cx_main, yf_v + 0.32),
            color=PALETTE["v_node"], lw=2.3, mutation_scale=12.5, zorder=23
        )
        ax.plot(cx_main, yf_v, marker="D", markersize=5.8,
                markerfacecolor=PALETTE["v_node"], markeredgecolor="white",
                markeredgewidth=1.0, zorder=24)
        crisp_text(
            ax, cx_main - 0.20, yf_v, v_lbl,
            color=PALETTE["v_node"], stroke_w=0.18, bg_pill=PALETTE["bg_canvas"], pad=0.12,
            fontsize=9.5, fontweight="bold", ha="right", va="center", zorder=25
        )
        crisp_text(
            ax, cx_main + 0.20, yf_v, "face horizontal",
            color=PALETTE["v_node"], stroke_w=0.12, bg_pill=PALETTE["bg_canvas"], pad=0.08,
            fontsize=7.6, fontstyle="italic", ha="left", va="center", zorder=25
        )

    # Dimension arrows dx and dy
    y_dim_dx = yB_m - H_nb - 0.24
    draw_2d_arrow(
        ax, (xL_m, y_dim_dx), (xR_m, y_dim_dx),
        color=PALETTE["ink_muted"], lw=1.0, mutation_scale=9, arrowstyle="<|-|>", zorder=15
    )
    crisp_text(
        ax, cx_main, y_dim_dx - 0.08, r"$\Delta x$",
        color=PALETTE["ink_primary"], stroke_w=0.16, bg_pill=PALETTE["bg_canvas"],
        fontsize=9.2, ha="center", va="top", zorder=18
    )

    x_dim_dy = xL_m - W_nb - 0.22
    draw_2d_arrow(
        ax, (x_dim_dy, yB_m), (x_dim_dy, yT_m),
        color=PALETTE["ink_muted"], lw=1.0, mutation_scale=9, arrowstyle="<|-|>", zorder=15
    )
    crisp_text(
        ax, x_dim_dy - 0.10, cy_main, r"$\Delta y$",
        color=PALETTE["ink_primary"], stroke_w=0.16, bg_pill=PALETTE["bg_canvas"],
        fontsize=9.2, ha="right", va="center", zorder=18
    )

    # -----------------------------------------------------------------------
    # Right-Side Legend & Synthesis Annotations Next to 2D Staggered Grid
    # -----------------------------------------------------------------------
    x_notes_R = 6.38

    # Note 1: Elevação no centro
    ax.plot(x_notes_R, -1.05, marker="o", markersize=7.5,
            markerfacecolor=PALETTE["z_node"], markeredgecolor="white", markeredgewidth=1.1, zorder=25)
    crisp_text(
        ax, x_notes_R + 0.22, -1.05,
        r"Elevação $z_{i,j}$ no centro da célula:",
        color=PALETTE["z_node"], stroke_w=0.18,
        fontsize=9.2, fontweight="bold", ha="left", va="center", zorder=25
    )
    crisp_text(
        ax, x_notes_R + 0.22, -1.24,
        "Representa o nível médio da coluna\n" + r"d'água no volume de controle $(i, j)$.",
        color=PALETTE["ink_secondary"], stroke_w=0.13,
        fontsize=8.3, ha="left", va="top", linespacing=1.24, zorder=25
    )

    # Note 2: Velocidade na direção x (u) nas faces verticais
    ax.plot(x_notes_R, -2.05, marker="s", markersize=6.2,
            markerfacecolor=PALETTE["u_node"], markeredgecolor="white", markeredgewidth=1.0, zorder=25)
    crisp_text(
        ax, x_notes_R + 0.22, -2.05,
        r"Velocidade na direção $x$ ($u_{i+1/2, j}$):",
        color=PALETTE["u_node"], stroke_w=0.18,
        fontsize=9.2, fontweight="bold", ha="left", va="center", zorder=25
    )
    crisp_text(
        ax, x_notes_R + 0.22, -2.24,
        r"Avaliada nas faces verticais (leste/oeste)," + "\n"
        + r"exatamente entre $z_{i,j}$ e $z_{i+1,j}$:",
        color=PALETTE["ink_secondary"], stroke_w=0.13,
        fontsize=8.3, ha="left", va="top", linespacing=1.22, zorder=25
    )
    crisp_text(
        ax, x_notes_R + 0.22, -2.75,
        r"$\left(\dfrac{\partial z}{\partial x}\right)_{i+1/2, j} \approx \dfrac{z_{i+1,j} - z_{i,j}}{\Delta x}$",
        color=PALETTE["ink_primary"], stroke_w=0.16,
        fontsize=8.8, ha="left", va="top", zorder=25
    )

    # Note 3: Velocidade na direção y (v) nas faces horizontais
    ax.plot(x_notes_R, -3.55, marker="D", markersize=6.0,
            markerfacecolor=PALETTE["v_node"], markeredgecolor="white", markeredgewidth=1.0, zorder=25)
    crisp_text(
        ax, x_notes_R + 0.22, -3.55,
        r"Velocidade na direção $y$ ($v_{i, j+1/2}$):",
        color=PALETTE["v_node"], stroke_w=0.18,
        fontsize=9.2, fontweight="bold", ha="left", va="center", zorder=25
    )
    crisp_text(
        ax, x_notes_R + 0.22, -3.74,
        r"Avaliada nas faces horizontais (norte/sul)," + "\n"
        + r"exatamente entre $z_{i,j}$ e $z_{i,j+1}$:",
        color=PALETTE["ink_secondary"], stroke_w=0.13,
        fontsize=8.3, ha="left", va="top", linespacing=1.22, zorder=25
    )
    crisp_text(
        ax, x_notes_R + 0.22, -4.25,
        r"$\left(\dfrac{\partial z}{\partial y}\right)_{i, j+1/2} \approx \dfrac{z_{i,j+1} - z_{i,j}}{\Delta y}$",
        color=PALETTE["ink_primary"], stroke_w=0.16,
        fontsize=8.8, ha="left", va="top", zorder=25
    )

    # Set clean bounds and remove default Matplotlib frame/ticks
    ax.set_xlim(-8.95, 9.65)
    ax.set_ylim(-4.85, 4.75)
    ax.set_aspect("equal")
    ax.axis("off")

    plt.tight_layout(pad=0.12)

    out_dir = Path(__file__).resolve().parent.parent / "figures"
    out_dir.mkdir(parents=True, exist_ok=True)

    svg_path = out_dir / "swe_staggered_grid.svg"
    pdf_path = out_dir / "swe_staggered_grid.pdf"
    png_path = out_dir / "swe_staggered_grid.png"

    fig.savefig(svg_path, format="svg", bbox_inches="tight", facecolor=fig.get_facecolor())
    fig.savefig(pdf_path, format="pdf", bbox_inches="tight", facecolor=fig.get_facecolor())
    fig.savefig(png_path, format="png", dpi=300, bbox_inches="tight", facecolor=fig.get_facecolor())
    print(f"Saved: {svg_path}")
    print(f"Saved: {pdf_path}")
    print(f"Saved: {png_path}")


if __name__ == "__main__":
    build_figure()
