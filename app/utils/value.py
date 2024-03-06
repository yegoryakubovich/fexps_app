from decimal import Decimal

from flet_core import colors

from config import settings


def get_history_color(type_: str):
    return colors.GREEN if type_ == 'receive' else colors.RED


def get_history_value_cleaned(value: str, type_: str) -> str:
    value = int(value) / settings.default_decimal
    if type_ == 'receive':
        return f'+ ${value}'
    return f'- ${value * -1}'


def get_decimal_places(value: float):
    return Decimal(str(value)).as_tuple().exponent * -1
