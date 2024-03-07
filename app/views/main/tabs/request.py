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


from flet_core import Column, Container

from app.controls.information.home.scope_row import ScopeRow
from app.views.main.tabs.base import BaseTab


class RequestTab(BaseTab):
    exercise: list[dict] = None
    scopes: list[dict]

    async def get_scope_row(self):
        self.scopes = [
            dict(
                name=await self.client.session.gtv(key=f'request_create'),
                on_click=self.go_create,
            ),
            dict(
                name=await self.client.session.gtv(key=f'request_test'),
            ),
        ]
        return ScopeRow(scopes=self.scopes)

    # async def get_history(self):
    #     transfers = await self.client.session.api.client.transfers.search(
    #         wallet_id=self.client.session.current_wallet.id,
    #         page=1,
    #     )
    #     return HistoryRow(
    #         title_text=await self.client.session.gtv(key='transaction_history'),
    #         transfers=transfers.transfers
    #     )

    async def build(self):
        self.client.session.wallets = await self.client.session.api.client.wallets.get_list()
        self.client.session.current_wallet = await self.client.session.api.client.wallets.get(
            id_=self.client.session.current_wallet.id,
        )
        self.controls = [
            Container(
                content=Column(
                    controls=[
                        await self.get_scope_row(),
                        # await self.get_history(),
                    ],
                ),
                padding=10,
            ),
        ]

    async def go_create(self, _):
        from app.views.client.requests import RequestCreateView
        await self.client.change_view(view=RequestCreateView(current_wallet=self.client.session.current_wallet))
