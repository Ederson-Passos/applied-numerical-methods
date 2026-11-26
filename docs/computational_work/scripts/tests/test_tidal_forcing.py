"""
Teste unitário do forçamento harmônico da maré semidiurna M2 na fronteira
aberta nos instantes notáveis t = 0, T/4, T/2, 3T/4 e T (Seção 2.4.2).
"""

import sys
import numpy as np


def _tidal_forcing_fallback(t, amplitude=0.4, period=12.0 * 3600.0):
    """Implementação de referência caso executada isoladamente via terminal."""
    omega = 2.0 * np.pi / period
    return amplitude * np.sin(omega * t)


def test_tidal_forcing(A=0.4, T=12.0 * 3600.0, tidal_forcing_fn=None):
    """
    Valida a função `tidal_forcing(t, A, T)` nos cinco marcos cardinais do
    período semidiurno T = 12 h (0, T/4, T/2, 3T/4, T).
    """
    if tidal_forcing_fn is None:
        tidal_forcing_fn = getattr(sys.modules.get("__main__"), "tidal_forcing", None)
    if tidal_forcing_fn is None:
        tidal_forcing_fn = _tidal_forcing_fallback

    test_times = [
        0.0,
        T / 4.0,
        T / 2.0,
        3.0 * T / 4.0,
        T,
    ]

    for t in test_times:
        eta_tide = tidal_forcing_fn(t, A, T)
        print(
            f"t = {t / 3600.0:5.1f} h | "
            f"Maré = {eta_tide:+.4f} m"
        )

    assert np.isclose(tidal_forcing_fn(0.0, A, T), 0.0, atol=1e-14)
    assert np.isclose(tidal_forcing_fn(T / 4.0, A, T), A, rtol=1e-12, atol=1e-14)
    assert np.isclose(tidal_forcing_fn(T / 2.0, A, T), 0.0, atol=1e-14)
    assert np.isclose(tidal_forcing_fn(3.0 * T / 4.0, A, T), -A, rtol=1e-12, atol=1e-14)
    assert np.isclose(tidal_forcing_fn(T, A, T), 0.0, atol=1e-14)

    print("\nForçamento da maré: APROVADO")


if __name__ == "__main__":
    test_tidal_forcing()
