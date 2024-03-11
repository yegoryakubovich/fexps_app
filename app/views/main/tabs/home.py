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

from flet_core import Column, Container, ControlEvent, Chip, colors, ScrollMode

from app.controls.information.home.account_row import HomeAccountRow
from app.controls.information.home.balance_row import HomeBalanceRow
from app.controls.information.home.history_row import HomeHistoryRow, HomeHistoryChip, TransferInfo
from app.controls.information.home.scope_row import HomeScopeRow
from app.controls.navigation.pagination import PaginationWidget
from app.views.main.tabs.base import BaseTab
from config import settings


class Chips:
    is_sender = 'is_sender'
    is_receiver = 'is_receiver'


class HomeTab(BaseTab):
    exercise: list[dict] = None
    scopes: list[dict]
    transfers = list[dict]
    page_transfer: int = 1
    total_pages: int = 1
    filter_chips: list[Chip]
    is_sender: bool
    is_receiver: bool

    async def get_account_row(self):
        return HomeAccountRow(
            hello_text=await self.client.session.gtv(key='hello'),
            name_text=self.client.session.account.firstname,
        )

    async def get_balance_row(self):
        return HomeBalanceRow(
            wallets=self.client.session.wallets,
            current_wallet=self.client.session.current_wallet,
            on_change=self.change_wallet,
        )

    async def get_scope_row(self):
        self.scopes = [
            dict(
                name=await self.client.session.gtv(key=f'scope_payment'),
                on_click=self.go_payment,
            ),
            dict(
                name=await self.client.session.gtv(key=f'scope_test'),
            ),
        ]
        return HomeScopeRow(scopes=self.scopes)

    async def get_history(self):
        self.filter_chips = [
            HomeHistoryChip(
                name=await self.client.session.gtv(key=f'chip_{Chips.is_sender}'),
                key=Chips.is_sender,
                on_select=self.chip_select,
                selected=self.is_sender,
            ),
            HomeHistoryChip(
                name=await self.client.session.gtv(key=f'chip_{Chips.is_receiver}'),
                key=Chips.is_receiver,
                on_select=self.chip_select,
                selected=self.is_receiver,
            ),
        ]
        response = await self.client.session.api.client.transfers.search(
            wallet_id=self.client.session.current_wallet.id,
            is_sender=self.is_sender,
            is_receiver=self.is_receiver,
            page=self.page_transfer,
        )
        self.transfers = response.transfers
        self.total_pages = response.pages
        self.scroll = ScrollMode.AUTO
        transfer_list: list[TransferInfo] = []
        for transfer in self.transfers:
            value = int(transfer.value) / settings.default_decimal
            if transfer.operation == 'send':
                color, value = colors.RED, f'- ${value}'
            elif transfer.operation == 'receive':
                color, value = colors.GREEN, f'+ ${value}'
            else:
                color, value = colors.GREY, f'${value}'
            transfer_list.append(TransferInfo(
                type_=await self.client.session.gtv(key=f'transfer_type_{transfer.type}'),
                description=f'from wallet.{transfer.wallet_from} to wallet.{transfer.wallet_to}',
                value=value,
                color=color,
                date=transfer.date,
            ))
        return HomeHistoryRow(
            title_text=await self.client.session.gtv(key='transaction_history'),
            filter_chips=self.filter_chips,
            transfer_list=transfer_list,
            pagination=PaginationWidget(
                current_page=self.page_transfer,
                total_pages=self.total_pages,
                on_back=self.previous_page,
                on_next=self.next_page,
                text_back=await self.client.session.gtv(key='back'),
                text_next=await self.client.session.gtv(key='next'),
            ),
        )

    async def build(self):
        self.is_sender, self.is_receiver = True, True
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

    async def go_account(self, _):
        from app.views.client.account import AccountView
        await self.client.change_view(view=AccountView())

    async def change_wallet(self, event: ControlEvent):
        self.client.session.wallets = await self.client.session.api.client.wallets.get_list()
        self.client.session.current_wallet = await self.client.session.api.client.wallets.get(id_=event.data)
        self.controls[0].content.controls[1] = await self.get_balance_row()
        self.controls[0].content.controls[3] = await self.get_history()
        await self.update_async()

    async def go_payment(self, _):
        from app.views.client.scopes import PaymentView
        await self.client.change_view(view=PaymentView())

    async def chip_select(self, event: ControlEvent):
        if event.control.key == Chips.is_sender:
            self.is_sender = True if event.data == 'true' else False
        elif event.control.key == Chips.is_receiver:
            self.is_receiver = True if event.data == 'true' else False
        self.controls[0].content.controls[3] = await self.get_history()
        await self.update_async()

    async def next_page(self, _):
        if self.page_transfer < self.total_pages:
            self.page_transfer += 1
            await self.build()
            await self.update_async()

    async def previous_page(self, _):
        if self.page_transfer > 1:
            self.page_transfer -= 1
            await self.build()
            await self.update_async()
