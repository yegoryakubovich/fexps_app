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
import logging
from decimal import Decimal
from typing import Optional

from config import settings

"""
CALCULATE
"""


def get_decimal_places(value: float):
    if isinstance(value, str):
        value = value.replace(',', '.')
    return Decimal(str(value)).as_tuple().exponent * -1


def get_fix_rate(rate: float) -> tuple[float, float]:
    if rate > 1:
        result_rate = rate
        result_div = 1
    else:
        result_rate = 1
        result_div = round(1 / rate, 2)
    return result_rate, result_div


def size_value_to_str(value: Optional[int]) -> str:
    if value is None:
        return ''
    value = float(value)
    n, power = 0, 2 ** 10
    power_labels = {0: '', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
    while value > power:
        value /= power
        n += 1
    value = round(value, 1)
    return f'{value} {power_labels[n]}B'


"""
VALUE FORMAT
"""


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
        return ''
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


"""
VALUE GET
"""


def get_input_currency_value(request):
    if request.rate_confirmed:
        result = request.input_currency_value_raw
    else:
        result = request.input_currency_value
    if not result and request.first_line == 'input_currency_value':
        result = request.first_line_value
    return result


def get_input_value(request):
    if request.rate_confirmed:
        result = request.input_value_raw
    else:
        result = request.input_value
    if not result and request.first_line == 'input_value':
        result = request.first_line_value
    return result


def get_output_currency_value(request):
    if request.rate_confirmed:
        result = request.output_currency_value_raw
    else:
        result = request.output_currency_value
    if not result and request.first_line == 'output_currency_value':
        result = request.first_line_value
    return result


def get_output_value(request):
    if request.rate_confirmed:
        result = request.output_value_raw
    else:
        result = request.output_value
    if not result and request.first_line == 'output_value':
        result = request.first_line_value
    return result
