#
# (c) 2024, Yegor Yakubovich, yegoryakubovich.com, personal@yegoryakybovich.com
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


from decimal import Decimal
from typing import Optional

from config import settings


def get_decimal_places(value: float):
    if isinstance(value, str):
        value = value.replace(',', '.')
    return Decimal(str(value)).as_tuple().exponent * -1


def value_to_int(value: Optional[float], decimal: int = settings.default_decimal) -> Optional[int]:
    if isinstance(value, str):
        value = value.replace(',', '.')
    if not value and value != 0:
        return
    return round(float(value) * (10 ** decimal))


def value_to_float(value: Optional[int], decimal: int = settings.default_decimal) -> Optional[float]:
    if isinstance(value, str):
        value = value.replace(',', '.')
    if not value and value != 0:
        return
    return round(float(value) / (10 ** decimal), 2)


def value_to_str(value: Optional[float]) -> Optional[str]:
    if isinstance(value, str):
        value = value.replace(',', '.')
    if not value and value != 0:
        return
    return f'{float(value):,}'.replace(',', ' ')


def requisite_value_to_str(
        value: Optional[str],
        card_number_replaces: bool = False,
) -> Optional[str]:
    if not value and value != 0:
        return
    value = str(value)
    if len(value) == 16:
        value_list = [f'{value[i * 4:(i * 4) + 4]}' for i in range(4)]
        if card_number_replaces:
            value_list[2], value_list[3] = '****', '****'
        value = ' '.join(value_list)
    return value
