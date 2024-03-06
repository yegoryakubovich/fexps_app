from decimal import Decimal

from flet_core import colors

from config import settings


def get_history_color(value: str):
    return colors.GREEN if int(value) > 0 else colors.RED


def get_history_value_cleaned(value: str):
    value = int(value) / settings.default_decimal
    if value < 0:
        return f'- ${value * -1}'
    return f'+ ${value}'


def get_decimal_places(value: float):
    return Decimal(str(value)).as_tuple().exponent * -1
