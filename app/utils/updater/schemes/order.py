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


from .currency import get_currency_scheme
from .method import get_method_scheme
from .order_request import get_order_request_scheme
from .request import get_request_scheme
from .requisite import get_requisite_scheme


def get_order_list_scheme(orders: list[dict] = None) -> list:
    if orders is None:
        return []
    return [
        get_order_scheme(order)
        for order in orders
    ]


def get_order_scheme(order: dict = None) -> list:
    if order is None:
        return []
    return [
        order['id'],
        order['type'],
        order['state'],
        order['canceled_reason'],
        *get_request_scheme(order['request']),
        *get_requisite_scheme(order['requisite']),
        *get_currency_scheme(order['currency']),
        order['currency_value'],
        order['value'],
        order['rate'],
        order['currency_value'],
        *get_method_scheme(order['input_method']),
        order['requisite_scheme_fields'],
        order['requisite_fields'],
        order['input_scheme_fields'],
        order['input_fields'],
        *get_order_request_scheme(order['order_request']),
        order['chat_is_read'],
    ]
