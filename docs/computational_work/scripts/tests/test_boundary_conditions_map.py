"""
Verificação visual e geométrica do mapa de condições de contorno sobre a
batimetria da Bacia de Casulli (Seção 2.4.2).

Preserva integralmente a lógica e o objetivo do mapa 2D (`imshow` de `grid_fine["h"]`
+ demarcação explícita da entrada aberta da maré M2 e dos 5 segmentos de
fronteiras fechadas), aplicando a identidade visual editorial Edward Tufte /
anos 80–90 e salvando/sobrescrevendo automaticamente a figura em
`docs/computational_work/figures/results/swe_boundary_conditions_map.{png,svg,pdf}`.
"""

import sys
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch

# Garante acesso ao módulo compartilhado `analysis.style`
_SCRIPTS_DIR = Path(__file__).resolve().parent.parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from analysis.style import (
    PALETTE_RESULTS as P,
    rc_tufte_context,
    style_tufte_axes,
    set_crisp_title,
    save_result_figure,
)


def _infer_geometry(grid):
    Nx, Ny = grid["Nx"], grid["Ny"]
    dx, dy = float(grid["dx"]), float(grid["dy"])
    xf = np.arange(Nx + 1) * dx
    yf = np.arange(Ny + 1) * dy
    Lx, Ly = float(xf[-1]), float(yf[-1])

    if "channel_mask" in grid and np.any(grid["channel_mask"]):
        ch_rows = np.where(grid["channel_mask"][:, 0])[0]
        y_min, y_max = float(yf[ch_rows[0]]), float(yf[ch_rows[-1] + 1])
    else:
        main_mod = sys.modules.get("__main__")
        y_min = float(getattr(main_mod, "y_channel_min", 1350.0))
        y_max = float(getattr(main_mod, "y_channel_max", 1650.0))

    return xf, yf, Lx, Ly, y_min, y_max


def plot_boundary_conditions_map(
    grid_fine,
    Lx=None,
    Ly=None,
    y_channel_min=None,
    y_channel_max=None,
    output_stem="swe_boundary_conditions_map",
    save_formats=("png", "svg", "pdf"),
    show=True,
    return_paths=False,
):
    """
    Plota e valida geometricamente as condições de contorno sobre `grid_fine["h"]`,
    sobrescrevendo os arquivos em `figures/results/` a cada execução.
    """
    xf, yf, Lx_inf, Ly_inf, ymin_inf, ymax_inf = _infer_geometry(grid_fine)
    Lx = float(Lx_inf if Lx is None else Lx)
    Ly = float(Ly_inf if Ly is None else Ly)
    y_channel_min = float(ymin_inf if y_channel_min is None else y_channel_min)
    y_channel_max = float(ymax_inf if y_channel_max is None else y_channel_max)

    # Se as máscaras de contorno já estiverem construídas, confere consistência geométrica
    if "boundary_masks" in grid_fine:
        masks = grid_fine["boundary_masks"]
        expected_open = int(round((y_channel_max - y_channel_min) / grid_fine["dy"]))
        assert np.count_nonzero(masks["open_west"]) == expected_open, (
            "Inconsistência entre open_west e a largura do canal."
        )

    bathy_cmap = ListedColormap(["#EFE9DD", "#A9CCE0"])

    with plt.rc_context(rc_tufte_context()):
        fig, ax = plt.subplots(figsize=(12.8, 5.8), dpi=180)
        style_tufte_axes(ax, grid=False)

        # 1. Fundo batimétrico discreto da bacia (planícies h=0,5 m vs. canal h=5,0 m)
        ax.imshow(
            (grid_fine["h"] > 1.0).astype(float),
            origin="lower",
            extent=(0.0, Lx, 0.0, Ly),
            aspect="equal",
            interpolation="nearest",
            cmap=bathy_cmap,
            vmin=0.0,
            vmax=1.0,
            zorder=1,
        )

        # Grade discreta finíssima para evidenciar o alinhamento exato das células
        ax.vlines(xf, 0.0, Ly, colors=P["ink_muted"], linewidth=0.20, alpha=0.28, zorder=2)
        ax.hlines(yf, 0.0, Lx, colors=P["ink_muted"], linewidth=0.20, alpha=0.28, zorder=2)

        # Linhas internas tracejadas do canal central
        for y_ch in (y_channel_min, y_channel_max):
            ax.plot(
                [0.0, Lx], [y_ch, y_ch],
                color=P["navy_deep"], linestyle=":", linewidth=0.95, alpha=0.75, zorder=3,
            )

        # 2. Fronteiras fechadas (5 segmentos exatos: Sul, Norte, Leste e 2 abas Oeste)
        wall_kw = dict(
            color=P["terracotta"],
            linestyle=(0, (5.5, 2.8)),
            linewidth=2.35,
            solid_capstyle="butt",
            zorder=6,
        )
        # Sul (y = 0) e Norte (y = Ly)
        ax.plot([0.0, Lx], [0.0, 0.0], **wall_kw)
        ax.plot([0.0, Lx], [Ly, Ly], **wall_kw)
        # Leste (x = Lx)
        ax.plot([Lx, Lx], [0.0, Ly], **wall_kw)
        # Oeste fechado (x = 0, fora do canal)
        ax.plot([0.0, 0.0], [0.0, y_channel_min], **wall_kw)
        ax.plot([0.0, 0.0], [y_channel_max, Ly], **wall_kw)

        # Hachuras externas sutis de parede rígida ao longo do contorno fechado
        tick_len = 85.0
        for x_t in np.linspace(180.0, Lx - 180.0, 22):
            ax.plot([x_t, x_t - 55.0], [0.0, -tick_len], color=P["terracotta"], lw=0.65, alpha=0.70, zorder=5)
            ax.plot([x_t, x_t + 55.0], [Ly, Ly + tick_len], color=P["terracotta"], lw=0.65, alpha=0.70, zorder=5)
        for y_t in np.linspace(150.0, Ly - 150.0, 12):
            ax.plot([Lx, Lx + tick_len], [y_t, y_t + 55.0], color=P["terracotta"], lw=0.65, alpha=0.70, zorder=5)
        for y_t in np.concatenate([
            np.linspace(140.0, y_channel_min - 120.0, 5),
            np.linspace(y_channel_max + 120.0, Ly - 140.0, 5),
        ]):
            ax.plot([0.0, -tick_len], [y_t, y_t - 55.0], color=P["terracotta"], lw=0.65, alpha=0.70, zorder=5)

        # 3. Entrada aberta (x = 0, y em [y_channel_min, y_channel_max]) — Maré M2
        ax.plot(
            [0.0, 0.0],
            [y_channel_min, y_channel_max],
            color=P["amber_acc"],
            linewidth=5.8,
            solid_capstyle="butt",
            zorder=8,
        )
        yc_mid = 0.5 * (y_channel_min + y_channel_max)
        arr_tide = FancyArrowPatch(
            (-210.0, yc_mid), (390.0, yc_mid),
            arrowstyle="<|-|>", mutation_scale=11.0,
            color=P["cerulean"], linewidth=1.85, zorder=9,
        )
        ax.add_patch(arr_tide)

        # 4. Anotações técnicas diretas sem sobreposições nas 5 fronteiras e regiões
        pill_wall = dict(boxstyle="square,pad=0.14", facecolor=P["panel_bg"], edgecolor="none", alpha=0.92)

        ax.text(
            0.5 * Lx, Ly + 115.0,
            r"Fronteira Norte ($y = L_y$): parede impermeável ($v = 0$, $u$ livre)",
            fontsize=8.4, fontweight="bold", color=P["terracotta"],
            ha="center", va="bottom", bbox=pill_wall, zorder=10,
        )
        ax.text(
            0.5 * Lx, -115.0,
            r"Fronteira Sul ($y = 0$): parede impermeável ($v = 0$, $u$ livre)",
            fontsize=8.4, fontweight="bold", color=P["terracotta"],
            ha="center", va="top", bbox=pill_wall, zorder=10,
        )
        ax.text(
            Lx + 125.0, 0.5 * Ly,
            r"Fronteira Leste ($x = L_x$): parede impermeável ($u = 0$, $v$ livre)",
            fontsize=8.3, fontweight="bold", color=P["terracotta"],
            rotation=90, ha="left", va="center", bbox=pill_wall, zorder=10,
        )
        for y_w_pos in (0.5 * y_channel_min, 0.5 * (y_channel_max + Ly)):
            ax.text(
                135.0, y_w_pos,
                r"Oeste fechado: parede impermeável ($u = 0$, $v$ livre)",
                fontsize=8.0, fontweight="bold", color=P["terracotta"],
                ha="left", va="center",
                bbox=dict(boxstyle="square,pad=0.13", facecolor="#EFE9DD", edgecolor="none", alpha=0.92),
                zorder=10,
            )

        ax.text(
            440.0, yc_mid,
            r"Entrada aberta ($\Gamma_{\mathrm{aberta}}$): $z(0,y,t) = A\sin(2\pi t / T)$",
            fontsize=8.35, fontweight="bold", color=P["navy_deep"],
            ha="left", va="center",
            bbox=dict(boxstyle="square,pad=0.14", facecolor="#E4F0F7", edgecolor=P["cerulean"], lw=0.65, alpha=0.95),
            zorder=10,
        )

        # Rótulos discretos da batimetria interna à direita
        ax.text(
            Lx - 150.0, Ly - 220.0,
            r"Planície rasa ($h = 0{,}5\,\mathrm{m}$)",
            fontsize=8.1, fontstyle="italic", color=P["ink_secondary"],
            ha="right", va="top",
            bbox=dict(boxstyle="square,pad=0.12", facecolor="#EFE9DD", edgecolor="none", alpha=0.90),
            zorder=5,
        )
        ax.text(
            Lx - 150.0, yc_mid,
            r"Canal central ($h = 5{,}0\,\mathrm{m}$, $300\,\mathrm{m}$)",
            fontsize=8.1, fontweight="bold", color=P["navy_deep"],
            ha="right", va="center",
            bbox=dict(boxstyle="square,pad=0.12", facecolor="#C6DFEE", edgecolor="none", alpha=0.92),
            zorder=5,
        )

        # Margem simétrica de respiro ao redor do retângulo [0, Lx] x [0, Ly]
        ax.set_xlim(-340.0, Lx + 410.0)
        ax.set_ylim(-350.0, Ly + 350.0)
        ax.set_xticks(np.arange(0, int(Lx) + 1, 1000))
        ax.set_yticks([0, 750, int(y_channel_min), int(y_channel_max), 2250, int(Ly)])
        ax.set_xlabel(r"$x\;(\mathrm{m})$", fontsize=9.5, color=P["ink_primary"])
        ax.set_ylabel(r"$y\;(\mathrm{m})$", fontsize=9.5, color=P["ink_primary"])

        set_crisp_title(
            ax,
            rf"Condições de Contorno — Bacia de Casulli (Malha ${grid_fine['Nx']} \times {grid_fine['Ny']}$, "
            rf"$\Delta x = \Delta y = {grid_fine['dx']:.0f}\,\mathrm{{m}}$)",
            fontsize=10.4,
        )

        legend_handles = [
            Line2D(
                [0], [0], color=P["amber_acc"], linewidth=5.0, solid_capstyle="butt",
                label=r"Entrada aberta — Maré $M_2$ ($x = 0$, $1350 \leq y \leq 1650\,\mathrm{m}$)",
            ),
            Line2D(
                [0], [0], color=P["terracotta"], linestyle=(0, (5.5, 2.8)), linewidth=2.2,
                label=r"Fronteiras fechadas — Parede impermeável ($\mathbf{u}\cdot\mathbf{n} = 0$)",
            ),
            Line2D(
                [0], [0], color=P["navy_deep"], linestyle=":", linewidth=1.1,
                label=r"Transição batimétrica do canal ($h: 0{,}5\,\mathrm{m} \leftrightarrow 5{,}0\,\mathrm{m}$)",
            ),
        ]
        leg = fig.legend(
            handles=legend_handles,
            loc="lower center",
            bbox_to_anchor=(0.5, -0.01),
            ncol=3,
            frameon=True,
            facecolor=P["legend_bg"],
            edgecolor=P["ink_secondary"],
            fontsize=8.35,
            handlelength=2.2,
            columnspacing=1.5,
        )
        leg.get_frame().set_linewidth(0.80)
        leg.get_frame().set_boxstyle("square,pad=0.26")

        fig.subplots_adjust(left=0.06, right=0.97, top=0.92, bottom=0.14)

        # Salva e sobrescreve automaticamente na subpasta `figures/results/`
        saved_paths = save_result_figure(
            fig, output_stem=output_stem, save_formats=save_formats, dpi=300
        )

        if show:
            plt.show()
        plt.close(fig)

    return saved_paths if return_paths else None


# Alias de conveniência para compatibilidade com o padrão test_*
test_boundary_conditions_map = plot_boundary_conditions_map


if __name__ == "__main__":
    dx, dy = 50.0, 50.0
    Nx, Ny = 120, 60
    yc = (np.arange(Ny) + 0.5) * dy
    ch_mask = np.broadcast_to(((yc >= 1350.0) & (yc < 1650.0))[:, None], (Ny, Nx))
    h = np.where(ch_mask, 5.0, 0.5)
    open_w = np.any(ch_mask, axis=1)
    mock_fine = {
        "Nx": Nx, "Ny": Ny, "dx": dx, "dy": dy,
        "h": h, "channel_mask": ch_mask,
        "boundary_masks": {
            "open_west": open_w,
            "closed_west": ~open_w,
            "closed_east": np.ones(Ny, dtype=bool),
            "closed_south": np.ones(Nx, dtype=bool),
            "closed_north": np.ones(Nx, dtype=bool),
        },
    }
    paths = plot_boundary_conditions_map(mock_fine, show=False, return_paths=True)
    for k, v in paths.items():
        print(f"Saved ({k}): {v}")
