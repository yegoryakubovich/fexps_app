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
from functools import partial

from flet_core import Column, ScrollMode, Row, ControlEvent, colors, Image, MainAxisAlignment

from app.controls.button import Chip, StandardButton
from app.controls.information import Text
from app.controls.information.subtitle import SubTitle
from app.controls.information.title import Title
from app.controls.navigation import PaginationWidget
from app.utils import value_to_float, Fonts, Icons
from app.views.main.tabs.base import BaseTab


class Chips:
    INPUT = 'input'
    OUTPUT = 'output'
    ALL = 'all'


class RequisiteTab(BaseTab):
    requisites = list[dict]
    history_requests = dict
    column: Column

    # History
    selected_chip: str
    page_requisites: int = 1
    total_pages: int = 1

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_chip = Chips.ALL

    """
    REQUISITE HISTORY
    """

    async def get_requisite_history_chips(self) -> list[Chip]:
        return [
            Chip(
                name=await self.client.session.gtv(key=f'chips_{Chips.INPUT}'),
                key=Chips.INPUT,
                on_select=self.chip_select,
                selected=True if self.selected_chip == Chips.INPUT else False,
            ),
            Chip(
                name=await self.client.session.gtv(key=f'chips_{Chips.OUTPUT}'),
                key=Chips.OUTPUT,
                on_select=self.chip_select,
                selected=True if self.selected_chip == Chips.OUTPUT else False,
            ),
            Chip(
                name=await self.client.session.gtv(key=f'chips_{Chips.ALL}'),
                key=Chips.ALL,
                on_select=self.chip_select,
                selected=True if self.selected_chip == Chips.ALL else False,
            ),
        ]

    async def get_requisite_history_cards(self) -> list[StandardButton]:
        params = dict(is_input=False, is_output=False)
        if self.selected_chip in [Chips.INPUT, Chips.ALL]:
            params['is_input'] = True
        if self.selected_chip in [Chips.OUTPUT, Chips.ALL]:
            params['is_output'] = True
        response = await self.client.session.api.client.requisites.search(**params, page=1)
        self.history_requests = response.requisites
        cards: list[StandardButton] = []
        for requisite in self.history_requests:
            currency = await self.client.session.api.client.currencies.get(id_str=requisite.currency)
            if requisite.type == 'input':
                method = await self.client.session.api.client.methods.get(id_=requisite.input_method)
            else:
                method = await self.client.session.api.client.methods.get(id_=requisite.output_method)
            type_ = await self.client.session.gtv(key=f'requisite_type_{requisite.type}')
            method = await self.client.session.gtv(key=method.name_text)
            type_str = f'{type_} {method}'
            name_str = f'No Name'
            currency_value = value_to_float(value=requisite.currency_value, decimal=currency.decimal)
            total_currency_value = value_to_float(value=requisite.total_currency_value, decimal=currency.decimal)
            currency_value_str = f'{currency_value}/{total_currency_value} {currency.id_str.upper()} '
            cards.append(
                StandardButton(
                    content=Row(
                        controls=[
                            Column(
                                controls=[
                                    Row(
                                        controls=[
                                            Text(
                                                value=type_str,
                                                size=12,
                                                font_family=Fonts.SEMIBOLD,
                                                color=colors.ON_PRIMARY_CONTAINER,
                                            ),
                                        ],
                                    ),
                                    Row(
                                        controls=[
                                            Text(
                                                value=name_str,
                                                size=28,
                                                font_family=Fonts.SEMIBOLD,
                                                color=colors.ON_PRIMARY_CONTAINER,
                                            ),
                                        ],
                                    ),
                                    Row(
                                        controls=[
                                            Text(
                                                value=currency_value_str,
                                                size=18,
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
                                height=32,
                                color=colors.ON_PRIMARY,
                            ),
                        ],
                        alignment=MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    on_click=partial(self.requisite_view, requisite.id),
                    bgcolor=colors.PRIMARY_CONTAINER,
                    horizontal=34,
                    vertical=24,
                )
            )
        return cards

    async def get_requisite_history(self):
        return Row(
            controls=[
                SubTitle(value=await self.client.session.gtv(key='requisites_history_title')),
                *await self.get_requisite_history_chips(),
                *await self.get_requisite_history_cards(),
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
        self.controls = [
            Title(
                value=await self.client.session.gtv(key='requisite'),
                create_name_text=await self.client.session.gtv(key='create'),
                on_create=self.requisite_create,
            ),
            await self.get_requisite_history(),
        ]

    async def requisite_create(self, _: ControlEvent):
        from app.views.client.requisites import RequisiteCreateView
        await self.client.change_view(view=RequisiteCreateView())

    async def chip_select(self, event: ControlEvent):
        self.selected_chip = event.control.key
        await self.build()
        await self.update_async()

    async def requisite_view(self, requisite_id: int, _: ControlEvent):
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
