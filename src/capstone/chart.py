"""A tiny, dependency-free SVG break-even chart (deterministic, stdlib only).

Draws closed-API cost (variable: a line through the origin) against self-host
cost (fixed: a horizontal line), marks the break-even crossover and the current
monthly volume. No matplotlib, no network — just a string, so it renders the
same byte-for-byte in CI and in a browser.
"""
from __future__ import annotations

W, H = 640, 400
PAD_L, PAD_R, PAD_T, PAD_B = 70, 30, 30, 50
PLOT_W = W - PAD_L - PAD_R
PLOT_H = H - PAD_T - PAD_B


def _x(v: float, x_max: float) -> float:
    return PAD_L + (v / x_max) * PLOT_W if x_max > 0 else PAD_L


def _y(c: float, y_max: float) -> float:
    return PAD_T + PLOT_H - (c / y_max) * PLOT_H if y_max > 0 else PAD_T + PLOT_H


def breakeven_svg(
    per_request_aud: float,
    fixed_selfhost_aud: float,
    break_even_requests: float | None,
    current_requests: float,
) -> str:
    """Return an SVG string for the break-even chart."""
    x_max = max(current_requests * 1.4, (break_even_requests or 0) * 1.4, 1.0)
    closed_at_max = per_request_aud * x_max
    y_max = max(closed_at_max, fixed_selfhost_aud) * 1.15 or 1.0

    closed_line = (
        f'<line x1="{_x(0, x_max):.1f}" y1="{_y(0, y_max):.1f}" '
        f'x2="{_x(x_max, x_max):.1f}" y2="{_y(closed_at_max, y_max):.1f}" '
        'stroke="#d9534f" stroke-width="2.5" />'
    )
    selfhost_line = (
        f'<line x1="{_x(0, x_max):.1f}" y1="{_y(fixed_selfhost_aud, y_max):.1f}" '
        f'x2="{_x(x_max, x_max):.1f}" y2="{_y(fixed_selfhost_aud, y_max):.1f}" '
        'stroke="#0275d8" stroke-width="2.5" />'
    )

    markers = ""
    if break_even_requests and break_even_requests <= x_max:
        bx = _x(break_even_requests, x_max)
        by = _y(per_request_aud * break_even_requests, y_max)
        markers += (
            f'<line x1="{bx:.1f}" y1="{PAD_T}" x2="{bx:.1f}" '
            f'y2="{PAD_T + PLOT_H}" stroke="#999" stroke-dasharray="4 3" />'
            f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="4" fill="#5cb85c" />'
            f'<text x="{bx + 6:.1f}" y="{PAD_T + 16}" font-size="12" '
            f'fill="#333">break-even {break_even_requests / 1e6:.2f}M/mo</text>'
        )
    cx = _x(current_requests, x_max)
    markers += (
        f'<line x1="{cx:.1f}" y1="{PAD_T}" x2="{cx:.1f}" '
        f'y2="{PAD_T + PLOT_H}" stroke="#333" stroke-dasharray="2 2" />'
        f'<text x="{cx + 6:.1f}" y="{PAD_T + 34}" font-size="12" '
        f'fill="#333">you: {current_requests / 1e6:.2f}M/mo</text>'
    )

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" font-family="sans-serif">'
        f'<rect width="{W}" height="{H}" fill="#ffffff" />'
        f'<text x="{W / 2:.0f}" y="18" font-size="14" text-anchor="middle" '
        f'fill="#111">Monthly cost vs volume: closed API vs self-host</text>'
        f'<line x1="{PAD_L}" y1="{PAD_T + PLOT_H}" x2="{PAD_L + PLOT_W}" '
        f'y2="{PAD_T + PLOT_H}" stroke="#333" />'
        f'<line x1="{PAD_L}" y1="{PAD_T}" x2="{PAD_L}" '
        f'y2="{PAD_T + PLOT_H}" stroke="#333" />'
        f'<text x="{PAD_L}" y="{H - 18}" font-size="12" fill="#333">'
        'requests / month -></text>'
        f'<text x="14" y="{PAD_T + 10}" font-size="12" fill="#333">A$/mo</text>'
        f'{selfhost_line}{closed_line}{markers}'
        f'<rect x="{PAD_L + 10}" y="{PAD_T + 6}" width="12" height="12" '
        'fill="#d9534f" />'
        f'<text x="{PAD_L + 28}" y="{PAD_T + 16}" font-size="12" fill="#333">'
        'closed API (variable)</text>'
        f'<rect x="{PAD_L + 10}" y="{PAD_T + 24}" width="12" height="12" '
        'fill="#0275d8" />'
        f'<text x="{PAD_L + 28}" y="{PAD_T + 34}" font-size="12" fill="#333">'
        'self-host (fixed)</text>'
        '</svg>'
    )
