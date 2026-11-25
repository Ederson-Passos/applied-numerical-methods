"""
Visualização editorial (estilo monografia científica dos anos 80/90) da
discretização espacial em malha escalonada de Casulli (Arakawa C) para a
Etapa 2.1 do trabalho computacional de Águas Rasas 2D.

Pode ser importado diretamente no notebook `implementation.ipynb`:
    from generate_swe_mesh_discretization_figure import grid_coords, plot_mesh_discretization
    plot_mesh_discretization(grid_coarse, grid_fine)

A cada execução da função, as figuras na pasta `../figures/` são geradas e
sobrescritas automaticamente (`swe_mesh_discretization.png`, `.svg` e `.pdf`),
além de serem exibidas inline na célula do notebook.
"""

import glob
import logging
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.colors import ListedColormap
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
import matplotlib.patheffects as pe

# Silencia avisos internos do fontTools sobre cabeçalhos OpenType do MiKTeX ao exportar PDF
logging.getLogger("fontTools").setLevel(logging.ERROR)

# ---------------------------------------------------------------------------
# 1. Registro único da tipografia LaTeX (Latin Modern Roman + Computer Modern)
# ---------------------------------------------------------------------------
for _fp in glob.glob(r"C:\Program Files\MiKTeX*\fonts\opentype\public\lm\lmroman*.otf"):
    fm.fontManager.addfont(_fp)
_HAS_LM = any(f.name == "Latin Modern Roman" for f in fm.fontManager.ttflist)

PALETTE_SWE = {
    "bg_canvas": "#FAF8F3",      # Papel creme/marfim editorial
    "shelf_fill": "#EFE9DD",     # Planície rasa (h = 0,5 m) — areia suave
    "channel_fill": "#A9CCE0",   # Canal profundo (h = 5,0 m) — azul-gelo (Fig. 1)
    "cell_focus": "#DCEAF3",     # Célula (i, j) destacada no zoom
    "ink_primary": "#11161C",    # Grafite profundo
    "ink_secondary": "#283648",  # Azul-ardósia escuro (bordas e eixos)
    "ink_muted": "#5E6A75",      # Cinza técnico para linhas de grade
    "navy_deep": "#0D3149",      # Azul-marinho (canal e títulos)
    "z_node": "#145374",         # Elevação z / eta (centro da célula)
    "u_node": "#8E321E",         # Velocidade u (face vertical — terracota)
    "v_node": "#17575A",         # Velocidade v (face horizontal — verde-petróleo)
    "amber_zoom": "#9C5E14",     # Âmbar suave (janela de recorte e maré M2)
}

FIGURES_DIR = Path(__file__).resolve().parent.parent / "figures"


def grid_coords(grid):
    """Retorna vetores 1D dos centros (xc, yc) e faces (xf, yf) da malha."""
    dx, dy = grid["dx"], grid["dy"]
    Nx, Ny = grid["Nx"], grid["Ny"]
    xc = (np.arange(Nx) + 0.5) * dx
    yc = (np.arange(Ny) + 0.5) * dy
    xf = np.arange(Nx + 1) * dx
    yf = np.arange(Ny + 1) * dy
    return xc, yc, xf, yf


def _style_axes(ax):
    ax.set_facecolor(PALETTE_SWE["bg_canvas"])
    for spine in ax.spines.values():
        spine.set_edgecolor(PALETTE_SWE["ink_secondary"])
        spine.set_linewidth(0.95)
    ax.tick_params(
        colors=PALETTE_SWE["ink_secondary"],
        labelsize=8.8,
        direction="out",
        length=3.5,
        width=0.8,
    )


def _infer_channel_bounds(grid, yf):
    if "channel_mask" in grid and np.any(grid["channel_mask"]):
        ch_rows = np.where(grid["channel_mask"][:, 0])[0]
        return float(yf[ch_rows[0]]), float(yf[ch_rows[-1] + 1])
    return 1350.0, 1650.0


def plot_mesh_discretization(
    grid_coarse,
    grid_fine,
    output_stem="swe_mesh_discretization",
    save_formats=("png", "svg", "pdf"),
    show=True,
    return_paths=False,
):
    """
    Constrói a prancha comparativa (Malha Grossa, Malha Fina e Zoom da Malha
    Escalonada Arakawa C), salva/sobrescreve os arquivos em `../figures/` a
    cada execução e exibe a figura inline no notebook.
    """
    rc_vintage = {
        "font.family": "Latin Modern Roman" if _HAS_LM else "serif",
        "mathtext.fontset": "cm",
        "svg.fonttype": "path",
        "pdf.fonttype": 42,
        "axes.unicode_minus": True,
        "figure.facecolor": PALETTE_SWE["bg_canvas"],
        "savefig.facecolor": PALETTE_SWE["bg_canvas"],
    }

    _, _, xf_c, yf_c = grid_coords(grid_coarse)
    Lx = float(xf_c[-1])
    Ly = float(yf_c[-1])
    y_channel_min, y_channel_max = _infer_channel_bounds(grid_coarse, yf_c)

    with plt.rc_context(rc_vintage):
        fig = plt.figure(figsize=(14.2, 7.8), dpi=180)
        gs = fig.add_gridspec(
            2, 2,
            width_ratios=[1.48, 1.00],
            height_ratios=[1.0, 1.0],
            wspace=0.12,
            hspace=0.28,
        )
        ax_coarse = fig.add_subplot(gs[0, 0])
        ax_fine = fig.add_subplot(gs[1, 0], sharex=ax_coarse, sharey=ax_coarse)
        ax_zoom = fig.add_subplot(gs[:, 1])

        bathymetry_cmap = ListedColormap(
            [PALETTE_SWE["shelf_fill"], PALETTE_SWE["channel_fill"]]
        )

        # -------------------------------------------------------------------
        # 1. Visão Global: (a) Malha Grossa (40 x 20) vs. (b) Malha Fina (120 x 60)
        # -------------------------------------------------------------------
        n_ch_coarse = int(round((y_channel_max - y_channel_min) / grid_coarse["dy"]))
        n_ch_fine = int(round((y_channel_max - y_channel_min) / grid_fine["dy"]))

        panels_global = [
            (
                ax_coarse,
                rf"(a) Malha Grossa (${grid_coarse['Nx']} \times {grid_coarse['Ny']}$, "
                rf"$\Delta x = \Delta y = {grid_coarse['dx']:.0f}\,\mathrm{{m}}$ — "
                rf"${n_ch_coarse}$ células no canal)",
                grid_coarse,
            ),
            (
                ax_fine,
                rf"(b) Malha Fina (${grid_fine['Nx']} \times {grid_fine['Ny']}$, "
                rf"$\Delta x = \Delta y = {grid_fine['dx']:.0f}\,\mathrm{{m}}$ — "
                rf"${n_ch_fine}$ células no canal)",
                grid_fine,
            ),
        ]

        for ax, title, g in panels_global:
            _style_axes(ax)
            _, _, xf, yf = grid_coords(g)
            is_fine = g["Nx"] > 60

            ax.imshow(
                (g["h"] > 1.0).astype(float),
                origin="lower",
                extent=(0, xf[-1], 0, yf[-1]),
                interpolation="nearest",
                aspect="equal",
                cmap=bathymetry_cmap,
                vmin=0.0,
                vmax=1.0,
                zorder=1,
            )

            ax.vlines(
                xf, 0, yf[-1],
                colors=PALETTE_SWE["ink_muted"],
                linewidth=0.22 if is_fine else 0.52,
                alpha=0.42 if is_fine else 0.65,
                zorder=2,
            )
            ax.hlines(
                yf, 0, xf[-1],
                colors=PALETTE_SWE["ink_muted"],
                linewidth=0.22 if is_fine else 0.52,
                alpha=0.42 if is_fine else 0.65,
                zorder=2,
            )

            for y_ch in (y_channel_min, y_channel_max):
                ax.axhline(
                    y_ch, color=PALETTE_SWE["navy_deep"],
                    linestyle=(0, (5, 3)), linewidth=1.05, zorder=4,
                )

            ax.plot(
                [0, 0], [y_channel_min, y_channel_max],
                color=PALETTE_SWE["amber_zoom"], linewidth=3.0,
                solid_capstyle="butt", zorder=6,
            )

            ax.text(
                Lx - 140, Ly - 270,
                r"Planície rasa ($h = 0{,}5\,\mathrm{m}$)",
                fontsize=8.3, color=PALETTE_SWE["ink_secondary"], ha="right", va="top",
                bbox=dict(
                    boxstyle="square,pad=0.18",
                    facecolor=PALETTE_SWE["bg_canvas"],
                    edgecolor="none",
                    alpha=0.88,
                ),
                zorder=5,
            )
            ax.text(
                Lx - 140, 0.5 * (y_channel_min + y_channel_max),
                r"Canal central ($h = 5{,}0\,\mathrm{m}$, $300\,\mathrm{m}$)",
                fontsize=8.2, fontweight="bold", color=PALETTE_SWE["navy_deep"],
                ha="right", va="center",
                bbox=dict(
                    boxstyle="square,pad=0.16",
                    facecolor="#E4F0F7",
                    edgecolor="none",
                    alpha=0.90,
                ),
                zorder=5,
            )

            ax.set_xlim(0, Lx)
            ax.set_ylim(0, Ly)
            ax.set_yticks([0, 750, int(y_channel_min), int(y_channel_max), 2250, int(Ly)])
            ax.set_ylabel(r"$y\;(\mathrm{m})$", fontsize=9.5, color=PALETTE_SWE["ink_primary"])
            t_obj = ax.set_title(
                title, loc="left", pad=7, fontsize=10.0,
                fontweight="bold", color=PALETTE_SWE["navy_deep"],
            )
            t_obj.set_path_effects(
                [pe.withStroke(linewidth=0.15, foreground=PALETTE_SWE["navy_deep"])]
            )

        ax_fine.set_xticks(np.arange(0, Lx + 1, 1000))
        ax_fine.set_xlabel(r"$x\;(\mathrm{m})$", fontsize=9.5, color=PALETTE_SWE["ink_primary"])

        # Janela de recorte do zoom destacada na Malha Grossa
        x_z0, x_z1 = 0.0, 900.0
        y_z0, y_z1 = 900.0, 2100.0
        ax_coarse.add_patch(Rectangle(
            (x_z0, y_z0), x_z1 - x_z0, y_z1 - y_z0,
            facecolor="none", edgecolor=PALETTE_SWE["amber_zoom"],
            linewidth=1.45, linestyle="-", zorder=7,
        ))
        ax_coarse.text(
            x_z1 + 90, y_z1 - 40, r"Recorte (c)",
            fontsize=8.2, fontweight="bold", fontstyle="italic",
            color=PALETTE_SWE["amber_zoom"], ha="left", va="top",
            bbox=dict(
                boxstyle="square,pad=0.14",
                facecolor=PALETTE_SWE["bg_canvas"],
                edgecolor="none",
                alpha=0.90,
            ),
            zorder=7,
        )

        # -------------------------------------------------------------------
        # 2. Detalhe da Malha Escalonada (Arakawa C — Boca e Transição do Canal)
        # -------------------------------------------------------------------
        _style_axes(ax_zoom)
        _, _, xf, yf = grid_coords(grid_coarse)
        Xc, Yc = grid_coarse["Xc"], grid_coarse["Yc"]
        Xu, Yu = grid_coarse["Xu"], grid_coarse["Yu"]
        Xv, Yv = grid_coarse["Xv"], grid_coarse["Yv"]

        ax_zoom.imshow(
            (grid_coarse["h"] > 1.0).astype(float),
            origin="lower",
            extent=(0, xf[-1], 0, yf[-1]),
            interpolation="nearest",
            aspect="equal",
            cmap=bathymetry_cmap,
            vmin=0.0,
            vmax=1.0,
            zorder=1,
        )

        i_ref, j_ref = 3, 9  # Célula (i, j) na primeira fileira interna do canal
        ax_zoom.add_patch(Rectangle(
            (xf[i_ref], yf[j_ref]), grid_coarse["dx"], grid_coarse["dy"],
            facecolor=PALETTE_SWE["cell_focus"], edgecolor=PALETTE_SWE["navy_deep"],
            linewidth=1.20, zorder=2,
        ))

        ax_zoom.vlines(
            xf, y_z0, y_z1,
            colors=PALETTE_SWE["ink_secondary"], linewidth=0.75, alpha=0.65, zorder=3,
        )
        ax_zoom.hlines(
            yf, x_z0, x_z1,
            colors=PALETTE_SWE["ink_secondary"], linewidth=0.75, alpha=0.65, zorder=3,
        )

        for y_ch in (y_channel_min, y_channel_max):
            ax_zoom.axhline(
                y_ch, color=PALETTE_SWE["navy_deep"],
                linestyle=(0, (5, 3)), linewidth=1.35, zorder=4,
            )
        ax_zoom.plot(
            [0, 0], [y_channel_min, y_channel_max],
            color=PALETTE_SWE["amber_zoom"], linewidth=3.6,
            solid_capstyle="butt", zorder=5,
        )

        eps = 1.0
        m_c = (Xc >= x_z0 - eps) & (Xc <= x_z1 + eps) & (Yc >= y_z0 - eps) & (Yc <= y_z1 + eps)
        m_u = (Xu >= x_z0 - eps) & (Xu <= x_z1 + eps) & (Yu >= y_z0 - eps) & (Yu <= y_z1 + eps)
        m_v = (Xv >= x_z0 - eps) & (Xv <= x_z1 + eps) & (Yv >= y_z0 - eps) & (Yv <= y_z1 + eps)

        ax_zoom.scatter(
            Xc[m_c], Yc[m_c], s=46, marker="o", clip_on=False,
            facecolor=PALETTE_SWE["z_node"], edgecolor=PALETTE_SWE["bg_canvas"],
            linewidth=0.80, zorder=6,
        )
        ax_zoom.scatter(
            Xu[m_u], Yu[m_u], s=40, marker="s", clip_on=False,
            facecolor=PALETTE_SWE["u_node"], edgecolor=PALETTE_SWE["bg_canvas"],
            linewidth=0.80, zorder=6,
        )
        ax_zoom.scatter(
            Xv[m_v], Yv[m_v], s=48, marker="^", clip_on=False,
            facecolor=PALETTE_SWE["v_node"], edgecolor=PALETTE_SWE["bg_canvas"],
            linewidth=0.80, zorder=6,
        )

        cx_r, cy_r = Xc[j_ref, i_ref], Yc[j_ref, i_ref]
        ax_zoom.text(
            cx_r, cy_r + 16, r"$z_{i,j}$", fontsize=8.8, fontweight="bold",
            color=PALETTE_SWE["z_node"], ha="center", va="bottom", zorder=8,
        )
        ax_zoom.text(
            xf[i_ref + 1] + 10, cy_r - 8, r"$u_{i+1/2,j}$", fontsize=8.5, fontweight="bold",
            color=PALETTE_SWE["u_node"], ha="left", va="top",
            bbox=dict(
                boxstyle="square,pad=0.06",
                facecolor=PALETTE_SWE["channel_fill"],
                edgecolor="none",
                alpha=0.88,
            ),
            zorder=8,
        )
        ax_zoom.text(
            cx_r + 10, yf[j_ref + 1] + 10, r"$v_{i,j+1/2}$", fontsize=8.5, fontweight="bold",
            color=PALETTE_SWE["v_node"], ha="left", va="bottom",
            bbox=dict(
                boxstyle="square,pad=0.06",
                facecolor=PALETTE_SWE["channel_fill"],
                edgecolor="none",
                alpha=0.88,
            ),
            zorder=8,
        )

        ax_zoom.text(
            882, 1985, r"Planície superior ($h = 0{,}5\,\mathrm{m}$)",
            fontsize=8.0, fontstyle="italic", color=PALETTE_SWE["ink_secondary"],
            ha="right", va="center",
            bbox=dict(
                boxstyle="square,pad=0.12",
                facecolor=PALETTE_SWE["shelf_fill"],
                edgecolor="none",
                alpha=0.92,
            ),
            zorder=7,
        )
        ax_zoom.text(
            882, 1425, r"Canal ($h = 5{,}0\,\mathrm{m}$)",
            fontsize=8.1, fontweight="bold", color=PALETTE_SWE["navy_deep"],
            ha="right", va="center",
            bbox=dict(
                boxstyle="square,pad=0.12",
                facecolor=PALETTE_SWE["channel_fill"],
                edgecolor="none",
                alpha=0.92,
            ),
            zorder=7,
        )
        ax_zoom.text(
            882, 1015, r"Planície inferior ($h = 0{,}5\,\mathrm{m}$)",
            fontsize=8.0, fontstyle="italic", color=PALETTE_SWE["ink_secondary"],
            ha="right", va="center",
            bbox=dict(
                boxstyle="square,pad=0.12",
                facecolor=PALETTE_SWE["shelf_fill"],
                edgecolor="none",
                alpha=0.92,
            ),
            zorder=7,
        )

        ax_zoom.set_xlim(x_z0, x_z1)
        ax_zoom.set_ylim(y_z0, y_z1)
        ax_zoom.set_xticks(np.arange(0, 901, 150))
        ax_zoom.set_yticks(np.arange(900, 2101, 150))
        ax_zoom.set_xlabel(r"$x\;(\mathrm{m})$", fontsize=9.5, color=PALETTE_SWE["ink_primary"])
        ax_zoom.set_ylabel(r"$y\;(\mathrm{m})$", fontsize=9.5, color=PALETTE_SWE["ink_primary"])

        tz_obj = ax_zoom.set_title(
            r"(c) Detalhe da Malha Escalonada (Malha Grossa — Boca e Canal)",
            loc="left", pad=7, fontsize=10.0, fontweight="bold", color=PALETTE_SWE["navy_deep"],
        )
        tz_obj.set_path_effects(
            [pe.withStroke(linewidth=0.15, foreground=PALETTE_SWE["navy_deep"])]
        )

        legend_handles = [
            Line2D(
                [0], [0], marker="o", linestyle="None",
                markerfacecolor=PALETTE_SWE["z_node"],
                markeredgecolor=PALETTE_SWE["bg_canvas"], markersize=7.2,
                label=r"$z / \eta_{i,j}$ (centro da célula)",
            ),
            Line2D(
                [0], [0], marker="s", linestyle="None",
                markerfacecolor=PALETTE_SWE["u_node"],
                markeredgecolor=PALETTE_SWE["bg_canvas"], markersize=6.8,
                label=r"$u_{i+1/2,j}$ (face vertical)",
            ),
            Line2D(
                [0], [0], marker="^", linestyle="None",
                markerfacecolor=PALETTE_SWE["v_node"],
                markeredgecolor=PALETTE_SWE["bg_canvas"], markersize=7.4,
                label=r"$v_{i,j+1/2}$ (face horizontal)",
            ),
            Line2D(
                [0], [0], color=PALETTE_SWE["navy_deep"],
                linestyle=(0, (5, 3)), linewidth=1.25,
                label=rf"Bordas do canal ($y = {y_channel_min:.0f},\, {y_channel_max:.0f}\,\mathrm{{m}}$)",
            ),
            Line2D(
                [0], [0], color=PALETTE_SWE["amber_zoom"], linewidth=3.2,
                label=r"Fronteira aberta ($x = 0$, maré $M_2$)",
            ),
        ]
        leg = fig.legend(
            handles=legend_handles,
            loc="lower center",
            bbox_to_anchor=(0.5, -0.01),
            ncol=5,
            frameon=True,
            facecolor="#F5F1E9",
            edgecolor=PALETTE_SWE["ink_secondary"],
            fontsize=8.5,
            handletextpad=0.45,
            columnspacing=1.35,
        )
        leg.get_frame().set_linewidth(0.85)
        leg.get_frame().set_boxstyle("square,pad=0.30")

        fig.subplots_adjust(left=0.055, right=0.985, top=0.94, bottom=0.115)

        # Salva sempre na pasta ../figures, sobrescrevendo execuções anteriores
        FIGURES_DIR.mkdir(parents=True, exist_ok=True)
        saved_paths = {}
        for fmt in save_formats:
            out_path = FIGURES_DIR / f"{output_stem}.{fmt}"
            save_kwargs = dict(
                format=fmt,
                bbox_inches="tight",
                facecolor=fig.get_facecolor(),
            )
            if fmt.lower() == "png":
                save_kwargs["dpi"] = 300
            fig.savefig(out_path, **save_kwargs)
            saved_paths[fmt] = out_path

        if show:
            plt.show()
        plt.close(fig)

    return saved_paths if return_paths else None


if __name__ == "__main__":
    # Permite execução autônoma do script para regenerar os arquivos em ../figures/
    Lx_def, Ly_def = 6000.0, 3000.0
    y_min_def, y_max_def = 1350.0, 1650.0

    def _build_demo_grid(Nx, Ny):
        dx, dy = Lx_def / Nx, Ly_def / Ny
        xc = (np.arange(Nx) + 0.5) * dx
        yc = (np.arange(Ny) + 0.5) * dy
        xf = np.arange(Nx + 1) * dx
        yf = np.arange(Ny + 1) * dy
        Xc, Yc = np.meshgrid(xc, yc, indexing="xy")
        Xu, Yu = np.meshgrid(xf, yc, indexing="xy")
        Xv, Yv = np.meshgrid(xc, yf, indexing="xy")
        ch_mask = np.broadcast_to(((yc >= y_min_def) & (yc < y_max_def))[:, None], (Ny, Nx))
        h = np.where(ch_mask, 5.0, 0.5)
        return {
            "Nx": Nx, "Ny": Ny, "dx": dx, "dy": dy,
            "Xc": Xc, "Yc": Yc, "Xu": Xu, "Yu": Yu, "Xv": Xv, "Yv": Yv,
            "h": h, "channel_mask": ch_mask,
        }

    paths = plot_mesh_discretization(
        _build_demo_grid(40, 20),
        _build_demo_grid(120, 60),
        show=False,
        return_paths=True,
    )
    for fmt_k, p_out in paths.items():
        print(f"Saved ({fmt_k}): {p_out}")
