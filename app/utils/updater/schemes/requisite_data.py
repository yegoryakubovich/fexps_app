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


def get_requisite_data_list_scheme(requisite_datas: list[dict] = None) -> list:
    if requisite_datas is None:
        return []
    return [
        get_requisite_data_scheme(requisite_data)
        for requisite_data in requisite_datas
    ]


def get_requisite_data_scheme(requisite_data: dict = None) -> list:
    if requisite_data is None:
        return []
    return [
        requisite_data['id'],
        requisite_data['account'],
        requisite_data['name'],
        requisite_data['id'],
        *get_method_scheme(requisite_data['method']),
        *get_currency_scheme(requisite_data['currency']),
        requisite_data['fields'],
    ]
