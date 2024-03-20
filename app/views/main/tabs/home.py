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


from datetime import datetime
from functools import partial

from flet_core import Column, Container, ControlEvent, colors, ScrollMode, Row, MainAxisAlignment, Image, TextAlign, \
    Padding

from app.controls.button import Chip
from app.controls.button.standart import StandardButton
from app.controls.information import Card, Text
from app.controls.navigation.pagination import PaginationWidget
from app.utils import Fonts, Icons
from app.utils.value import get_fix_value
from app.views.main.tabs.base import BaseTab
from config import settings


class Chips:
    input = 'input'
    output = 'output'
    all = 'all'


class HomeTab(BaseTab):
    exercise: list[dict] = None
    transfers = list[dict]
    cards: list[Card]
    page_transfer: int = 1
    total_pages: int = 1
    filter_chips: list[Chip]
    selected_chip: str

    async def get_account_row(self):
        hello_text_key = 'good_morning'

        return Row(
            controls=[
                Text(
                    value=await self.client.session.gtv(key=hello_text_key),
                    size=32,
                    font_family=Fonts.MEDIUM,
                    color=colors.ON_BACKGROUND,
                ),
                Text(
                    value=f'{self.client.session.account.firstname.title()}.',
                    size=32,
                    font_family=Fonts.SEMIBOLD,
                    color=colors.ON_BACKGROUND,
                ),
            ],
        )

    async def get_balance_row(self):
        wallet_name = self.client.session.current_wallet.name
        value = get_fix_value(value=self.client.session.current_wallet.value)
        return Container(
            content=Row(
                controls=[
                    Column(
                        controls=[
                            Row(
                                controls=[
                                    Text(
                                        value=f'{wallet_name}',
                                        size=24,
                                        font_family=Fonts.REGULAR,
                                        color=colors.ON_PRIMARY,
                                    ),
                                ],
                                alignment=MainAxisAlignment.CENTER,
                            ),
                            Row(
                                controls=[
                                    Image(
                                        src=Icons.VALUE,
                                        width=36,
                                        color=colors.ON_PRIMARY,
                                    ),
                                    Text(
                                        value=f'{value}',
                                        size=32,
                                        font_family=Fonts.BOLD,
                                        color=colors.ON_PRIMARY,
                                    ),
                                ],
                                alignment=MainAxisAlignment.CENTER,
                            ),

                        ],
                        alignment=MainAxisAlignment.CENTER,
                        expand=True,
                    ),
                    Column(
                        controls=[
                            Container(
                                content=Image(
                                    src=Icons.WALLET_MENU,
                                    width=36,
                                    color=colors.ON_BACKGROUND,
                                ),
                                on_click=self.select_wallet_view,
                                padding=20,
                            )
                        ],
                    ),
                ],
                alignment=MainAxisAlignment.SPACE_BETWEEN,
            ),
            bgcolor=colors.PRIMARY,
            height=150,
        )

    async def get_actions_row(self):
        return Row(
            controls=[
                StandardButton(
                    content=Row(
                        controls=[
                            Image(
                                src=Icons.MAKE_EXCHANGE,
                                height=32,
                                width=32,
                            ),
                            Text(
                                value=await self.client.session.gtv(key=f'action_make_exchange'),
                                size=16,
                                font_family=Fonts.BOLD,
                                color=colors.ON_PRIMARY,
                            ),
                        ],
                        alignment=MainAxisAlignment.CENTER,
                    ),
                    on_click=self.request_create,
                    expand=2,
                    bgcolor=colors.PRIMARY,
                ),
                StandardButton(
                    content=Row(
                        controls=[
                            Image(
                                src=Icons.SEND,
                                height=32,
                                width=32,
                            ),
                            Text(
                                value=await self.client.session.gtv(key=f'action_send'),
                                size=16,
                                font_family=Fonts.BOLD,
                                color=colors.ON_PRIMARY_CONTAINER,
                            ),
                        ],
                        alignment=MainAxisAlignment.CENTER,
                    ),
                    bgcolor=colors.PRIMARY_CONTAINER,
                    expand=1,
                    on_click=self.go_send,
                ),
                StandardButton(
                    content=Row(
                        controls=[
                            Image(
                                src=Icons.DEV,
                                height=32,
                                width=32,
                            ),
                            Text(
                                value=await self.client.session.gtv(key=f'action_dev'),
                                size=16,
                                font_family=Fonts.BOLD,
                                color=colors.ON_PRIMARY_CONTAINER,
                            ),
                        ],
                        alignment=MainAxisAlignment.CENTER,
                    ),
                    bgcolor=colors.PRIMARY_CONTAINER,
                    expand=1,
                ),
            ],
            spacing=10,
        )

    async def get_history(self):
        self.filter_chips = [
            Chip(
                name=await self.client.session.gtv(key=f'chip_{Chips.input}'),
                key=Chips.input,
                on_select=self.chip_select,
                selected=True if self.selected_chip == Chips.input else False,
            ),
            Chip(
                name=await self.client.session.gtv(key=f'chip_{Chips.output}'),
                key=Chips.output,
                on_select=self.chip_select,
                selected=True if self.selected_chip == Chips.output else False,
            ),
            Chip(
                name=await self.client.session.gtv(key=f'chip_{Chips.all}'),
                key=Chips.all,
                on_select=self.chip_select,
                selected=True if self.selected_chip == Chips.all else False,
            ),

        ]
        response = await self.client.session.api.client.transfers.search(
            wallet_id=self.client.session.current_wallet.id,
            is_sender=True if self.selected_chip in [Chips.output, Chips.all] else False,
            is_receiver=True if self.selected_chip in [Chips.input, Chips.all] else False,
            page=self.page_transfer,
        )
        self.transfers = response.transfers
        self.total_pages = response.pages
        self.scroll = ScrollMode.AUTO
        self.cards: list = []
        for transfer in self.transfers:
            value = get_fix_value(value=transfer.value)
            if transfer.operation == 'send':
                value = f'- {value}'
            elif transfer.operation == 'receive':
                value = f'+ {value}'
            date = datetime.strptime(transfer.date, settings.datetime_format).strftime('%Y-%m-%d')
            self.cards.append(
                Container(
                    content=Row(
                        controls=[
                            Text(
                                value=f'To wallet.{transfer.wallet_to}',
                                size=32,
                                font_family=Fonts.SEMIBOLD,
                                color=colors.ON_BACKGROUND,
                                expand=True,
                                text_align=TextAlign.LEFT,
                            ),
                            Container(
                                content=Column(
                                    controls=[
                                        Text(
                                            value=value,
                                            size=32,
                                            font_family=Fonts.BOLD,
                                            color=colors.ON_BACKGROUND,
                                        ),
                                        Text(
                                            value=date,
                                            size=16,
                                            font_family=Fonts.REGULAR,
                                            color=colors.ON_BACKGROUND,
                                        ),
                                    ],
                                ),
                            ),
                        ],
                        alignment=MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    on_click=partial(self.transfer_view, transfer.id),
                    bgcolor=colors.SECONDARY,
                    padding=Padding(left=16, right=16, top=12, bottom=12),
                )
            )

        return Row(
            controls=[
                Row(
                    controls=[
                        Text(
                            value=await self.client.session.gtv(key='last_transactions'),
                            size=32,
                            font_family=Fonts.BOLD,
                            color=colors.ON_BACKGROUND,
                        )
                    ]
                ),
                *self.filter_chips,
                *self.cards,
                PaginationWidget(
                    current_page=self.page_transfer,
                    total_pages=self.total_pages,
                    on_back=self.previous_page,
                    on_next=self.next_page,
                    text_back=await self.client.session.gtv(key='back'),
                    text_next=await self.client.session.gtv(key='next'),
                ),
            ],
            wrap=True,
        )

    async def build(self):
        self.selected_chip = Chips.all
        self.client.session.wallets = await self.client.session.api.client.wallets.get_list()
        self.client.session.current_wallet = await self.client.session.api.client.wallets.get(
            id_=self.client.session.current_wallet['id'],
        )
        self.scroll = ScrollMode.AUTO
        self.controls = [
            Container(
                content=Column(
                    controls=[
                        await self.get_account_row(),
                        await self.get_balance_row(),
                        await self.get_actions_row(),
                        await self.get_history(),
                        Container(
                            content=Text(value='ACCOUNT', color=colors.BLACK),
                            on_click=self.go_account
                        )
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

    async def chip_select(self, event: ControlEvent):
        self.selected_chip = event.control.key
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

    async def select_wallet_view(self, _):
        from app.views.client.wallets import WalletSelectView
        await self.client.change_view(view=WalletSelectView())

    async def request_create(self, _):
        from app.views.client.actions import RequestCreateView
        await self.client.change_view(view=RequestCreateView())

    async def go_send(self, _):
        from app.views.client.actions import SendMoneyView
        await self.client.change_view(view=SendMoneyView())

    async def transfer_view(self, transfer_id: int, _):
        from app.views.client.tansfers import TransferView
        await self.client.change_view(view=TransferView(transfer_id=transfer_id))
