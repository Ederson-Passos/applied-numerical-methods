"""
Visualização editorial (estilo monografia de engenharia costeira dos anos 80/90)
da Batimetria Discreta h(x, y) na Malha Refinada de Casulli (120 x 60, dx = dy = 50 m).

Pode ser importado diretamente no notebook `implementation.ipynb`:
    from generate_swe_bathymetry_figure import plot_bathymetry_fine
    plot_bathymetry_fine(grid_fine)

A cada execução da função, os arquivos em `../figures/` são gerados e
sobrescritos automaticamente (`swe_bathymetry_fine.png`, `.svg` e `.pdf`),
além da exibição inline na célula do notebook.
"""

import glob
import logging
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Polygon, FancyArrowPatch
import matplotlib.patheffects as pe

# Silencia avisos internos do fontTools sobre cabeçalhos OpenType do MiKTeX ao exportar PDF
logging.getLogger("fontTools").setLevel(logging.ERROR)

for _fp in glob.glob(r"C:\Program Files\MiKTeX*\fonts\opentype\public\lm\lmroman*.otf"):
    fm.fontManager.addfont(_fp)
_HAS_LM = any(f.name == "Latin Modern Roman" for f in fm.fontManager.ttflist)

PALETTE_BATHY = {
    "bg_canvas": "#FAF8F3",      # Papel creme/marfim editorial
    "ink_primary": "#11161C",    # Grafite profundo
    "ink_secondary": "#283648",  # Azul-ardósia escuro (bordas e eixos)
    "ink_muted": "#5E6A75",      # Cinza técnico
    "navy_deep": "#0D3149",      # Azul-marinho profundo
    "chan_deep": "#184E70",      # Azul hidrográfico do canal central (h = 5,0 m)
    "shelf_pale": "#E2ECF2",     # Azul-areia raso das planícies (h = 0,5 m)
    "water_col": "#9CC4DC",      # Coluna d'água em corte transversal
    "bed_fill": "#CFC3B4",       # Sedimento/leito em corte geológico (Fig. 1)
    "bed_edge": "#5E4F41",       # Contorno do leito batimétrico
    "bed_hatch": "#827161",      # Hachura geológica clássica
    "terracotta": "#8E321E",     # Linha de corte A-A' e destaques técnicos
    "amber_tide": "#A86518",     # Fronteira aberta da maré M2 (x = 0)
}

FIGURES_DIR = Path(__file__).resolve().parent.parent / "figures"


def _build_hydro_cmap():
    """Escala hidrográfica contínua calibrada para a paleta editorial da série."""
    return LinearSegmentedColormap.from_list(
        "casulli_hydro",
        [
            (0.00, "#F1ECE1"),  # 0,0 m — areia costeira
            (0.09, "#E2ECF2"),  # 0,5 m — lâmina rasa das planícies
            (0.35, "#A9CCE0"),  # ~1,9 m — azul-gelo intermediário
            (0.68, "#4E86AB"),  # ~3,7 m — cerúleo médio
            (0.91, "#184E70"),  # 5,0 m — canal central profundo
            (1.00, "#0D3149"),  # 5,5 m — azul-marinho abissal
        ],
        N=256,
    )


def _style_axes(ax):
    ax.set_facecolor(PALETTE_BATHY["bg_canvas"])
    for spine in ax.spines.values():
        spine.set_edgecolor(PALETTE_BATHY["ink_secondary"])
        spine.set_linewidth(0.95)
    ax.tick_params(
        colors=PALETTE_BATHY["ink_secondary"],
        labelsize=8.8,
        direction="out",
        length=3.5,
        width=0.8,
    )


def _infer_domain_and_channel(grid):
    Nx, Ny = grid["Nx"], grid["Ny"]
    dx, dy = grid["dx"], grid["dy"]
    xf = np.arange(Nx + 1) * dx
    yf = np.arange(Ny + 1) * dy
    Lx, Ly = float(xf[-1]), float(yf[-1])
    if "channel_mask" in grid and np.any(grid["channel_mask"]):
        ch_rows = np.where(grid["channel_mask"][:, 0])[0]
        y_min, y_max = float(yf[ch_rows[0]]), float(yf[ch_rows[-1] + 1])
    else:
        ch_rows = np.where(grid["h"][:, 0] > 1.0)[0]
        y_min = float(yf[ch_rows[0]]) if len(ch_rows) else 1350.0
        y_max = float(yf[ch_rows[-1] + 1]) if len(ch_rows) else 1650.0
    return xf, yf, Lx, Ly, y_min, y_max


def plot_bathymetry_fine(
    grid_fine,
    output_stem="swe_bathymetry_fine",
    save_formats=("png", "svg", "pdf"),
    show=True,
    return_paths=False,
):
    """
    Gera a prancha batimétrica da malha refinada de Casulli (planta 2D + barra
    hidrográfica + corte transversal A-A' alinhado em y), sobrescrevendo os
    arquivos em `../figures/` a cada execução.
    """
    rc_vintage = {
        "font.family": "Latin Modern Roman" if _HAS_LM else "serif",
        "mathtext.fontset": "cm",
        "svg.fonttype": "path",
        "pdf.fonttype": 42,
        "axes.unicode_minus": True,
        "figure.facecolor": PALETTE_BATHY["bg_canvas"],
        "savefig.facecolor": PALETTE_BATHY["bg_canvas"],
    }

    xf, yf, Lx, Ly, y_channel_min, y_channel_max = _infer_domain_and_channel(grid_fine)
    Nx, Ny = grid_fine["Nx"], grid_fine["Ny"]
    dx, dy = grid_fine["dx"], grid_fine["dy"]
    h_arr = grid_fine["h"]

    # Contagem de fileiras nas planícies e no canal
    n_ch_rows = int(round((y_channel_max - y_channel_min) / dy))
    n_sh_bot = int(round(y_channel_min / dy))
    n_sh_top = Ny - n_sh_bot - n_ch_rows

    # Razão exata de aspecto (Ly / Lx = 0.5) sincronizada nos eixos da linha
    w_map, w_cbar, w_gap, w_prof = 1.00, 0.028, 0.085, 0.34
    box_h = Ly / Lx  # 0.50

    with plt.rc_context(rc_vintage):
        fig = plt.figure(figsize=(14.4, 5.4), dpi=180)
        gs = fig.add_gridspec(
            1, 4,
            width_ratios=[w_map, w_cbar, w_gap, w_prof],
            wspace=0.03,
        )
        ax_map = fig.add_subplot(gs[0, 0])
        cax = fig.add_subplot(gs[0, 1])
        ax_gap = fig.add_subplot(gs[0, 2])
        ax_gap.axis("off")
        ax_prof = fig.add_subplot(gs[0, 3], sharey=ax_map)

        # -------------------------------------------------------------------
        # (a) Planta Batimétrica h(x, y) — Malha Refinada (120 x 60)
        # -------------------------------------------------------------------
        _style_axes(ax_map)
        hydro_cmap = _build_hydro_cmap()

        im = ax_map.imshow(
            h_arr,
            origin="lower",
            extent=(0, Lx, 0, Ly),
            interpolation="nearest",
            aspect="equal",
            cmap=hydro_cmap,
            vmin=0.0,
            vmax=5.5,
            zorder=1,
        )
        ax_map.set_box_aspect(box_h)

        # Malha fina discreta (120 x 60 células de 50 m)
        ax_map.vlines(xf, 0, Ly, colors="#384B5C", linewidth=0.18, alpha=0.26, zorder=2)
        ax_map.hlines(yf, 0, Lx, colors="#384B5C", linewidth=0.18, alpha=0.26, zorder=2)

        # Bordas do canal central (y = 1350 m e y = 1650 m) com alto contraste
        for y_ch in (y_channel_min, y_channel_max):
            ax_map.axhline(y_ch, color="#FAF8F3", linestyle="-", linewidth=1.6, alpha=0.75, zorder=3)
            ax_map.axhline(
                y_ch, color=PALETTE_BATHY["navy_deep"],
                linestyle=(0, (5, 3)), linewidth=1.15, zorder=4,
            )

        # Fronteira aberta na entrada esquerda do canal (x = 0, y em [1350, 1650])
        ax_map.plot(
            [0, 0], [y_channel_min, y_channel_max],
            color=PALETTE_BATHY["amber_tide"], linewidth=3.8,
            solid_capstyle="butt", clip_on=False, zorder=7,
        )
        arr_in = FancyArrowPatch(
            (40, 0.5 * (y_channel_min + y_channel_max)),
            (430, 0.5 * (y_channel_min + y_channel_max)),
            arrowstyle="-|>", mutation_scale=10.5,
            color="#FAF8F3", linewidth=1.35, zorder=7,
        )
        ax_map.add_patch(arr_in)
        ax_map.text(
            130, y_channel_max + 85,
            r"Boca aberta: Maré $M_2$ ($\Gamma_{\mathrm{aberta}}$)",
            fontsize=8.1, fontweight="bold", color=PALETTE_BATHY["amber_tide"],
            ha="left", va="bottom",
            bbox=dict(
                boxstyle="square,pad=0.14",
                facecolor=PALETTE_BATHY["bg_canvas"],
                edgecolor="none",
                alpha=0.90,
            ),
            zorder=6,
        )

        # Linha de corte transversal A-A' em x = Lx / 2
        x_sec = 0.5 * Lx
        ax_map.axvline(
            x_sec, color=PALETTE_BATHY["terracotta"],
            linestyle=(0, (6, 2, 1.5, 2)), linewidth=1.15, zorder=5,
        )
        for y_lbl_s, s_tag, va_s in [(110, r"$A$", "bottom"), (Ly - 110, r"$A'$", "top")]:
            ax_map.text(
                x_sec + 75, y_lbl_s, s_tag,
                fontsize=9.0, fontweight="bold", color=PALETTE_BATHY["terracotta"],
                ha="left", va=va_s,
                bbox=dict(
                    boxstyle="square,pad=0.10",
                    facecolor=PALETTE_BATHY["bg_canvas"],
                    edgecolor="none",
                    alpha=0.90,
                ),
                zorder=6,
            )

        # Anotações batimétricas nas três faixas do domínio
        ax_map.text(
            Lx - 130, Ly - 210,
            rf"Planície rasa norte: $h = 0{{,}}5\,\mathrm{{m}}$ (${n_sh_top}$ fileiras)",
            fontsize=8.2, color=PALETTE_BATHY["ink_secondary"], ha="right", va="top",
            bbox=dict(
                boxstyle="square,pad=0.16",
                facecolor=PALETTE_BATHY["bg_canvas"],
                edgecolor="none",
                alpha=0.90,
            ),
            zorder=6,
        )
        ax_map.text(
            Lx - 130, 0.5 * (y_channel_min + y_channel_max),
            rf"Canal profundo: $h = 5{{,}}0\,\mathrm{{m}}$ ($300\,\mathrm{{m}} = {n_ch_rows}$ fileiras)",
            fontsize=8.2, fontweight="bold", color=PALETTE_BATHY["navy_deep"],
            ha="right", va="center",
            bbox=dict(
                boxstyle="square,pad=0.15",
                facecolor="#EDF4F8",
                edgecolor="none",
                alpha=0.93,
            ),
            zorder=6,
        )
        ax_map.text(
            Lx - 130, 210,
            rf"Planície rasa sul: $h = 0{{,}}5\,\mathrm{{m}}$ (${n_sh_bot}$ fileiras)",
            fontsize=8.2, color=PALETTE_BATHY["ink_secondary"], ha="right", va="bottom",
            bbox=dict(
                boxstyle="square,pad=0.16",
                facecolor=PALETTE_BATHY["bg_canvas"],
                edgecolor="none",
                alpha=0.90,
            ),
            zorder=6,
        )

        ax_map.set_xlim(0, Lx)
        ax_map.set_ylim(0, Ly)
        ax_map.set_xticks(np.arange(0, Lx + 1, 1000))
        ax_map.set_yticks([0, 750, int(y_channel_min), int(y_channel_max), 2250, int(Ly)])
        ax_map.set_xlabel(r"$x\;(\mathrm{m})$", fontsize=9.6, color=PALETTE_BATHY["ink_primary"])
        ax_map.set_ylabel(r"$y\;(\mathrm{m})$", fontsize=9.6, color=PALETTE_BATHY["ink_primary"])

        t_map = ax_map.set_title(
            rf"(a) Batimetria — Malha Refinada de Casulli (${Nx} \times {Ny}$, "
            rf"$\Delta x = \Delta y = {dx:.0f}\,\mathrm{{m}}$)",
            loc="left", pad=8, fontsize=10.2,
            fontweight="bold", color=PALETTE_BATHY["navy_deep"],
        )
        t_map.set_path_effects(
            [pe.withStroke(linewidth=0.15, foreground=PALETTE_BATHY["navy_deep"])]
        )

        # -------------------------------------------------------------------
        # Escala Hidrográfica Vertical (Colorbar alinhada exatamente em altura)
        # -------------------------------------------------------------------
        cax.set_box_aspect(box_h * (w_map / w_cbar))
        cbar = fig.colorbar(im, cax=cax)
        cbar.outline.set_edgecolor(PALETTE_BATHY["ink_secondary"])
        cbar.outline.set_linewidth(0.90)
        cbar.set_ticks([0.0, 0.5, 1.5, 2.5, 3.5, 5.0])
        cbar.set_ticklabels(["0,0", "0,5", "1,5", "2,5", "3,5", "5,0"])
        cbar.ax.tick_params(
            colors=PALETTE_BATHY["ink_secondary"], labelsize=8.3, length=3.0, width=0.8
        )
        cbar.set_label(
            r"Profundidade $h\;(\mathrm{m})$",
            fontsize=9.2, color=PALETTE_BATHY["ink_primary"], labelpad=6,
        )
        # Marcas nos dois patamares discretos (0,5 m e 5,0 m)
        for h_lvl, col_m in [(0.5, PALETTE_BATHY["ink_secondary"]), (5.0, "#FAF8F3")]:
            cbar.ax.axhline(h_lvl, color=col_m, linewidth=1.1, linestyle="-")

        # -------------------------------------------------------------------
        # (b) Corte Geológico Transversal A-A' — Perfil h(y) alinhado em y
        # -------------------------------------------------------------------
        _style_axes(ax_prof)
        ax_prof.set_box_aspect(box_h * (w_map / w_prof))

        # Constrói perfil exato em degrau a partir da coluna central i = Nx // 2
        i_mid = Nx // 2
        y_step = np.repeat(yf, 2)[1:-1]
        h_step = np.repeat(h_arr[:, i_mid], 2)
        h_max_box = 6.15

        # Preenchimento da coluna d'água entre z = 0 e o fundo h(y)
        water_poly = [(0.0, 0.0)] + list(zip(h_step, y_step)) + [(0.0, Ly)]
        ax_prof.add_patch(Polygon(
            water_poly, closed=True,
            facecolor="#B8D6E8", edgecolor="none", alpha=0.78, zorder=2,
        ))
        # Realce mais profundo no trecho do canal central
        ax_prof.add_patch(Polygon(
            [
                (0.0, y_channel_min),
                (5.0, y_channel_min),
                (5.0, y_channel_max),
                (0.0, y_channel_max),
            ],
            closed=True, facecolor="#74A9C9", edgecolor="none", alpha=0.65, zorder=2.2,
        ))

        # Bloco geológico do leito com hachura clássica (mesma estética da Fig. 1)
        bed_poly = (
            list(zip(h_step, y_step))
            + [(h_max_box, Ly), (h_max_box, 0.0)]
        )
        ax_prof.add_patch(Polygon(
            bed_poly, closed=True,
            facecolor=PALETTE_BATHY["bed_fill"],
            edgecolor=PALETTE_BATHY["bed_hatch"],
            hatch="///",
            linewidth=0.0,
            zorder=3,
        ))
        ax_prof.plot(
            h_step, y_step,
            color=PALETTE_BATHY["bed_edge"], linewidth=1.55, zorder=5,
        )

        # Linha de referência da superfície livre em repouso (z = 0)
        ax_prof.axvline(
            0.0, color=PALETTE_BATHY["navy_deep"],
            linestyle=(0, (4, 2.5)), linewidth=1.05, zorder=5,
        )
        for y_ch in (y_channel_min, y_channel_max):
            ax_prof.axhline(
                y_ch, color=PALETTE_BATHY["navy_deep"],
                linestyle=":", linewidth=0.85, alpha=0.75, zorder=4,
            )

        # Cotas técnicas no corte transversal
        y_ch_mid = 0.5 * (y_channel_min + y_channel_max)
        arr_ch = FancyArrowPatch(
            (0.0, y_ch_mid - 55),
            (5.0, y_ch_mid - 55),
            arrowstyle="<|-|>", mutation_scale=8.0,
            color=PALETTE_BATHY["navy_deep"], linewidth=1.10, zorder=6,
        )
        ax_prof.add_patch(arr_ch)
        ax_prof.text(
            2.50, y_ch_mid + 42,
            r"$h = 5{,}0\,\mathrm{m}$",
            fontsize=7.9, fontweight="bold", color=PALETTE_BATHY["navy_deep"],
            ha="center", va="center",
            bbox=dict(boxstyle="square,pad=0.08", facecolor="#E6F1F7", edgecolor="none", alpha=0.92),
            zorder=7,
        )

        for y_sh_pos in (675.0, 2325.0):
            ax_prof.text(
                0.72, y_sh_pos,
                r"$h = 0{,}5\,\mathrm{m}$",
                fontsize=8.0, fontweight="bold", color=PALETTE_BATHY["bed_edge"],
                ha="left", va="center",
                bbox=dict(
                    boxstyle="square,pad=0.12",
                    facecolor=PALETTE_BATHY["bg_canvas"],
                    edgecolor="none",
                    alpha=0.92,
                ),
                zorder=7,
            )

        ax_prof.text(
            -0.14, Ly - 120, r"$z = 0$",
            fontsize=7.9, fontstyle="italic", color=PALETTE_BATHY["navy_deep"],
            rotation=90, ha="right", va="top", zorder=6,
        )

        ax_prof.set_xlim(-0.55, h_max_box)
        ax_prof.set_xticks([0, 0.5, 2.5, 5.0])
        ax_prof.set_xticklabels(["0", "0,5", "2,5", "5,0"])
        ax_prof.tick_params(left=False, labelleft=False)
        ax_prof.set_xlabel(
            r"Profundidade $h\;(\mathrm{m})$",
            fontsize=9.6, color=PALETTE_BATHY["ink_primary"],
        )

        t_prof = ax_prof.set_title(
            r"(b) Corte $A$–$A'$ ($h(y)$)",
            loc="left", pad=8, fontsize=10.2,
            fontweight="bold", color=PALETTE_BATHY["terracotta"],
        )
        t_prof.set_path_effects(
            [pe.withStroke(linewidth=0.15, foreground=PALETTE_BATHY["terracotta"])]
        )

        fig.subplots_adjust(left=0.055, right=0.985, top=0.90, bottom=0.13)

        # Salva sempre em ../figures/, sobrescrevendo execuções anteriores
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
    Lx_def, Ly_def = 6000.0, 3000.0
    Nx_def, Ny_def = 120, 60
    dx_def, dy_def = Lx_def / Nx_def, Ly_def / Ny_def
    yc_def = (np.arange(Ny_def) + 0.5) * dy_def
    ch_mask_def = np.broadcast_to(((yc_def >= 1350.0) & (yc_def < 1650.0))[:, None], (Ny_def, Nx_def))
    demo_fine = {
        "Nx": Nx_def, "Ny": Ny_def, "dx": dx_def, "dy": dy_def,
        "h": np.where(ch_mask_def, 5.0, 0.5),
        "channel_mask": ch_mask_def,
    }
    paths = plot_bathymetry_fine(demo_fine, show=False, return_paths=True)
    for fmt_k, p_out in paths.items():
        print(f"Saved ({fmt_k}): {p_out}")
