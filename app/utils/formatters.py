def format_brl(value: float) -> str:
    formatted = f"{value:,.2f}"
    return f"R$ {formatted}".replace(",", "X").replace(".", ",").replace("X", ".")


def format_percent(value: float) -> str:
    return f"{value:.1%}".replace(".", ",")
