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


from typing import Optional

from app.utils.value import value_to_float, value_to_int


async def calculate_request_rate_output_by_output_currency_value(
        calculation: dict,
        output_currency_value: int,
) -> Optional[float]:
    # output rate
    output_currency = calculation['output_method']['currency']
    output_rate_float = value_to_float(value=calculation['output_rate'], decimal=output_currency['rate_decimal'])
    # output values
    output_currency_value_float = value_to_float(value=output_currency_value, decimal=output_currency['decimal'])
    output_value_float = output_currency_value_float / output_rate_float
    output_value = value_to_int(value=output_value_float)

    return value_to_float(value=output_value)
