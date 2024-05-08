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


import datetime
from functools import partial

from flet_core import Column, Container, ControlEvent, colors, ScrollMode, Row, MainAxisAlignment, Image, TextAlign, \
    Stack, alignment

from app.controls.button import Chip, StandardButton
from app.controls.information import Card, Text, InformationContainer, SubTitle
from app.controls.navigation.pagination import PaginationWidget
from app.utils import Fonts, Icons, value_to_float, value_to_str
from app.utils.value import get_output_currency_value, get_input_currency_value, get_output_value, get_input_value
from app.views.client.requests import RequestView
from app.views.main.tabs.base import BaseTab


class Chips:
    input = 'input'
    output = 'output'
    all = 'all'


class HomeTab(BaseTab):
    transfers = list[dict]
    control_dict: dict

    cards: list[Card]
    current_requests = list[dict]

    page_transfer: int = 1
    total_pages: int = 1
    selected_chip: str

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_chip = Chips.all
        self.control_dict = {
            'account': None,
            'balance': None,
            'actions': None,
            'currently_request': None,
            'history_transfer': None,
        }

    async def update_account(self, update: bool = True):
        time_utcnow = datetime.datetime.now(tz=datetime.UTC).replace(tzinfo=None)
        time_delta = datetime.timedelta(hours=self.client.session.timezone.deviation)
        time_now = time_utcnow + time_delta
        if time_now.hour < 6:
            hello_text_str = await self.client.session.gtv(key='good_night')
        elif time_now.hour < 12:
            hello_text_str = await self.client.session.gtv(key='good_morning')
        elif time_now.hour < 18:
            hello_text_str = await self.client.session.gtv(key='good_afternoon')
        else:
            hello_text_str = await self.client.session.gtv(key='good_evening')
        hello_text_str = f'{hello_text_str},'
        self.control_dict['account'] = Row(
            controls=[
                Text(
                    value=hello_text_str,
                    size=20,
                    font_family=Fonts.MEDIUM,
                    color=colors.ON_BACKGROUND,
                ),
                Text(
                    value=f'{self.client.session.account.firstname.title()}.',
                    size=24,
                    font_family=Fonts.SEMIBOLD,
                    color=colors.ON_BACKGROUND,
                ),
            ],
            wrap=True,
        )
        if update:
            await self.update_async()

    async def update_balance(self, update: bool = True):
        wallet_name = self.client.session.current_wallet.name
        value = value_to_float(value=self.client.session.current_wallet.value)
        value_str = value_to_str(value=value)
        self.control_dict['balance'] = InformationContainer(
            content=Stack(
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
                                    )
                                ],
                                alignment=MainAxisAlignment.CENTER,
                            ),
                            Row(
                                controls=[
                                    Image(
                                        src=Icons.COIN,
                                        width=28,
                                        color=colors.ON_PRIMARY,
                                    ),
                                    Text(
                                        value=f'{value_str}',
                                        size=32,
                                        font_family=Fonts.BOLD,
                                        color=colors.ON_PRIMARY,
                                    ),
                                ],
                                alignment=MainAxisAlignment.CENTER,
                            ),
                        ],
                        alignment=MainAxisAlignment.CENTER,
                    ),
                    Container(
                        content=StandardButton(
                            content=Image(
                                src=Icons.WALLET_MENU,
                                width=24,
                                color=colors.ON_PRIMARY,
                            ),
                            color=colors.PRIMARY,
                            on_click=self.select_wallet_view,
                            horizontal=20,
                            vertical=20,
                        ),
                        alignment=alignment.top_right,
                    ),
                ],
                expand=True,
            ),
            height=150,
        )
        if update:
            await self.update_async()

    async def update_actions(self, update: bool = True):
        self.control_dict['actions'] = Row(
            controls=[
                StandardButton(
                    content=Row(
                        controls=[
                            Image(
                                src=Icons.MAKE_EXCHANGE,
                                height=20,
                                width=20,
                            ),
                            Text(
                                value=await self.client.session.gtv(key=f'action_make_exchange'),
                                size=12,
                                font_family=Fonts.BOLD,
                                color=colors.ON_PRIMARY,
                            ),
                        ],
                        alignment=MainAxisAlignment.CENTER,
                    ),
                    on_click=self.request_create,
                    expand=3,
                    bgcolor=colors.PRIMARY,
                ),
                StandardButton(
                    content=Row(
                        controls=[
                            Image(
                                src=Icons.PAYMENT,
                                height=20,
                                width=20,
                            ),
                            Text(
                                value=await self.client.session.gtv(key=f'action_send'),
                                size=12,
                                font_family=Fonts.BOLD,
                                color=colors.ON_PRIMARY_CONTAINER,
                            ),
                        ],
                        alignment=MainAxisAlignment.CENTER,
                    ),
                    bgcolor=colors.PRIMARY_CONTAINER,
                    expand=2,
                    on_click=self.go_send,
                ),
            ],
        )
        if update:
            await self.update_async()

    """
    CURRENTLY REQUESTS
    """

    async def get_currently_request_cards(self) -> list[StandardButton]:
        response = await self.client.session.api.client.requests.search()
        self.current_requests = response.requests
        cards: list[StandardButton] = []
        for request in self.current_requests:
            state_str = await self.client.session.gtv(key=f'request_state_{request.state}')
            if request.type == 'input':
                input_currency = request.input_currency
                input_currency_value = value_to_float(
                    value=get_input_currency_value(request=request),
                    decimal=input_currency.decimal,
                )
                input_value = value_to_float(
                    value=get_input_value(request=request),
                    decimal=input_currency.decimal,
                )
                value_str = (
                    f'{value_to_str(value=input_currency_value)} {input_currency.id_str.upper()}'
                    f' -> '
                    f'{value_to_str(value=input_value)}'
                )
            elif request.type == 'output':
                output_currency = request.output_currency
                output_currency_value = value_to_float(
                    value=get_output_currency_value(request=request),
                    decimal=output_currency.decimal,
                )
                output_value = value_to_float(
                    value=get_output_value(request=request),
                    decimal=output_currency.decimal,
                )
                value_str = (
                    f'{value_to_str(value=output_value)}'
                    f' -> '
                    f'{value_to_str(value=output_currency_value)} {output_currency.id_str.upper()}'
                )

            else:
                input_currency = request.input_currency
                output_currency = request.output_currency
                input_currency_value = value_to_float(
                    value=get_input_currency_value(request=request),
                    decimal=input_currency.decimal,
                )
                output_currency_value = value_to_float(
                    value=get_output_currency_value(request=request),
                    decimal=output_currency.decimal,
                )
                value_str = (
                    f'{value_to_str(value=input_currency_value)} {input_currency.id_str.upper()}'
                    f' -> '
                    f'{value_to_str(value=output_currency_value)} {output_currency.id_str.upper()}'
                )
            cards.append(
                StandardButton(
                    content=Row(
                        controls=[
                            Column(
                                controls=[
                                    Row(
                                        controls=[
                                            Text(
                                                value=value_str,
                                                size=22,
                                                font_family=Fonts.SEMIBOLD,
                                                color=colors.ON_PRIMARY,
                                            ),
                                        ],
                                    ),
                                    Row(
                                        controls=[
                                            Text(
                                                value=state_str,
                                                size=16,
                                                font_family=Fonts.SEMIBOLD,
                                                color=colors.ON_PRIMARY,
                                            ),
                                        ],
                                    ),
                                ],
                                expand=True,
                            ),
                            Image(
                                src=Icons.OPEN,
                                height=28,
                                color=colors.ON_PRIMARY,
                            ),
                        ],
                        alignment=MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    on_click=partial(self.request_view, request.id),
                    bgcolor=colors.PRIMARY,
                    horizontal=24,
                    vertical=16,
                )
            )
        return cards

    async def update_currently_request(self, update: bool = True):
        cards = await self.get_currently_request_cards()
        self.control_dict['currently_request'] = Row()
        if cards:
            self.control_dict['currently_request'] = Row(
                controls=[
                    SubTitle(value=await self.client.session.gtv(key='requests_currently_title')),
                    *cards,
                ],
                wrap=True,
            )
        if update:
            await self.update_async()

    """
    HISTORY TRANSFER
    """

    async def get_history_transfer_chips(self) -> list[Chip]:
        return [
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

    async def get_history_transfer_cards(self) -> list[StandardButton]:
        response = await self.client.session.api.client.transfers.search(
            wallet_id=self.client.session.current_wallet.id,
            is_sender=self.selected_chip in [Chips.output, Chips.all],
            is_receiver=self.selected_chip in [Chips.input, Chips.all],
            page=self.page_transfer,
        )
        self.transfers = response.transfers
        self.total_pages = response.pages
        self.scroll = ScrollMode.AUTO
        cards: list = []
        for transfer in self.transfers:
            value = value_to_float(value=transfer.value)
            value_str, short_name = '', ''
            if transfer.operation == 'send':
                short_name = f'To {transfer.account_to.short_name}'
                value_str = f'- {value_to_str(value=value)}'
            elif transfer.operation == 'receive':
                short_name = f'From {transfer.account_from.short_name}'
                value_str = f'+ {value_to_str(value=value)}'
            date = transfer.date.strftime('%Y-%m-%d')
            cards.append(
                StandardButton(
                    content=Row(
                        controls=[
                            Text(
                                value=short_name.title(),
                                size=24,
                                font_family=Fonts.SEMIBOLD,
                                color=colors.ON_PRIMARY_CONTAINER,
                                expand=True,
                                text_align=TextAlign.LEFT,
                            ),
                            Container(
                                content=Column(
                                    controls=[
                                        Text(
                                            value=value_str,
                                            size=24,
                                            font_family=Fonts.BOLD,
                                            color=colors.ON_PRIMARY_CONTAINER,
                                        ),
                                        Text(
                                            value=date,
                                            size=14,
                                            font_family=Fonts.REGULAR,
                                            color=colors.ON_PRIMARY_CONTAINER,
                                            text_align=TextAlign.RIGHT,
                                        ),
                                    ],
                                ),
                            ),
                        ],
                        alignment=MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    on_click=partial(self.transfer_view, transfer.id),
                    bgcolor=colors.PRIMARY_CONTAINER,
                    horizontal=16,
                    vertical=12,
                ),
            )
        return cards

    async def update_history_transfer(self, update: bool = True):
        self.control_dict['history_transfer'] = Row(
            controls=[
                SubTitle(value=await self.client.session.gtv(key='last_transfers_title')),
                *await self.get_history_transfer_chips(),
                *await self.get_history_transfer_cards(),
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
        if update:
            await self.update_async()

    async def construct(self):
        self.client.session.wallets = await self.client.session.api.client.wallets.get_list()
        self.client.session.current_wallet = await self.client.session.api.client.wallets.get(
            id_=self.client.session.current_wallet['id'],
        )
        await self.update_account(update=False)
        await self.update_balance(update=False)
        await self.update_actions(update=False)
        await self.update_currently_request(update=False)
        await self.update_history_transfer(update=False)
        self.scroll = ScrollMode.AUTO
        self.controls = [
            Container(
                content=Column(
                    controls=[
                        self.control_dict['account'],
                        self.control_dict['balance'],
                        self.control_dict['actions'],
                        self.control_dict['currently_request'],
                        self.control_dict['history_transfer'],
                    ]
                ),
                padding=10,
            )
        ]

    async def select_wallet_view(self, _):
        from app.views.client.wallets import WalletSelectView
        await self.client.change_view(
            view=WalletSelectView(
                current_wallet_id=self.client.session.current_wallet.id,
            ),
        )

    async def request_create(self, _):
        from app.views.client.requests import RequestCreateView
        await self.client.change_view(view=RequestCreateView())

    async def go_send(self, _):
        from app.views.client.transfers import TransferCreateView
        await self.client.change_view(view=TransferCreateView())

    async def request_view(self, request_id: int, _):
        await self.client.change_view(view=RequestView(request_id=request_id))

    async def transfer_view(self, transfer_id: int, _):
        from app.views.client.transfers import TransferView
        await self.client.change_view(view=TransferView(transfer_id=transfer_id))

    async def chip_select(self, event: ControlEvent):
        self.selected_chip = event.control.key
        await self.construct()
        await self.update_async()

    async def next_page(self, _):
        if self.page_transfer < self.total_pages:
            self.page_transfer += 1
            await self.construct()
            await self.update_async()

    async def previous_page(self, _):
        if self.page_transfer > 1:
            self.page_transfer -= 1
            await self.construct()
            await self.update_async()
