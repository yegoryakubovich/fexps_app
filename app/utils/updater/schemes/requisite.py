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

from .currency import get_currency_scheme
from .method import get_method_scheme
from .requisite_data import get_requisite_data_scheme
from .wallet import get_wallet_scheme


def get_requisite_list_scheme(requisites: list[dict] = None) -> list:
    if requisites is None:
        return []
    return [
        get_requisite_scheme(requisite)
        for requisite in requisites
    ]


def get_requisite_scheme(requisite: dict = None) -> list:
    if requisite is None:
        return []
    return [
        requisite['id'],
        requisite['type'],
        requisite['state'],
        *get_wallet_scheme(requisite['wallet']),
        *get_method_scheme(requisite['input_method']),
        *get_method_scheme(requisite['output_method']),
        *get_requisite_data_scheme(requisite['output_requisite_data']),
        *get_currency_scheme(requisite['currency']),
        requisite['currency_value'],
        requisite['total_currency_value'],
        requisite['currency_value_min'],
        requisite['currency_value_max'],
        requisite['rate'],
        requisite['value'],
        requisite['total_value'],
        requisite['value_min'],
        requisite['value_max'],
    ]
