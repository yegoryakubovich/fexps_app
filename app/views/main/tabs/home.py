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

    async def build(self):
        api: FexpsApiClient
        wallets = await self.client.session.api.client.wallets.get_list()
        base_wallet = wallets[0]
        transactions = [
            {
                'category': 'Payment',
                'description': 'To wallet.5',
                'value': 500,
                'date': '26.02.2024 10:30'
            },
        ]
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
                        ),
                        BalanceRow(wallet_name=base_wallet.name, wallet_value=base_wallet.value),
                        HistoryRow(
                            title_text=await self.client.session.gtv(key='transaction_history'),
                            transactions=transactions
                        ),
                    ],
                ),
                padding=10,
            ),
        ]
