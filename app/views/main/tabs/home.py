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
import logging

from flet_core import Column, Container, ControlEvent, Chip, colors, Row

from app.controls.information.home.account_row import AccountInfoRow
from app.controls.information.home.balance_row import BalanceRow
from app.controls.information.home.history_row import HistoryRow, HistoryChip
from app.controls.information.home.scope_row import ScopeRow
from app.views.main.tabs.base import BaseTab


class Chips:
    is_sender = 'is_sender'
    is_receiver = 'is_receiver'


class HomeTab(BaseTab):
    exercise: list[dict] = None
    scopes: list[dict]
    filter_chips: list[Chip]
    history_chip_is_sender: bool
    history_chip_is_receiver: bool

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

    async def get_scope_row(self):
        self.scopes = [
            dict(
                name='Payment',
                on_click=self.go_payment,
            ),
            dict(
                name='Test',
            ),
        ]
        return ScopeRow(scopes=self.scopes)

    async def get_history(self):
        self.filter_chips = [
            HistoryChip(
                name=await self.client.session.gtv(key=f'chip_{Chips.is_sender}'),
                key=Chips.is_sender,
                on_select=self.chip_select,
                selected=self.history_chip_is_sender,
            ),
            HistoryChip(
                name=await self.client.session.gtv(key=f'chip_{Chips.is_receiver}'),
                key=Chips.is_receiver,
                on_select=self.chip_select,
                selected=self.history_chip_is_receiver,
            ),
        ]
        transfers = await self.client.session.api.client.transfers.search(
            wallet_id=self.client.session.current_wallet.id,
            is_sender=self.history_chip_is_sender,
            is_receiver=self.history_chip_is_receiver,
            page=1,
        )
        return HistoryRow(
            title_text=await self.client.session.gtv(key='transaction_history'),
            filter_chips=self.filter_chips,
            transfers=transfers.transfers,
        )

    async def build(self):
        self.history_chip_is_sender, self.history_chip_is_receiver = True, True
        self.client.session.wallets = await self.client.session.api.client.wallets.get_list()
        self.client.session.current_wallet = await self.client.session.api.client.wallets.get(
            id_=self.client.session.current_wallet.id,
        )
        self.controls = [
            Container(
                content=Column(
                    controls=[
                        Container(
                            content=await self.get_account_row(),
                            on_click=self.go_account,
                        ),
                        await self.get_balance_row(),
                        await self.get_scope_row(),
                        await self.get_history(),
                    ],
                ),
                padding=10,
            ),
        ]

    async def chip_select(self, event: ControlEvent):
        if event.control.key == Chips.is_sender:
            self.history_chip_is_sender = True if event.data == 'true' else False
        elif event.control.key == Chips.is_receiver:
            self.history_chip_is_receiver = True if event.data == 'true' else False
        self.controls[0].content.controls[3] = await self.get_history()
        await self.update_async()

    async def go_payment(self, _):
        from app.views.client.scopes import PaymentView
        await self.client.change_view(view=PaymentView())

    async def go_account(self, _):
        from app.views.client.account import AccountView
        await self.client.change_view(view=AccountView())

    async def change_wallet(self, event: ControlEvent):
        self.client.session.wallets = await self.client.session.api.client.wallets.get_list()
        self.client.session.current_wallet = await self.client.session.api.client.wallets.get(id_=event.data)
        self.controls[0].content.controls[1] = await self.get_balance_row()
        self.controls[0].content.controls[3] = await self.get_history()
        await self.update_async()
