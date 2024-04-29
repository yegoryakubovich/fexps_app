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


from .wallet import get_wallet_scheme


def get_order_request_list_scheme(order_requests: list[dict] = None) -> list:
    if order_requests is None:
        return []
    return [
        get_order_request_scheme(order_request)
        for order_request in order_requests
    ]


def get_order_request_scheme(order_request: dict = None) -> list:
    if order_request is None:
        return []
    return [
        order_request['id'],
        *get_wallet_scheme(order_request['wallet']),
        order_request['type'],
        order_request['state'],
        order_request['data'],
    ]
