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


def get_currency_list_scheme(currencies: list[dict] = None) -> list:
    if currencies is None:
        return []
    return [
        get_currency_scheme(currency)
        for currency in currencies
    ]


def get_currency_scheme(currency: dict = None) -> list:
    if currency is None:
        return []
    return [
        currency['id'],
        currency['id_str'],
        currency['decimal'],
        currency['rate_decimal'],
        currency['div'],
    ]
