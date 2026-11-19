"""
Generate an Edward Tufte-inspired vector scientific illustration explaining the
physical and mathematical meaning of the x-momentum equation in the 2D Shallow
Water Equations (2D SWE), following Casulli (1990):

    du/dt + u du/dx + v du/dy = -g dz/dx - gamma u + tau_x

Pure, spacious longitudinal illustration with razor-sharp LaTeX Latin Modern
Roman & Computer Modern Math typography (no blurry stroke halos; self-colored
micro-stroke reinforcement for sub-pixel screen clarity).

Outputs:
  - ../figures/swe_momentum_x_meaning.svg (vector SVG with embedded glyph paths)
  - ../figures/swe_momentum_x_meaning.pdf (vector PDF for LaTeX publication)
  - ../figures/swe_momentum_x_meaning.png (high-resolution raster preview)
"""

import glob
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.patches import Polygon, FancyArrowPatch
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
    "ink_muted": "#687380",       # Clean slate gray for leader lines
    "rule_light": "#D6CFC4",      # Subtle section divider
    "water_fill": "#C4DFEE",      # Translucent water body fill
    "water_col": "#E8F3F9",       # Highlighted central control column
    "water_edge": "#1E4966",      # Crisp structural free-surface curve
    "datum_line": "#283648",      # Undisturbed reference plane z = 0
    "velocity_u": "#0C2F47",      # Deep Prussian navy for velocity u & LHS terms
    "pressure_g": "#154E75",      # Rich cerulean blue for -g dz/dx & hydrostatic pressure
    "wind_tau": "#17575A",        # Deep sea-teal for wind forcing tau_x
    "friction_gamma": "#8E321E",  # Deep Venetian terracotta for bottom friction -gamma u
    "bed_fill": "#C8BBAE",        # Geological seabed cross-section
    "bed_edge": "#5E4F41",        # Seabed interface curve
    "bed_hatch": "#827161",       # Fine geological sediment hatching
}


def crisp_text(ax, x, y, s, color="#11161C", stroke_w=0.16, bg_pill=None, **kwargs):
    """
    Render razor-sharp LaTeX text by reinforcing ultra-thin Computer Modern
    hairlines with a micro self-colored stroke (no blurry halo!).
    """
    if bg_pill is not None:
        kwargs["bbox"] = dict(
            boxstyle="round,pad=0.16",
            facecolor=bg_pill,
            edgecolor="none",
            alpha=0.84,
        )
    t = ax.text(x, y, s, color=color, **kwargs)
    if stroke_w > 0:
        t.set_path_effects([pe.withStroke(linewidth=stroke_w, foreground=color)])
    return t


def draw_arrow(
    ax, p0, p1, color, lw=1.35, mutation_scale=11.5, arrowstyle="-|>",
    zorder=20, ls="-", alpha=1.0, connectionstyle="arc3,rad=0.0"
):
    """Draw a precision 2D vector arrow."""
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


def add_tufte_callout(
    ax, target_pt, anchor_pt, text_pt, title, lines,
    title_color=None, align="left", rad=0.14, zorder=28
):
    """Draw a razor-sharp Tufte callout with leader line starting outside the text block."""
    if title_color is None:
        title_color = PALETTE["ink_primary"]
    tx, ty = target_pt
    ax.plot(tx, ty, marker="o", markersize=3.6, color=title_color, zorder=zorder)
    conn = FancyArrowPatch(
        anchor_pt, target_pt,
        connectionstyle=f"arc3,rad={rad}",
        arrowstyle="-",
        color=PALETTE["ink_muted"],
        linewidth=0.75,
        zorder=zorder - 2,
    )
    ax.add_patch(conn)

    bx, by = text_pt
    crisp_text(
        ax, bx, by, title,
        color=title_color, stroke_w=0.20,
        fontsize=10.6, fontweight="bold",
        ha=align, va="bottom", zorder=zorder + 1
    )

    crisp_text(
        ax, bx, by - 0.10, "\n".join(lines),
        color=PALETTE["ink_secondary"], stroke_w=0.14,
        fontsize=9.4, ha=align, va="top",
        linespacing=1.35, zorder=zorder + 1
    )


def build_figure():
    # Compact, high-density figure size matched to notebook width so text isn't shrunk
    fig, ax = plt.subplots(figsize=(13.2, 6.4), dpi=300)
    fig.patch.set_facecolor(PALETTE["bg_canvas"])
    ax.set_facecolor(PALETTE["bg_canvas"])

    # Coordinate setup for the longitudinal water channel (x from 1.1 to 13.4)
    x_ch0, x_ch1 = 1.10, 13.40
    xs = np.linspace(x_ch0, x_ch1, 240)

    y_datum = 4.35  # Undisturbed reference level z = 0

    # Free surface z(x,y,t): higher on the left, sloping smoothly downward to the right (dz/dx < 0)
    def z_surf_fn(x_val):
        s = (x_val - x_ch0) / (x_ch1 - x_ch0)
        return y_datum + 1.02 * np.cos(0.86 * np.pi * s) + 0.14

    # Gently varying seabed z = -h(x,y)
    def z_bed_fn(x_val):
        s = (x_val - x_ch0) / (x_ch1 - x_ch0)
        return 1.35 + 0.24 * np.sin(1.08 * np.pi * s - 0.25)

    ys_surf = z_surf_fn(xs)
    ys_bed = z_bed_fn(xs)
    y_rock_base = 0.55

    # -----------------------------------------------------------------------
    # 1. Water Body & Highlighted Central Control Column [x_L, x_R]
    # -----------------------------------------------------------------------
    ax.add_patch(Polygon(
        list(zip(np.concatenate([xs, xs[::-1]]), np.concatenate([ys_surf, ys_bed[::-1]]))),
        facecolor=PALETTE["water_fill"], edgecolor="none", alpha=0.45, zorder=3
    ))

    # Central Control Volume Column [x_L, x_R]
    x_L, x_R = 4.25, 10.15
    xs_col = np.linspace(x_L, x_R, 100)
    ax.add_patch(Polygon(
        list(zip(
            np.concatenate([xs_col, xs_col[::-1]]),
            np.concatenate([z_surf_fn(xs_col), z_bed_fn(xs_col[::-1])])
        )),
        facecolor=PALETTE["water_col"], edgecolor="none", alpha=0.80, zorder=4
    ))

    y_surf_L, y_bed_L = z_surf_fn(x_L), z_bed_fn(x_L)
    y_surf_R, y_bed_R = z_surf_fn(x_R), z_bed_fn(x_R)
    ax.plot([x_L, x_L], [y_bed_L, y_surf_L], color=PALETTE["pressure_g"], lw=1.35, ls="-", zorder=8)
    ax.plot([x_R, x_R], [y_bed_R, y_surf_R], color=PALETTE["pressure_g"], lw=1.35, ls="-", zorder=8)

    # -----------------------------------------------------------------------
    # 2. Geological Seabed Substratum & Tufte Hatching
    # -----------------------------------------------------------------------
    ax.add_patch(Polygon(
        list(zip(
            np.concatenate([xs, [x_ch1, x_ch0]]),
            np.concatenate([ys_bed, [y_rock_base, y_rock_base]])
        )),
        facecolor=PALETTE["bed_fill"], edgecolor="none", alpha=0.92, zorder=5
    ))
    ax.plot(xs, ys_bed, color=PALETTE["bed_edge"], lw=1.55, zorder=9)
    ax.plot([x_ch0, x_ch1], [y_rock_base, y_rock_base], color=PALETTE["rule_light"], lw=0.85, zorder=6)

    for xh in np.linspace(x_ch0 + 0.22, x_ch1 - 0.22, 52):
        for k_s in range(3):
            xs_h = xh + (k_s - 1) * 0.06
            yt_h = z_bed_fn(xs_h)
            yb_h = max(y_rock_base + 0.08, yt_h - 0.36 + 0.05 * k_s)
            ax.plot(
                [xs_h, xs_h - 0.18], [yt_h, yb_h],
                color=PALETTE["bed_hatch"], lw=0.48, alpha=0.65, zorder=6
            )

    crisp_text(
        ax, 7.20, y_rock_base + 0.24,
        r"Fundo do mar / leito impermeável   $z = -h(x,y)$   (coeficiente de rugosidade de Chézy $C_z$)",
        color="#332920", stroke_w=0.14,
        fontsize=9.6, fontstyle="italic", ha="center", va="center", zorder=15
    )

    # -----------------------------------------------------------------------
    # 3. Free-Surface Curve z(x,y,t) & Undisturbed Reference Level z = 0
    # -----------------------------------------------------------------------
    ax.plot(xs, ys_surf, color=PALETTE["water_edge"], lw=1.85, zorder=10)
    ax.plot([x_ch0, x_ch1], [y_datum, y_datum], color=PALETTE["datum_line"], lw=1.10, ls=(0, (5, 3)), zorder=9)
    crisp_text(
        ax, x_ch1 - 0.10, y_datum + 0.12,
        r"Nível de referência não perturbado ($z = 0$)",
        color=PALETTE["datum_line"], stroke_w=0.14,
        fontsize=9.4, fontstyle="italic",
        ha="right", va="bottom", zorder=15
    )

    # Elevation dimensions on the left (z(x,y,t) > 0) and right (z(x,y,t) < 0) + depth h(x,y)
    x_dim_L = 1.50
    draw_arrow(
        ax, (x_dim_L, y_datum), (x_dim_L, z_surf_fn(x_dim_L)),
        color=PALETTE["water_edge"], lw=1.10, mutation_scale=8.5, arrowstyle="<|-|>"
    )
    crisp_text(
        ax, x_dim_L + 0.14, 0.5 * (y_datum + z_surf_fn(x_dim_L)),
        r"$z(x,y,t) > 0$" + "\n" + r"(superfície mais alta à esq.)",
        color=PALETTE["water_edge"], stroke_w=0.15,
        fontsize=9.3, ha="left", va="center", zorder=18
    )

    draw_arrow(
        ax, (x_dim_L, z_bed_fn(x_dim_L)), (x_dim_L, y_datum),
        color=PALETTE["water_edge"], lw=1.10, mutation_scale=8.5, arrowstyle="<|-|>"
    )
    crisp_text(
        ax, x_dim_L + 0.14, 0.52 * y_datum + 0.48 * z_bed_fn(x_dim_L) - 0.18,
        r"$h(x,y)$",
        color=PALETTE["water_edge"], stroke_w=0.18,
        fontsize=10.2, ha="left", va="center", zorder=18
    )

    # Right side depression z < 0 dimension
    x_dim_R = 12.78
    draw_arrow(
        ax, (x_dim_R, z_surf_fn(x_dim_R)), (x_dim_R, y_datum),
        color=PALETTE["water_edge"], lw=1.05, mutation_scale=8, arrowstyle="<|-|>"
    )
    crisp_text(
        ax, x_dim_R - 0.14, 0.5 * (y_datum + z_surf_fn(x_dim_R)),
        r"$z(x,y,t) < 0$" + "\n" + r"(mais baixa à dir.)",
        color=PALETTE["water_edge"], stroke_w=0.15,
        fontsize=9.2, ha="right", va="center", zorder=18
    )

    # -----------------------------------------------------------------------
    # 4. Free-Surface Slope Triangle (dz/dx < 0) & Gravity g
    # -----------------------------------------------------------------------
    x_tan_c = 7.35
    y_tan_c = z_surf_fn(x_tan_c)
    dz_dx_num = (z_surf_fn(x_tan_c + 0.01) - z_surf_fn(x_tan_c - 0.01)) / 0.02

    ax.plot(
        [x_tan_c - 1.05, x_tan_c + 1.45],
        [y_tan_c - 1.05 * dz_dx_num, y_tan_c + 1.45 * dz_dx_num],
        color=PALETTE["pressure_g"], lw=1.25, ls="--", zorder=14
    )
    x_tri0 = x_tan_c - 0.25
    y_tri0 = z_surf_fn(x_tri0)
    x_tri1 = x_tri0 + 1.45
    y_tri1 = z_surf_fn(x_tri1)
    ax.plot([x_tri0, x_tri1], [y_tri0, y_tri0], color=PALETTE["pressure_g"], lw=0.95, ls=":", zorder=14)
    ax.plot([x_tri1, x_tri1], [y_tri0, y_tri1], color=PALETTE["pressure_g"], lw=1.15, zorder=14)
    crisp_text(
        ax, 0.5 * (x_tri0 + x_tri1), y_tri0 + 0.08,
        r"$\partial x$", color=PALETTE["pressure_g"], stroke_w=0.16,
        fontsize=9.8, ha="center", va="bottom", zorder=20
    )
    crisp_text(
        ax, x_tri1 + 0.12, 0.5 * (y_tri0 + y_tri1),
        r"$\partial z < 0$", color=PALETTE["pressure_g"], stroke_w=0.16,
        fontsize=9.8, ha="left", va="center", zorder=20
    )

    add_tufte_callout(
        ax,
        target_pt=(x_tan_c + 0.35, z_surf_fn(x_tan_c + 0.35)),
        anchor_pt=(10.15, 5.42),
        text_pt=(10.30, 5.82),
        title=r"Inclinação da superfície livre $\;\partial z/\partial x < 0$",
        lines=[
            r"Superfície mais alta à esquerda ($z_E$) que à direita ($z_D$):",
            r"o termo $-g\,\partial z/\partial x > 0$ impulsiona o fluido para a direita;",
            r"se a inclinação se inverter ($\partial z/\partial x > 0$), o termo freia $u$."
        ],
        title_color=PALETTE["pressure_g"],
        align="left",
        rad=0.15
    )

    # Gravity vector g
    draw_arrow(
        ax, (1.45, 6.48), (1.45, 5.68),
        color=PALETTE["ink_primary"], lw=1.80, mutation_scale=12, zorder=20
    )
    crisp_text(
        ax, 1.62, 6.08, r"$\mathbf{g}$ (gravidade $g$)",
        color=PALETTE["ink_primary"], stroke_w=0.18,
        fontsize=10.2, ha="left", va="center", zorder=20
    )

    # -----------------------------------------------------------------------
    # 5. Left & Right Hydrostatic Pressure Profiles p_E(z') vs p_D(z')
    # -----------------------------------------------------------------------
    w_press_L = 1.50
    ax.add_patch(Polygon(
        [(x_L - w_press_L, y_bed_L), (x_L, y_bed_L), (x_L, y_surf_L)],
        facecolor=PALETTE["pressure_g"], edgecolor=PALETTE["pressure_g"],
        lw=0.90, alpha=0.18, zorder=7
    ))
    ax.plot([x_L - w_press_L, x_L], [y_bed_L, y_surf_L], color=PALETTE["pressure_g"], lw=1.15, zorder=8)
    for frac in [0.18, 0.36, 0.54, 0.72, 0.90]:
        yp = y_surf_L - frac * (y_surf_L - y_bed_L)
        wp = frac * w_press_L
        draw_arrow(
            ax, (x_L - wp, yp), (x_L - 0.03, yp),
            color=PALETTE["pressure_g"], lw=1.05, mutation_scale=9, zorder=9
        )
    crisp_text(
        ax, x_L - 0.78, 3.60,
        r"Pressão hidrostática" + "\n" + r"à esquerda $p_E(z')$" + "\n"
        + r"$\mathbf{maior}$ (coluna $H_E$ maior)",
        color=PALETTE["pressure_g"], stroke_w=0.15,
        fontsize=9.3, ha="right", va="center", zorder=18
    )

    w_press_R = 0.85
    ax.add_patch(Polygon(
        [(x_R + w_press_R, y_bed_R), (x_R, y_bed_R), (x_R, y_surf_R)],
        facecolor=PALETTE["pressure_g"], edgecolor=PALETTE["pressure_g"],
        lw=0.90, alpha=0.18, zorder=7
    ))
    ax.plot([x_R + w_press_R, x_R], [y_bed_R, y_surf_R], color=PALETTE["pressure_g"], lw=1.15, zorder=8)
    for frac in [0.22, 0.46, 0.70, 0.92]:
        yp = y_surf_R - frac * (y_surf_R - y_bed_R)
        wp = frac * w_press_R
        draw_arrow(
            ax, (x_R + wp, yp), (x_R + 0.03, yp),
            color=PALETTE["pressure_g"], lw=0.95, mutation_scale=8, zorder=9
        )
    crisp_text(
        ax, x_R + w_press_R + 0.14, 0.46 * y_bed_R + 0.54 * y_surf_R,
        r"Pressão hidrostática" + "\n" + r"à direita $p_D(z')$" + "\n"
        + r"$\mathbf{menor}$ (coluna $H_D$ menor)",
        color=PALETTE["pressure_g"], stroke_w=0.15,
        fontsize=9.3, ha="left", va="center", zorder=18
    )

    # -----------------------------------------------------------------------
    # 6. Inside the Control Column [x_L, x_R]: Dynamical Balance & LHS/RHS Terms
    # -----------------------------------------------------------------------
    x_mid = 0.5 * (x_L + x_R)  # 7.20

    # (A) Net Hydrostatic Pressure Gradient Acceleration: -g dz/dx > 0
    y_fg = 3.68
    draw_arrow(
        ax, (x_mid - 1.65, y_fg), (x_mid + 1.65, y_fg),
        color=PALETTE["pressure_g"], lw=2.7, mutation_scale=16, zorder=18
    )
    crisp_text(
        ax, x_mid, y_fg + 0.16,
        r"Força de gradiente hidrostático: $\;-g\dfrac{\partial z}{\partial x} > 0$",
        color=PALETTE["pressure_g"], stroke_w=0.20,
        fontsize=11.0, fontweight="bold", ha="center", va="bottom", zorder=22
    )
    crisp_text(
        ax, x_mid, y_fg - 0.13,
        r"Desequilíbrio hidrostático ($p_E > p_D$) desloca a água da maior para a menor altura, acelerando $u$",
        color=PALETTE["pressure_g"], stroke_w=0.14,
        fontsize=8.6, fontstyle="italic", ha="center", va="top", zorder=22
    )

    # (B) Velocity u(x,y,t) & Left-Hand Side Material Rate of Change (du/dt + u du/dx + v du/dy)
    y_vel = 2.65
    draw_arrow(
        ax, (x_mid - 1.45, y_vel), (x_mid + 1.45, y_vel),
        color=PALETTE["velocity_u"], lw=2.4, mutation_scale=14.5, zorder=18
    )
    crisp_text(
        ax, x_mid, y_vel + 0.14,
        r"Velocidade $u(x,y,t)$ e variação total $\;\dfrac{\partial u}{\partial t} + u\dfrac{\partial u}{\partial x} + v\dfrac{\partial u}{\partial y}$",
        color=PALETTE["velocity_u"], stroke_w=0.20,
        fontsize=10.6, fontweight="bold", ha="center", va="bottom", zorder=22
    )
    crisp_text(
        ax, x_mid, y_vel - 0.13,
        r"Mudança no tempo ($\partial u/\partial t$) e variação no campo espacial $x \times y$ ($\partial u/\partial x$ e $\partial u/\partial y$)",
        color=PALETTE["velocity_u"], stroke_w=0.14,
        fontsize=8.8, fontstyle="italic", ha="center", va="top", zorder=22
    )

    # (C) Bottom Friction Dissipation: -gamma u (Near seabed, strictly opposing u!)
    y_fric = z_bed_fn(x_mid) + 0.25
    draw_arrow(
        ax, (x_mid + 1.40, y_fric), (x_mid - 1.40, y_fric),
        color=PALETTE["friction_gamma"], lw=2.35, mutation_scale=14.5, zorder=18
    )
    crisp_text(
        ax, x_mid, y_fric + 0.14,
        r"Dissipação / amortecimento por atrito com o fundo: $\;-\gamma u < 0\quad (\gamma \geq 0)$",
        color=PALETTE["friction_gamma"], stroke_w=0.20,
        fontsize=10.2, fontweight="bold", ha="center", va="bottom", zorder=22
    )

    # (D) Surface Wind Forcing: tau_x (Above the free surface)
    x_w0 = 4.65
    y_w0 = z_surf_fn(x_w0) + 0.36
    x_w1 = 7.05
    y_w1 = z_surf_fn(x_w1) + 0.36
    draw_arrow(
        ax, (x_w0, y_w0), (x_w1, y_w1),
        color=PALETTE["wind_tau"], lw=2.25, mutation_scale=13.5, zorder=18
    )
    draw_arrow(
        ax, (x_w1, y_w1 + 0.22), (x_w0 + 0.65, y_w0 + 0.22),
        color=PALETTE["wind_tau"], lw=1.15, mutation_scale=9, ls="--", alpha=0.72, zorder=17
    )
    crisp_text(
        ax, 0.5 * (x_w0 + x_w1) + 0.10, y_w0 + 0.48,
        r"Forçamento externo pelo vento na superfície $\;\tau_x$",
        color=PALETTE["wind_tau"], stroke_w=0.20,
        fontsize=10.6, fontweight="bold", ha="center", va="bottom", zorder=22
    )
    crisp_text(
        ax, 0.5 * (x_w0 + x_w1) + 0.10, y_w0 + 0.24,
        r"(acelera o escoamento se $\tau_x > 0$ ou desacelera se $\tau_x < 0$, conforme a direção do vento)",
        color=PALETTE["wind_tau"], stroke_w=0.14,
        fontsize=9.0, fontstyle="italic", ha="center", va="bottom", zorder=22
    )

    # -----------------------------------------------------------------------
    # 7. Coordinate Axes (x, z) & Control Column Dimension [x, x + dx]
    # -----------------------------------------------------------------------
    draw_arrow(
        ax, (0.70, y_rock_base), (0.70, 6.45),
        color=PALETTE["ink_primary"], lw=1.30, mutation_scale=10.5, zorder=20
    )
    crisp_text(
        ax, 0.70, 6.54, r"$z$",
        color=PALETTE["ink_primary"], stroke_w=0.20,
        fontsize=12.5, ha="center", va="bottom", zorder=22
    )

    draw_arrow(
        ax, (0.70, y_rock_base), (13.80, y_rock_base),
        color=PALETTE["ink_primary"], lw=1.30, mutation_scale=10.5, zorder=20
    )
    crisp_text(
        ax, 13.92, y_rock_base, r"$x$",
        color=PALETTE["ink_primary"], stroke_w=0.20,
        fontsize=12.5, ha="left", va="center", zorder=22
    )

    # Transverse y-axis perspective indicator at the origin (0.70, y_rock_base) showing field (x * y)
    draw_arrow(
        ax, (0.70, y_rock_base), (1.35, y_rock_base + 0.42),
        color=PALETTE["ink_secondary"], lw=1.10, mutation_scale=9, zorder=20
    )
    crisp_text(
        ax, 1.42, y_rock_base + 0.44, r"$y$ (campo espacial $x \times y$)",
        color=PALETTE["ink_secondary"], stroke_w=0.14,
        fontsize=9.4, ha="left", va="bottom", zorder=22
    )

    # Control column horizontal span bracket [x, x + dx] below x-axis
    ax.plot([x_L, x_L], [y_rock_base, 0.22], color=PALETTE["ink_muted"], lw=0.80, ls=":", zorder=15)
    ax.plot([x_R, x_R], [y_rock_base, 0.22], color=PALETTE["ink_muted"], lw=0.80, ls=":", zorder=15)
    draw_arrow(
        ax, (x_L, 0.26), (x_R, 0.26),
        color=PALETTE["ink_secondary"], lw=1.05, mutation_scale=8.5, arrowstyle="<|-|>"
    )
    crisp_text(ax, x_L, 0.14, r"$x$", color=PALETTE["ink_primary"], stroke_w=0.18, fontsize=10.4, ha="center", va="top")
    crisp_text(ax, x_R, 0.14, r"$x + \Delta x$", color=PALETTE["ink_primary"], stroke_w=0.18, fontsize=10.4, ha="center", va="top")
    crisp_text(
        ax, 0.5 * (x_L + x_R), 0.14,
        r"Elemento diferencial da coluna de água ($\Delta x$)",
        color=PALETTE["ink_secondary"], stroke_w=0.14,
        fontsize=9.4, fontstyle="italic", ha="center", va="top"
    )

    # Set clean bounds and remove default Matplotlib frame/ticks
    ax.set_xlim(0.35, 15.10)
    ax.set_ylim(-0.15, 6.85)
    ax.set_aspect("equal")
    ax.axis("off")

    plt.tight_layout(pad=0.12)

    out_dir = Path(__file__).resolve().parent.parent / "figures"
    out_dir.mkdir(parents=True, exist_ok=True)

    svg_path = out_dir / "swe_momentum_x_meaning.svg"
    pdf_path = out_dir / "swe_momentum_x_meaning.pdf"
    png_path = out_dir / "swe_momentum_x_meaning.png"

    fig.savefig(svg_path, format="svg", bbox_inches="tight", facecolor=fig.get_facecolor())
    fig.savefig(pdf_path, format="pdf", bbox_inches="tight", facecolor=fig.get_facecolor())
    fig.savefig(png_path, format="png", dpi=300, bbox_inches="tight", facecolor=fig.get_facecolor())
    print(f"Saved: {svg_path}")
    print(f"Saved: {pdf_path}")
    print(f"Saved: {png_path}")


if __name__ == "__main__":
    build_figure()
