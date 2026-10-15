from capstone.chart import breakeven_svg


def test_svg_is_well_formed():
    svg = breakeven_svg(
        per_request_aud=0.00684,
        fixed_selfhost_aud=7550.72,
        break_even_requests=1_103_906,
        current_requests=1_500_000,
    )
    assert svg.startswith("<svg")
    assert svg.rstrip().endswith("</svg>")
    assert "break-even" in svg
    assert "self-host" in svg


def test_svg_handles_no_break_even():
    svg = breakeven_svg(
        per_request_aud=0.00684,
        fixed_selfhost_aud=7550.72,
        break_even_requests=None,
        current_requests=1_500_000,
    )
    assert svg.startswith("<svg")
    assert "you:" in svg
