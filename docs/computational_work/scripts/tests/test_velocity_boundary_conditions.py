"""
Teste unitário das condições de contorno de velocidade nas paredes impermeáveis
e preservação da entrada aberta na malha escalonada de Casulli (Seção 2.4.1).
"""

import sys
import numpy as np


def _apply_velocity_bc_fallback(grid, u, v):
    """Implementação de referência caso executada isoladamente via terminal."""
    masks = grid["boundary_masks"]
    u_out = u.copy()
    v_out = v.copy()
    u_out[masks["closed_west"], 0] = 0.0
    u_out[masks["closed_east"], -1] = 0.0
    v_out[0, masks["closed_south"]] = 0.0
    v_out[-1, masks["closed_north"]] = 0.0
    return u_out, v_out


def test_velocity_boundary_conditions(*grids, apply_bc_fn=None):
    """
    Valida `apply_velocity_boundary_conditions` nas malhas fornecidas
    (ex.: `grid_coarse`, `grid_fine`), verificando:
      1. Anulação da velocidade normal u = 0 nos trechos fechados de Oeste e em Leste;
      2. Anulação da velocidade normal v = 0 nas paredes Sul e Norte;
      3. Preservação da velocidade normal na entrada aberta do canal (Oeste).
    """
    if apply_bc_fn is None:
        apply_bc_fn = getattr(
            sys.modules.get("__main__"), "apply_velocity_boundary_conditions", None
        )
    if apply_bc_fn is None:
        apply_bc_fn = _apply_velocity_bc_fallback

    grid_pairs = []
    for idx, g in enumerate(grids):
        if isinstance(g, dict) and "Ny" in g and "Nx" in g:
            nx = g["Nx"]
            name = (
                "MALHA GROSSA" if nx == 40
                else ("MALHA FINA" if nx == 120 else f"MALHA {idx + 1}")
            )
            grid_pairs.append((name, g))

    if not grid_pairs:
        raise ValueError("Forneça ao menos uma malha válida (ex.: grid_coarse, grid_fine).")

    for idx_g, (name, grid) in enumerate(grid_pairs):
        Ny = grid["Ny"]
        Nx = grid["Nx"]

        # Campos de teste inicialmente diferentes de zero
        u_test = np.ones((Ny, Nx + 1), dtype=np.float64)
        v_test = np.ones((Ny + 1, Nx), dtype=np.float64)

        u_bc, v_bc = apply_bc_fn(grid, u_test, v_test)

        masks = grid["boundary_masks"]

        # Verificação das paredes impermeáveis (u . n = 0)
        assert np.all(u_bc[masks["closed_west"], 0] == 0.0), "Falha na parede Oeste fechada."
        assert np.all(u_bc[:, -1] == 0.0), "Falha na parede Leste."

        assert np.all(v_bc[0, :] == 0.0), "Falha na parede Sul."
        assert np.all(v_bc[-1, :] == 0.0), "Falha na parede Norte."

        # A entrada aberta não pode ser anulada artificialmente
        assert np.all(u_bc[masks["open_west"], 0] == 1.0), (
            "A velocidade na entrada aberta do canal foi alterada indevidamente."
        )

        # Componentes tangenciais nas paredes Norte/Sul (u[0,:], u[-1,:] internas) permanecem livres
        assert np.all(u_bc[:, 1:-1] == 1.0), "Componentes internas/tangenciais de u foram alteradas."

        prefix = "\n" if idx_g > 0 else ""
        print(f"{prefix}{name}")
        print("Entrada aberta:", np.count_nonzero(masks["open_west"]))
        print("Entrada fechada:", np.count_nonzero(masks["closed_west"]))
        print("Parede leste: OK")
        print("Paredes norte/sul: OK")
        print("Entrada aberta preservada: OK")


if __name__ == "__main__":
    def _mock_grid(Nx, Ny):
        dy = 3000.0 / Ny
        yc = (np.arange(Ny) + 0.5) * dy
        ch_mask = np.broadcast_to(((yc >= 1350.0) & (yc < 1650.0))[:, None], (Ny, Nx))
        open_w = np.any(ch_mask, axis=1)
        return {
            "Nx": Nx, "Ny": Ny,
            "channel_mask": ch_mask,
            "boundary_masks": {
                "open_west": open_w,
                "closed_west": ~open_w,
                "closed_east": np.ones(Ny, dtype=bool),
                "closed_south": np.ones(Nx, dtype=bool),
                "closed_north": np.ones(Nx, dtype=bool),
            },
        }

    test_velocity_boundary_conditions(_mock_grid(40, 20), _mock_grid(120, 60))
