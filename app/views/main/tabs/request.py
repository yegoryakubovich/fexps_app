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

from flet_core import Column, ControlEvent, colors, ScrollMode, Row, MainAxisAlignment, Image, Container

from app.controls.button import Chip, StandardButton
from app.controls.button.actions import ActionItem
from app.controls.information import Text, SubTitle, Title
from app.controls.navigation import PaginationWidget
from app.utils import Fonts, Icons, value_to_float
from app.utils.value import value_to_str, get_output_currency_value, get_input_currency_value, get_output_value, \
    get_input_value
from app.views.client.requests import RequestView
from app.views.main.tabs.base import BaseTab


class Chips:
    COMPLETED = 'completed'
    CANCELED = 'canceled'
    ALL = 'all'


class RequestTab(BaseTab):
    scopes: list[ActionItem]
    control_dict: dict

    current_requests = list[dict]
    history_requests = list[dict]

    page_request: int = 1
    total_pages: int = 1
    selected_chip: str

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_chip = Chips.COMPLETED
        self.control_dict = {
            'currently_request': None,
            'history_request': None,
        }

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
                                                size=14,
                                                font_family=Fonts.SEMIBOLD,
                                                color=colors.ON_PRIMARY,
                                            ),
                                        ],
                                    ),
                                    Row(
                                        controls=[
                                            Text(
                                                value=state_str,
                                                size=12,
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
                                height=24,
                                color=colors.ON_PRIMARY,
                            ),
                        ],
                        alignment=MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    on_click=partial(self.request_view, request.id),
                    bgcolor=colors.PRIMARY,
                    horizontal=16,
                    vertical=12,
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
    HISTORY REQUESTS
    """

    async def get_history_request_chips(self) -> list[Chip]:
        return [
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

    async def get_history_request_cards(self) -> list[StandardButton]:
        response = await self.client.session.api.client.requests.search(
            is_completed=self.selected_chip in [Chips.COMPLETED, Chips.ALL],
            is_canceled=self.selected_chip in [Chips.CANCELED, Chips.ALL],
            page=self.page_request,
        )
        self.history_requests = response.requests
        self.total_pages = response.pages
        cards: list[StandardButton] = []
        for request in self.history_requests:
            state_str = await self.client.session.gtv(key=f'request_state_{request.state}')
            date_str = request.date.strftime('%d %b %Y, %H:%M')
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
                                                value=date_str,
                                                size=10,
                                                font_family=Fonts.SEMIBOLD,
                                                color=colors.ON_PRIMARY_CONTAINER,
                                            ),
                                        ],
                                    ),
                                    Row(
                                        controls=[
                                            Text(
                                                value=value_str,
                                                size=14,
                                                font_family=Fonts.SEMIBOLD,
                                                color=colors.ON_PRIMARY_CONTAINER,
                                            ),
                                        ],
                                    ),
                                    Row(
                                        controls=[
                                            Text(
                                                value=state_str,
                                                size=12,
                                                font_family=Fonts.SEMIBOLD,
                                                color=colors.ON_PRIMARY_CONTAINER,
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
                    bgcolor=colors.PRIMARY_CONTAINER,
                    horizontal=16,
                    vertical=12,
                )
            )
        return cards

    async def update_history_request(self, update: bool = True):
        self.control_dict['history_request'] = Row(
            controls=[
                SubTitle(value=await self.client.session.gtv(key='request_history_title')),
                *await self.get_history_request_chips(),
                *await self.get_history_request_cards(),
                PaginationWidget(
                    current_page=self.page_request,
                    total_pages=self.total_pages,
                    on_next=self.next_page,
                    on_back=self.previous_page,
                    text_next=await self.client.session.gtv(key='next'),
                    text_back=await self.client.session.gtv(key='back'),
                ),
            ],
            wrap=True,
        )
        if update:
            await self.update_async()

    async def construct(self):
        await self.update_currently_request(update=False)
        await self.update_history_request(update=False)
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
                        self.control_dict['currently_request'],
                        self.control_dict['history_request'],
                    ]
                ),
                padding=10,
            )
        ]

    async def request_create(self, _):
        from app.views.client.requests import RequestCreateView
        await self.client.change_view(view=RequestCreateView(current_wallet=self.client.session.current_wallet))

    async def request_view(self, request_id: int, _):
        await self.client.change_view(view=RequestView(request_id=request_id))

    async def chip_select(self, event: ControlEvent):
        self.selected_chip = event.control.key
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
