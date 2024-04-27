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

from flet_core import Column, ScrollMode, Row, ControlEvent, colors, Image, MainAxisAlignment, Container

from app.controls.button import Chip, StandardButton
from app.controls.information import Text
from app.controls.information.subtitle import SubTitle
from app.controls.information.title import Title
from app.controls.navigation import PaginationWidget
from app.utils import value_to_float, Fonts, Icons
from app.views.main.tabs.base import BaseTab


class TypeChips:
    INPUT = 'input'
    OUTPUT = 'output'
    ALL = 'all'


class StateChips:
    ENABLE = 'enable'
    STOP = 'stop'
    DISABLE = 'disable'
    ALL = 'all'


class RequisiteTab(BaseTab):
    requisites = list[dict]
    control_dict: dict

    history_requests = dict
    currency_orders = dict
    column: Column

    # History
    selected_type_chip: str
    selected_state_chip: str
    page_requisites: int = 1
    total_pages: int = 1

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_type_chip = TypeChips.ALL
        self.selected_state_chip = StateChips.ENABLE
        self.control_dict = {
            'currently_orders': None,
            'history_requisites': None,
        }

    """
    CURRENCY ORDERS
    """

    async def get_currently_orders_cards(self) -> list[StandardButton]:
        self.currency_orders = await self.client.session.api.client.orders.list_get.main(
            by_request=False,
            by_requisite=True,
            is_active=True,
            is_finished=False,
        )
        cards: list[StandardButton] = []
        for order in self.currency_orders:
            currency = order.currency
            state_str = await self.client.session.gtv(key=f'requisite_order_{order.type}_{order.state}')
            value = value_to_float(value=order.currency_value, decimal=currency.decimal)
            value_str = f'{value} {currency.id_str.upper()}'
            cards.append(
                StandardButton(
                    content=Row(
                        controls=[
                            Column(
                                controls=[
                                    Row(
                                        controls=[
                                            Text(
                                                value=state_str,
                                                size=8,
                                                font_family=Fonts.SEMIBOLD,
                                                color=colors.ON_PRIMARY,
                                            ),
                                        ],
                                    ),
                                    Row(
                                        controls=[
                                            Text(
                                                value=f'404 CARD NUMBER',
                                                size=28,
                                                font_family=Fonts.SEMIBOLD,
                                                color=colors.ON_PRIMARY,
                                            ),
                                        ],
                                    ),
                                    Row(
                                        controls=[
                                            Text(
                                                value=value_str,
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
                                height=32,
                                color=colors.ON_PRIMARY,
                            ),
                        ],
                        alignment=MainAxisAlignment.SPACE_BETWEEN,
                        spacing=2,
                    ),
                    on_click=partial(self.order_view, order.id),
                    bgcolor=colors.PRIMARY,
                ),
            )
        return cards

    async def update_currently_orders(self, update: bool = True):
        cards = await self.get_currently_orders_cards()
        self.control_dict['currently_orders'] = Row()
        if cards:
            self.control_dict['currently_orders'] = Row(
                controls=[
                    SubTitle(value=await self.client.session.gtv(key='requisite_currently_orders_title')),
                    *cards,
                ],
                wrap=True,
            )
        if update:
            await self.update_async()

    """
    REQUISITE HISTORY
    """

    async def get_requisite_history_chips(self) -> list[Row]:
        type_chips = [
            Chip(
                name=await self.client.session.gtv(key=f'chip_{TypeChips.INPUT}'),
                key=TypeChips.INPUT,
                on_select=partial(
                    self.chip_type_select,
                    TypeChips.INPUT,
                ),
                selected=True if self.selected_type_chip == TypeChips.INPUT else False,
            ),
            Chip(
                name=await self.client.session.gtv(key=f'chip_{TypeChips.OUTPUT}'),
                key=TypeChips.OUTPUT,
                on_select=partial(
                    self.chip_type_select,
                    TypeChips.OUTPUT,
                ),
                selected=True if self.selected_type_chip == TypeChips.OUTPUT else False,
            ),
            Chip(
                name=await self.client.session.gtv(key=f'chip_{TypeChips.ALL}'),
                key=TypeChips.ALL,
                on_select=partial(
                    self.chip_type_select,
                    TypeChips.ALL,
                ),
                selected=True if self.selected_type_chip == TypeChips.ALL else False,
            ),
        ]
        state_chips = [
            Chip(
                name=await self.client.session.gtv(key=f'chip_{StateChips.ENABLE}'),
                key=StateChips.ENABLE,
                on_select=partial(
                    self.chip_state_select,
                    StateChips.ENABLE,
                ),
                selected=True if self.selected_state_chip == StateChips.ENABLE else False,
            ),
            Chip(
                name=await self.client.session.gtv(key=f'chip_{StateChips.STOP}'),
                key=StateChips.STOP,
                on_select=partial(
                    self.chip_state_select,
                    StateChips.STOP,
                ),
                selected=True if self.selected_state_chip == StateChips.STOP else False,
            ),
            Chip(
                name=await self.client.session.gtv(key=f'chip_{StateChips.DISABLE}'),
                key=StateChips.DISABLE,
                on_select=partial(
                    self.chip_state_select,
                    StateChips.DISABLE,
                ),
                selected=True if self.selected_state_chip == StateChips.DISABLE else False,
            ),
            Chip(
                name=await self.client.session.gtv(key=f'chip_{StateChips.ALL}'),
                key=StateChips.ALL,
                on_select=partial(
                    self.chip_state_select,
                    StateChips.ALL,
                ),
                selected=True if self.selected_state_chip == StateChips.ALL else False,
            ),
        ]

        return [
            Row(
                controls=type_chips,
            ),
            Row(
                controls=state_chips,
            ),
        ]

    async def get_requisite_history_cards(self) -> list[StandardButton]:
        params = dict(
            is_type_input=False,
            is_type_output=False,
            is_state_enable=False,
            is_state_stop=False,
            is_state_disable=False,
        )
        if self.selected_type_chip in [TypeChips.INPUT, TypeChips.ALL]:
            params['is_type_input'] = True
        if self.selected_type_chip in [TypeChips.OUTPUT, TypeChips.ALL]:
            params['is_type_output'] = True
        if self.selected_state_chip in [StateChips.ENABLE, StateChips.ALL]:
            params['is_state_enable'] = True
        if self.selected_state_chip in [StateChips.STOP, StateChips.ALL]:
            params['is_state_stop'] = True
        if self.selected_state_chip in [StateChips.DISABLE, StateChips.ALL]:
            params['is_state_disable'] = True
        response = await self.client.session.api.client.requisites.search(**params, page=self.page_requisites)
        self.history_requests = response.requisites
        cards: list[StandardButton] = []
        for requisite in self.history_requests:
            currency = requisite.currency
            if requisite.type == 'input':
                method = requisite.input_method
            else:
                method = requisite.output_method
            type_ = await self.client.session.gtv(key=f'requisite_type_{requisite.type}')
            method = await self.client.session.gtv(key=method.name_text)
            type_str = f'{type_} ({method})'
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

    async def update_history_requisites(self, update: bool = True):
        self.control_dict['history_requisites'] = Row(
            controls=[
                SubTitle(value=await self.client.session.gtv(key='requisite_history_title')),
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
        if update:
            await self.update_async()

    async def construct(self):
        await self.update_currently_orders(update=False)
        await self.update_history_requisites(update=False)
        self.scroll = ScrollMode.AUTO
        self.controls = [
            Container(
                content=Column(
                    controls=[
                        Title(
                            value=await self.client.session.gtv(key='requisite_tab_title'),
                            create_name_text=await self.client.session.gtv(key='create'),
                            on_create=self.requisite_create,
                        ),
                        self.control_dict['currently_orders'],
                        self.control_dict['history_requisites'],
                    ]
                ),
                padding=10,
            )
        ]

    async def requisite_create(self, _: ControlEvent):
        from app.views.client.requisites import RequisiteCreateView
        await self.client.change_view(view=RequisiteCreateView())

    async def order_view(self, order_id: int, _: ControlEvent):
        from app.views.client.requisites.orders import RequisiteOrderView
        await self.client.change_view(view=RequisiteOrderView(order_id=order_id))

    async def chip_type_select(self, type_: str, _):
        self.selected_type_chip = type_
        await self.construct()
        await self.update_async()

    async def chip_state_select(self, state: str, _):
        self.selected_state_chip = state
        await self.construct()
        await self.update_async()

    async def requisite_view(self, requisite_id: int, _: ControlEvent):
        from app.views.client.requisites import RequisiteView
        await self.client.change_view(view=RequisiteView(requisite_id=requisite_id))

    async def next_page(self, _):
        if self.page_requisites < self.total_pages:
            self.page_requisites += 1
            await self.construct()
            await self.update_async()

    async def previous_page(self, _):
        if self.page_requisites > 1:
            self.page_requisites -= 1
            await self.construct()
            await self.update_async()
