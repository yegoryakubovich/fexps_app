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
from typing import Optional

from flet_core import Column, ControlEvent, colors, ScrollMode, Row, MainAxisAlignment, Image, Container

from app.controls.button import Chip, StandardButton
from app.controls.button.actions import ActionItem
from app.controls.information import Text, SubTitle, Title
from app.controls.input import TextField
from app.controls.navigation import PaginationWidget
from app.utils import Fonts, Icons, value_to_float
from app.utils.value import value_to_str
from app.views.client.requests import RequestView
from app.views.main.tabs.base import BaseTab


class Chips:
    ACTIVE = 'active'
    COMPLETED = 'completed'
    CANCELED = 'canceled'
    ALL = 'all'
    PARTNERS = 'partners'


class RequestTab(BaseTab):
    scopes: list[ActionItem]

    current_requests = list[dict]
    current_requests_column: Column
    history_requests = list[dict]
    history_requests_column: Column
    tf_history_requests_search: TextField

    page_request: int = 1
    total_pages: int = 1
    selected_chip: str
    partner_chip: bool
    search_value: Optional[str]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_chip = Chips.COMPLETED
        self.partner_chip = False
        self.search_value = None

    async def get_request_cards(self, requests: list) -> list[StandardButton]:
        cards: list[StandardButton] = []
        for request in requests:
            color, bgcolor = colors.ON_PRIMARY_CONTAINER, colors.PRIMARY_CONTAINER
            if request.state not in ['completed', 'canceled']:
                color, bgcolor = colors.ON_PRIMARY, colors.PRIMARY
            state_str = await self.client.session.gtv(key=f'request_state_{request.state}')
            date_str = request.date.strftime('%d %b %Y, %H:%M')
            input_currency_id_str, output_currency_id_str, rate_currency_id_str = '', '', ''
            if request.type == 'input':
                input_currency = request.input_method.currency
                input_currency_id_str = input_currency.id_str.upper()
                input_value = value_to_float(
                    value=request.input_currency_value,
                    decimal=input_currency.decimal,
                )
                output_value = value_to_float(value=request.input_value)
            elif request.type == 'output':
                input_value = value_to_float(value=request.output_value)
                output_currency = request.output_method.currency
                output_currency_id_str = output_currency.id_str.upper()
                output_value = value_to_float(
                    value=request.output_currency_value,
                    decimal=output_currency.decimal,
                )
            else:
                input_currency = request.input_method.currency
                input_currency_id_str = input_currency.id_str.upper()
                input_value = value_to_float(
                    value=request.input_currency_value,
                    decimal=input_currency.decimal,
                )
                output_currency = request.output_method.currency
                output_currency_id_str = output_currency.id_str.upper()
                output_value = value_to_float(
                    value=request.output_currency_value,
                    decimal=output_currency.decimal,
                )
            value_str = (
                f'{value_to_str(value=input_value)} {input_currency_id_str}'
                f' -> '
                f'{value_to_str(value=output_value)} {output_currency_id_str}'
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
                                                value=f'#{request.id:08}',
                                                size=10,
                                                font_family=Fonts.SEMIBOLD,
                                                color=color,
                                            ),
                                            Text(
                                                value='|',
                                                size=10,
                                                font_family=Fonts.SEMIBOLD,
                                                color=color,
                                            ),
                                            Text(
                                                value=date_str,
                                                size=10,
                                                font_family=Fonts.SEMIBOLD,
                                                color=color,
                                            ),
                                        ],
                                    ),
                                    Row(
                                        controls=[
                                            Text(
                                                value=value_str,
                                                size=14,
                                                font_family=Fonts.SEMIBOLD,
                                                color=color,
                                            ),
                                        ],
                                    ),
                                    Row(
                                        controls=[
                                            Text(
                                                value=state_str,
                                                size=12,
                                                font_family=Fonts.SEMIBOLD,
                                                color=color,
                                            ),
                                        ],
                                    ),
                                ],
                                expand=True,
                            ),
                            Image(
                                src=Icons.OPEN,
                                height=28,
                                color=color,
                            ),
                        ],
                        alignment=MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    on_click=partial(self.request_view, request.id),
                    bgcolor=bgcolor,
                    horizontal=16,
                    vertical=12,
                )
            )
        return cards

    """
    CURRENTLY REQUESTS
    """

    async def update_current_request_column(self, update: bool = True):
        response = await self.client.session.api.client.requests.search(is_active=True)
        self.current_requests = response.requests
        cards = await self.get_request_cards(requests=self.current_requests)
        self.current_requests_column = Column()
        if cards:
            self.current_requests_column.controls = [
                SubTitle(value=await self.client.session.gtv(key='requests_currently_title')),
                *cards,
            ]
        if update:
            await self.current_requests_column.update_async()

    """
    HISTORY REQUESTS
    """

    async def get_history_request_chips(self) -> list[Chip]:
        chips = [
            Chip(
                name=await self.client.session.gtv(key=f'chip_{Chips.ACTIVE}'),
                key=Chips.ACTIVE,
                on_select=self.chip_select,
                selected=True if self.selected_chip == Chips.ACTIVE else False,
            ),
            Chip(
                name=await self.client.session.gtv(key=f'chip_{Chips.COMPLETED}'),
                key=Chips.COMPLETED,
                on_select=self.chip_select,
                selected=True if self.selected_chip == Chips.COMPLETED else False,
            ),
            Chip(
                name=await self.client.session.gtv(key=f'chip_{Chips.CANCELED}'),
                key=Chips.CANCELED,
                on_select=self.chip_select,
                selected=True if self.selected_chip == Chips.CANCELED else False,
            ),
            Chip(
                name=await self.client.session.gtv(key=f'chip_{Chips.ALL}'),
                key=Chips.ALL,
                on_select=self.chip_select,
                selected=True if self.selected_chip == Chips.ALL else False,
            ),
        ]
        if 'partner_requests' in self.client.session.account.permissions:
            chips += [
                Chip(
                    name=await self.client.session.gtv(key=f'chip_{Chips.PARTNERS}'),
                    key=Chips.PARTNERS,
                    on_select=self.chip_partner_select,
                    selected=True if self.partner_chip else False,
                ),
            ]
        return chips

    async def update_history_request_column(self, update: bool = True):
        response = await self.client.session.api.client.requests.search(
            id_=self.search_value,
            is_active=self.selected_chip in [Chips.ACTIVE, Chips.ALL],
            is_completed=self.selected_chip in [Chips.COMPLETED, Chips.ALL],
            is_canceled=self.selected_chip in [Chips.CANCELED, Chips.ALL],
            is_partner=self.partner_chip,
            page=self.page_request,
        )
        self.history_requests = response.requests
        self.total_pages = response.pages
        self.tf_history_requests_search = TextField(
            label=await self.client.session.gtv(key='request_history_search'),
            value=self.search_value,
            width=250,
        )
        self.history_requests_column = Column(
            controls=[
                Row(
                    controls=[
                        Text(
                            value=await self.client.session.gtv(key='request_history_title'),
                            size=24,
                            font_family=Fonts.BOLD,
                            color=colors.ON_BACKGROUND,
                        ),
                        Row(
                            controls=[
                                self.tf_history_requests_search,
                                StandardButton(
                                    content=Image(
                                        src=Icons.SEARCH,
                                        height=14,
                                        color=colors.ON_PRIMARY_CONTAINER,
                                    ),
                                    on_click=self.change_request_search,
                                    bgcolor=colors.PRIMARY_CONTAINER
                                ),
                            ],
                            spacing=8,
                        ),
                    ],
                    alignment=MainAxisAlignment.SPACE_BETWEEN,
                ),
                Row(
                    controls=await self.get_history_request_chips(),
                    wrap=True,
                ),
                *await self.get_request_cards(requests=self.history_requests),
                PaginationWidget(
                    current_page=self.page_request,
                    total_pages=self.total_pages,
                    on_next=self.next_page,
                    on_back=self.previous_page,
                    text_next=await self.client.session.gtv(key='next'),
                    text_back=await self.client.session.gtv(key='back'),
                ),
            ],
        )
        if update:
            await self.update_async()

    async def construct(self):
        await self.update_current_request_column(update=False)
        await self.update_history_request_column(update=False)
        self.scroll = ScrollMode.AUTO
        self.controls = [
            Container(
                content=Column(
                    controls=[
                        Title(
                            value=await self.client.session.gtv(key='request_tab_title'),
                            create_name_text=await self.client.session.gtv(key='create'),
                            on_create=self.request_create,
                        ),
                        self.current_requests_column,
                        self.history_requests_column,
                    ]
                ),
                padding=10,
            )
        ]

    async def change_request_search(self, _=None):
        self.search_value = self.tf_history_requests_search.value
        await self.construct()
        await self.update_async()

    async def request_create(self, _):
        from app.views.client.requests import RequestCreateView
        await self.client.change_view(view=RequestCreateView(current_wallet=self.client.session.current_wallet))

    async def request_view(self, request_id: int, _):
        await self.client.change_view(view=RequestView(request_id=request_id))

    async def chip_select(self, event: ControlEvent):
        self.selected_chip = event.control.key
        await self.construct()
        await self.update_async()

    async def chip_partner_select(self, _: ControlEvent):
        self.partner_chip = False if self.partner_chip else True
        await self.construct()
        await self.update_async()

    async def next_page(self, _):
        if self.page_request < self.total_pages:
            self.page_request += 1
            await self.construct()
            await self.update_async()

    async def previous_page(self, _):
        if self.page_request > 1:
            self.page_request -= 1
            await self.construct()
            await self.update_async()
