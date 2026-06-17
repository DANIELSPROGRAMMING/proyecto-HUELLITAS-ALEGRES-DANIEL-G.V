from django import template

register = template.Library()


@register.filter(name='pesos')
def pesos(value):
    """Format a number as Colombian pesos with dots as thousands separator.
    Handles integers and decimals.
    Examples: 78000 → $78.000  |  361500.50 → $361.500,50  |  0 → $0
    """
    try:
        value = float(value)
    except (ValueError, TypeError):
        return '$0'

    if value == int(value):
        # Integer: 78000 → $78.000
        formatted = f'{int(value):,}'.replace(',', '.')
        return f'${formatted}'
    else:
        # Decimal: split integer and decimal parts
        int_part = int(value)
        dec_str = f'{value - int_part:.2f}'.split('.')[1]
        formatted_int = f'{int_part:,}'.replace(',', '.')
        return f'${formatted_int},{dec_str}'


@register.filter(name='miles')
def miles(value):
    """Format a number with dots as thousands separator, no currency symbol.
    Example: 85000 → 85.000
    """
    try:
        value = int(value)
    except (ValueError, TypeError):
        return '0'
    return f'{value:,}'.replace(',', '.')