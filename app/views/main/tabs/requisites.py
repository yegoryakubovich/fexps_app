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

from flet_core import Column, Container, ScrollMode, Image, Row, MainAxisAlignment, colors, ControlEvent, Padding

from app.controls.button import StandardButton, Chip
from app.controls.information import Text
from app.controls.navigation.pagination import PaginationWidget
from app.utils import Icons, Fonts
from app.utils.value import value_to_float
from app.views.main.tabs.base import BaseTab


class Chips:
    input = 'input'
    output = 'output'
    all = 'all'


class RequisiteTab(BaseTab):
    requisites = list[dict]
    column: Column

    # History
    selected_chip: str
    page_requisites: int = 1
    total_pages: int = 1

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
                                value=await self.client.session.gtv(key=f'requisite_create'),
                                size=16,
                                font_family=Fonts.BOLD,
                                color=colors.ON_PRIMARY,
                            ),
                        ],
                        alignment=MainAxisAlignment.CENTER,
                    ),
                    on_click=self.requisite_create,
                    expand=2,
                    bgcolor=colors.PRIMARY,
                ),
            ],
            spacing=10,
        )

    async def get_history(self):
        filter_chips = [
            Chip(
                name=await self.client.session.gtv(key=f'chips_{Chips.input}'),
                key=Chips.input,
                on_select=self.chip_select,
                selected=True if self.selected_chip == Chips.input else False,
            ),
            Chip(
                name=await self.client.session.gtv(key=f'chips_{Chips.output}'),
                key=Chips.output,
                on_select=self.chip_select,
                selected=True if self.selected_chip == Chips.output else False,
            ),
            Chip(
                name=await self.client.session.gtv(key=f'chips_{Chips.all}'),
                key=Chips.all,
                on_select=self.chip_select,
                selected=True if self.selected_chip == Chips.all else False,
            ),
        ]
        response = await self.client.session.api.client.requisites.search(
            is_output=True if self.selected_chip in [Chips.output, Chips.all] else False,
            is_input=True if self.selected_chip in [Chips.input, Chips.all] else False,
            page=self.page_requisites,
        )
        self.requisites = response.requisites
        cards = []
        requisite_text_name = await self.client.session.gtv(key=f'requisite')

        for requisite in self.requisites:
            currency = await self.client.session.api.client.currencies.get(id_str=requisite.currency)
            currency_value = value_to_float(value=requisite.currency_value, decimal=currency.decimal)
            value = value_to_float(value=requisite.value)
            cards.append(
                Container(
                    content=Row(
                        controls=[
                            Column(
                                controls=[
                                    Row(
                                        controls=[
                                            Text(
                                                value=f'{requisite_text_name} #{requisite.id}',
                                                size=28,
                                                font_family=Fonts.REGULAR,
                                                color=colors.ON_PRIMARY_CONTAINER,
                                            ),
                                        ],
                                    ),
                                    Row(
                                        controls=[
                                            Text(
                                                value=await self.client.session.gtv(
                                                    key=f'requisite_type_{requisite.type}'),
                                                size=28,
                                                font_family=Fonts.REGULAR,
                                                color=colors.ON_PRIMARY_CONTAINER,
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                            Column(
                                controls=[
                                    Row(
                                        controls=[
                                            Text(
                                                value=f'{currency_value}({currency.id_str.upper()})',
                                                size=28,
                                                font_family=Fonts.REGULAR,
                                                color=colors.ON_PRIMARY_CONTAINER,

                                            )
                                        ],
                                    ),
                                    Row(
                                        controls=[
                                            Text(
                                                value=f'{value}',
                                                size=28,
                                                font_family=Fonts.REGULAR,
                                                color=colors.ON_PRIMARY_CONTAINER,
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                        alignment=MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    on_click=partial(self.requisite_get, requisite.id),
                    bgcolor=colors.PRIMARY_CONTAINER,
                    padding=Padding(left=16, right=16, top=12, bottom=12),
                ))

        return Row(
            controls=[
                Row(controls=[Text(
                    value=await self.client.session.gtv(key='requisite_history'),
                    size=32,
                    font_family=Fonts.BOLD,
                    color=colors.ON_BACKGROUND,
                )]),
                *filter_chips,
                *cards,
                PaginationWidget(
                    current_page=self.page_requisites,
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
        self.scroll = ScrollMode.AUTO
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

    # Action
    async def requisite_create(self, _: ControlEvent):
        from app.views.client.requisites import RequisiteCreateView
        await self.client.change_view(view=RequisiteCreateView())

    # History
    async def chip_select(self, event: ControlEvent):
        self.selected_chip = event.control.key
        await self.build()
        await self.update_async()

    async def requisite_get(self, requisite_id: int, _: ControlEvent):
        from app.views.client.requisites import RequisiteView
        await self.client.change_view(view=RequisiteView(requisite_id=requisite_id))

    async def next_page(self, _):
        if self.page_requisites < self.total_pages:
            self.page_requisites += 1
            await self.build()
            await self.update_async()

    async def previous_page(self, _):
        if self.page_requisites > 1:
            self.page_requisites -= 1
            await self.build()
            await self.update_async()
