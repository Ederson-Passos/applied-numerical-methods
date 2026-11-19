"""
Generate an Edward Tufte-inspired vector scientific illustration of the
2D Shallow Water Equations (2D SWE) physical domain, vertical cross-section,
and physical variables following Casulli (1990).

Outputs:
  - ../figures/swe_physical_domain.svg (vector SVG with embedded glyph paths)
  - ../figures/swe_physical_domain.pdf (vector PDF for LaTeX publication)
  - ../figures/swe_physical_domain.png (high-resolution raster preview)
"""

import glob
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.patches import Polygon, FancyArrowPatch, Rectangle
from matplotlib.colors import LinearSegmentedColormap
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
# 2. Edward Tufte Muted Cartographic & Oceanographic Palette
# ---------------------------------------------------------------------------
PALETTE = {
    "bg_canvas": "#FCFBF7",       # Warm archival paper ivory
    "bg_panel": "#F5F2EB",        # Soft warm stone for marginalia panels
    "rule_dark": "#8C8275",       # Bookplate structural rule
    "rule_light": "#D6CFC4",      # Subtle section divider
    "ink_primary": "#1E242B",     # Deep charcoal ink for primary typography
    "ink_secondary": "#485360",   # Muted slate for explanatory annotations
    "ink_muted": "#7A8490",       # Whisper-quiet gray for leader lines
    "water_front": "#A9CCE0",     # Front-left water column face
    "water_right": "#8EB8D1",     # Front-right water column face
    "water_edge": "#275473",      # Crisp structural water edge
    "water_mesh": "#4A7C9B",      # Fine wave isolines
    "datum_line": "#334155",      # Undisturbed reference plane z = 0
    "column_fill": "#FFF9EB",     # Highlighted internal fluid column
    "column_edge": "#234966",     # Internal column wireframe
    "velocity_uv": "#113852",     # Deep Prussian navy for u, v vectors
    "wind_tau": "#1F686B",        # Muted sea-teal for wind stress tau_x, tau_y
    "friction_gamma": "#9A3B26",  # Warm Venetian terracotta for bottom friction
    "pressure_col": "#355378",    # Hydrostatic pressure distribution
    "bed_front": "#C8BBAE",       # Geological cross-section left face
    "bed_right": "#B3A494",       # Geological cross-section right face
    "bed_edge": "#6B5B4C",        # Seabed contour & outline
    "bed_hatch": "#877666",       # Fine sediment hatching
}

# ---------------------------------------------------------------------------
# 3. 3D Axonometric Projection & Physical Geometry (Casulli 1990 Setup)
# ---------------------------------------------------------------------------
LX = 10.4
LY = 6.2
Z_BASE = -2.55  # Bottom of geological block

angle_x = np.deg2rad(-15.5)
angle_y = np.deg2rad(27.0)
scale_x = 1.00
scale_y = 0.65
scale_z = 1.00

EX = np.array([scale_x * np.cos(angle_x), scale_x * np.sin(angle_x)])
EY = np.array([scale_y * np.cos(angle_y), scale_y * np.sin(angle_y)])
EZ = np.array([0.0, scale_z])


def proj(x, y, z):
    """Project 3D coordinates (x, y, z) to 2D canvas coordinates (X, Y)."""
    x_arr = np.asarray(x)
    y_arr = np.asarray(y)
    z_arr = np.asarray(z)
    X = x_arr * EX[0] + y_arr * EY[0] + z_arr * EZ[0]
    Y = x_arr * EX[1] + y_arr * EY[1] + z_arr * EZ[1]
    return X, Y


def free_surface_z(x, y):
    """Smooth 2D gravity-wave free-surface elevation z(x, y, t)."""
    term1 = 0.44 * np.sin(2.0 * np.pi * x / (0.82 * LX) + 0.35) * np.cos(
        0.45 * np.pi * y / LY
    )
    term2 = 0.14 * np.cos(2.0 * np.pi * x / (0.45 * LX) - 0.8 * np.pi * y / LY)
    return term1 + term2 + 0.05


def depth_h(x, y):
    """Smooth variable undisturbed water depth h(x, y) > 0."""
    h0 = 1.92
    shoal = -0.33 * np.sin(np.pi * x / LX - 0.2) * np.cos(0.6 * np.pi * y / LY)
    ripple = 0.15 * np.cos(2.0 * np.pi * x / LX + 0.4 * np.pi * y / LY)
    return h0 + shoal + ripple


def seabed_z(x, y):
    """Seabed elevation z = -h(x, y)."""
    return -depth_h(x, y)


def draw_3d_arrow(
    ax, p_start, p_end, color, lw=1.3, mutation_scale=12, arrowstyle="-|>",
    zorder=20, ls="-", alpha=1.0, shrinkA=0, shrinkB=0
):
    """Draw a sharp vector arrow between two 3D points."""
    x0, y0 = proj(*p_start)
    x1, y1 = proj(*p_end)
    arr = FancyArrowPatch(
        (x0, y0), (x1, y1),
        arrowstyle=arrowstyle,
        mutation_scale=mutation_scale,
        color=color,
        linewidth=lw,
        linestyle=ls,
        alpha=alpha,
        shrinkA=shrinkA,
        shrinkB=shrinkB,
        zorder=zorder,
    )
    ax.add_patch(arr)
    return arr


def draw_2d_arrow(
    ax, p0, p1, color, lw=1.2, mutation_scale=11, arrowstyle="-|>",
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


def add_callout_block(
    ax, target_2d, box_pos_2d, leader_start_2d, title_str, lines_list,
    align="left", rad=0.14, zorder=28, dot_color=None
):
    """
    Draw a clean Tufte callout with bold title, regular body lines,
    and a whisper-quiet curved leader line starting from leader_start_2d
    (outside the text block so it never crosses any text).
    """
    tx, ty = target_2d
    bx, by = box_pos_2d
    lx, ly = leader_start_2d
    if dot_color is None:
        dot_color = PALETTE["ink_secondary"]

    ax.plot(tx, ty, marker="o", markersize=3.4, color=dot_color, zorder=zorder)
    conn = FancyArrowPatch(
        (lx, ly), (tx, ty),
        connectionstyle=f"arc3,rad={rad}",
        arrowstyle="-",
        color=PALETTE["ink_muted"],
        linewidth=0.68,
        zorder=zorder - 2,
    )
    ax.add_patch(conn)

    t_obj = ax.text(
        bx, by, title_str,
        fontsize=10.0, fontweight="bold", color=PALETTE["ink_primary"],
        ha=align, va="bottom", zorder=zorder + 1
    )
    t_obj.set_path_effects([pe.withStroke(linewidth=3.2, foreground=PALETTE["bg_canvas"])])

    body_text = "\n".join(lines_list)
    b_obj = ax.text(
        bx, by - 0.08, body_text,
        fontsize=8.9, color=PALETTE["ink_secondary"],
        ha=align, va="top", linespacing=1.34, zorder=zorder + 1
    )
    b_obj.set_path_effects([pe.withStroke(linewidth=3.2, foreground=PALETTE["bg_canvas"])])


def build_figure():
    fig, ax = plt.subplots(figsize=(16.6, 10.2), dpi=300)
    fig.patch.set_facecolor(PALETTE["bg_canvas"])
    ax.set_facecolor(PALETTE["bg_canvas"])

    # Grid resolution for smooth surfaces
    nx, ny = 66, 46
    xg = np.linspace(0, LX, nx)
    yg = np.linspace(0, LY, ny)
    XX, YY = np.meshgrid(xg, yg, indexing="ij")
    ZZ_surf = free_surface_z(XX, YY)
    ZZ_bed = seabed_z(XX, YY)

    # -----------------------------------------------------------------------
    # LAYER 1: Back Faces & Seabed Top Surface (z = -h(x, y))
    # -----------------------------------------------------------------------
    ax.plot(
        *proj(np.zeros(ny), yg, free_surface_z(0, yg)),
        color=PALETTE["water_edge"], lw=0.65, alpha=0.42, zorder=2
    )
    ax.plot(
        *proj(xg, np.full(nx, LY), free_surface_z(xg, LY)),
        color=PALETTE["water_edge"], lw=0.65, alpha=0.42, zorder=2
    )
    ax.plot(
        *proj([0, 0], [LY, LY], [seabed_z(0, LY), free_surface_z(0, LY)]),
        color=PALETTE["water_edge"], lw=0.55, ls=":", alpha=0.42, zorder=2
    )

    bed_cmap = LinearSegmentedColormap.from_list(
        "tufte_bed", ["#AD9C8A", "#C8B9A8", "#E2D9CC"]
    )
    z_bed_min, z_bed_max = ZZ_bed.min(), ZZ_bed.max()

    for i in range(nx - 1):
        for j in range(ny - 1):
            xs = [XX[i, j], XX[i + 1, j], XX[i + 1, j + 1], XX[i, j + 1]]
            ys = [YY[i, j], YY[i + 1, j], YY[i + 1, j + 1], YY[i, j + 1]]
            zs = [ZZ_bed[i, j], ZZ_bed[i + 1, j], ZZ_bed[i + 1, j + 1], ZZ_bed[i, j + 1]]
            X2, Y2 = proj(xs, ys, zs)
            z_mean = 0.25 * sum(zs)
            norm_z = (z_mean - z_bed_min) / (z_bed_max - z_bed_min + 1e-9)
            dz_dx = (ZZ_bed[i + 1, j] - ZZ_bed[i, j]) / (xg[1] - xg[0])
            shade = np.clip(0.55 * norm_z + 0.35 - 0.35 * dz_dx, 0.05, 0.95)
            col = bed_cmap(shade)
            poly = Polygon(
                list(zip(X2, Y2)),
                facecolor=col, edgecolor=col, lw=0.15, alpha=0.92, zorder=3
            )
            ax.add_patch(poly)

    for i in range(0, nx, 6):
        ax.plot(
            *proj(XX[i, :], YY[i, :], ZZ_bed[i, :]),
            color=PALETTE["bed_edge"], lw=0.32, alpha=0.38, zorder=4
        )
    for j in range(0, ny, 5):
        ax.plot(
            *proj(XX[:, j], YY[:, j], ZZ_bed[:, j]),
            color=PALETTE["bed_edge"], lw=0.32, alpha=0.38, zorder=4
        )

    # Back undisturbed datum lines (z = 0)
    ax.plot(
        *proj([0, 0], [0, LY], [0, 0]),
        color=PALETTE["datum_line"], lw=0.65, ls=(0, (4, 3)), alpha=0.40, zorder=5
    )
    ax.plot(
        *proj([0, LX], [LY, LY], [0, 0]),
        color=PALETTE["datum_line"], lw=0.65, ls=(0, (4, 3)), alpha=0.40, zorder=5
    )

    # -----------------------------------------------------------------------
    # LAYER 2: Internal Differential Fluid Column (Coluna d'água H = h + z)
    #          and Depth-Averaged Velocities u(x,y,t), v(x,y,t)
    # -----------------------------------------------------------------------
    xc, yc = 4.25, 2.75
    dx_col, dy_col = 0.74, 0.64
    c_corners_xy = [
        (xc - dx_col / 2, yc - dy_col / 2),
        (xc + dx_col / 2, yc - dy_col / 2),
        (xc + dx_col / 2, yc + dy_col / 2),
        (xc - dx_col / 2, yc + dy_col / 2),
    ]
    z_col_bot = [seabed_z(x_, y_) for x_, y_ in c_corners_xy]
    z_col_top = [free_surface_z(x_, y_) for x_, y_ in c_corners_xy]

    for face_idx, f_alpha in [((0, 1), 0.36), ((1, 2), 0.30)]:
        i0, i1 = face_idx
        pts_3d = [
            (*c_corners_xy[i0], z_col_bot[i0]),
            (*c_corners_xy[i1], z_col_bot[i1]),
            (*c_corners_xy[i1], z_col_top[i1]),
            (*c_corners_xy[i0], z_col_top[i0]),
        ]
        pts_2d = [proj(*p) for p in pts_3d]
        ax.add_patch(Polygon(
            pts_2d, facecolor=PALETTE["column_fill"],
            edgecolor=PALETTE["column_edge"], lw=0.7, ls="-",
            alpha=f_alpha, zorder=8
        ))

    for idx in range(4):
        x_, y_ = c_corners_xy[idx]
        ax.plot(
            *proj([x_, x_], [y_, y_], [z_col_bot[idx], z_col_top[idx]]),
            color=PALETTE["column_edge"], lw=0.80 if idx in (0, 1, 2) else 0.45,
            ls="-" if idx in (0, 1, 2) else ":", alpha=0.78, zorder=9
        )
    for z_list, z_ord in [(z_col_bot, 9), (z_col_top, 16)]:
        pts_rim = [proj(*c_corners_xy[k], z_list[k]) for k in [0, 1, 2, 3, 0]]
        ax.plot(
            [p[0] for p in pts_rim], [p[1] for p in pts_rim],
            color=PALETTE["column_edge"], lw=0.85, alpha=0.88, zorder=z_ord
        )

    # Vertical velocity profile & depth-averaged velocity vectors u(x,y,t), v(x,y,t)
    z_cb = seabed_z(xc, yc)
    z_ct = free_surface_z(xc, yc)
    z_prof = np.linspace(z_cb, z_ct, 32)
    s_norm = (z_prof - z_cb) / (z_ct - z_cb)
    u_mag = 1.48
    v_mag = 1.24
    u_prof = u_mag * (1.12 * (s_norm ** 0.28) + 0.14 * s_norm)
    u_prof = u_prof * (u_mag / np.mean(u_prof))

    ax.plot(
        *proj(np.full_like(z_prof, xc), np.full_like(z_prof, yc), z_prof),
        color=PALETTE["velocity_uv"], lw=0.85, ls="-", alpha=0.75, zorder=10
    )
    ax.plot(
        *proj(xc + u_prof, np.full_like(z_prof, yc), z_prof),
        color=PALETTE["velocity_uv"], lw=0.85, ls="--", alpha=0.65, zorder=10
    )
    ax.plot(
        *proj([xc + u_mag, xc + u_mag], [yc, yc], [z_cb, z_ct]),
        color=PALETTE["velocity_uv"], lw=0.7, ls=":", alpha=0.55, zorder=10
    )
    for frac in [0.18, 0.40, 0.72, 0.90]:
        zp = z_cb + frac * (z_ct - z_cb)
        up = u_mag * (1.12 * (frac ** 0.28) + 0.14 * frac) * (u_mag / 1.01)
        draw_3d_arrow(
            ax, (xc, yc, zp), (xc + up, yc, zp),
            color=PALETTE["velocity_uv"], lw=0.65, mutation_scale=6.5,
            alpha=0.45, zorder=10
        )

    # Primary Depth-Averaged Velocity Vectors u(x,y,t) and v(x,y,t) at mid-depth
    z_mid = 0.50 * (z_cb + z_ct)
    draw_3d_arrow(
        ax, (xc, yc, z_mid), (xc + u_mag, yc, z_mid),
        color=PALETTE["velocity_uv"], lw=2.2, mutation_scale=13.5, zorder=16
    )
    draw_3d_arrow(
        ax, (xc, yc, z_mid), (xc, yc + v_mag, z_mid),
        color=PALETTE["velocity_uv"], lw=2.2, mutation_scale=13.5, zorder=16
    )
    draw_3d_arrow(
        ax, (xc, yc, z_mid), (xc + u_mag, yc + v_mag, z_mid),
        color="#0B2545", lw=1.5, mutation_scale=11.5, ls="-", alpha=0.92, zorder=16
    )
    ax.plot(
        *proj([xc + u_mag, xc + u_mag], [yc, yc + v_mag], [z_mid, z_mid]),
        color=PALETTE["velocity_uv"], lw=0.75, ls=":", alpha=0.78, zorder=15.8
    )
    ax.plot(
        *proj([xc, xc + u_mag], [yc + v_mag, yc + v_mag], [z_mid, z_mid]),
        color=PALETTE["velocity_uv"], lw=0.75, ls=":", alpha=0.78, zorder=15.8
    )

    # Clear labels for u(x,y,t), v(x,y,t), and resultant u_vec
    xu_lbl, yu_lbl = proj(xc + u_mag + 0.12, yc - 0.14, z_mid - 0.04)
    t_u = ax.text(
        xu_lbl, yu_lbl, r"$u(x,y,t)$",
        fontsize=11.0, color=PALETTE["velocity_uv"],
        ha="left", va="center", zorder=25
    )
    t_u.set_path_effects([pe.withStroke(linewidth=3.0, foreground="#D5E7F2")])

    xv_lbl, yv_lbl = proj(xc + 0.08, yc + v_mag + 0.14, z_mid + 0.06)
    t_v = ax.text(
        xv_lbl, yv_lbl, r"$v(x,y,t)$",
        fontsize=11.0, color=PALETTE["velocity_uv"],
        ha="left", va="bottom", zorder=25
    )
    t_v.set_path_effects([pe.withStroke(linewidth=3.0, foreground="#D5E7F2")])

    xuv_lbl, yuv_lbl = proj(xc + u_mag + 0.14, yc + v_mag + 0.06, z_mid - 0.02)
    t_uv = ax.text(
        xuv_lbl, yuv_lbl, r"$\mathbf{u} = (u, v)^\top$",
        fontsize=9.8, color="#0B2545", ha="left", va="center", zorder=25
    )
    t_uv.set_path_effects([pe.withStroke(linewidth=2.8, foreground="#D5E7F2")])

    # -----------------------------------------------------------------------
    # LAYER 3: Bottom Friction Vectors (-gamma u, -gamma v) at the Seabed
    # -----------------------------------------------------------------------
    xf, yf = xc + 0.10, yc - 0.20
    zf = seabed_z(xf, yf) + 0.05
    zf_x_end = seabed_z(xf - 1.15, yf) + 0.05
    zf_y_end = seabed_z(xf, yf - 0.95) + 0.05
    draw_3d_arrow(
        ax, (xf, yf, zf), (xf - 1.15, yf, zf_x_end),
        color=PALETTE["friction_gamma"], lw=1.8, mutation_scale=11.5, zorder=11
    )
    draw_3d_arrow(
        ax, (xf, yf, zf), (xf, yf - 0.95, zf_y_end),
        color=PALETTE["friction_gamma"], lw=1.8, mutation_scale=11.5, zorder=11
    )

    xg_lu, yg_lu = proj(xf - 1.20, yf + 0.04, zf_x_end + 0.04)
    t_gu = ax.text(
        xg_lu, yg_lu, r"$-\gamma u$",
        fontsize=10.5, color=PALETTE["friction_gamma"], ha="right", va="bottom", zorder=25
    )
    t_gu.set_path_effects([pe.withStroke(linewidth=2.8, foreground="#D5C8BA")])

    xg_lv, yg_lv = proj(xf + 0.06, yf - 0.98, zf_y_end - 0.03)
    t_gv = ax.text(
        xg_lv, yg_lv, r"$-\gamma v$",
        fontsize=10.5, color=PALETTE["friction_gamma"], ha="left", va="top", zorder=25
    )
    t_gv.set_path_effects([pe.withStroke(linewidth=2.8, foreground="#D5C8BA")])

    # -----------------------------------------------------------------------
    # LAYER 4: Front Vertical Water Faces & Geological Seabed Cross-Sections
    # -----------------------------------------------------------------------
    # Front-Left Geological Seabed (y = 0, x in [0, LX])
    x_bed_fl = np.concatenate([xg, xg[::-1]])
    y_bed_fl = np.zeros_like(x_bed_fl)
    z_bed_fl = np.concatenate([seabed_z(xg, 0), np.full(nx, Z_BASE)])
    X_bfl, Y_bfl = proj(x_bed_fl, y_bed_fl, z_bed_fl)
    ax.add_patch(Polygon(
        list(zip(X_bfl, Y_bfl)),
        facecolor=PALETTE["bed_front"], edgecolor=PALETTE["bed_edge"],
        lw=0.9, alpha=0.96, zorder=12
    ))

    for xh in np.linspace(0.25, LX - 0.25, 38):
        for k_sub in range(3):
            dx_s = (k_sub - 1) * 0.06
            x_s = np.clip(xh + dx_s, 0.05, LX - 0.05)
            zt = seabed_z(x_s, 0)
            zb = max(Z_BASE + 0.06, zt - 0.28 + 0.05 * k_sub)
            ax.plot(
                *proj([x_s, x_s - 0.14], [0, 0], [zt, zb]),
                color=PALETTE["bed_hatch"], lw=0.45, alpha=0.65, zorder=12.5
            )

    # Front-Right Geological Seabed (x = LX, y in [0, LY])
    x_bed_fr = np.full(2 * ny, LX)
    y_bed_fr = np.concatenate([yg, yg[::-1]])
    z_bed_fr = np.concatenate([seabed_z(LX, yg), np.full(ny, Z_BASE)])
    X_bfr, Y_bfr = proj(x_bed_fr, y_bed_fr, z_bed_fr)
    ax.add_patch(Polygon(
        list(zip(X_bfr, Y_bfr)),
        facecolor=PALETTE["bed_right"], edgecolor=PALETTE["bed_edge"],
        lw=0.9, alpha=0.96, zorder=12
    ))

    for yh in np.linspace(0.25, LY - 0.25, 24):
        for k_sub in range(3):
            dy_s = (k_sub - 1) * 0.06
            y_s = np.clip(yh + dy_s, 0.05, LY - 0.05)
            zt = seabed_z(LX, y_s)
            zb = max(Z_BASE + 0.06, zt - 0.28 + 0.05 * k_sub)
            ax.plot(
                *proj([LX, LX], [y_s, y_s - 0.14], [zt, zb]),
                color="#736354", lw=0.45, alpha=0.65, zorder=12.5
            )

    # Translucent Front-Left Water Face (y = 0)
    x_w_fl = np.concatenate([xg, xg[::-1]])
    y_w_fl = np.zeros_like(x_w_fl)
    z_w_fl = np.concatenate([free_surface_z(xg, 0), seabed_z(xg[::-1], 0)])
    X_wfl, Y_wfl = proj(x_w_fl, y_w_fl, z_w_fl)
    ax.add_patch(Polygon(
        list(zip(X_wfl, Y_wfl)),
        facecolor=PALETTE["water_front"], edgecolor="none",
        alpha=0.33, zorder=13
    ))

    # Translucent Front-Right Water Face (x = LX)
    x_w_fr = np.full(2 * ny, LX)
    y_w_fr = np.concatenate([yg, yg[::-1]])
    z_w_fr = np.concatenate([free_surface_z(LX, yg), seabed_z(LX, yg[::-1])])
    X_wfr, Y_wfr = proj(x_w_fr, y_w_fr, z_w_fr)
    ax.add_patch(Polygon(
        list(zip(X_wfr, Y_wfr)),
        facecolor=PALETTE["water_right"], edgecolor="none",
        alpha=0.39, zorder=13
    ))

    # -----------------------------------------------------------------------
    # LAYER 5: Hydrostatic Pressure Distribution p(z') on Front-Left Face
    # -----------------------------------------------------------------------
    xp = 6.55
    zp_top = free_surface_z(xp, 0)
    zp_bot = seabed_z(xp, 0)
    p_max_width = 0.85

    pts_press = [
        proj(xp, 0, zp_top),
        proj(xp, 0, zp_bot),
        proj(xp + p_max_width, 0, zp_bot),
    ]
    ax.add_patch(Polygon(
        pts_press, facecolor="#3D5A80", edgecolor="#233852",
        lw=0.75, alpha=0.20, zorder=14
    ))
    ax.plot(
        *proj([xp, xp], [0, 0], [zp_bot, zp_top]),
        color="#233852", lw=0.95, zorder=14.5
    )
    ax.plot(
        *proj([xp, xp + p_max_width], [0, 0], [zp_top, zp_bot]),
        color="#233852", lw=0.95, ls="-", zorder=14.5
    )
    for frac in [0.22, 0.44, 0.66, 0.88]:
        z_curr = zp_top - frac * (zp_top - zp_bot)
        w_curr = frac * p_max_width
        draw_3d_arrow(
            ax, (xp + w_curr, 0, z_curr), (xp, 0, z_curr),
            color="#233852", lw=0.75, mutation_scale=7.5, zorder=14.6
        )
    xp_lbl, yp_lbl = proj(xp + p_max_width + 0.08, 0, 0.65 * zp_bot + 0.35 * zp_top)
    tp = ax.text(
        xp_lbl, yp_lbl,
        r"$p(z') = p_0 + \rho g(z - z')$",
        fontsize=9.1, color="#19304B", ha="left", va="center", zorder=25
    )
    tp.set_path_effects([pe.withStroke(linewidth=2.8, foreground="#CFE3F0")])

    # -----------------------------------------------------------------------
    # LAYER 6: Undulating Free Surface z(x, y, t) at Top of Parallelepiped
    # -----------------------------------------------------------------------
    water_cmap = LinearSegmentedColormap.from_list(
        "tufte_water", ["#7FAAC6", "#B3D2E5", "#E8F3FA"]
    )
    z_s_min, z_s_max = ZZ_surf.min(), ZZ_surf.max()

    for i in range(nx - 1):
        for j in range(ny - 1):
            xs = [XX[i, j], XX[i + 1, j], XX[i + 1, j + 1], XX[i, j + 1]]
            ys = [YY[i, j], YY[i + 1, j], YY[i + 1, j + 1], YY[i, j + 1]]
            zs = [
                ZZ_surf[i, j], ZZ_surf[i + 1, j],
                ZZ_surf[i + 1, j + 1], ZZ_surf[i, j + 1]
            ]
            X2, Y2 = proj(xs, ys, zs)
            z_mean = 0.25 * sum(zs)
            norm_z = (z_mean - z_s_min) / (z_s_max - z_s_min + 1e-9)
            dz_dx = (ZZ_surf[i + 1, j] - ZZ_surf[i, j]) / (xg[1] - xg[0])
            dz_dy = (ZZ_surf[i, j + 1] - ZZ_surf[i, j]) / (yg[1] - yg[0])
            light = np.clip(0.62 * norm_z + 0.28 - 0.35 * dz_dx + 0.15 * dz_dy, 0.05, 0.98)
            col = water_cmap(light)
            poly = Polygon(
                list(zip(X2, Y2)),
                facecolor=col, edgecolor=col, lw=0.12, alpha=0.76, zorder=15
            )
            ax.add_patch(poly)

    for i in range(0, nx, 4):
        ax.plot(
            *proj(XX[i, :], YY[i, :], ZZ_surf[i, :]),
            color=PALETTE["water_mesh"], lw=0.38, alpha=0.48, zorder=15.5
        )
    for j in range(0, ny, 4):
        ax.plot(
            *proj(XX[:, j], YY[:, j], ZZ_surf[:, j]),
            color=PALETTE["water_mesh"], lw=0.38, alpha=0.48, zorder=15.5
        )

    # Crisp Foreground Edges of the Parallelepiped
    ax.plot(
        *proj(xg, np.zeros(nx), free_surface_z(xg, 0)),
        color=PALETTE["water_edge"], lw=1.45, zorder=17
    )
    ax.plot(
        *proj(np.full(ny, LX), yg, free_surface_z(LX, yg)),
        color=PALETTE["water_edge"], lw=1.35, zorder=17
    )
    ax.plot(
        *proj(xg, np.zeros(nx), seabed_z(xg, 0)),
        color=PALETTE["bed_edge"], lw=1.35, zorder=17
    )
    ax.plot(
        *proj(np.full(ny, LX), yg, seabed_z(LX, yg)),
        color=PALETTE["bed_edge"], lw=1.25, zorder=17
    )
    for (xc_edge, yc_edge), lw_e in [((0, 0), 1.15), ((LX, 0), 1.3), ((LX, LY), 1.05)]:
        ax.plot(
            *proj(
                [xc_edge, xc_edge], [yc_edge, yc_edge],
                [Z_BASE, free_surface_z(xc_edge, yc_edge)]
            ),
            color=PALETTE["water_edge"], lw=lw_e, zorder=17
        )

    # -----------------------------------------------------------------------
    # LAYER 7: Undisturbed Reference Datum Plane (z = 0)
    # -----------------------------------------------------------------------
    ax.plot(
        *proj([0, LX], [0, 0], [0, 0]),
        color=PALETTE["datum_line"], lw=1.1, ls=(0, (5, 3)), zorder=18
    )
    ax.plot(
        *proj([LX, LX], [0, LY], [0, 0]),
        color=PALETTE["datum_line"], lw=1.05, ls=(0, (5, 3)), zorder=18
    )

    xd_m, yd_m = proj(5.15, 0, 0)
    ax.text(
        xd_m, yd_m + 0.14,
        r"nível de referência $z = 0$",
        fontsize=8.8, fontstyle="italic", color=PALETTE["datum_line"],
        ha="center", va="bottom", rotation=-15.5, zorder=25
    ).set_path_effects([pe.withStroke(linewidth=2.8, foreground="#D5E7F2")])

    # -----------------------------------------------------------------------
    # LAYER 8: Wind Shear Stress (tau_x, tau_y) on the Free Surface
    # -----------------------------------------------------------------------
    xw, yw = 8.05, 4.10
    zw = free_surface_z(xw, yw) + 0.12
    tau_x_len = 1.35
    tau_y_len = 1.05

    for dy_s, dz_s in [(-0.40, 0.25), (0.0, 0.33), (0.40, 0.23)]:
        xs_line = np.linspace(xw - 0.95, xw + 1.40, 28)
        ys_line = (yw + dy_s) + 0.20 * (xs_line - xw)
        zs_line = free_surface_z(xs_line, ys_line) + dz_s
        ax.plot(
            *proj(xs_line[:-2], ys_line[:-2], zs_line[:-2]),
            color=PALETTE["wind_tau"], lw=0.65, ls="-", alpha=0.45, zorder=18
        )
        draw_3d_arrow(
            ax,
            (xs_line[-4], ys_line[-4], zs_line[-4]),
            (xs_line[-1], ys_line[-1], zs_line[-1]),
            color=PALETTE["wind_tau"], lw=0.65, mutation_scale=7,
            alpha=0.5, zorder=18
        )

    zw_x = free_surface_z(xw + tau_x_len, yw) + 0.12
    zw_y = free_surface_z(xw, yw + tau_y_len) + 0.12
    zw_xy = free_surface_z(xw + tau_x_len, yw + tau_y_len) + 0.12

    draw_3d_arrow(
        ax, (xw, yw, zw), (xw + tau_x_len, yw, zw_x),
        color=PALETTE["wind_tau"], lw=1.9, mutation_scale=12, zorder=19
    )
    draw_3d_arrow(
        ax, (xw, yw, zw), (xw, yw + tau_y_len, zw_y),
        color=PALETTE["wind_tau"], lw=1.9, mutation_scale=12, zorder=19
    )
    draw_3d_arrow(
        ax, (xw, yw, zw), (xw + tau_x_len, yw + tau_y_len, zw_xy),
        color="#184A4D", lw=1.3, mutation_scale=10, ls="-", alpha=0.88, zorder=19
    )
    ax.plot(
        *proj([xw + tau_x_len, xw + tau_x_len], [yw, yw + tau_y_len], [zw_x, zw_xy]),
        color=PALETTE["wind_tau"], lw=0.6, ls=":", alpha=0.65, zorder=18.5
    )
    ax.plot(
        *proj([xw, xw + tau_x_len], [yw + tau_y_len, yw + tau_y_len], [zw_y, zw_xy]),
        color=PALETTE["wind_tau"], lw=0.6, ls=":", alpha=0.65, zorder=18.5
    )

    xt_x, yt_x = proj(xw + tau_x_len + 0.12, yw - 0.10, zw_x)
    ttx = ax.text(
        xt_x, yt_x, r"$\tau_x$",
        fontsize=11.2, color=PALETTE["wind_tau"],
        ha="left", va="center", zorder=25
    )
    ttx.set_path_effects([pe.withStroke(linewidth=2.8, foreground="#E4F1F8")])

    xt_y, yt_y = proj(xw - 0.08, yw + tau_y_len + 0.14, zw_y)
    tty = ax.text(
        xt_y, yt_y, r"$\tau_y$",
        fontsize=11.2, color=PALETTE["wind_tau"],
        ha="right", va="bottom", zorder=25
    )
    tty.set_path_effects([pe.withStroke(linewidth=2.8, foreground="#E4F1F8")])

    xt_xy, yt_xy = proj(xw + tau_x_len + 0.10, yw + tau_y_len + 0.10, zw_xy)
    ttxy = ax.text(
        xt_xy, yt_xy, r"$\boldsymbol{\tau} = (\tau_x, \tau_y)^\top$",
        fontsize=9.6, color="#184A4D", ha="left", va="bottom", zorder=25
    )
    ttxy.set_path_effects([pe.withStroke(linewidth=2.8, foreground="#E4F1F8")])

    # -----------------------------------------------------------------------
    # LAYER 9: Gravity Vector g & Continuity Volume Flux (h+z)u, (h+z)v
    # -----------------------------------------------------------------------
    xg_v, yg_v, zg_v = 2.85, 4.30, 1.38
    draw_3d_arrow(
        ax, (xg_v, yg_v, zg_v), (xg_v, yg_v, zg_v - 0.90),
        color=PALETTE["ink_primary"], lw=1.75, mutation_scale=12, zorder=22
    )
    x_gl, y_gl = proj(xg_v + 0.16, yg_v, zg_v - 0.42)
    tg = ax.text(
        x_gl, y_gl,
        r"$\mathbf{g}$ (gravidade $g$)",
        fontsize=10.0, color=PALETTE["ink_primary"], ha="left", va="center", zorder=25
    )
    tg.set_path_effects([pe.withStroke(linewidth=3.0, foreground=PALETTE["bg_canvas"])])

    # Continuity Flux arrow exiting the front-right face (x = LX, y = 3.0)
    yf_flux = 3.00
    zf_flux = 0.50 * (free_surface_z(LX, yf_flux) + seabed_z(LX, yf_flux))
    draw_3d_arrow(
        ax, (LX - 0.25, yf_flux, zf_flux), (LX + 1.05, yf_flux, zf_flux),
        color="#235170", lw=1.65, mutation_scale=11.5, zorder=20
    )
    xfl_t, yfl_t = proj(LX + 0.55, yf_flux, zf_flux + 0.22)
    t_flux = ax.text(
        xfl_t, yfl_t,
        r"$(h+z)u$",
        fontsize=10.2, color="#1D3557", ha="center", va="bottom", zorder=25
    )
    t_flux.set_path_effects([pe.withStroke(linewidth=2.8, foreground=PALETTE["bg_canvas"])])

    # -----------------------------------------------------------------------
    # LAYER 10: 3D Visualization Coordinate Axes (x, y, z) anchored at (0, 0, 0)
    # -----------------------------------------------------------------------
    draw_3d_arrow(
        ax, (0, 0, 0), (0, 0, 1.70),
        color=PALETTE["ink_primary"], lw=1.35, mutation_scale=11.5, zorder=22
    )
    xz_a, yz_a = proj(0, 0, 1.80)
    ax.text(
        xz_a, yz_a, r"$z$",
        fontsize=12.5, color=PALETTE["ink_primary"], ha="center", va="bottom", zorder=25
    )

    draw_3d_arrow(
        ax, (LX, 0, 0), (LX + 1.35, 0, 0),
        color=PALETTE["ink_primary"], lw=1.35, mutation_scale=11.5, zorder=22
    )
    xx_a, yx_a = proj(LX + 1.48, 0, 0)
    ax.text(
        xx_a, yx_a, r"$x$",
        fontsize=12.5, color=PALETTE["ink_primary"], ha="left", va="center", zorder=25
    )

    draw_3d_arrow(
        ax, (0, LY, 0), (0, LY + 1.25, 0),
        color=PALETTE["ink_primary"], lw=1.35, mutation_scale=11.5, zorder=22
    )
    xy_a, yy_a = proj(0, LY + 1.36, 0)
    ax.text(
        xy_a, yy_a, r"$y$",
        fontsize=12.5, color=PALETTE["ink_primary"], ha="left", va="bottom", zorder=25
    )

    xo_0, yo_0 = proj(0, 0, 0)
    ax.plot(xo_0, yo_0, marker="o", markersize=4.2, color=PALETTE["ink_primary"], zorder=23)
    ax.text(
        xo_0 - 0.12, yo_0 - 0.06,
        r"$z = 0$",
        fontsize=9.6, color=PALETTE["datum_line"], ha="right", va="top", zorder=25
    ).set_path_effects([pe.withStroke(linewidth=2.8, foreground=PALETTE["bg_canvas"])])

    # -----------------------------------------------------------------------
    # LAYER 11: Precision Dimension Callouts: z(x,y,t), h(x,y), H(x,y,t), and L
    # -----------------------------------------------------------------------
    # 11A. Free-surface elevation z(x,y,t) > 0 at wave crest on front-left face
    x_crest = 1.42
    z_crest = free_surface_z(x_crest, 0)
    draw_3d_arrow(
        ax, (x_crest, 0, 0.0), (x_crest, 0, z_crest),
        color="#18435A", lw=1.05, mutation_scale=8.5, arrowstyle="<|-|>", zorder=24
    )
    x_zl, y_zl = proj(x_crest + 0.14, 0, 0.36 * z_crest)
    tz_lbl = ax.text(
        x_zl, y_zl, r"$z(x,y,t)$",
        fontsize=10.4, color="#18435A", ha="left", va="center", zorder=25
    )
    tz_lbl.set_path_effects([pe.withStroke(linewidth=3.0, foreground="#D5E7F2")])

    # 11B. Undisturbed water depth h(x,y) from z = 0 down to seabed z = -h(x,y)
    x_depth_dim = 2.10
    z_bed_dim = seabed_z(x_depth_dim, 0)
    draw_3d_arrow(
        ax, (x_depth_dim, 0, z_bed_dim), (x_depth_dim, 0, 0.0),
        color="#18435A", lw=1.05, mutation_scale=8.5, arrowstyle="<|-|>", zorder=24
    )
    x_hl, y_hl = proj(x_depth_dim + 0.16, 0, 0.50 * z_bed_dim)
    th_lbl = ax.text(
        x_hl, y_hl, r"$h(x,y)$",
        fontsize=10.8, color="#18435A", ha="left", va="center", zorder=25
    )
    th_lbl.set_path_effects([pe.withStroke(linewidth=3.0, foreground="#D5E7F2")])

    # 11C. Total water column depth H(x,y,t) = h(x,y) + z(x,y,t) at left corner (0, 0)
    x0_top, y0_top = proj(0, 0, free_surface_z(0, 0))
    x0_bot, y0_bot = proj(0, 0, seabed_z(0, 0))
    dx_H = -0.65
    ax.plot([x0_top, x0_top + dx_H * 1.18], [y0_top, y0_top], color=PALETTE["ink_primary"], lw=0.55, alpha=0.65, zorder=23)
    ax.plot([x0_bot, x0_bot + dx_H * 1.18], [y0_bot, y0_bot], color=PALETTE["ink_primary"], lw=0.55, alpha=0.65, zorder=23)
    draw_2d_arrow(
        ax, (x0_bot + dx_H, y0_bot), (x0_top + dx_H, y0_top),
        color=PALETTE["ink_primary"], lw=1.05, mutation_scale=8.5, arrowstyle="<|-|>", zorder=24
    )
    y_mid_H = 0.5 * (y0_top + y0_bot)
    ax.text(
        x0_bot + dx_H - 0.18, y_mid_H + 0.12,
        r"$H(x,y,t) = h(x,y) + z(x,y,t)$",
        fontsize=10.4, color=PALETTE["ink_primary"], ha="right", va="bottom", zorder=25
    )
    ax.text(
        x0_bot + dx_H - 0.18, y_mid_H - 0.04,
        "Profundidade total da coluna d'água",
        fontsize=8.8, fontstyle="italic", color=PALETTE["ink_secondary"],
        ha="right", va="top", zorder=25
    )

    # 11D. Characteristic Horizontal Length Scale L along front-left base edge
    xL_0, yL_0 = proj(0, 0, Z_BASE)
    xL_1, yL_1 = proj(LX, 0, Z_BASE)
    off_x, off_y = -0.16, -0.52
    ax.plot([xL_0, xL_0 + off_x * 1.2], [yL_0, yL_0 + off_y * 1.2], color=PALETTE["ink_primary"], lw=0.55, alpha=0.65, zorder=23)
    ax.plot([xL_1, xL_1 + off_x * 1.2], [yL_1, yL_1 + off_y * 1.2], color=PALETTE["ink_primary"], lw=0.55, alpha=0.65, zorder=23)
    qL_0 = (xL_0 + off_x, yL_0 + off_y)
    qL_1 = (xL_1 + off_x, yL_1 + off_y)
    draw_2d_arrow(
        ax, qL_0, qL_1,
        color=PALETTE["ink_primary"], lw=1.0, mutation_scale=8.5, arrowstyle="<|-|>", zorder=24
    )
    xL_m = 0.5 * (qL_0[0] + qL_1[0]) - 0.12
    yL_m = 0.5 * (qL_0[1] + qL_1[1]) - 0.24
    ax.text(
        xL_m, yL_m,
        r"Escala horizontal característica $L \gg H \quad \left(\frac{H}{L} \ll 1\right)$",
        fontsize=10.2, color=PALETTE["ink_primary"],
        ha="center", va="top", rotation=-15.5, zorder=25
    )

    # Direct seabed geological stratum label on the front-left rock block
    xb_str, yb_str = proj(4.8, 0, Z_BASE + 0.42)
    ax.text(
        xb_str, yb_str,
        r"Fundo do mar / leito impermeável   $z = -h(x,y)$",
        fontsize=9.2, fontstyle="italic", color="#473B30", ha="center", va="center",
        rotation=-15.5, zorder=25
    ).set_path_effects([pe.withStroke(linewidth=2.5, foreground=PALETTE["bed_front"])])

    # -----------------------------------------------------------------------
    # LAYER 12: Well-Spaced Edward Tufte Direct Callouts (Zero Overlaps)
    # -----------------------------------------------------------------------
    # Callout 1: Free surface z(x,y,t) (Upper-Left; leader starts below text block)
    add_callout_block(
        ax,
        target_2d=proj(2.3, 3.8, free_surface_z(2.3, 3.8)),
        box_pos_2d=(-0.45, 3.90),
        leader_start_2d=(1.40, 2.75),
        title_str=r"Superfície livre ondulante $z(x,y,t)$",
        lines_list=[
            "Elevação medida a partir do nível não perturbado ($z = 0$);",
            "perturbações propagam-se com velocidade real e finita",
            r"ao longo das curvas características ($c = \sqrt{gH}$)."
        ],
        align="left",
        rad=0.14,
        dot_color=PALETTE["water_edge"]
    )

    # Callout 2: Internal fluid column & depth-averaged velocity (u, v) (Upper-Center)
    add_callout_block(
        ax,
        target_2d=proj(xc, yc, z_ct),
        box_pos_2d=(5.25, 3.90),
        leader_start_2d=(5.65, 2.75),
        title_str=r"Velocidades médias na vertical $u(x,y,t)$ e $v(x,y,t)$",
        lines_list=[
            r"Componentes horizontais mediadas na coluna $H = h + z$,",
            r"governadas pelo gradiente barotrópico $-g\nabla z$,",
            r"atrito com o fundo $-\gamma\mathbf{u}$ e estresse do vento $\boldsymbol{\tau}$."
        ],
        align="left",
        rad=-0.12,
        dot_color=PALETTE["velocity_uv"]
    )

    # Callout 3: Wind stress tau_x, tau_y (Upper-Right of 3D block)
    add_callout_block(
        ax,
        target_2d=proj(xw + 0.60, yw + 0.50, zw + 0.08),
        box_pos_2d=(9.90, 2.85),
        leader_start_2d=(11.15, 2.02),
        title_str=r"Estresse do vento $(\tau_x, \tau_y)$",
        lines_list=[
            r"Termos de forçante superficial nas direções $x$ e $y$",
            "atuando tangencialmente sobre a superfície livre."
        ],
        align="left",
        rad=0.14,
        dot_color=PALETTE["wind_tau"]
    )

    # Callout 4: Bottom friction & Seabed bathymetry (Clean space below front-right face)
    add_callout_block(
        ax,
        target_2d=proj(xf - 0.55, yf - 0.30, zf),
        box_pos_2d=(10.65, -5.32),
        leader_start_2d=(10.50, -5.20),
        title_str=r"Atrito com o fundo $(\gamma, C_z)$",
        lines_list=[
            r"Resistência $-\gamma u$ e $-\gamma v$ imposta pelo leito,",
            r"com $\gamma = \frac{g\sqrt{u^2 + v^2}}{C_z^2\,H}$ (Chézy $C_z$)."
        ],
        align="left",
        rad=-0.14,
        dot_color=PALETTE["friction_gamma"]
    )

    # -----------------------------------------------------------------------
    # LAYER 13: Right-Hand Tufte Analytical Marginalia Column
    #           (2D Orthographic Cross-Section + Mathematical Synthesis)
    # -----------------------------------------------------------------------
    m_x0, m_x1 = 14.35, 20.45

    # --- Panel A: 2D Orthographic Vertical Section (Corte Vertical x-z) ---
    pa_y0, pa_y1 = 0.25, 4.35
    ax.add_patch(Rectangle(
        (m_x0, pa_y0), m_x1 - m_x0, pa_y1 - pa_y0,
        facecolor=PALETTE["bg_panel"], edgecolor="none", alpha=0.92, zorder=20
    ))
    ax.plot([m_x0, m_x1], [pa_y1, pa_y1], color=PALETTE["rule_dark"], lw=1.0, zorder=22)
    ax.plot([m_x0, m_x1], [pa_y0, pa_y0], color=PALETTE["rule_light"], lw=0.7, zorder=22)

    ax.text(
        m_x0 + 0.22, pa_y1 - 0.20,
        "Corte Vertical Ortográfico da Coluna d'Água — Plano $(x, z)$",
        fontsize=10.0, fontweight="bold", color=PALETTE["ink_primary"],
        ha="left", va="top", zorder=24
    )
    ax.text(
        m_x0 + 0.22, pa_y1 - 0.48,
        r"Integração vertical na profundidade total $H(x,y,t) = h(x,y) + z(x,y,t)$",
        fontsize=8.6, fontstyle="italic", color=PALETTE["ink_secondary"],
        ha="left", va="top", zorder=24
    )

    # Draw 2D schematic cross-section inside Panel A
    sx0, sx1 = m_x0 + 0.38, m_x1 - 0.52
    sy_datum = 2.58
    xs_2d = np.linspace(sx0, sx1, 120)
    xn_2d = (xs_2d - sx0) / (sx1 - sx0)
    ys_surf = sy_datum + 0.34 * np.sin(2 * np.pi * xn_2d + 0.3)
    ys_bed = sy_datum - 1.30 + 0.20 * np.sin(np.pi * xn_2d - 0.2)
    sy_base = pa_y0 + 0.28

    # 2D Water fill
    poly_2d_w = Polygon(
        list(zip(np.concatenate([xs_2d, xs_2d[::-1]]), np.concatenate([ys_surf, ys_bed[::-1]]))),
        facecolor="#B8D6E8", edgecolor="none", alpha=0.55, zorder=21
    )
    ax.add_patch(poly_2d_w)

    # 2D Bed fill
    poly_2d_b = Polygon(
        list(zip(np.concatenate([xs_2d, [sx1, sx0]]), np.concatenate([ys_bed, [sy_base, sy_base]]))),
        facecolor=PALETTE["bed_front"], edgecolor="none", alpha=0.88, zorder=21
    )
    ax.add_patch(poly_2d_b)

    # Surface, datum, and bed curves in 2D cross-section
    ax.plot(xs_2d, ys_surf, color=PALETTE["water_edge"], lw=1.35, zorder=23)
    ax.plot([sx0, sx1], [sy_datum, sy_datum], color=PALETTE["datum_line"], lw=0.95, ls=(0, (4, 2.5)), zorder=23)
    ax.plot(xs_2d, ys_bed, color=PALETTE["bed_edge"], lw=1.25, zorder=23)

    ax.text(sx1 + 0.06, sy_datum, r"$z=0$", fontsize=8.5, color=PALETTE["datum_line"], ha="left", va="center", zorder=24)

    # z(x,y,t) and h(x,y) dimension arrows at left wave crest (xn = 0.16)
    idx_c = 19
    xc_2d = xs_2d[idx_c]
    draw_2d_arrow(ax, (xc_2d, sy_datum), (xc_2d, ys_surf[idx_c]), color="#18435A", lw=0.9, mutation_scale=7, arrowstyle="<|-|>")
    ax.text(xc_2d + 0.08, 0.5 * (sy_datum + ys_surf[idx_c]), r"$z$", fontsize=9.5, color="#18435A", ha="left", va="center", zorder=24)

    draw_2d_arrow(ax, (xc_2d, ys_bed[idx_c]), (xc_2d, sy_datum), color="#18435A", lw=0.9, mutation_scale=7, arrowstyle="<|-|>")
    ax.text(xc_2d + 0.08, 0.5 * (sy_datum + ys_bed[idx_c]), r"$h$", fontsize=9.5, color="#18435A", ha="left", va="center", zorder=24)

    # Depth-averaged velocity block vs profile at center-left (xn = 0.42)
    idx_m = 50
    xm_2d = xs_2d[idx_m]
    yb_m, yt_m = ys_bed[idx_m], ys_surf[idx_m]
    u_bar_w = 0.66
    ax.add_patch(Rectangle(
        (xm_2d, yb_m), u_bar_w, yt_m - yb_m,
        facecolor="#113852", edgecolor="#113852", lw=0.7, ls=":", alpha=0.14, zorder=22
    ))
    ax.plot([xm_2d, xm_2d], [yb_m, yt_m], color=PALETTE["velocity_uv"], lw=0.85, zorder=23)
    draw_2d_arrow(
        ax, (xm_2d, 0.5 * (yb_m + yt_m)), (xm_2d + u_bar_w, 0.5 * (yb_m + yt_m)),
        color=PALETTE["velocity_uv"], lw=1.55, mutation_scale=9.5, zorder=24
    )
    ax.text(
        xm_2d + u_bar_w + 0.07, 0.5 * (yb_m + yt_m),
        r"$u, v$", fontsize=9.4, color=PALETTE["velocity_uv"], ha="left", va="center", zorder=24
    )

    # Wind stress arrow tau_x at top of 2D section
    draw_2d_arrow(
        ax, (xm_2d - 0.10, yt_m + 0.16), (xm_2d + 0.78, yt_m + 0.10),
        color=PALETTE["wind_tau"], lw=1.35, mutation_scale=8.5, zorder=24
    )
    ax.text(xm_2d + 0.35, yt_m + 0.22, r"$\tau_x, \tau_y$", fontsize=8.9, color=PALETTE["wind_tau"], ha="center", va="bottom", zorder=24)

    # Bottom friction arrow -gamma u at seabed of 2D section
    draw_2d_arrow(
        ax, (xm_2d + 0.55, yb_m - 0.11), (xm_2d - 0.30, yb_m - 0.14),
        color=PALETTE["friction_gamma"], lw=1.35, mutation_scale=8.5, zorder=24
    )
    ax.text(
        xm_2d + 0.15, yb_m - 0.22,
        r"$-\gamma u, -\gamma v \;\; (C_z)$",
        fontsize=8.7, color=PALETTE["friction_gamma"], ha="center", va="top", zorder=24
    )

    # Total depth H = h + z bracket on the right of 2D section (xn = 0.86)
    idx_r = 103
    xr_2d = xs_2d[idx_r]
    draw_2d_arrow(
        ax, (xr_2d, ys_bed[idx_r]), (xr_2d, ys_surf[idx_r]),
        color=PALETTE["ink_primary"], lw=0.95, mutation_scale=7.5, arrowstyle="<|-|>", zorder=24
    )
    ax.text(
        xr_2d - 0.08, 0.5 * (ys_bed[idx_r] + ys_surf[idx_r]),
        r"$H = h + z$", fontsize=9.1, color=PALETTE["ink_primary"], ha="right", va="center", zorder=24
    )

    # --- Panel B: Mathematical & Physical Synthesis (Casulli, 1990) ---
    pb_y0, pb_y1 = -5.78, -0.05
    ax.add_patch(Rectangle(
        (m_x0, pb_y0), m_x1 - m_x0, pb_y1 - pb_y0,
        facecolor=PALETTE["bg_panel"], edgecolor="none", alpha=0.92, zorder=20
    ))
    ax.plot([m_x0, m_x1], [pb_y1, pb_y1], color=PALETTE["rule_dark"], lw=1.0, zorder=22)
    ax.plot([m_x0, m_x1], [pb_y0, pb_y0], color=PALETTE["rule_dark"], lw=0.8, zorder=22)

    ax.text(
        m_x0 + 0.22, pb_y1 - 0.22,
        "Síntese da Formulação Física (Casulli, 1990)",
        fontsize=10.2, fontweight="bold", color=PALETTE["ink_primary"],
        ha="left", va="top", zorder=24
    )

    # Item 1
    ax.text(
        m_x0 + 0.24, pb_y1 - 0.62,
        "1. Hipótese de Águas Rasas e Equilíbrio Hidrostático:",
        fontsize=8.9, fontweight="bold", color=PALETTE["ink_secondary"],
        ha="left", va="top", zorder=24
    )
    ax.text(
        m_x0 + 0.38, pb_y1 - 0.96,
        r"$\dfrac{H}{L} \ll 1 \;\;\Longrightarrow\;\; \dfrac{\partial p}{\partial z} = -\rho g \;\;\Longrightarrow\;\; -\dfrac{1}{\rho}\nabla_H p = -g\nabla z$",
        fontsize=9.2, color=PALETTE["ink_primary"],
        ha="left", va="top", zorder=24
    )

    # Item 2 (two separate ax.text calls so fractions have generous vertical spacing)
    ax.text(
        m_x0 + 0.24, pb_y1 - 1.68,
        "2. Conservação da Quantidade de Movimento Horizontal:",
        fontsize=8.9, fontweight="bold", color=PALETTE["ink_secondary"],
        ha="left", va="top", zorder=24
    )
    ax.text(
        m_x0 + 0.38, pb_y1 - 2.02,
        r"$\dfrac{\partial u}{\partial t} + u\dfrac{\partial u}{\partial x} + v\dfrac{\partial u}{\partial y} = -g\dfrac{\partial z}{\partial x} - \gamma u + \tau_x$",
        fontsize=9.2, color=PALETTE["ink_primary"],
        ha="left", va="top", zorder=24
    )
    ax.text(
        m_x0 + 0.38, pb_y1 - 2.74,
        r"$\dfrac{\partial v}{\partial t} + u\dfrac{\partial v}{\partial x} + v\dfrac{\partial v}{\partial y} = -g\dfrac{\partial z}{\partial y} - \gamma v + \tau_y$",
        fontsize=9.2, color=PALETTE["ink_primary"],
        ha="left", va="top", zorder=24
    )

    # Item 3
    ax.text(
        m_x0 + 0.24, pb_y1 - 3.50,
        "3. Conservação de Massa Integrada na Vertical:",
        fontsize=8.9, fontweight="bold", color=PALETTE["ink_secondary"],
        ha="left", va="top", zorder=24
    )
    ax.text(
        m_x0 + 0.38, pb_y1 - 3.84,
        r"$\dfrac{\partial z}{\partial t} + \dfrac{\partial [(h+z)u]}{\partial x} + \dfrac{\partial [(h+z)v]}{\partial y} = 0$",
        fontsize=9.2, color=PALETTE["ink_primary"],
        ha="left", va="top", zorder=24
    )

    # Item 4
    ax.text(
        m_x0 + 0.24, pb_y1 - 4.58,
        "4. Coeficiente de Atrito com o Fundo (Fricção de Chézy):",
        fontsize=8.9, fontweight="bold", color=PALETTE["ink_secondary"],
        ha="left", va="top", zorder=24
    )
    ax.text(
        m_x0 + 0.38, pb_y1 - 5.06,
        r"$\gamma = \dfrac{g\sqrt{u^2 + v^2}}{C_z^2\,H}, \qquad H(x,y,t) = h(x,y) + z(x,y,t)$",
        fontsize=9.2, color=PALETTE["ink_primary"],
        ha="left", va="top", zorder=24
    )

    # -----------------------------------------------------------------------
    # LAYER 14: Tufte Bookplate Header (Top Margin)
    # -----------------------------------------------------------------------
    ax.text(
        -3.65, 5.38,
        "Domínio Físico, Escalas e Variáveis das Equações de Águas Rasas Bidimensionais (2D SWE)",
        fontsize=14.2, fontweight="bold", color=PALETTE["ink_primary"],
        ha="left", va="top", zorder=30
    )
    ax.text(
        -3.65, 4.92,
        r"Representação tridimensional de uma coluna fluida incompressível sob aproximação hidrostática ($H/L \ll 1$), superfície livre $z(x,y,t)$, batimetria $h(x,y)$ e velocidades médias $(u,v)$ — ref. Casulli (1990).",
        fontsize=10.0, fontstyle="italic", color=PALETTE["ink_secondary"],
        ha="left", va="top", zorder=30
    )
    ax.plot([-3.65, 20.45], [4.55, 4.55], color=PALETTE["rule_light"], lw=0.85, zorder=28)

    # Set clean bounds and remove default Matplotlib frame/ticks
    ax.set_xlim(-3.85, 20.65)
    ax.set_ylim(-6.35, 5.65)
    ax.set_aspect("equal")
    ax.axis("off")

    plt.tight_layout(pad=0.15)

    out_dir = Path(__file__).resolve().parent.parent / "figures"
    out_dir.mkdir(parents=True, exist_ok=True)

    svg_path = out_dir / "swe_physical_domain.svg"
    pdf_path = out_dir / "swe_physical_domain.pdf"
    png_path = out_dir / "swe_physical_domain.png"

    fig.savefig(svg_path, format="svg", bbox_inches="tight", facecolor=fig.get_facecolor())
    fig.savefig(pdf_path, format="pdf", bbox_inches="tight", facecolor=fig.get_facecolor())
    fig.savefig(png_path, format="png", dpi=300, bbox_inches="tight", facecolor=fig.get_facecolor())
    print(f"Saved: {svg_path}")
    print(f"Saved: {pdf_path}")
    print(f"Saved: {png_path}")


if __name__ == "__main__":
    build_figure()
