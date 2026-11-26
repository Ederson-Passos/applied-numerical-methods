import sys
import numpy as np


def flux_divergence_fallback(grid, qx, qy):
    """Implementação padrão de referência da divergência de fluxos."""
    dx = grid["dx"]
    dy = grid["dy"]
    div_x = (qx[:, 1:] - qx[:, :-1]) / dx
    div_y = (qy[1:, :] - qy[:-1, :]) / dy
    return div_x + div_y


def test_linear_divergence(grid, flux_divergence=None, a=2.0, b=3.0):
    """
    Testa a exatidão do operador de divergência contra fluxos lineares
    qx = a * Xu e qy = b * Yv, onde div(q) = d(qx)/dx + d(qy)/dy = a + b (constante).
    """
    # 1. Se flux_divergence não foi passado, busca no escopo do notebook (__main__)
    if flux_divergence is None:
        flux_divergence = getattr(sys.modules.get("__main__"), "flux_divergence", None)

    # 2. Se ainda não encontrado, usa o fallback de referência
    if flux_divergence is None:
        flux_divergence = flux_divergence_fallback

    Ny, Nx = grid["Ny"], grid["Nx"]
    qx = a * grid["Xu"]
    qy = b * grid["Yv"]

    divergence = flux_divergence(
        grid,
        qx,
        qy
    )

    expected = a + b

    # Conferência dimensional e finitude
    assert divergence.shape == (Ny, Nx), (
        f"Dimensão incorreta: esperado {(Ny, Nx)}, obtido {divergence.shape}"
    )
    assert np.all(np.isfinite(divergence)), "Divergência contém valores NaN ou Inf."

    error = np.max(np.abs(divergence - expected))

    print(f"Divergência esperada: {expected}")
    print(f"Erro máximo: {error:.2e}")

    assert np.allclose(divergence, expected, rtol=1e-12, atol=1e-12), (
        f"Falha no teste linear de divergência: erro = {error}"
    )

    print("Teste da divergência: APROVADO")
    return divergence
