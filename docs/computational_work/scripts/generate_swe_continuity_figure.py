"""
Generate an Edward Tufte-inspired vector scientific illustration explaining the
physical and mathematical meaning of the Continuity (Mass Conservation) Equation
in the 2D Shallow Water Equations (2D SWE), following Casulli (1990):

    dz/dt + d[(h+z)u]/dx + d[(h+z)v]/dy = 0
    <=> dz/dt = -( d[(h+z)u]/dx + d[(h+z)v]/dy )

Spacious, single-canvas 3D axonometric layout without internal headers or side
boxes, featuring razor-sharp LaTeX Latin Modern Roman & Computer Modern Math
typography (self-colored micro-stroke reinforcement, no blurry stroke halos).

Outputs:
  - ../figures/swe_continuity_meaning.svg (vector SVG with embedded glyph paths)
  - ../figures/swe_continuity_meaning.pdf (vector PDF for LaTeX publication)
  - ../figures/swe_continuity_meaning.png (high-resolution raster preview)
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
    "rule_light": "#D6CFC4",      # Subtle divider rule
    "water_front": "#B3D4E6",     # Front-left water column face
    "water_right": "#97C0D8",     # Front-right water column face
    "water_top": "#D6EAF5",       # Free surface at t + dt
    "water_rise": "#7FB3D5",      # Rising volume cap (dz/dt > 0)
    "water_drop": "#E8D5C8",      # Depleted volume cap (dz/dt < 0)
    "water_edge": "#1E4966",      # Crisp structural water edge
    "datum_line": "#283648",      # Undisturbed reference plane z = 0
    "flux_in": "#0D3B59",         # Deep Prussian blue for incoming/x volumetric flux
    "flux_y": "#17575A",          # Deep sea-teal for transverse y volumetric flux
    "rise_col": "#145374",        # Deep cerulean for dz/dt > 0 (column rises)
    "drop_col": "#8E321E",        # Deep Venetian terracotta for dz/dt < 0 (column drops)
    "bed_top": "#D8CEC0",         # Seabed top surface
    "bed_front": "#C8BBAE",       # Geological cross-section left face
    "bed_right": "#B3A494",       # Geological cross-section right face
    "bed_edge": "#5E4F41",        # Seabed contour & outline
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
            alpha=0.86,
        )
    t = ax.text(x, y, s, color=color, **kwargs)
    if stroke_w > 0:
        t.set_path_effects([pe.withStroke(linewidth=stroke_w, foreground=color)])
    return t


# ---------------------------------------------------------------------------
# 3. 3D Axonometric Projection Helper
# ---------------------------------------------------------------------------
angle_x = np.deg2rad(-14.5)
angle_y = np.deg2rad(28.0)
scale_x = 1.00
scale_y = 0.64
scale_z = 1.00

EX = np.array([scale_x * np.cos(angle_x), scale_x * np.sin(angle_x)])
EY = np.array([scale_y * np.cos(angle_y), scale_y * np.sin(angle_y)])
EZ = np.array([0.0, scale_z])


def proj(x, y, z, origin_2d=(0.0, 0.0)):
    """Project 3D coordinates (x, y, z) to 2D canvas coordinates (X, Y) relative to origin_2d."""
    x_arr = np.asarray(x)
    y_arr = np.asarray(y)
    z_arr = np.asarray(z)
    X = origin_2d[0] + x_arr * EX[0] + y_arr * EY[0] + z_arr * EZ[0]
    Y = origin_2d[1] + x_arr * EX[1] + y_arr * EY[1] + z_arr * EZ[1]
    return X, Y


def draw_3d_arrow(
    ax, p_start, p_end, origin_2d, color, lw=1.5, mutation_scale=12,
    arrowstyle="-|>", zorder=20, ls="-", alpha=1.0
):
    x0, y0 = proj(*p_start, origin_2d=origin_2d)
    x1, y1 = proj(*p_end, origin_2d=origin_2d)
    arr = FancyArrowPatch(
        (x0, y0), (x1, y1),
        arrowstyle=arrowstyle,
        mutation_scale=mutation_scale,
        color=color,
        linewidth=lw,
        linestyle=ls,
        alpha=alpha,
        shrinkA=0,
        shrinkB=0,
        zorder=zorder,
    )
    ax.add_patch(arr)
    return arr


def draw_2d_arrow(
    ax, p0, p1, color, lw=1.25, mutation_scale=11, arrowstyle="-|>",
    zorder=25, ls="-", alpha=1.0
):
    arr = FancyArrowPatch(
        p0, p1,
        arrowstyle=arrowstyle,
        mutation_scale=mutation_scale,
        color=color,
        linewidth=lw,
        linestyle=ls,
        alpha=alpha,
        shrinkA=0,
        shrinkB=0,
        zorder=zorder,
    )
    ax.add_patch(arr)
    return arr


def draw_control_column_3d(
    ax, origin_2d, is_rising=True
):
    """
    Draw a 3D axonometric fluid control column [x, x+dx] x [y, y+dy]
    of total depth H = h + z resting on an impermeable seabed z = -h,
    showing volumetric fluxes (h+z)u and (h+z)v and the resulting
    free-surface rise (dz/dt > 0) or drop (dz/dt < 0).
    """
    dx = 3.20
    dy = 2.55
    z_bed = -1.85
    z_rock = -2.42
    z_datum = 0.0

    if is_rising:
        z_t0 = 0.35      # Initial surface z(t)
        z_t1 = 0.98      # Raised surface z(t + dt)
    else:
        z_t0 = 0.88      # Initial surface z(t)
        z_t1 = 0.22      # Lowered surface z(t + dt)

    z_main = z_t1

    # 1. Geological Seabed Block at bottom [z_rock, z_bed]
    # Front-left geological face (y = 0)
    pts_rock_fl = [
        proj(0, 0, z_rock, origin_2d),
        proj(dx, 0, z_rock, origin_2d),
        proj(dx, 0, z_bed, origin_2d),
        proj(0, 0, z_bed, origin_2d),
    ]
    ax.add_patch(Polygon(
        pts_rock_fl, facecolor=PALETTE["bed_front"],
        edgecolor=PALETTE["bed_edge"], lw=0.95, alpha=0.95, zorder=5
    ))
    # Front-right geological face (x = dx)
    pts_rock_fr = [
        proj(dx, 0, z_rock, origin_2d),
        proj(dx, dy, z_rock, origin_2d),
        proj(dx, dy, z_bed, origin_2d),
        proj(dx, 0, z_bed, origin_2d),
    ]
    ax.add_patch(Polygon(
        pts_rock_fr, facecolor=PALETTE["bed_right"],
        edgecolor=PALETTE["bed_edge"], lw=0.95, alpha=0.95, zorder=5
    ))
    # Seabed floor top face (z = z_bed)
    pts_bed_top = [
        proj(0, 0, z_bed, origin_2d),
        proj(dx, 0, z_bed, origin_2d),
        proj(dx, dy, z_bed, origin_2d),
        proj(0, dy, z_bed, origin_2d),
    ]
    ax.add_patch(Polygon(
        pts_bed_top, facecolor=PALETTE["bed_top"],
        edgecolor=PALETTE["bed_edge"], lw=0.75, alpha=0.90, zorder=4
    ))

    # Fine Tufte geological hatching on front-left and front-right rock faces
    for xh in np.linspace(0.22, dx - 0.22, 13):
        for k_s in range(2):
            xs_h = xh + k_s * 0.07
            ax.plot(
                *proj([xs_h, xs_h - 0.14], [0, 0], [z_bed, z_bed - 0.34], origin_2d),
                color=PALETTE["bed_hatch"], lw=0.48, alpha=0.68, zorder=5.5
            )
    for yh in np.linspace(0.22, dy - 0.22, 9):
        for k_s in range(2):
            ys_h = yh + k_s * 0.07
            ax.plot(
                *proj([dx, dx], [ys_h, ys_h - 0.14], [z_bed, z_bed - 0.34], origin_2d),
                color="#736354", lw=0.48, alpha=0.68, zorder=5.5
            )

    # Back vertical edges of the water column
    ax.plot(
        *proj([0, 0], [dy, dy], [z_bed, max(z_t0, z_t1)], origin_2d),
        color=PALETTE["water_edge"], lw=0.65, ls=":", alpha=0.50, zorder=6
    )
    ax.plot(
        *proj([0, 0], [0, dy], [z_datum, z_datum], origin_2d),
        color=PALETTE["datum_line"], lw=0.65, ls=(0, (4, 3)), alpha=0.42, zorder=6
    )
    ax.plot(
        *proj([0, dx], [dy, dy], [z_datum, z_datum], origin_2d),
        color=PALETTE["datum_line"], lw=0.65, ls=(0, (4, 3)), alpha=0.42, zorder=6
    )

    # 2. Main Water Column up to min(z_t0, z_t1)
    z_low = min(z_t0, z_t1)
    z_high = max(z_t0, z_t1)

    pts_w_fl = [
        proj(0, 0, z_bed, origin_2d),
        proj(dx, 0, z_bed, origin_2d),
        proj(dx, 0, z_low, origin_2d),
        proj(0, 0, z_low, origin_2d),
    ]
    ax.add_patch(Polygon(
        pts_w_fl, facecolor=PALETTE["water_front"],
        edgecolor="none", alpha=0.46, zorder=10
    ))

    pts_w_fr = [
        proj(dx, 0, z_bed, origin_2d),
        proj(dx, dy, z_bed, origin_2d),
        proj(dx, dy, z_low, origin_2d),
        proj(dx, 0, z_low, origin_2d),
    ]
    ax.add_patch(Polygon(
        pts_w_fr, facecolor=PALETTE["water_right"],
        edgecolor="none", alpha=0.52, zorder=10
    ))

    # 3. Upper Volume Cap between z_t0 and z_t1 (Delta z = (dz/dt) * dt)
    cap_fill_fl = "#88BBD8" if is_rising else "#E3ECF2"
    cap_fill_fr = "#72A8C8" if is_rising else "#D4E1EA"
    cap_alpha = 0.58 if is_rising else 0.30

    pts_cap_fl = [
        proj(0, 0, z_low, origin_2d),
        proj(dx, 0, z_low, origin_2d),
        proj(dx, 0, z_high, origin_2d),
        proj(0, 0, z_high, origin_2d),
    ]
    ax.add_patch(Polygon(
        pts_cap_fl, facecolor=cap_fill_fl,
        edgecolor="none", alpha=cap_alpha, zorder=11
    ))

    pts_cap_fr = [
        proj(dx, 0, z_low, origin_2d),
        proj(dx, dy, z_low, origin_2d),
        proj(dx, dy, z_high, origin_2d),
        proj(dx, 0, z_high, origin_2d),
    ]
    ax.add_patch(Polygon(
        pts_cap_fr, facecolor=cap_fill_fr,
        edgecolor="none", alpha=cap_alpha, zorder=11
    ))

    # Top face at z_t1 (current/new surface)
    pts_top_t1 = [
        proj(0, 0, z_t1, origin_2d),
        proj(dx, 0, z_t1, origin_2d),
        proj(dx, dy, z_t1, origin_2d),
        proj(0, dy, z_t1, origin_2d),
    ]
    ax.add_patch(Polygon(
        pts_top_t1, facecolor=PALETTE["water_top"],
        edgecolor=PALETTE["water_edge"], lw=1.45, alpha=0.82, zorder=14
    ))

    # Ghost / Initial surface rim at z_t0 (dashed)
    pts_top_t0 = [
        proj(0, 0, z_t0, origin_2d),
        proj(dx, 0, z_t0, origin_2d),
        proj(dx, dy, z_t0, origin_2d),
        proj(0, dy, z_t0, origin_2d),
        proj(0, 0, z_t0, origin_2d),
    ]
    ax.plot(
        [p[0] for p in pts_top_t0], [p[1] for p in pts_top_t0],
        color=PALETTE["water_edge"], lw=1.10, ls="--", alpha=0.85, zorder=15
    )

    # Vertical foreground edges of the column
    for (xe, ye), lwe in [((0, 0), 1.30), ((dx, 0), 1.40), ((dx, dy), 1.20)]:
        ax.plot(
            *proj([xe, xe], [ye, ye], [z_rock, z_high], origin_2d),
            color=PALETTE["water_edge"], lw=lwe, zorder=16
        )

    # Undisturbed Reference Plane z = 0 on foreground faces
    ax.plot(
        *proj([0, dx], [0, 0], [z_datum, z_datum], origin_2d),
        color=PALETTE["datum_line"], lw=1.05, ls=(0, (5, 3)), zorder=16
    )
    ax.plot(
        *proj([dx, dx], [0, dy], [z_datum, z_datum], origin_2d),
        color=PALETTE["datum_line"], lw=1.05, ls=(0, (5, 3)), zorder=16
    )

    # 4. Vertical arrows inside/above the cap showing dz/dt > 0 (Sobe) or dz/dt < 0 (Desce)
    col_dz = PALETTE["rise_col"] if is_rising else PALETTE["drop_col"]
    for (xv, yv) in [(0.30 * dx, 0.32 * dy), (0.70 * dx, 0.32 * dy), (0.50 * dx, 0.68 * dy)]:
        draw_3d_arrow(
            ax, (xv, yv, z_t0), (xv, yv, z_t1), origin_2d,
            color=col_dz, lw=2.0, mutation_scale=11.5, zorder=18
        )

    # 5. Volumetric Fluxes per Unit Width: (h+z)u along x, (h+z)v along y
    z_flux = -0.78  # Mid-depth of the water column
    y_mid = 0.44 * dy
    x_mid = 0.36 * dx

    if is_rising:
        # CONVERGENCE: Large inflow, small outflow
        len_in_x, len_out_x = 1.55, 0.82
        len_in_y, len_out_y = 1.35, 0.85
        lw_in, lw_out = 2.6, 1.45
        ms_in, ms_out = 15.0, 10.5
    else:
        # DIVERGENCE: Small inflow, large outflow
        len_in_x, len_out_x = 0.82, 1.55
        len_in_y, len_out_y = 0.85, 1.45
        lw_in, lw_out = 1.45, 2.6
        ms_in, ms_out = 10.5, 15.0

    # x-direction volumetric flux entering left face (x = 0)
    draw_3d_arrow(
        ax, (-len_in_x, y_mid, z_flux), (0.05, y_mid, z_flux), origin_2d,
        color=PALETTE["flux_in"], lw=lw_in, mutation_scale=ms_in, zorder=19
    )
    # x-direction volumetric flux leaving right face (x = dx)
    draw_3d_arrow(
        ax, (dx - 0.05, y_mid, z_flux), (dx + len_out_x, y_mid, z_flux), origin_2d,
        color=PALETTE["flux_in"], lw=lw_out, mutation_scale=ms_out, zorder=19
    )

    # y-direction volumetric flux entering front face (y = 0)
    draw_3d_arrow(
        ax, (x_mid, -len_in_y, z_flux - 0.12), (x_mid, 0.15, z_flux - 0.12), origin_2d,
        color=PALETTE["flux_y"], lw=lw_in, mutation_scale=ms_in, zorder=19
    )
    # y-direction volumetric flux leaving back face (y = dy)
    draw_3d_arrow(
        ax, (x_mid, dy - 0.05, z_flux + 0.05), (x_mid, dy + len_out_y, z_flux + 0.05), origin_2d,
        color=PALETTE["flux_y"], lw=lw_out, mutation_scale=ms_out, zorder=7
    )

    # Labels on the volumetric flux arrows (cleanly positioned without edge overlaps)
    x_in_p = proj(-0.55 * len_in_x, y_mid, z_flux + 0.24, origin_2d)
    crisp_text(
        ax, x_in_p[0] - 0.15, x_in_p[1],
        r"$[(h+z)u]_{\mathrm{ent}}$",
        color=PALETTE["flux_in"], stroke_w=0.18, bg_pill=PALETTE["bg_canvas"],
        fontsize=9.6, ha="center", va="bottom", zorder=25
    )

    x_out_p = proj(dx + len_out_x + 0.10, y_mid, z_flux, origin_2d)
    crisp_text(
        ax, x_out_p[0], x_out_p[1],
        r"$[(h+z)u]_{\mathrm{sai}}$",
        color=PALETTE["flux_in"], stroke_w=0.18,
        fontsize=9.6, ha="left", va="center", zorder=25
    )

    y_in_p = proj(x_mid + 0.18, -0.32, z_flux - 0.22, origin_2d)
    crisp_text(
        ax, y_in_p[0], y_in_p[1],
        r"$[(h+z)v]_{\mathrm{ent}}$",
        color=PALETTE["flux_y"], stroke_w=0.18, bg_pill="#D8EAF4",
        fontsize=9.4, ha="left", va="center", zorder=25
    )

    y_out_p = proj(x_mid + 0.38, dy + 0.48 * len_out_y, z_flux - 0.10, origin_2d)
    crisp_text(
        ax, y_out_p[0], y_out_p[1],
        r"$[(h+z)v]_{\mathrm{sai}}$",
        color=PALETTE["flux_y"], stroke_w=0.18, bg_pill="#E1EFF7",
        fontsize=9.4, ha="left", va="top", zorder=25
    )

    # Surface elevation labels z(t) and z(t + dt) on the right-most vertical corner (x = dx, y = dy)
    p_zt0 = proj(dx, dy, z_t0, origin_2d)
    p_zt1 = proj(dx, dy, z_t1, origin_2d)
    crisp_text(
        ax, p_zt0[0] + 0.16, p_zt0[1],
        r"$z(t)$", color=PALETTE["ink_secondary"], stroke_w=0.15,
        fontsize=9.4, ha="left", va="center", zorder=25
    )
    crisp_text(
        ax, p_zt1[0] + 0.16, p_zt1[1],
        r"$z(t+\Delta t)$", color=col_dz, stroke_w=0.18,
        fontsize=9.6, fontweight="bold", ha="left", va="center", zorder=25
    )

    # Datum z = 0 on the front corner (x = dx, y = 0)
    p_z0_r = proj(dx, 0, z_datum, origin_2d)
    crisp_text(
        ax, p_z0_r[0] - 0.16, p_z0_r[1] + 0.08,
        r"$z = 0$", color=PALETTE["datum_line"], stroke_w=0.15,
        bg_pill="#D8EAF4", fontsize=9.0, ha="right", va="bottom", zorder=25
    )

    # Total depth bracket H = h + z on the far-left of the first column only
    if is_rising:
        p_top_l = proj(0, 0, z_t1, origin_2d)
        p_bot_l = proj(0, 0, z_bed, origin_2d)
        off_H = -1.65
        ax.plot([p_top_l[0], p_top_l[0] + off_H * 1.06], [p_top_l[1], p_top_l[1]], color=PALETTE["ink_muted"], lw=0.6, zorder=20)
        ax.plot([p_bot_l[0], p_bot_l[0] + off_H * 1.06], [p_bot_l[1], p_bot_l[1]], color=PALETTE["ink_muted"], lw=0.6, zorder=20)
        draw_2d_arrow(
            ax, (p_bot_l[0] + off_H, p_bot_l[1]), (p_top_l[0] + off_H, p_top_l[1]),
            color=PALETTE["ink_primary"], lw=1.05, mutation_scale=8.5, arrowstyle="<|-|>"
        )
        ym_H = 0.5 * (p_top_l[1] + p_bot_l[1])
        crisp_text(
            ax, p_bot_l[0] + off_H - 0.15, ym_H + 0.08,
            r"$H = h + z$", color=PALETTE["ink_primary"], stroke_w=0.20,
            fontsize=10.5, ha="right", va="bottom", zorder=25
        )
        crisp_text(
            ax, p_bot_l[0] + off_H - 0.15, ym_H - 0.08,
            "Profundidade\ntotal da coluna",
            color=PALETTE["ink_secondary"], stroke_w=0.14,
            fontsize=8.9, fontstyle="italic", ha="right", va="top", zorder=25
        )

    # Bottom impermeabilidade note on geological stratum
    p_bed_lbl = proj(0.52 * dx, 0, 0.5 * (z_bed + z_rock), origin_2d)
    crisp_text(
        ax, p_bed_lbl[0], p_bed_lbl[1],
        r"Sem infiltração ($z = -h$)",
        color="#332920", stroke_w=0.14,
        fontsize=8.8, fontstyle="italic", ha="center", va="center",
        rotation=-14.5, zorder=25
    )

    return {
        "top_center": proj(0.5 * dx, 0.5 * dy, max(z_t0, z_t1), origin_2d),
        "bot_center": proj(0.5 * dx, 0.0, z_rock, origin_2d),
        "dx": dx,
        "dy": dy,
    }


def build_figure():
    fig, ax = plt.subplots(figsize=(13.6, 7.2), dpi=300)
    fig.patch.set_facecolor(PALETTE["bg_canvas"])
    ax.set_facecolor(PALETTE["bg_canvas"])

    # Origins for the two 3D control columns (Left: Rising dz/dt > 0; Right: Dropping dz/dt < 0)
    orig_left = (0.0, 0.0)
    orig_right = (8.35, 0.0)

    info_L = draw_control_column_3d(ax, orig_left, is_rising=True)
    info_R = draw_control_column_3d(ax, orig_right, is_rising=False)

    # -----------------------------------------------------------------------
    # Top Descriptions Above Left & Right Control Columns
    # -----------------------------------------------------------------------
    # Left Column Header: Convergence -> Column Rises (dz/dt > 0)
    xc_L = 2.15
    crisp_text(
        ax, xc_L, 3.88,
        r"1. Entra mais água do que sai  $\Longrightarrow$  Coluna sobe $\left(\dfrac{\partial z}{\partial t} > 0\right)$",
        color=PALETTE["rise_col"], stroke_w=0.20,
        fontsize=11.0, fontweight="bold", ha="center", va="bottom", zorder=28
    )
    crisp_text(
        ax, xc_L, 3.68,
        r"Convergência de fluxo: $\;\dfrac{\partial [(h+z)u]}{\partial x} + \dfrac{\partial [(h+z)v]}{\partial y} < 0$",
        color=PALETTE["ink_primary"], stroke_w=0.16,
        fontsize=9.8, ha="center", va="top", zorder=28
    )
    crisp_text(
        ax, xc_L, 2.95,
        r"Lado direito positivo: $-\nabla\cdot[(h+z)\mathbf{u}] > 0$ (acúmulo de volume $\Delta V > 0$)",
        color=PALETTE["ink_secondary"], stroke_w=0.13,
        fontsize=8.9, fontstyle="italic", ha="center", va="top", zorder=28
    )

    # Right Column Header: Divergence -> Column Drops (dz/dt < 0)
    xc_R = 10.50
    crisp_text(
        ax, xc_R, 3.88,
        r"2. Sai mais água do que entra  $\Longrightarrow$  Coluna desce $\left(\dfrac{\partial z}{\partial t} < 0\right)$",
        color=PALETTE["drop_col"], stroke_w=0.20,
        fontsize=11.0, fontweight="bold", ha="center", va="bottom", zorder=28
    )
    crisp_text(
        ax, xc_R, 3.68,
        r"Divergência de fluxo: $\;\dfrac{\partial [(h+z)u]}{\partial x} + \dfrac{\partial [(h+z)v]}{\partial y} > 0$",
        color=PALETTE["ink_primary"], stroke_w=0.16,
        fontsize=9.8, ha="center", va="top", zorder=28
    )
    crisp_text(
        ax, xc_R, 2.95,
        r"Lado direito negativo: $-\nabla\cdot[(h+z)\mathbf{u}] < 0$ (déficit de volume $\Delta V < 0$)",
        color=PALETTE["ink_secondary"], stroke_w=0.13,
        fontsize=8.9, fontstyle="italic", ha="center", va="top", zorder=28
    )

    # Subtle vertical separator hairline between the two scenarios
    ax.plot([6.25, 6.25], [-3.85, 4.15], color=PALETTE["rule_light"], lw=0.85, ls="--", zorder=3)

    # -----------------------------------------------------------------------
    # Bottom Synthesis Strip (Volumetric Flux Definition & Incompressibility)
    # -----------------------------------------------------------------------
    ax.plot([-3.25, 15.15], [-3.95, -3.95], color=PALETTE["rule_light"], lw=0.85, zorder=20)

    # Left bottom note: Meaning of Volumetric Fluxes (h+z)u and (h+z)v
    crisp_text(
        ax, -3.05, -4.18,
        r"Fluxos volumétricos por unidade de largura: $\;q_x = (h+z)u = H\,u\;$ e $\;q_y = (h+z)v = H\,v$",
        color=PALETTE["flux_in"], stroke_w=0.18,
        fontsize=9.8, fontweight="bold", ha="left", va="top", zorder=28
    )
    crisp_text(
        ax, -3.05, -4.52,
        r"Correspondem à profundidade total $H(x,y,t) = h(x,y) + z(x,y,t)$" + "\n"
        + r"multiplicada pelas velocidades $u$ e $v$ nas direções $x$ e $y$.",
        color=PALETTE["ink_secondary"], stroke_w=0.13,
        fontsize=9.0, fontstyle="italic", ha="left", va="top", linespacing=1.32, zorder=28
    )

    # Right bottom note: Conservation of Mass & Incompressibility (Why RHS = 0)
    crisp_text(
        ax, 6.65, -4.18,
        r"Fluido incompressível: sem evaporação, sem chuva e sem infiltração ($\text{soma} = 0$)",
        color=PALETTE["ink_primary"], stroke_w=0.18,
        fontsize=9.8, fontweight="bold", ha="left", va="top", zorder=28
    )
    crisp_text(
        ax, 6.65, -4.52,
        r"O balanço líquido dos fluxos governa o sobe-e-desce da superfície livre:",
        color=PALETTE["ink_secondary"], stroke_w=0.13,
        fontsize=9.0, fontstyle="italic", ha="left", va="top", zorder=28
    )
    crisp_text(
        ax, 6.65, -4.92,
        r"$\dfrac{\partial z}{\partial t} = -\left(\dfrac{\partial [(h+z)u]}{\partial x} + \dfrac{\partial [(h+z)v]}{\partial y}\right)$",
        color=PALETTE["ink_primary"], stroke_w=0.16,
        fontsize=9.6, ha="left", va="top", zorder=28
    )

    # 3D Coordinate Triad (x, y, z) in the lower-center between the two columns
    tri_orig = (6.25, -2.95)
    draw_3d_arrow(ax, (0, 0, 0), (0.95, 0, 0), tri_orig, color=PALETTE["ink_primary"], lw=1.25, mutation_scale=10)
    px_t = proj(1.08, 0, 0, tri_orig)
    crisp_text(ax, px_t[0], px_t[1], r"$x$", color=PALETTE["ink_primary"], stroke_w=0.18, fontsize=11.0, ha="left", va="center")

    draw_3d_arrow(ax, (0, 0, 0), (0, 0.95, 0), tri_orig, color=PALETTE["ink_primary"], lw=1.25, mutation_scale=10)
    py_t = proj(0, 1.08, 0, tri_orig)
    crisp_text(ax, py_t[0], py_t[1], r"$y$", color=PALETTE["ink_primary"], stroke_w=0.18, fontsize=11.0, ha="left", va="bottom")

    draw_3d_arrow(ax, (0, 0, 0), (0, 0, 0.95), tri_orig, color=PALETTE["ink_primary"], lw=1.25, mutation_scale=10)
    pz_t = proj(0, 0, 1.05, tri_orig)
    crisp_text(ax, pz_t[0], pz_t[1], r"$z$", color=PALETTE["ink_primary"], stroke_w=0.18, fontsize=11.0, ha="center", va="bottom")

    # Top boundary condition note ("Sem chuva ou evaporação") on both columns
    crisp_text(
        ax, 2.25, 2.15,
        "Sem chuva ou evaporação",
        color=PALETTE["ink_muted"], stroke_w=0.12,
        fontsize=8.6, fontstyle="italic", ha="center", va="bottom", zorder=25
    )
    crisp_text(
        ax, 10.60, 2.15,
        "Sem chuva ou evaporação",
        color=PALETTE["ink_muted"], stroke_w=0.12,
        fontsize=8.6, fontstyle="italic", ha="center", va="bottom", zorder=25
    )

    # Set clean bounds and remove default Matplotlib frame/ticks
    ax.set_xlim(-3.55, 15.35)
    ax.set_ylim(-5.65, 4.45)
    ax.set_aspect("equal")
    ax.axis("off")

    plt.tight_layout(pad=0.12)

    out_dir = Path(__file__).resolve().parent.parent / "figures"
    out_dir.mkdir(parents=True, exist_ok=True)

    svg_path = out_dir / "swe_continuity_meaning.svg"
    pdf_path = out_dir / "swe_continuity_meaning.pdf"
    png_path = out_dir / "swe_continuity_meaning.png"

    fig.savefig(svg_path, format="svg", bbox_inches="tight", facecolor=fig.get_facecolor())
    fig.savefig(pdf_path, format="pdf", bbox_inches="tight", facecolor=fig.get_facecolor())
    fig.savefig(png_path, format="png", dpi=300, bbox_inches="tight", facecolor=fig.get_facecolor())
    print(f"Saved: {svg_path}")
    print(f"Saved: {pdf_path}")
    print(f"Saved: {png_path}")


if __name__ == "__main__":
    build_figure()
