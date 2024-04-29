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


def get_method_list_scheme(methods: list[dict] = None) -> list:
    if methods is None:
        return []
    return [
        get_method_scheme(method)
        for method in methods
    ]


def get_method_scheme(method: dict = None) -> list:
    if method is None:
        return []
    return [
        method['id'],
        *get_currency_scheme(method['currency']),
        method['name_text'],
        method['schema_fields'],
        method['schema_input_fields'],
        method['color'],
        method['bgcolor'],
        method['is_active'],
    ]
