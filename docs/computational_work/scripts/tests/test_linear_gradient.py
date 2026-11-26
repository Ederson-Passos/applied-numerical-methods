import sys
import numpy as np


def surface_gradient_fallback(grid, eta=None):
    """Implementação padrão de referência nas faces internas."""
    if eta is None:
        eta = grid["eta"]
    dx = grid["dx"]
    dy = grid["dy"]
    grad_x = (eta[:, 1:] - eta[:, :-1]) / dx
    grad_y = (eta[1:, :] - eta[:-1, :]) / dy
    return grad_x, grad_y


def test_linear_gradient(grid, surface_gradient=None, a=2.5e-3, b=-1.2e-3, c=0.4):
    """
    Testa a exatidão do operador de gradiente discreto contra um campo linear
    eta(x, y) = a*x + b*y + c, onde as derivadas exatas são d(eta)/dx = a e d(eta)/dy = b.
    """
    # 1. Se surface_gradient não foi passado, busca no escopo do notebook (__main__)
    if surface_gradient is None:
        surface_gradient = getattr(sys.modules.get("__main__"), "surface_gradient", None)
    
    # 2. Se ainda não encontrado, usa o fallback de referência
    if surface_gradient is None:
        surface_gradient = surface_gradient_fallback

    eta_test = (
        a * grid["Xc"] +
        b * grid["Yc"] +
        c
    )

    grad_x, grad_y = surface_gradient(
        grid,
        eta_test
    )

    error_x = np.max(np.abs(grad_x - a))
    error_y = np.max(np.abs(grad_y - b))

    print(f"Erro máximo em Gx: {error_x:.2e}")
    print(f"Erro máximo em Gy: {error_y:.2e}")

    assert np.allclose(grad_x, a, rtol=1e-12, atol=1e-12), f"Falha em Gx: {error_x}"
    assert np.allclose(grad_y, b, rtol=1e-12, atol=1e-12), f"Falha em Gy: {error_y}"

    print("Teste do gradiente: APROVADO")
    return grad_x, grad_y


if __name__ == "__main__":
    # Autoteste isolado no terminal
    dx, dy = 150.0, 150.0
    Nx, Ny = 40, 20
    xc = (np.arange(Nx) + 0.5) * dx
    yc = (np.arange(Ny) + 0.5) * dy
    Xc, Yc = np.meshgrid(xc, yc, indexing="xy")
    mock_grid = {"dx": dx, "dy": dy, "Nx": Nx, "Ny": Ny, "Xc": Xc, "Yc": Yc, "eta": np.zeros((Ny, Nx))}
    test_linear_gradient(mock_grid)
