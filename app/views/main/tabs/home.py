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


import webbrowser

from flet_core import Column, Container

from app.controls.information.account_row import AccountInfoRow
from app.controls.information.balance_row import BalanceRow
from app.controls.information.history_row import HistoryRow
from app.views.main.tabs.base import BaseTab
from config import settings
from fexps_api_client import FexpsApiClient


async def support(_):
    webbrowser.open(settings.url_telegram)


class HomeTab(BaseTab):
    exercise: list[dict] = None
    scopes: list[dict]

    async def get_account_row(self):
        return AccountInfoRow(
            hello_text=await self.client.session.gtv(key='hello'),
            name_text=self.client.session.account.firstname,
        )

    async def get_balance_row(self):
        return BalanceRow(
            wallets=self.client.session.wallets,
            current_wallet=self.client.session.current_wallet,
            on_change=self.change_wallet,
        )

    async def build(self):
        self.client.session.wallets = await self.client.session.api.client.wallets.get_list()
        self.client.session.current_wallet = await self.client.session.api.client.wallets.get(
            id_=self.client.session.current_wallet.id,
        )
        self.controls = [
            Container(
                content=Column(
                    controls=[
                        Container(
                            content=AccountInfoRow(
                                hello_text=await self.client.session.gtv(key='hello'),
                                name_text=self.client.session.account.firstname,
                            ),
                            alignment=alignment.center,
                            on_click=self.go_admin,
                            padding=padding.symmetric(vertical=4),
                            ink=True,
                            content=await self.get_account_row(),
                            on_click=self.go_account,
                        ),
                        BalanceRow(wallet_name=base_wallet.name, wallet_value=base_wallet.value),
                        HistoryRow(
                            title_text=await self.client.session.gtv(key='transaction_history'),
                            transactions=transactions
                        ),
                        await self.get_balance_row(),
                        await self.get_history(),
                    ],
                ),
                padding=10,
            ),
        ]


    async def go_account(self, _):
        from app.views.client.account import AccountView
        await self.client.change_view(view=AccountView())

    async def change_wallet(self, event: ControlEvent):
        self.client.session.wallets = await self.client.session.api.client.wallets.get_list()
        self.client.session.current_wallet = await self.client.session.api.client.wallets.get(id_=event.data)
        self.controls[0].content.controls[1] = await self.get_balance_row()
        self.controls[0].content.controls[3] = await self.get_history()
        await self.update_async()
