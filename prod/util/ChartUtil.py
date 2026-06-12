"""
Pure rendering helpers for the little terminal visualizations. These take plain numbers and
return strings, so they are easy to unit test independently of curses.
"""


"""
Renders a horizontal gauge showing where `current` sits between today's `low` and `high`.

I.E. low=160, high=170, current=166 ->  "$160.00 ▕────●─────▏ $170.00"

Returns an empty string when the range is not yet known (high <= low).
"""
def render_range_gauge(low: float, high: float, current: float, width: int = 10) -> str:
    if high <= low:
        return ""

    clamped = min(max(current, low), high)
    position = int(round((clamped - low) / (high - low) * (width - 1)))

    bar = ["─"] * width
    bar[position] = "●"
    return "${:,.2f} ▕{}▏ ${:,.2f}".format(low, "".join(bar), high)
