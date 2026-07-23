def format_brl(value: float) -> str:
    if abs(value) >= 1_000_000:
        return f"R$ {value / 1_000_000:,.1f} mi".replace(",", "X").replace(".", ",").replace("X", ".")
    formatted = f"{value:,.2f}"
    return f"R$ {formatted}".replace(",", "X").replace(".", ",").replace("X", ".")


def format_number(value: float) -> str:
    if abs(value) >= 1_000_000:
        return f"{value / 1_000_000:,.1f} mi".replace(",", "X").replace(".", ",").replace("X", ".")
    if abs(value) >= 1_000:
        return f"{value / 1_000:,.1f} mil".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{value:,.0f}".replace(",", ".")


def format_percent(value: float) -> str:
    return f"{value:.1%}".replace(".", ",")
