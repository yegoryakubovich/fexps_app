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


from functools import partial

from flet_core import ScrollMode, colors, Row, MainAxisAlignment

from app.controls.information import Text
from app.controls.information.card import Card
from app.controls.layout import AdminBaseView
from app.utils import Fonts, value_to_float
from fexps_api_client import FexpsApiClient
from .get import AccountWalletView


class AccountWalletListView(AdminBaseView):
    route = '/admin/account/wallets/list/get'
    wallets = list[dict]

    def __init__(self, account_id):
        super().__init__()
        self.account_id = account_id

    async def build(self):
        self.client.session.api: FexpsApiClient

        await self.set_type(loading=True)
        self.wallets = await self.client.session.api.admin.wallets.get_list(account_id=self.account_id)
        await self.set_type(loading=False)
        self.scroll = ScrollMode.AUTO
        self.controls = await self.get_controls(
            title=await self.client.session.gtv(key='admin_account_wallet_get_list_view_title'),
            main_section_controls=[
                Card(
                    controls=[
                        Row(
                            controls=[
                                Text(
                                    value=wallet.name,
                                    size=18,
                                    font_family=Fonts.SEMIBOLD,
                                    color=colors.ON_PRIMARY_CONTAINER,
                                ),
                                Text(
                                    value=value_to_float(value=wallet.value),
                                    size=18,
                                    font_family=Fonts.SEMIBOLD,
                                    color=colors.ON_PRIMARY_CONTAINER,
                                ),
                            ],
                            alignment=MainAxisAlignment.SPACE_BETWEEN,
                        ),

                    ],
                    on_click=partial(self.wallet_view, wallet.id),
                    color=colors.PRIMARY_CONTAINER,
                )
                for wallet in self.wallets
            ],
        )

    async def wallet_view(self, wallet_id: int, _):
        await self.client.change_view(
            view=AccountWalletView(
                wallet_id=wallet_id,
            ),
        )
