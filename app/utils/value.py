from flet_core import colors


def get_history_color(value: str):
    return colors.GREEN if int(value) > 0 else colors.RED


def get_history_value_cleaned(value: str):
    if value < 0:
        return f'- ${value * -1}'
    return f'+ ${value}'
