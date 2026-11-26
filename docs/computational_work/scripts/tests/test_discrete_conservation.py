import sys
import numpy as np


def flux_divergence_fallback(grid, qx, qy):
    """Implementação padrão de referência da divergência de fluxos."""
    dx = grid["dx"]
    dy = grid["dy"]
    div_x = (qx[:, 1:] - qx[:, :-1]) / dx
    div_y = (qy[1:, :] - qy[:-1, :]) / dy
    return div_x + div_y


def test_discrete_conservation(grid, flux_divergence=None, seed=42):
    """
    Testa a conservação discreta exata do operador de divergência:
    A soma telescópica da divergência no volume cancela todos os fluxos das faces
    internas, reduzindo-se rigorosamente ao fluxo líquido pelas fronteiras externas:
        sum_{j, i} div[j, i] * dx * dy == boundary_flux
    """
    # 1. Se flux_divergence não foi passado, busca no escopo do notebook (__main__)
    if flux_divergence is None:
        flux_divergence = getattr(sys.modules.get("__main__"), "flux_divergence", None)

    # 2. Se ainda não encontrado, usa o fallback de referência
    if flux_divergence is None:
        flux_divergence = flux_divergence_fallback

    rng = np.random.default_rng(seed)

    Nx = grid["Nx"]
    Ny = grid["Ny"]

    dx = grid["dx"]
    dy = grid["dy"]

    # Campos aleatórios de fluxo nas faces verticais (u) e horizontais (v)
    qx = rng.standard_normal((Ny, Nx + 1))
    qy = rng.standard_normal((Ny + 1, Nx))

    divergence = flux_divergence(
        grid,
        qx,
        qy
    )

    # Integral discreta da divergência em todo o domínio
    volume_integral = (
        np.sum(divergence) * dx * dy
    )

    # Fluxo líquido integrado nas 4 fronteiras externas
    boundary_flux = (
        dy * np.sum(qx[:, -1] - qx[:, 0]) +
        dx * np.sum(qy[-1, :] - qy[0, :])
    )

    error = abs(volume_integral - boundary_flux)

    print(f"Integral da divergência: {volume_integral:.6e}")
    print(f"Fluxo pelas fronteiras:  {boundary_flux:.6e}")
    print(f"Erro de conservação:     {error:.2e}")

    assert np.isclose(
        volume_integral,
        boundary_flux,
        rtol=1e-12,
        atol=1e-12
    ), f"Falha na conservação discreta: erro = {error:.2e}"

    print("Conservação discreta: APROVADA")
    return volume_integral, boundary_flux, error

