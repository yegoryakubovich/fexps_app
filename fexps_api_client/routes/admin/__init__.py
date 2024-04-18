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


from fexps_api_client.utils import BaseRoute
from .accounts import AdminAccountRoute
from .commissions_packs import AdminCommissionPackRoute
from .contacts import AdminContactRoute
from .countries import AdminCountryRoute
from .currencies import AdminCurrencyRoute
from .images import AdminImageRoute
from .languages import AdminLanguageRoute
from .methods import AdminMethodRoute
from .orders import AdminOrderRoute
from .permissions import AdminPermissionRoute
from .roles import AdminRoleRoute
from .texts import AdminTextRoute
from .timezones import AdminTimezoneRoute
from .wallets import AdminWalletRoute


class AdminRoute(BaseRoute):
    prefix = '/admin'

    accounts = AdminAccountRoute()
    commissions_packs = AdminCommissionPackRoute()
    contacts = AdminContactRoute()
    countries = AdminCountryRoute()
    currencies = AdminCurrencyRoute()
    images = AdminImageRoute()
    languages = AdminLanguageRoute()
    methods = AdminMethodRoute()
    orders = AdminOrderRoute()
    permissions = AdminPermissionRoute()
    roles = AdminRoleRoute()
    texts = AdminTextRoute()
    timezones = AdminTimezoneRoute()
    wallets = AdminWalletRoute()
