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

from flet_core import Column, ControlEvent, colors, ScrollMode, Row, MainAxisAlignment, Container, Padding, Image

from app.controls.button import Chip, StandardButton
from app.controls.button.actions import ActionItem
from app.controls.information import Text, SubTitle, Title
from app.controls.navigation import PaginationWidget
from app.utils import Fonts, Icons, value_to_float
from app.views.client.requests import RequestView
from app.views.main.tabs.base import BaseTab


class Chips:
    COMPLETED = 'completed'
    CANCELED = 'canceled'
    ALL = 'all'


class RequestTab(BaseTab):
    scopes: list[ActionItem]
    column: Column
    current_requests = list[dict]
    history_requests = list[dict]
    page_request: int = 1
    total_pages: int = 1
    selected_chip: str

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_chip = Chips.COMPLETED

    """
    CURRENCY REQUESTS
    """

    async def get_currency_request_cards(self) -> list[StandardButton]:
        response = await self.client.session.api.client.requests.search()
        self.history_requests = response.requests
        cards: list[StandardButton] = []
        for request in self.history_requests:
            state = await self.client.session.gtv(key=f'request_state_{request.state}')
            if request.type == 'input':
                input_currency = await self.client.session.api.client.currencies.get(id_str=request.input_currency)
                input_currency_value = value_to_float(
                    value=request.input_currency_value_raw,
                    decimal=input_currency.decimal,
                ) if request.input_currency_value_raw else None
                input_value = value_to_float(
                    value=request.input_value_raw,
                    decimal=input_currency.decimal,
                ) if request.input_value_raw else None
                value = f'{input_currency_value} {input_currency.id_str.upper()} -> {input_value}'
            elif request.type == 'output':
                output_currency = await self.client.session.api.client.currencies.get(
                    id_str=request.output_currency)
                output_currency_value = value_to_float(
                    value=request.output_currency_value_raw,
                    decimal=output_currency.decimal,
                ) if request.output_currency_value_raw else None
                output_value = value_to_float(
                    value=request.output_raw,
                    decimal=output_currency.decimal,
                ) if request.output_raw else None
                value = f'{output_value} -> {output_currency_value} {output_currency.id_str.upper()}'
            else:
                input_currency = await self.client.session.api.client.currencies.get(id_str=request.input_currency)
                output_currency = await self.client.session.api.client.currencies.get(
                    id_str=request.output_currency)
                input_currency_value = value_to_float(
                    value=request.input_currency_value_raw,
                    decimal=input_currency.decimal,
                ) if request.input_currency_value_raw else None
                output_currency_value = value_to_float(
                    value=request.output_currency_value_raw,
                    decimal=output_currency.decimal,
                ) if request.output_currency_value_raw else None
                value = (
                    f'{input_currency_value} {input_currency.id_str.upper()}'
                    f' -> '
                    f'{output_currency_value} {output_currency.id_str.upper()}'
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
                                                value=value,
                                                size=28,
                                                font_family=Fonts.SEMIBOLD,
                                                color=colors.ON_PRIMARY,
                                            ),
                                        ],
                                    ),
                                    Row(
                                        controls=[
                                            Text(
                                                value=state,
                                                size=18,
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
                                height=32,
                                color=colors.ON_PRIMARY,
                            ),
                        ],
                        alignment=MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    on_click=partial(self.request_view, request.id),
                    bgcolor=colors.PRIMARY,
                    horizontal=34,
                    vertical=24,
                )
            )
        return cards

    async def get_currency_request(self):
        return Row(
            controls=[
                SubTitle(value=await self.client.session.gtv(key='requests_currency_title')),
                *await self.get_currency_request_cards(),
            ],
            wrap=True,
        )

    """
    HISTORY REQUESTS
    """

    async def get_history_request_chips(self) -> list[Chip]:
        return [
            Chip(
                name=await self.client.session.gtv(key=f'chips_{Chips.COMPLETED}'),
                key=Chips.COMPLETED,
                on_select=self.chip_select,
                selected=True if self.selected_chip == Chips.COMPLETED else False,
            ),
            Chip(
                name=await self.client.session.gtv(key=f'chips_{Chips.CANCELED}'),
                key=Chips.CANCELED,
                on_select=self.chip_select,
                selected=True if self.selected_chip == Chips.CANCELED else False,
            ),
            Chip(
                name=await self.client.session.gtv(key=f'chips_{Chips.ALL}'),
                key=Chips.ALL,
                on_select=self.chip_select,
                selected=True if self.selected_chip == Chips.ALL else False,
            ),
        ]

    async def get_history_request_cards(self) -> list[StandardButton]:
        params = dict(is_completed=False, is_canceled=False)
        if self.selected_chip in [Chips.COMPLETED, Chips.ALL]:
            params['is_completed'] = True
        if self.selected_chip in [Chips.CANCELED, Chips.ALL]:
            params['is_canceled'] = True
        response = await self.client.session.api.client.requests.search(**params, page=self.page_request)
        self.history_requests = response.requests
        self.total_pages = response.pages
        cards: list[StandardButton] = []
        for request in self.history_requests:
            state = await self.client.session.gtv(key=f'request_state_{request.state}')
            date = request.date.strftime('%d %b %Y, %H:%M')
            if request.type == 'input':
                input_currency = await self.client.session.api.client.currencies.get(id_str=request.input_currency)
                input_currency_value = value_to_float(
                    value=request.input_currency_value_raw,
                    decimal=input_currency.decimal,
                ) if request.input_currency_value_raw else None
                input_value = value_to_float(
                    value=request.input_value_raw,
                    decimal=input_currency.decimal,
                ) if request.input_value_raw else None
                value = f'{input_currency_value} {input_currency.id_str.upper()} -> {input_value}'
            elif request.type == 'output':
                output_currency = await self.client.session.api.client.currencies.get(id_str=request.output_currency)
                output_currency_value = value_to_float(
                    value=request.output_currency_value_raw,
                    decimal=output_currency.decimal,
                ) if request.output_currency_value_raw else None
                output_value = value_to_float(
                    value=request.output_raw,
                    decimal=output_currency.decimal,
                ) if request.output_raw else None
                value = f'{output_value} -> {output_currency_value} {output_currency.id_str.upper()}'
            else:
                input_currency = await self.client.session.api.client.currencies.get(id_str=request.input_currency)
                output_currency = await self.client.session.api.client.currencies.get(id_str=request.output_currency)
                input_currency_value = value_to_float(
                    value=request.input_currency_value_raw,
                    decimal=input_currency.decimal,
                ) if request.input_currency_value_raw else None
                output_currency_value = value_to_float(
                    value=request.output_currency_value_raw,
                    decimal=output_currency.decimal,
                ) if request.output_currency_value_raw else None
                value = (
                    f'{input_currency_value} {input_currency.id_str.upper()}'
                    f' -> '
                    f'{output_currency_value} {output_currency.id_str.upper()}'
                )

            cards.append(
                StandardButton(
                    content=Column(
                        controls=[
                            Row(
                                controls=[
                                    Text(
                                        value=date,
                                        size=12,
                                        font_family=Fonts.SEMIBOLD,
                                        color=colors.ON_PRIMARY_CONTAINER,
                                    ),
                                ],
                            ),
                            Row(
                                controls=[
                                    Text(
                                        value=value,
                                        size=28,
                                        font_family=Fonts.SEMIBOLD,
                                        color=colors.ON_PRIMARY_CONTAINER,
                                    ),
                                ],
                            ),
                            Row(
                                controls=[
                                    Text(
                                        value=state,
                                        size=18,
                                        font_family=Fonts.SEMIBOLD,
                                        color=colors.ON_PRIMARY_CONTAINER,
                                    ),
                                ],
                            ),
                        ],
                        alignment=MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    on_click=partial(self.request_view, request.id),
                    bgcolor=colors.PRIMARY_CONTAINER,
                    horizontal=34,
                    vertical=24,
                )
            )
        return cards

    async def get_history_request(self):
        return Row(
            controls=[
                SubTitle(value=await self.client.session.gtv(key='requests_history_title')),
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

    async def build(self):
        self.is_input, self.is_output, self.is_all, self.is_finish = True, True, True, False
        self.client.session.wallets = await self.client.session.api.client.wallets.get_list()
        self.client.session.current_wallet = await self.client.session.api.client.wallets.get(
            id_=self.client.session.current_wallet.id,
        )
        self.scroll = ScrollMode.AUTO
        self.controls = [
            Container(
                content=Column(
                    controls=[
                        Title(
                            value=await self.client.session.gtv(key='request'),
                            create_name_text=await self.client.session.gtv(key='create'),
                            on_create=self.request_create,
                        ),
                        await self.get_currency_request(),
                        await self.get_history_request(),
                    ],
                    expand=True,
                ),
                padding=Padding(right=48, left=48, top=0, bottom=0),
            )
        ]

    async def request_create(self, _):
        from app.views.client.requests import RequestCreateView
        await self.client.change_view(view=RequestCreateView(current_wallet=self.client.session.current_wallet))

    async def request_view(self, request_id: int, _):
        await self.client.change_view(view=RequestView(request_id=request_id))

    async def chip_select(self, event: ControlEvent):
        self.selected_chip = event.control.key
        await self.build()
        await self.update_async()

    async def next_page(self, _):
        if self.page_request < self.total_pages:
            self.page_request += 1
            await self.build()
            await self.update_async()

    async def previous_page(self, _):
        if self.page_request > 1:
            self.page_request -= 1
            await self.build()
            await self.update_async()
