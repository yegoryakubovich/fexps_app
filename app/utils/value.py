from typing import Optional

from config import settings


def get_fix_value(value: Optional[int], decimal: int = settings.default_decimal) -> float:
    value = float(value)
    return value / 10 ** decimal
