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


import math
from typing import Optional

from app.utils.calculations.commissions import get_output_commission
from app.utils.value import value_to_float, value_to_int


async def calculate_request_rate_input_by_input_value(
        calculation: dict,
        input_value: int,
) -> Optional[float]:
    # input rate
    input_currency = calculation['input_method']['currency']
    input_rate_float = value_to_float(value=calculation['input_rate'], decimal=input_currency['rate_decimal'])
    # output values
    output_value = input_value
    output_value_float = value_to_float(value=output_value)
    # commission
    commission = await get_output_commission(commissions_packs=calculation['commissions_packs'], value=output_value)
    if commission is None:
        return
    commission_float = value_to_float(value=commission)
    # input values
    input_value_float = output_value_float + commission_float
    input_currency_value_float = input_value_float * input_rate_float
    input_currency_value = value_to_int(value=input_currency_value_float, decimal=input_currency['decimal'])
    input_currency_value = math.ceil(input_currency_value / input_currency['div']) * input_currency['div']

    return value_to_float(value=input_currency_value, decimal=input_currency['decimal'])
