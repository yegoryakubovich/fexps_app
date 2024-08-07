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


from .account import get_account_scheme, get_account_list_scheme
from .currency import get_currency_scheme, get_currency_list_scheme
from .file import get_file_scheme, get_file_list_scheme
from .method import get_method_scheme, get_method_list_scheme
from .order import get_order_scheme, get_order_list_scheme
from .order_request import get_order_request_scheme, get_order_request_list_scheme
from .request import get_request_scheme, get_request_list_scheme
from .requisite import get_requisite_scheme, get_requisite_list_scheme
from .requisite_data import get_requisite_data_scheme, get_requisite_data_list_scheme
from .transfer import get_transfer_scheme, get_transfer_list_scheme
from .wallet import get_wallet_scheme, get_wallet_list_scheme
