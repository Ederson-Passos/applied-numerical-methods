"""
Visualização analítica e física do forçamento harmônico da maré semidiurna M2
na fronteira aberta (Seção 2.4.2 — Imposição da Maré na Bacia de Casulli).

Estrutura em 3 painéis complementares (estética Edward Tufte / anos 80–90,
zero sobreposições):
  (a) Ciclo temporal harmônico em x = 0: z(0, y, t) = A sin(2*pi*t / T),
      destacando enchente, vazante, marcos de fase, amplitude A e excursão 2A.
  (b) Corte transversal global na fronteira Oeste (x = 0, 0 <= y <= 3000 m),
      contrastando as paredes impermeáveis rasas (h = 0,5 m) com a fenda do
      canal profundo (h = 5,0 m, 1350 <= y <= 1650 m).
  (c) Detalhe ampliado da abertura do canal (1230 <= y <= 1770 m), evidenciando
      em escala legível a uniformidade transversal (dz/dy = 0) entre preamar
      (+0,4 m), nível médio (0,0 m) e baixa-mar (-0,4 m) sobre as células da malha.

Salva e sobrescreve automaticamente a cada execução em:
  `docs/computational_work/figures/results/swe_tidal_boundary_forcing.{png,svg,pdf}`
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle, FancyArrowPatch
from matplotlib.lines import Line2D

from .style import (
    PALETTE_RESULTS as P,
    rc_tufte_context,
    style_tufte_axes,
    set_crisp_title,
    save_result_figure,
)


def plot_tidal_boundary_forcing(
    grid=None,
    A=0.4,
    T_hours=12.0,
    Ly=3000.0,
    y_ch_min=1350.0,
    y_ch_max=1650.0,
    h_shelf=0.5,
    h_channel=5.0,
    output_stem="swe_tidal_boundary_forcing",
    save_formats=("png", "svg", "pdf"),
    show=True,
    return_paths=False,
):
    """
    Gera a prancha analítica da imposição da maré M2 na fronteira aberta (x = 0),
    sobrescrevendo os arquivos na subpasta `figures/results/` a cada execução.

    Se um dicionário `grid` (ex.: `grid_fine` ou `grid_coarse`) for passado,
    extrai automaticamente `Ly`, `dy` e as faces discretas do canal.
    """
    dy_grid = None
    if isinstance(grid, dict):
        dy_grid = float(grid.get("dy", 50.0))
        Ly = float(grid["Ny"] * dy_grid)
        if "channel_mask" in grid and np.any(grid["channel_mask"]):
            yf_g = np.arange(grid["Ny"] + 1) * dy_grid
            ch_idx = np.where(grid["channel_mask"][:, 0])[0]
            y_ch_min = float(yf_g[ch_idx[0]])
            y_ch_max = float(yf_g[ch_idx[-1] + 1])

    T_sec = T_hours * 3600.0
    omega = 2.0 * np.pi / T_sec

    t_hours = np.linspace(0.0, T_hours, 720)
    z_tide = A * np.sin(omega * (t_hours * 3600.0))

    with plt.rc_context(rc_tufte_context()):
        fig = plt.figure(figsize=(15.2, 6.9), dpi=180)
        gs = fig.add_gridspec(
            2, 2,
            width_ratios=[1.34, 1.00],
            height_ratios=[0.90, 1.18],
            wspace=0.19,
            hspace=0.42,
        )

        ax_time = fig.add_subplot(gs[:, 0])
        ax_glob = fig.add_subplot(gs[0, 1])
        ax_zoom = fig.add_subplot(gs[1, 1])

        # ===================================================================
        # PAINEL (a): Evolução Temporal z(0, y, t) = A sin(2*pi*t / T)
        # ===================================================================
        style_tufte_axes(ax_time, grid=True)

        # Sombreamento harmônico: cota positiva (enchente/preamar) vs. negativa (vazante/baixa-mar)
        ax_time.fill_between(
            t_hours, 0.0, z_tide, where=(z_tide >= 0.0),
            facecolor=P["water_fill"], alpha=0.52, interpolate=True, zorder=1,
            label=r"Cota positiva ($z > 0$, lâmina acima do nível médio)",
        )
        ax_time.fill_between(
            t_hours, 0.0, z_tide, where=(z_tide <= 0.0),
            facecolor=P["ebb_fill"], alpha=0.52, interpolate=True, zorder=1,
            label=r"Cota negativa ($z < 0$, lâmina abaixo do nível médio)",
        )

        # Linhas de referência (z = 0 e envelopes +A, -A estendidos até a cota 2A)
        ax_time.axhline(0.0, color=P["ink_secondary"], lw=1.05, ls="-", zorder=2)
        ax_time.plot([0.0, 12.55], [+A, +A], color=P["cerulean"], lw=0.90, ls=(0, (5, 3)), alpha=0.80, zorder=2)
        ax_time.plot([0.0, 12.55], [-A, -A], color=P["terracotta"], lw=0.90, ls=(0, (5, 3)), alpha=0.80, zorder=2)

        # Curva senoidal principal
        ax_time.plot(
            t_hours, z_tide, color=P["navy_deep"], lw=2.25, zorder=4,
            label=rf"$z(0, y, t) = A\sin(2\pi t / T)\;\; (A = {A:.1f}\,\mathrm{{m}},\, T = {T_hours:.0f}\,\mathrm{{h}})$".replace(".", "{,}"),
        )

        # Cota da Amplitude A = 0,4 m sob o pico t = 3 h (espaço interno amplo)
        arr_amp = FancyArrowPatch(
            (3.0, 0.01), (3.0, A - 0.01),
            arrowstyle="<|-|>", mutation_scale=8.5,
            color=P["cerulean"], linewidth=1.20, zorder=5,
        )
        ax_time.add_patch(arr_amp)
        ax_time.text(
            3.18, 0.50 * A,
            r"Amplitude" + "\n" + r"$A = 0{,}4\,\mathrm{m}$",
            fontsize=8.4, fontweight="bold", color=P["cerulean"],
            ha="left", va="center",
            bbox=dict(boxstyle="square,pad=0.12", facecolor=P["water_fill"], edgecolor="none", alpha=0.72),
            zorder=6,
        )

        # Cota externa direita da Excursão Total 2A = 0,8 m (em t = 12,42 h, fora da senoide!)
        x_exc = 12.42
        arr_exc = FancyArrowPatch(
            (x_exc, -A), (x_exc, +A),
            arrowstyle="<|-|>", mutation_scale=8.5,
            color=P["ink_primary"], linewidth=1.15, zorder=5,
        )
        ax_time.add_patch(arr_exc)
        ax_time.text(
            x_exc + 0.16, 0.0,
            "Excursão\n" + r"$2A = 0{,}8\,\mathrm{m}$",
            fontsize=8.1, fontweight="bold", color=P["ink_primary"],
            ha="left", va="center", rotation=90,
            bbox=dict(boxstyle="square,pad=0.08", facecolor=P["panel_bg"], edgecolor="none", alpha=0.95),
            zorder=6,
        )

        # Cinco instantes-chave posicionados nos quadrantes vazios da senoide (zero colisão!)
        milestones = [
            (0.0,  0.0, r"$t = 0\,\mathrm{h}$" + "\nInício ($0{,}0\,\mathrm{m}$)", P["ink_secondary"], (0.20, -0.09), "left",   "top"),
            (3.0,  +A,  r"$t = 3\,\mathrm{h}\;(T/4)$ — Preamar ($+0{,}4\,\mathrm{m}$)", P["cerulean"],      (3.00, +0.46), "center", "bottom"),
            (6.0,  0.0, r"$t = 6\,\mathrm{h}\;(T/2)$" + "\nMeia-maré ($0{,}0\,\mathrm{m}$)", P["teal_mid"],      (6.22, +0.09), "left",   "bottom"),
            (9.0,  -A,  r"$t = 9\,\mathrm{h}\;(3T/4)$ — Baixa-mar ($-0{,}4\,\mathrm{m}$)", P["terracotta"],    (9.00, -0.46), "center", "top"),
            (12.0, 0.0, r"$t = 12\,\mathrm{h}\;(T)$" + "\nFim do ciclo", P["ink_secondary"], (11.82, +0.26), "right",  "bottom"),
        ]

        for th, zh, lbl_m, col_m, (tx, ty), ha_m, va_m in milestones:
            ax_time.plot(
                th, zh, marker="o", markersize=6.8,
                markerfacecolor=col_m, markeredgecolor=P["panel_bg"],
                markeredgewidth=1.15, zorder=7,
            )
            # Guia curta apenas para o ponto t = 12 h para deixá-lo distante do eixo z = 0
            if np.isclose(th, 12.0):
                ax_time.plot([th, tx + 0.05], [zh + 0.02, ty - 0.02],
                             color=col_m, lw=0.75, ls="-", zorder=5)
            ax_time.text(
                tx, ty, lbl_m,
                fontsize=8.25, fontweight="bold", color=col_m,
                ha=ha_m, va=va_m, linespacing=1.18,
                bbox=dict(
                    boxstyle="square,pad=0.14",
                    facecolor=P["panel_bg"],
                    edgecolor=col_m,
                    linewidth=0.60,
                    alpha=0.94,
                ),
                zorder=8,
            )

        ax_time.set_xlim(-0.45, 13.15)
        ax_time.set_ylim(-0.64, 0.64)
        ax_time.set_xticks([0, 3, 6, 9, 12])
        ax_time.set_xticklabels([
            r"$0\,\mathrm{h}$" + "\n" + r"$(0)$",
            r"$3\,\mathrm{h}$" + "\n" + r"$(T/4)$",
            r"$6\,\mathrm{h}$" + "\n" + r"$(T/2)$",
            r"$9\,\mathrm{h}$" + "\n" + r"$(3T/4)$",
            r"$12\,\mathrm{h}$" + "\n" + r"$(T)$",
        ])
        ax_time.set_yticks([-0.6, -0.4, -0.2, 0.0, 0.2, 0.4, 0.6])
        ax_time.set_yticklabels(["−0,6", "−0,4", "−0,2", "0,0", "+0,2", "+0,4", "+0,6"])
        ax_time.set_xlabel(
            r"Tempo $t$ ao longo de um período semidiurno ($T = 12\,\mathrm{h} = 43\,200\,\mathrm{s}$)",
            fontsize=9.4, color=P["ink_primary"], labelpad=6,
        )
        ax_time.set_ylabel(
            r"Elevação prescrita $z(0, y, t)\;(\mathrm{m})$",
            fontsize=9.4, color=P["ink_primary"],
        )
        set_crisp_title(
            ax_time,
            r"(a) Evolução Temporal na Entrada Aberta ($x = 0$, $y \in [1350, 1650]\,\mathrm{m}$)",
            fontsize=10.0,
        )

        # Legenda posicionada no quadrante inferior-esquerdo 100% livre (t in [0, 5.5], z < -0.25)
        leg1 = ax_time.legend(
            loc="lower left",
            bbox_to_anchor=(0.015, 0.02),
            frameon=True,
            facecolor=P["legend_bg"],
            edgecolor=P["ink_secondary"],
            fontsize=8.05,
            handlelength=1.9,
        )
        leg1.get_frame().set_linewidth(0.80)
        leg1.get_frame().set_boxstyle("square,pad=0.25")

        # ===================================================================
        # PAINEL (b): Corte Transversal Global em x = 0 (0 <= y <= 3000 m)
        # ===================================================================
        style_tufte_axes(ax_glob, grid=True)

        z_floor_box = -5.75
        # Polígono exato do leito em degrau com hachura geológica estilo Figura 1
        bed_pts_glob = [
            (0.0, z_floor_box),
            (Ly, z_floor_box),
            (Ly, -h_shelf),
            (y_ch_max, -h_shelf),
            (y_ch_max, -h_channel),
            (y_ch_min, -h_channel),
            (y_ch_min, -h_shelf),
            (0.0, -h_shelf),
        ]
        ax_glob.add_patch(Polygon(
            bed_pts_glob, closed=True,
            facecolor=P["bed_fill"], edgecolor=P["bed_hatch"],
            hatch="///", linewidth=0.0, zorder=2,
        ))
        ax_glob.plot(
            [0.0, y_ch_min, y_ch_min, y_ch_max, y_ch_max, Ly],
            [-h_shelf, -h_shelf, -h_channel, -h_channel, -h_shelf, -h_shelf],
            color=P["bed_edge"], lw=1.45, zorder=4,
        )

        # Faixas laterais sombreadas indicando parede impermeável fechada (u = 0)
        ax_glob.axvspan(0.0, y_ch_min, ymin=0.0, ymax=1.0, facecolor=P["wall_shade"], alpha=0.40, zorder=1)
        ax_glob.axvspan(y_ch_max, Ly, ymin=0.0, ymax=1.0, facecolor=P["wall_shade"], alpha=0.40, zorder=1)

        # Coluna d'água no canal central aberto
        ax_glob.add_patch(Rectangle(
            (y_ch_min, -h_channel), y_ch_max - y_ch_min, h_channel,
            facecolor=P["water_deep"], edgecolor="none", alpha=0.68, zorder=3,
        ))
        ax_glob.plot([y_ch_min, y_ch_max], [+A, +A], color=P["cerulean"], lw=1.8, zorder=5)
        ax_glob.plot([y_ch_min, y_ch_max], [-A, -A], color=P["terracotta"], lw=1.8, zorder=5)

        # Rótulos limpos sobre as abas fechadas e janela de recorte âmbar para (c)
        for y_wall_c, tag_dir in [(675.0, "Sul"), (2325.0, "Norte")]:
            ax_glob.text(
                y_wall_c, -2.95,
                f"Parede fechada ({tag_dir})\n" + r"$u = 0\;\;(h = 0{,}5\,\mathrm{m})$",
                fontsize=8.0, fontweight="bold", color=P["ink_secondary"],
                ha="center", va="center", linespacing=1.18,
                bbox=dict(boxstyle="square,pad=0.18", facecolor=P["panel_bg"], edgecolor=P["bed_edge"], lw=0.6, alpha=0.94),
                zorder=6,
            )

        # Retângulo de recorte âmbar apontando para o painel (c)
        ax_glob.add_patch(Rectangle(
            (1230.0, -1.05), 540.0, 2.00,
            facecolor="none", edgecolor=P["amber_acc"], lw=1.45, ls="-", zorder=7,
        ))
        ax_glob.text(
            1810.0, 0.55, r"Detalhe (c)",
            fontsize=8.0, fontweight="bold", fontstyle="italic", color=P["amber_acc"],
            ha="left", va="center",
            bbox=dict(boxstyle="square,pad=0.10", facecolor=P["panel_bg"], edgecolor="none", alpha=0.90),
            zorder=7,
        )
        ax_glob.text(
            0.5 * (y_ch_min + y_ch_max), -3.20,
            r"$h = 5{,}0\,\mathrm{m}$",
            fontsize=7.8, fontweight="bold", color=P["navy_deep"],
            rotation=90, ha="center", va="center",
            bbox=dict(boxstyle="square,pad=0.08", facecolor="#E4F0F7", edgecolor="none", alpha=0.90),
            zorder=6,
        )

        ax_glob.set_xlim(0.0, Ly)
        ax_glob.set_ylim(z_floor_box, 1.18)
        ax_glob.set_xticks([0, 750, int(y_ch_min), int(y_ch_max), 2250, int(Ly)])
        ax_glob.set_yticks([-5.0, -2.5, 0.0])
        ax_glob.set_yticklabels(["−5,0", "−2,5", "0,0"])
        ax_glob.set_xlabel(r"Coordenada transversal $y\;(\mathrm{m})$ na fronteira Oeste ($x = 0$)", fontsize=8.9, color=P["ink_primary"])
        ax_glob.set_ylabel(r"Cota $z\;(\mathrm{m})$", fontsize=9.0, color=P["ink_primary"])
        set_crisp_title(
            ax_glob,
            r"(b) Corte Global em $x = 0$ ($L_y = 3000\,\mathrm{m}$): Paredes vs. Canal",
            fontsize=9.6,
        )

        # ===================================================================
        # PAINEL (c): Detalhe Ampliado da Boca Aberta (1230 <= y <= 1770 m)
        #             Escala legível sem qualquer sobreposição!
        # ===================================================================
        style_tufte_axes(ax_zoom, grid=True)
        yz0, yz1 = 1230.0, 1770.0
        zz_bot, zz_top = -1.02, 0.92

        # Ombreiras laterais do leito raso (y < 1350 e y > 1650, h = 0,5 m) + parede impermeável acima
        for xa_s, xb_s in [(yz0, y_ch_min), (y_ch_max, yz1)]:
            ax_zoom.add_patch(Rectangle(
                (xa_s, zz_bot), xb_s - xa_s, -h_shelf - zz_bot,
                facecolor=P["bed_fill"], edgecolor=P["bed_hatch"],
                hatch="///", linewidth=0.0, zorder=3,
            ))
            ax_zoom.add_patch(Rectangle(
                (xa_s, -h_shelf), xb_s - xa_s, zz_top - (-h_shelf),
                facecolor=P["wall_shade"], edgecolor="none", alpha=0.65, zorder=2,
            ))

        # Contorno das quinas batimétricas em y = 1350 e y = 1650 m
        ax_zoom.plot([yz0, y_ch_min, y_ch_min], [-h_shelf, -h_shelf, zz_bot], color=P["bed_edge"], lw=1.55, zorder=5)
        ax_zoom.plot([y_ch_max, y_ch_max, yz1], [zz_bot, -h_shelf, -h_shelf], color=P["bed_edge"], lw=1.55, zorder=5)
        ax_zoom.axvline(y_ch_min, color=P["ink_secondary"], lw=1.0, ls=":", zorder=5)
        ax_zoom.axvline(y_ch_max, color=P["ink_secondary"], lw=1.0, ls=":", zorder=5)

        # Preenchimento da coluna d'água dentro da boca do canal:
        #   - Água permanente abaixo da baixa-mar (-0,4 m até zz_bot)
        #   - Faixa de oscilação da maré [-0,4 m, +0,4 m]
        ax_zoom.add_patch(Rectangle(
            (y_ch_min, zz_bot), y_ch_max - y_ch_min, -A - zz_bot,
            facecolor=P["water_deep"], edgecolor="none", alpha=0.55, zorder=1.5,
        ))
        ax_zoom.add_patch(Rectangle(
            (y_ch_min, -A), y_ch_max - y_ch_min, 2.0 * A,
            facecolor=P["water_fill"], edgecolor="none", alpha=0.45, zorder=1.8,
        ))

        # Se dy_grid disponível (ex.: 50 m na malha fina), marca sutilmente as divisões das células do canal
        if dy_grid is not None and dy_grid <= 150.0:
            y_faces_ch = np.arange(y_ch_min, y_ch_max + 0.1, dy_grid)
            for yf_c in y_faces_ch[1:-1]:
                ax_zoom.axvline(yf_c, color=P["navy_deep"], lw=0.55, ls="--", alpha=0.30, zorder=2)

        # Três patamares horizontais planos (mostrando dz / dy = 0)
        y_open = np.array([y_ch_min, y_ch_max])
        ax_zoom.plot(y_open, [+A, +A], color=P["cerulean"], lw=2.4, zorder=6)
        ax_zoom.plot(y_open, [0.0, 0.0], color=P["teal_mid"], lw=1.9, ls="-.", zorder=6)
        ax_zoom.plot(y_open, [-A, -A], color=P["terracotta"], lw=2.4, zorder=6)

        # Setas verticais sincronizadas demonstrando movimento uniforme em y (pistão plano)
        for y_arr in (1400.0, 1500.0, 1600.0):
            arr_sync = FancyArrowPatch(
                (y_arr, -A + 0.02), (y_arr, +A - 0.02),
                arrowstyle="<|-|>", mutation_scale=8.5,
                color=P["navy_deep"], linewidth=1.15, alpha=0.85, zorder=7,
            )
            ax_zoom.add_patch(arr_sync)

        # Rótulos claros e 100% contidos entre as paredes do canal [1350, 1650]
        ax_zoom.text(
            1500.0, +A + 0.08,
            r"Preamar ($t = 3\,\mathrm{h}$): $z = +0{,}4\,\mathrm{m}$  ($\partial z / \partial y = 0$)",
            fontsize=7.85, fontweight="bold", color=P["cerulean"],
            ha="center", va="bottom",
            bbox=dict(boxstyle="square,pad=0.08", facecolor=P["panel_bg"], edgecolor="none", alpha=0.93),
            zorder=8,
        )
        ax_zoom.text(
            1500.0, -A - 0.08,
            r"Baixa-mar ($t = 9\,\mathrm{h}$): $z = -0{,}4\,\mathrm{m}$" + "\n"
            + r"($\downarrow$ canal segue até $z = -5{,}0\,\mathrm{m}$)",
            fontsize=7.75, fontweight="bold", color=P["terracotta"],
            ha="center", va="top", linespacing=1.18,
            bbox=dict(boxstyle="square,pad=0.08", facecolor=P["panel_bg"], edgecolor="none", alpha=0.92),
            zorder=8,
        )

        # Rótulos laterais nas ombreiras fechadas
        for y_sh_c in (1290.0, 1710.0):
            ax_zoom.text(
                y_sh_c, 0.12,
                "Parede\nfechada\n" + r"($u = 0$)",
                fontsize=7.75, fontweight="bold", color=P["ink_secondary"],
                ha="center", va="center", linespacing=1.15, zorder=7,
            )
            ax_zoom.text(
                y_sh_c, -0.76,
                r"$z = -0{,}5\,\mathrm{m}$",
                fontsize=7.3, fontweight="bold", color=P["bed_edge"],
                ha="center", va="center",
                bbox=dict(boxstyle="square,pad=0.06", facecolor=P["panel_bg"], edgecolor="none", alpha=0.90),
                zorder=7,
            )

        # Legenda compacta no topo apenas para os 3 níveis
        leg_handles_z = [
            Line2D([0], [0], color=P["cerulean"], lw=2.3, label=r"$+0{,}4\,\mathrm{m}$ (Preamar)"),
            Line2D([0], [0], color=P["teal_mid"], lw=1.8, ls="-.", label=r"$0{,}0\,\mathrm{m}$ (Nível médio)"),
            Line2D([0], [0], color=P["terracotta"], lw=2.3, label=r"$-0{,}4\,\mathrm{m}$ (Baixa-mar)"),
        ]
        leg2 = ax_zoom.legend(
            handles=leg_handles_z,
            loc="upper center",
            bbox_to_anchor=(0.5, 0.99),
            ncol=3,
            frameon=True,
            facecolor=P["legend_bg"],
            edgecolor=P["ink_secondary"],
            fontsize=7.65,
            handlelength=1.6,
            columnspacing=0.95,
        )
        leg2.get_frame().set_linewidth(0.75)
        leg2.get_frame().set_boxstyle("square,pad=0.18")

        ax_zoom.set_xlim(yz0, yz1)
        ax_zoom.set_ylim(zz_bot, zz_top)
        ax_zoom.set_xticks([1250, 1350, 1450, 1500, 1550, 1650, 1750])
        ax_zoom.set_yticks([-0.8, -0.4, 0.0, 0.4, 0.8])
        ax_zoom.set_yticklabels(["−0,8", "−0,4", "0,0", "+0,4", "+0,8"])
        ax_zoom.set_xlabel(r" Detalhe na abertura do canal $y\;(\mathrm{m})$  ($1350 \leq y \leq 1650\,\mathrm{m}$)", fontsize=8.9, color=P["ink_primary"])
        ax_zoom.set_ylabel(r"Cota $z\;(\mathrm{m})$", fontsize=9.0, color=P["ink_primary"])
        set_crisp_title(
            ax_zoom,
            r"(c) Detalhe da Boca Aberta: Movimento Uniforme em $y$ ($\partial z / \partial y = 0$)",
            fontsize=9.6,
            color=P["amber_acc"],
        )

        fig.subplots_adjust(left=0.055, right=0.985, top=0.925, bottom=0.105)

        # Persistência automática obrigatória em `figures/results/`
        saved_paths = save_result_figure(
            fig, output_stem=output_stem, save_formats=save_formats, dpi=300
        )

        if show:
            plt.show()
        plt.close(fig)

    return saved_paths if return_paths else None


if __name__ == "__main__":
    paths = plot_tidal_boundary_forcing(show=False, return_paths=True)
    for fmt_k, p_out in paths.items():
        print(f"Saved ({fmt_k}): {p_out}")
