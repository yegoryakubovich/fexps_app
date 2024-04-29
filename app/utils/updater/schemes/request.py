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
from .requisite_data import get_requisite_data_scheme
from .wallet import get_wallet_scheme


def get_request_list_scheme(requests: list[dict] = None) -> list:
    if requests is None:
        return []
    return [
        get_request_scheme(request)
        for request in requests
    ]


def get_request_scheme(request: dict = None) -> list:
    if request is None:
        return []
    return [
        request['id'],
        request['name'],
        *get_wallet_scheme(request['wallet']),
        request['type'],
        request['state'],
        request['rate_decimal'],
        request['rate_confirmed'],
        request['difference_confirmed'],
        request['first_line'],
        request['first_line_value'],
        *get_currency_scheme(request['input_currency']),
        request['input_currency_value_raw'],
        request['input_currency_value'],
        request['input_value_raw'],
        request['input_value'],
        request['input_rate_raw'],
        request['input_rate'],
        request['commission_value'],
        request['rate'],
        *get_currency_scheme(request['output_currency']),
        request['output_currency_value_raw'],
        request['output_currency_value'],
        request['output_value_raw'],
        request['output_value'],
        request['output_rate_raw'],
        request['output_rate'],
        *get_method_scheme(request['input_method']),
        *get_requisite_data_scheme(request['output_requisite_data']),
        *get_method_scheme(request['output_method']),
        request['date'],
        request['waiting_delta'],
    ]
