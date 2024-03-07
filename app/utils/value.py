from decimal import Decimal

from flet_core import colors

from config import settings


def get_history_color(operation: str):
    if operation == 'send':
        return colors.RED
    elif operation == 'receive':
        return colors.GREEN
    return colors.GREY


def get_history_value_cleaned(value: str, operation: str) -> str:
    value = int(value) / settings.default_decimal
    if operation == 'send':
        return f'- ${value}'
    elif operation == 'receive':
        return f'+ ${value}'
    return f'${value}'


def get_decimal_places(value: float):
    return Decimal(str(value)).as_tuple().exponent * -1
