"""
Generate an Edward Tufte-inspired vector scientific illustration of the
3D Space-Time Characteristic Cone (x, y, t) for the 2D Shallow Water Equations
(2D SWE), following Casulli (1990).

Single elongated 3D horizontal cone layout:
  - Time axis t as the horizontal abscissa (left to right)
  - Spatial plane (x, y) oriented vertically at t = 0 on the left
  - Stacked vertical circular wave cross-sections expanding along t
  - Normal vector n = (r, s, q) perpendicular to the cone mantle, decomposed into
    its vertical spatial component (r, s) and horizontal temporal component q
  - Interior ("região alcançada pela perturbação") and Exterior ("informação ainda
    não chegou") clearly demarcated.

Outputs:
  - ../figures/swe_characteristic_cone.svg (vector SVG with embedded glyph paths)
  - ../figures/swe_characteristic_cone.pdf (vector PDF for LaTeX publication)
  - ../figures/swe_characteristic_cone.png (high-resolution raster preview)
"""

import glob
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.patches import Polygon, FancyArrowPatch
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
# 2. High-Contrast Typography & Edward Tufte Muted Cartographic Palette
# ---------------------------------------------------------------------------
PALETTE = {
    "bg_canvas": "#FCFBF7",       # Warm archival paper ivory
    "ink_primary": "#11161C",     # Deep, razor-sharp obsidian ink for titles & math
    "ink_secondary": "#222B35",   # Crisp dark charcoal for explanatory body text
    "ink_muted": "#687380",       # Clean slate gray for leader lines
    "plane_fill": "#E8F1F6",      # Vertical spatial water plane (t = 0)
    "plane_edge": "#6C8EA4",      # Spatial plane border
    "cone_edge": "#1E4966",       # Crisp cone boundary & wave rings
    "slice_fill": "#B5D6EA",      # Circular wave slices at t1, t2, t3, t4
    "normal_vec": "#8E321E",      # Deep Venetian terracotta for normal vector (r, s, q)
    "spatial_rs": "#145374",      # Deep cerulean for spatial component (r, s)
    "temporal_q": "#17575A",      # Deep sea-teal for temporal component q
    "advec_u": "#3D405B",         # Muted indigo-slate for advection u = (u, v)
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
            alpha=0.88,
        )
    t = ax.text(x, y, s, color=color, **kwargs)
    if stroke_w > 0:
        t.set_path_effects([pe.withStroke(linewidth=stroke_w, foreground=color)])
    return t


def draw_2d_arrow(
    ax, p0, p1, color, lw=1.35, mutation_scale=11.5, arrowstyle="-|>",
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
        fontsize=10.5, fontweight="bold",
        ha=align, va="bottom", zorder=zorder + 1
    )

    crisp_text(
        ax, bx, by - 0.10, "\n".join(lines),
        color=PALETTE["ink_secondary"], stroke_w=0.14,
        fontsize=9.3, ha=align, va="top",
        linespacing=1.35, zorder=zorder + 1
    )


# ---------------------------------------------------------------------------
# 3. 3D Space-Time Projection with Horizontal Time Abscissa t
#    and Vertical Spatial Plane (x, y)
# ---------------------------------------------------------------------------
# t-axis: horizontal abscissa (pointing right along +X)
ET = np.array([1.00, 0.00])
# y-axis: vertical ordinate of the spatial plane (pointing straight up along +Y)
EY = np.array([0.00, 1.00])
# x-axis: depth axis of the vertical spatial plane (pointing down-left in 3D axonometric perspective)
angle_x_persp = np.deg2rad(-147.0)  # Down-left (-X, -Y)
scale_x_persp = 0.56
EX = np.array([scale_x_persp * np.cos(angle_x_persp), scale_x_persp * np.sin(angle_x_persp)])


def proj_xyt(x, y, t, orig=(0.0, 0.0)):
    """Project 3D space-time coordinates (x, y, t) to 2D canvas coordinates (X, Y)."""
    x_a = np.asarray(x)
    y_a = np.asarray(y)
    t_a = np.asarray(t)
    X = orig[0] + x_a * EX[0] + y_a * EY[0] + t_a * ET[0]
    Y = orig[1] + x_a * EX[1] + y_a * EY[1] + t_a * ET[1]
    return X, Y


def draw_xyt_arrow(
    ax, p0, p1, orig, color, lw=1.4, mutation_scale=11.5,
    arrowstyle="-|>", zorder=20, ls="-", alpha=1.0
):
    x0, y0 = proj_xyt(*p0, orig=orig)
    x1, y1 = proj_xyt(*p1, orig=orig)
    return draw_2d_arrow(
        ax, (x0, y0), (x1, y1), color=color, lw=lw,
        mutation_scale=mutation_scale, arrowstyle=arrowstyle,
        zorder=zorder, ls=ls, alpha=alpha
    )


def build_figure():
    fig, ax = plt.subplots(figsize=(13.8, 6.8), dpi=300)
    fig.patch.set_facecolor(PALETTE["bg_canvas"])
    ax.set_facecolor(PALETTE["bg_canvas"])

    # Origin (x=0, y=0, t=0) on the left of the canvas
    orig_3d = (-3.35, -0.10)

    # Elongated cone parameters along the horizontal t-axis
    T_MAX = 9.40
    c_wave = 0.285             # Wave celerity c = sqrt(gH) (controls cone opening dR/dt)
    u_adv, v_adv = -0.02, 0.032 # Gentle advective tilt (u, v) of the cone axis
    t_levels = [2.15, 4.45, 6.75, 9.05]
    t_labels = [r"$t_1$", r"$t_2$", r"$t_3$", r"$t_4$"]

    # Compute exact 2D top & bottom silhouette tangent angles of the horizontal 3D cone
    th_dense = np.linspace(0, 2 * np.pi, 2400)
    X_unit, Y_unit = proj_xyt(
        u_adv + c_wave * np.cos(th_dense),
        v_adv + c_wave * np.sin(th_dense),
        np.ones_like(th_dense),
        orig=(0.0, 0.0)
    )
    # Angle relative to the horizontal (+X) axis: atan2(Y_unit, X_unit)
    cone_2d_ang = np.arctan2(Y_unit, X_unit)
    th_sil_top = th_dense[np.argmax(cone_2d_ang)]  # True 2D upper silhouette tangent
    th_sil_bot = th_dense[np.argmin(cone_2d_ang)]  # True 2D lower silhouette tangent

    # Also find the lowest point on a vertical circular cross-section (minimum Y)
    Y_circ_only = c_wave * (EX[1] * np.cos(th_dense) + EY[1] * np.sin(th_dense))
    th_min_Y = th_dense[np.argmin(Y_circ_only)]
    th_max_Y = th_dense[np.argmax(Y_circ_only)]

    # -----------------------------------------------------------------------
    # 1. Vertical Spatial Water Plane (x, y) at t = 0 (on the Left)
    # -----------------------------------------------------------------------
    Lp = 2.85
    plane_corners = [
        proj_xyt(-Lp, -Lp, 0, orig_3d),
        proj_xyt(Lp, -Lp, 0, orig_3d),
        proj_xyt(Lp, Lp, 0, orig_3d),
        proj_xyt(-Lp, Lp, 0, orig_3d),
    ]
    ax.add_patch(Polygon(
        plane_corners, facecolor=PALETTE["plane_fill"],
        edgecolor=PALETTE["plane_edge"], lw=1.0, alpha=0.74, zorder=2
    ))

    # Subtle spatial grid lines on the vertical plane t = 0
    for g_val in np.linspace(-2.1, 2.1, 7):
        ax.plot(
            *proj_xyt([g_val, g_val], [-Lp, Lp], [0, 0], orig_3d),
            color="#B8CEDC", lw=0.45, alpha=0.55, zorder=2.5
        )
        ax.plot(
            *proj_xyt([-Lp, Lp], [g_val, g_val], [0, 0], orig_3d),
            color="#B8CEDC", lw=0.45, alpha=0.55, zorder=2.5
        )

    # Projected concentric circular wave rings on the vertical spatial plane (t = 0)
    theta = np.linspace(0, 2 * np.pi, 180)
    for t_lv in t_levels[:3]:
        r_lv = c_wave * t_lv
        xc_lv = r_lv * np.cos(theta)
        yc_lv = r_lv * np.sin(theta)
        ax.plot(
            *proj_xyt(xc_lv, yc_lv, np.zeros_like(theta), orig_3d),
            color=PALETTE["cone_edge"], lw=0.70, ls=":", alpha=0.50, zorder=3
        )

    # Label on the bottom edge of the vertical spatial plane (t = 0)
    p_plane_bot = proj_xyt(0.0, -Lp, 0, orig_3d)
    crisp_text(
        ax, p_plane_bot[0] - 0.15, p_plane_bot[1] - 0.35,
        r"Plano espacial vertical $(x, y)$ em $t = 0$" + "\n"
        + r"(projeção dos círculos concêntricos)",
        color=PALETTE["ink_secondary"], stroke_w=0.14,
        fontsize=9.1, fontstyle="italic", ha="center", va="top",
        linespacing=1.30, zorder=20
    )

    # -----------------------------------------------------------------------
    # 2. 3D Space-Time Axes: Vertical (x, y) and Horizontal Abscissa t
    # -----------------------------------------------------------------------
    # Dashed negative x and y axes on the t = 0 plane
    ax.plot(*proj_xyt([-Lp, 0], [0, 0], [0, 0], orig_3d), color=PALETTE["ink_muted"], lw=0.8, ls="--", zorder=4)
    ax.plot(*proj_xyt([0, 0], [-Lp, 0], [0, 0], orig_3d), color=PALETTE["ink_muted"], lw=0.8, ls="--", zorder=4)

    # Positive y-axis (pointing straight up)
    draw_xyt_arrow(ax, (0, 0, 0), (0, Lp + 0.65, 0), orig_3d, color=PALETTE["ink_primary"], lw=1.40, mutation_scale=11.5, zorder=18)
    py_ax = proj_xyt(0, Lp + 0.78, 0, orig_3d)
    crisp_text(ax, py_ax[0], py_ax[1], r"$y$", color=PALETTE["ink_primary"], stroke_w=0.20, fontsize=12.6, ha="center", va="bottom", zorder=25)

    # Positive x-axis (pointing down-left in 3D perspective)
    draw_xyt_arrow(ax, (0, 0, 0), (Lp + 0.75, 0, 0), orig_3d, color=PALETTE["ink_primary"], lw=1.40, mutation_scale=11.5, zorder=18)
    px_ax = proj_xyt(Lp + 0.92, 0, 0, orig_3d)
    crisp_text(ax, px_ax[0] - 0.05, px_ax[1] - 0.04, r"$x$", color=PALETTE["ink_primary"], stroke_w=0.20, fontsize=12.6, ha="right", va="top", zorder=25)

    # Horizontal time axis t (abscissa, running from left to right through the cone)
    ax.plot(*proj_xyt([0, 0], [0, 0], [0, T_MAX], orig_3d), color=PALETTE["ink_primary"], lw=1.05, ls="-.", alpha=0.68, zorder=11)
    draw_xyt_arrow(ax, (0, 0, T_MAX), (0, 0, T_MAX + 1.45), orig_3d, color=PALETTE["ink_primary"], lw=1.45, mutation_scale=12, zorder=22)
    pt_ax = proj_xyt(0, 0, T_MAX + 1.58, orig_3d)
    crisp_text(
        ax, pt_ax[0], pt_ax[1], r"$t$ (tempo)",
        color=PALETTE["ink_primary"], stroke_w=0.20,
        fontsize=12.2, ha="left", va="center", zorder=25
    )

    # Advective centerline trajectory (u*t, v*t, t)
    ax.plot(
        *proj_xyt([0, u_adv * T_MAX], [0, v_adv * T_MAX], [0, T_MAX], orig_3d),
        color=PALETTE["advec_u"], lw=1.20, ls="--", alpha=0.88, zorder=12
    )
    draw_xyt_arrow(
        ax, (u_adv * T_MAX, v_adv * T_MAX, T_MAX),
        (u_adv * (T_MAX + 1.15), v_adv * (T_MAX + 1.15), T_MAX + 1.15),
        orig_3d, color=PALETTE["advec_u"], lw=1.30, mutation_scale=10.5, zorder=22
    )
    p_adv_lbl = proj_xyt(u_adv * (T_MAX + 1.22), v_adv * (T_MAX + 1.22) + 0.14, T_MAX + 1.15, orig_3d)
    crisp_text(
        ax, p_adv_lbl[0] + 0.05, p_adv_lbl[1],
        r"Eixo advectivo $\vec{u} = (u, v)$",
        color=PALETTE["advec_u"], stroke_w=0.16,
        fontsize=9.5, fontstyle="italic", ha="left", va="bottom", zorder=25
    )

    # -----------------------------------------------------------------------
    # 3. Shaded 3D Elongated Horizontal Cone Mantle (t from 0 to T_MAX)
    #    Warm Golden-Amber / Ochre Space-Time Palette (contrasting with blue water slices)
    # -----------------------------------------------------------------------
    n_t, n_th = 36, 72
    t_grid = np.linspace(0, T_MAX, n_t)
    th_grid = np.linspace(0, 2 * np.pi, n_th)
    cone_cmap = LinearSegmentedColormap.from_list(
        "tufte_spacetime_amber", ["#B89768", "#DEC69E", "#F5EBDC"]
    )
    cone_mantle_edge = "#6B5233"  # Warm sepia-umber for temporal cone generator rays

    for i in range(n_t - 1):
        t0_c, t1_c = t_grid[i], t_grid[i + 1]
        r0_c, r1_c = c_wave * t0_c, c_wave * t1_c
        for j in range(n_th - 1):
            th0, th1 = th_grid[j], th_grid[j + 1]
            xs_f = [
                u_adv * t0_c + r0_c * np.cos(th0),
                u_adv * t0_c + r0_c * np.cos(th1),
                u_adv * t1_c + r1_c * np.cos(th1),
                u_adv * t1_c + r1_c * np.cos(th0),
            ]
            ys_f = [
                v_adv * t0_c + r0_c * np.sin(th0),
                v_adv * t0_c + r0_c * np.sin(th1),
                v_adv * t1_c + r1_c * np.sin(th1),
                v_adv * t1_c + r1_c * np.sin(th0),
            ]
            ts_f = [t0_c, t0_c, t1_c, t1_c]
            X2, Y2 = proj_xyt(xs_f, ys_f, ts_f, orig_3d)
            th_mid = 0.5 * (th0 + th1)
            # Directional illumination from top-front (theta near +pi/2)
            light = 0.52 + 0.44 * np.sin(th_mid + 0.25)
            col = cone_cmap(np.clip(light, 0.05, 0.96))
            # Front half (x > 0, cos(th_mid) > 0) vs back half
            is_front = np.cos(th_mid) > -0.15
            z_ord = 13 if is_front else 6
            f_alpha = 0.30 if is_front else 0.22
            ax.add_patch(Polygon(
                list(zip(X2, Y2)), facecolor=col, edgecolor="none",
                alpha=f_alpha, zorder=z_ord
            ))

    # -----------------------------------------------------------------------
    # 4. Stacked Vertical Circular Wave Cross-Sections at t1, t2, t3, t4
    #    Each circle has the exact same proportional (x, y) Cartesian grid
    #    as the t = 0 origin plane, clipped analytically inside the circle!
    # -----------------------------------------------------------------------
    grid_step = 0.70  # Exact same grid spacing as np.linspace(-2.1, 2.1, 7) on t=0 plane
    grid_lines_vals = np.arange(-3.5, 3.51, grid_step)

    for idx_lv, (t_lv, lbl_lv) in enumerate(zip(t_levels, t_labels)):
        r_lv = c_wave * t_lv
        cx_lv = u_adv * t_lv
        cy_lv = v_adv * t_lv
        xc_lv = cx_lv + r_lv * np.cos(theta)
        yc_lv = cy_lv + r_lv * np.sin(theta)
        tc_lv = np.full_like(theta, t_lv)
        X_sl, Y_sl = proj_xyt(xc_lv, yc_lv, tc_lv, orig_3d)

        # Translucent blue water spatial disc at time t_lv
        ax.add_patch(Polygon(
            list(zip(X_sl, Y_sl)),
            facecolor=PALETTE["slice_fill"], edgecolor="none",
            alpha=0.34, zorder=9 + idx_lv * 0.5
        ))

        # Proportional (x, y) Cartesian grid clipped strictly inside the circle of radius r_lv
        for gv in grid_lines_vals:
            # 1) Grid line x = gv (vertical in y, clipped to circle (x - cx_lv)^2 + (y - cy_lv)^2 <= r_lv^2)
            dx_g = gv - cx_lv
            if abs(dx_g) < r_lv - 1e-6:
                half_y = np.sqrt(r_lv ** 2 - dx_g ** 2)
                y_g0, y_g1 = cy_lv - half_y, cy_lv + half_y
                ax.plot(
                    *proj_xyt([gv, gv], [y_g0, y_g1], [t_lv, t_lv], orig_3d),
                    color="#7FA6C0", lw=0.52, alpha=0.68, zorder=9.15 + idx_lv * 0.5
                )
            # 2) Grid line y = gv (horizontal in x, clipped to circle)
            dy_g = gv - cy_lv
            if abs(dy_g) < r_lv - 1e-6:
                half_x = np.sqrt(r_lv ** 2 - dy_g ** 2)
                x_g0, x_g1 = cx_lv - half_x, cx_lv + half_x
                ax.plot(
                    *proj_xyt([x_g0, x_g1], [gv, gv], [t_lv, t_lv], orig_3d),
                    color="#7FA6C0", lw=0.52, alpha=0.68, zorder=9.15 + idx_lv * 0.5
                )

        # Inner concentric ripple rings inside each vertical circular cross-section
        for r_frac in [0.42, 0.72]:
            xr_i = cx_lv + (r_frac * r_lv) * np.cos(theta)
            yr_i = cy_lv + (r_frac * r_lv) * np.sin(theta)
            ax.plot(
                *proj_xyt(xr_i, yr_i, tc_lv, orig_3d),
                color=PALETTE["cone_edge"], lw=0.45, ls=":", alpha=0.42, zorder=9.25 + idx_lv * 0.5
            )

        # Outer circumference of the wave circle at t_lv
        ax.plot(
            X_sl, Y_sl,
            color=PALETTE["cone_edge"], lw=1.35, alpha=0.92, zorder=14
        )

        # Radial wave celerity vector (measured from the advective centerline!) inside the 3rd & 4th slices
        if idx_lv in (2, 3):
            p_cent = proj_xyt(cx_lv, cy_lv, t_lv, orig_3d)
            p_rim_bot = proj_xyt(
                cx_lv + r_lv * np.cos(th_min_Y),
                cy_lv + r_lv * np.sin(th_min_Y),
                t_lv, orig_3d
            )
            ax.plot(p_cent[0], p_cent[1], marker="o", markersize=3.2, color=PALETTE["cone_edge"], zorder=15)
            draw_2d_arrow(
                ax, p_cent, p_rim_bot,
                color=PALETTE["cone_edge"], lw=1.05, mutation_scale=8.5, ls="--", alpha=0.85, zorder=15
            )
            crisp_text(
                ax, 0.5 * (p_cent[0] + p_rim_bot[0]) + 0.14, 0.5 * (p_cent[1] + p_rim_bot[1]),
                f"$c\\,{lbl_lv[1:-1]}$",
                color=PALETTE["cone_edge"], stroke_w=0.16, bg_pill="#DCEBF5",
                fontsize=8.9, ha="left", va="center", zorder=22
            )

        # Time level label placed cleanly below the lowest point of each vertical circle
        p_bot_lv = proj_xyt(
            cx_lv + r_lv * np.cos(th_min_Y),
            cy_lv + r_lv * np.sin(th_min_Y),
            t_lv, orig_3d
        )
        # Small vertical tick mark connecting circle bottom to time label
        ax.plot(
            [p_bot_lv[0], p_bot_lv[0]], [p_bot_lv[1], p_bot_lv[1] - 0.16],
            color=PALETTE["cone_edge"], lw=0.70, ls=":", alpha=0.75, zorder=15
        )
        crisp_text(
            ax, p_bot_lv[0], p_bot_lv[1] - 0.20,
            f"{lbl_lv}\n($\\mathrm{{raio}} = c\\,{lbl_lv[1:-1]}$)",
            color=PALETTE["cone_edge"], stroke_w=0.16,
            fontsize=9.2, ha="center", va="top", linespacing=1.25, zorder=25
        )

    # Open right mouth of the temporal cone at t = T_MAX
    r_top = c_wave * T_MAX
    xc_top = u_adv * T_MAX + r_top * np.cos(theta)
    yc_top = v_adv * T_MAX + r_top * np.sin(theta)
    tc_top = np.full_like(theta, T_MAX)
    X_top, Y_top = proj_xyt(xc_top, yc_top, tc_top, orig_3d)
    ax.add_patch(Polygon(
        list(zip(X_top, Y_top)),
        facecolor="#F2E6D4", edgecolor=cone_mantle_edge,
        lw=1.40, alpha=0.26, zorder=14.5
    ))

    # Exact outer 2D silhouette generator rays (th_sil_top and th_sil_bot) + internal characteristic ribs
    for th_ray, lw_r, al_r in [
        (th_sil_top, 1.80, 0.95),
        (th_sil_bot, 1.80, 0.95),
        (0.0, 0.72, 0.50),
        (np.pi, 0.60, 0.35),
    ]:
        x_ray = u_adv * T_MAX + r_top * np.cos(th_ray)
        y_ray = v_adv * T_MAX + r_top * np.sin(th_ray)
        ax.plot(
            *proj_xyt([0, x_ray], [0, y_ray], [0, T_MAX], orig_3d),
            color=cone_mantle_edge, lw=lw_r, alpha=al_r, zorder=15
        )

    # Origin Perturbation Point (0, 0, 0)
    p_orig = proj_xyt(0, 0, 0, orig_3d)
    ax.plot(p_orig[0], p_orig[1], marker="o", markersize=6.0, color=PALETTE["normal_vec"], zorder=25)
    ax.plot(p_orig[0], p_orig[1], marker="o", markersize=9.8, markerfacecolor="none", markeredgecolor=PALETTE["normal_vec"], lw=1.15, zorder=24)

    # -----------------------------------------------------------------------
    # 5. Normal Vector (r, s, q) Perpendicular to the Top Silhouette Ray
    # -----------------------------------------------------------------------
    th_n = th_sil_top
    t_n = 4.95
    r_n = c_wave * t_n
    px_n = u_adv * t_n + r_n * np.cos(th_n)
    py_n = v_adv * t_n + r_n * np.sin(th_n)
    pt_n = t_n

    P0_2d = np.array(proj_xyt(0, 0, 0, orig_3d))
    P1_2d = np.array(proj_xyt(u_adv * T_MAX + r_top * np.cos(th_n), v_adv * T_MAX + r_top * np.sin(th_n), T_MAX, orig_3d))
    P_2d = np.array(proj_xyt(px_n, py_n, pt_n, orig_3d))

    ray_dir = P1_2d - P0_2d
    ray_unit = ray_dir / np.linalg.norm(ray_dir)
    # Outward normal to the top silhouette ray (pointing up-left: (-ray_unit[1], +ray_unit[0]))
    norm_unit_2d = np.array([-ray_unit[1], ray_unit[0]])
    n_len = 1.68

    N_tip_2d = P_2d + n_len * norm_unit_2d
    # Orthogonal decomposition of (r, s, q):
    # - Spatial component (r, s) points vertically (parallel to the vertical (x,y) plane!)
    # - Temporal component q points horizontally (parallel to the horizontal time abscissa t!)
    RS_tip_2d = np.array([P_2d[0], N_tip_2d[1]])
    Q_tip_2d = np.array([N_tip_2d[0], P_2d[1]])

    # Soft shaded interior of the decomposition rectangle so the vector sum is immediately visible
    ax.add_patch(Polygon(
        [tuple(P_2d), tuple(Q_tip_2d), tuple(N_tip_2d), tuple(RS_tip_2d)],
        facecolor="#F3ECE3", edgecolor="none", alpha=0.65, zorder=20.5
    ))

    # Right-Angle Perpendicularity Symbol (perp) between the cone silhouette ray and Normal Vector (r, s, q)
    sq_sz = 0.22
    sq_p1 = P_2d + sq_sz * ray_unit
    sq_p2 = sq_p1 + sq_sz * norm_unit_2d
    sq_p3 = P_2d + sq_sz * norm_unit_2d
    ax.plot(
        [sq_p1[0], sq_p2[0], sq_p3[0]],
        [sq_p1[1], sq_p2[1], sq_p3[1]],
        color=PALETTE["normal_vec"], lw=1.10, zorder=22
    )

    ax.plot(P_2d[0], P_2d[1], marker="o", markersize=4.6, color=PALETTE["normal_vec"], zorder=25)

    # Crisp dashed lines closing the rectangle between the tip of n and its components (r, s) and q
    ax.plot(
        [RS_tip_2d[0], N_tip_2d[0]], [RS_tip_2d[1], N_tip_2d[1]],
        color="#334155", lw=1.20, ls=(0, (4, 2.2)), alpha=0.92, zorder=22.5
    )
    ax.plot(
        [Q_tip_2d[0], N_tip_2d[0]], [Q_tip_2d[1], N_tip_2d[1]],
        color="#334155", lw=1.20, ls=(0, (4, 2.2)), alpha=0.92, zorder=22.5
    )

    # Spatial component arrow (r, s) — pointing vertically along (x, y)
    draw_2d_arrow(
        ax, tuple(P_2d), tuple(RS_tip_2d),
        color=PALETTE["spatial_rs"], lw=2.0, mutation_scale=12, zorder=23
    )
    crisp_text(
        ax, RS_tip_2d[0] + 0.14, RS_tip_2d[1],
        r"$(r, s)$ — direção espacial $(x, y)$",
        color=PALETTE["spatial_rs"], stroke_w=0.18,
        fontsize=9.6, ha="left", va="center", zorder=26
    )

    # Temporal component arrow q — pointing horizontally along t
    draw_2d_arrow(
        ax, tuple(P_2d), tuple(Q_tip_2d),
        color=PALETTE["temporal_q"], lw=2.0, mutation_scale=12, zorder=23
    )
    crisp_text(
        ax, Q_tip_2d[0] - 0.10, Q_tip_2d[1] + 0.04,
        r"$q$ — direção temporal $t$",
        color=PALETTE["temporal_q"], stroke_w=0.18, bg_pill=PALETTE["bg_canvas"],
        fontsize=9.4, ha="right", va="center", zorder=26
    )

    # Resultant Normal Vector (r, s, q)
    draw_2d_arrow(
        ax, tuple(P_2d), tuple(N_tip_2d),
        color=PALETTE["normal_vec"], lw=2.5, mutation_scale=14.5, zorder=24
    )
    crisp_text(
        ax, N_tip_2d[0] - 0.10, N_tip_2d[1] + 0.10,
        r"Vetor normal $\vec{n} = (r, s, q)$" + "\n"
        + r"(perpendicular à superfície do cone)",
        color=PALETTE["normal_vec"], stroke_w=0.18,
        fontsize=9.8, fontweight="bold", ha="right", va="bottom", zorder=26
    )

    # -----------------------------------------------------------------------
    # 6. Interior vs. Exterior Regions & Explanatory Callouts
    # -----------------------------------------------------------------------
    # Interior of the cone label (inside the wide right part of the cone between t3 and t4)
    p_int = proj_xyt(u_adv * 7.85, v_adv * 7.85 + 0.98, 7.85, orig_3d)
    crisp_text(
        ax, p_int[0], p_int[1],
        "Interior do cone:\nregião alcançada pela perturbação\n" + r"($\mathrm{raio} \leq c\,t$, com $c = \sqrt{gH}$)",
        color="#4E3A21", stroke_w=0.15, bg_pill="#F5ECE0",
        fontsize=9.0, fontstyle="italic", ha="center", va="center",
        linespacing=1.30, zorder=25
    )

    # Exterior of the cone label (requested by user from the 2D view, placed cleanly in the 3D view!)
    crisp_text(
        ax, 1.05, -2.72,
        "Exterior do cone:\nregião onde a informação da perturbação ainda não chegou ($\\mathrm{raio} > c\\,t$)",
        color=PALETTE["ink_muted"], stroke_w=0.14,
        fontsize=9.4, fontstyle="italic", ha="center", va="top",
        linespacing=1.32, zorder=25
    )
    crisp_text(
        ax, -1.25, 1.95,
        "Exterior do cone:\ninformação ainda não chegou",
        color=PALETTE["ink_muted"], stroke_w=0.13,
        fontsize=9.0, fontstyle="italic", ha="center", va="bottom",
        linespacing=1.28, zorder=25
    )

    # Callout 1: Origin perturbation (0, 0) at t = 0 (Upper-Left, completely outside plane)
    add_tufte_callout(
        ax,
        target_pt=p_orig,
        anchor_pt=(-5.15, 1.30),
        text_pt=(-8.65, 2.25),
        title=r"Perturbação inicial em $(0, 0)$ ($t = 0$)",
        lines=[
            "Origem da perturbação no plano espacial $(x, y)$;",
            "a onda espalha-se em círculos cada vez maiores",
            r"com velocidade $c = \sqrt{gH}$ conforme o tempo $t$ avança."
        ],
        title_color=PALETTE["normal_vec"],
        align="left",
        rad=-0.16
    )

    # Callout 2: Surface of the characteristic cone (Upper-Right, comfortably above the cone rim)
    p_cone_top_R = proj_xyt(
        u_adv * 7.85 + (c_wave * 7.85) * np.cos(th_sil_top),
        v_adv * 7.85 + (c_wave * 7.85) * np.sin(th_sil_top),
        7.85, orig_3d
    )
    add_tufte_callout(
        ax,
        target_pt=p_cone_top_R,
        anchor_pt=(4.95, 3.15),
        text_pt=(4.35, 3.98),
        title=r"Superfície do cone característico ($x \times y \times t$)",
        lines=[
            "Formada pelo empilhamento dos círculos de onda ao longo de $t$;",
            "demarca a fronteira física até onde a informação",
            "da perturbação conseguiu chegar no espaço-tempo."
        ],
        title_color="#5C4428",
        align="left",
        rad=0.14
    )

    # Set clean bounds and remove default Matplotlib frame/ticks
    ax.set_xlim(-8.85, 8.65)
    ax.set_ylim(-3.65, 4.45)
    ax.set_aspect("equal")
    ax.axis("off")

    plt.tight_layout(pad=0.12)

    out_dir = Path(__file__).resolve().parent.parent / "figures"
    out_dir.mkdir(parents=True, exist_ok=True)

    svg_path = out_dir / "swe_characteristic_cone.svg"
    pdf_path = out_dir / "swe_characteristic_cone.pdf"
    png_path = out_dir / "swe_characteristic_cone.png"

    fig.savefig(svg_path, format="svg", bbox_inches="tight", facecolor=fig.get_facecolor())
    fig.savefig(pdf_path, format="pdf", bbox_inches="tight", facecolor=fig.get_facecolor())
    fig.savefig(png_path, format="png", dpi=300, bbox_inches="tight", facecolor=fig.get_facecolor())
    print(f"Saved: {svg_path}")
    print(f"Saved: {pdf_path}")
    print(f"Saved: {png_path}")


if __name__ == "__main__":
    build_figure()
