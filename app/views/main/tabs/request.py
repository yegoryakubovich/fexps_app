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

from flet_core import Column, Container, ControlEvent, colors, ScrollMode, Row, MainAxisAlignment, Image

from app.controls.button import Chip, StandardButton
from app.controls.button.actions import ActionItem
from app.controls.information import Text, Card
from app.controls.navigation.pagination import PaginationWidget
from app.utils import Fonts, Icons
from app.views.client.requests import RequestView
from app.views.main.tabs.base import BaseTab
from config import settings


class Chips:
    input = 'is_input'
    output = 'is_output'
    all = 'is_all'
    is_finish = 'is_finish'


class RequestTab(BaseTab):
    scopes: list[ActionItem]
    column: Column
    requests = list[dict]
    page_request: int = 1
    total_pages: int = 1
    filter_chips: list[Chip]
    cards: list[Card]
    is_input: bool
    is_output: bool
    is_all: bool
    is_finish: bool
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_chip = Chips.all

    async def get_actions(self):
        return Row(
            controls=[
                StandardButton(
                    content=Row(
                        controls=[
                            Image(
                                src=Icons.ERROR,
                                height=32,
                                width=32,
                            ),
                            Text(
                                value=await self.client.session.gtv(key=f'request_create'),
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
            ],
            spacing=10,
        )

    async def get_history(self):
        self.filter_chips = [
            Chip(
                name=await self.client.session.gtv(key=f'chips_{Chips.input}'),
                key=Chips.input,
                on_select=self.chip_select,
                selected=self.is_input,
            ),
            Chip(
                name=await self.client.session.gtv(key=f'chips_{Chips.output}'),
                key=Chips.output,
                on_select=self.chip_select,
                selected=self.is_output,
            ),
            Chip(
                name=await self.client.session.gtv(key=f'chips_{Chips.all}'),
                key=Chips.all,
                on_select=self.chip_select,
                selected=self.is_all,
            ),
            Chip(
                name=await self.client.session.gtv(key=f'chips_{Chips.is_finish}'),
                key=Chips.is_finish,
                on_select=self.chip_select,
                selected=self.is_finish,
            ),
        ]
        response = await self.client.session.api.client.requests.search(
            is_input=self.is_input,
            is_output=self.is_output,
            is_all=self.is_all,
            is_finish=self.is_finish,
            page=self.page_request,
        )
        self.requests = response.requests
        self.total_pages = response.pages
        self.scroll = ScrollMode.AUTO
        self.cards: list[Card] = []
        for request in self.requests:
            color, value = None, None
            if request.type == 'input':
                color, value = colors.GREEN, request.input_value / settings.default_decimal
            elif request.type == 'output':
                color, value = colors.RED, request.output_value / settings.default_decimal
            elif request.type == 'all':
                color, value = colors.GREY, f'{0} -> {0}'
            self.cards.append(Card(
                controls=[
                    Row(
                        controls=[
                            Text(
                                value=await self.client.session.gtv(key=f'request_type_{request.type}'),
                                size=28,
                                font_family=Fonts.REGULAR,
                                color=colors.ON_BACKGROUND,
                            ),
                            Text(
                                value=value,
                                size=32,
                                font_family=Fonts.REGULAR,
                                color=color,
                            ),
                        ],
                        alignment=MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    Row(
                        controls=[
                            Text(
                                value=await self.client.session.gtv(key=f'request_state_{request.state}'),
                                size=16,
                                font_family=Fonts.REGULAR,
                                color=colors.ON_BACKGROUND,

                            ),
                            Text(
                                value=request.date,
                                size=16,
                                font_family=Fonts.REGULAR,
                                color=colors.ON_BACKGROUND,
                            ),
                        ],
                        alignment=MainAxisAlignment.SPACE_BETWEEN,
                    ),
                ],
                on_click=partial(self.request_view, request.id),
            ))

        return Row(
            controls=[
                Row(controls=[Text(
                    value=await self.client.session.gtv(key='requests_history'),
                    size=32,
                    font_family=Fonts.BOLD,
                    color=colors.ON_BACKGROUND,
                )]),
                *self.filter_chips,
                *self.cards,
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
        self.column = Column(
            controls=[
                await self.get_actions(),
                await self.get_history(),
            ],
        )
        self.controls = [
            Container(
                content=self.column,
                padding=10,
            ),
        ]

    async def request_create(self, _):
        from app.views.client.requests import RequestCreateView
        await self.client.change_view(view=RequestCreateView(current_wallet=self.client.session.current_wallet))

    async def chip_select(self, event: ControlEvent):
        if event.control.key == Chips.input:
            self.is_input = True if event.data == 'true' else False
        elif event.control.key == Chips.output:
            self.is_output = True if event.data == 'true' else False
        elif event.control.key == Chips.all:
            self.is_all = True if event.data == 'true' else False
        elif event.control.key == Chips.is_finish:
            self.is_finish = True if event.data == 'true' else False
        self.column.controls[1] = await self.get_history()
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

    async def request_view(self, request_id: int, _):
        await self.client.change_view(view=RequestView(request_id=request_id))
