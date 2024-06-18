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

from app.utils.value import value_to_float, value_to_int


async def get_output_commission(commissions_packs: list, value: int) -> Optional[int]:
    commission_pack = None
    for item in commissions_packs:
        if item['value_from'] <= value <= item['value_to']:
            commission_pack = item
            break
        if item['value_from'] <= value and item['value_to'] == 0:
            commission_pack = item
            break
    if not commission_pack:
        return
    value_float = value_to_float(value=value)
    commission_value_float = value_to_float(value=commission_pack['value'])
    commission_percent_float = value_to_float(value=commission_pack['percent'])

    value_float = round(value_float - commission_value_float, 2)
    commission_float = commission_value_float + value_float / (100 - commission_percent_float) * 100 - value_float
    return value_to_int(value=commission_float, round_method=math.ceil)
