"""
General helper functions for vendor metrics and formatting.
"""


def format_currency(value: float) -> str:
    """Format numerical value to USD currency representation."""
    return f"${value:,.2f}"


def round_score(score: float, decimals: int = 2) -> float:
    """Round score to specified decimal places."""
    return round(float(score), decimals)
