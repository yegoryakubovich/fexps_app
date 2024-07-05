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

from flet_core import Column, ScrollMode, Row, ControlEvent, colors, Image, MainAxisAlignment, Container, Divider

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
    history_requisites_column: Column
    current_orders_column: Column
    orders_column: Column

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

    async def get_orders_cards(
            self,
            orders: list,
            bgcolor: str = colors.PRIMARY_CONTAINER,
            color: str = colors.ON_PRIMARY_CONTAINER,
    ) -> list[StandardButton]:
        cards: list[StandardButton] = []
        for order in orders:
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
                                    Text(
                                        value=f'#{order.id:08}',
                                        size=10,
                                        font_family=Fonts.SEMIBOLD,
                                        color=color,
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
                                height=24,
                                color=color,
                            ),
                        ],
                        alignment=MainAxisAlignment.SPACE_BETWEEN,
                        spacing=2,
                    ),
                    on_click=partial(self.order_view, order.id),
                    bgcolor=bgcolor,
                    horizontal=16,
                    vertical=12,
                ),
            )
        return cards

    """
    CURRENCY ORDERS
    """

    async def update_current_orders_column(self, update: bool = True):
        cards = await self.get_orders_cards(
            orders=await self.client.session.api.client.orders.list_get.main(
                by_request=False,
                by_requisite=True,
                is_active=True,
                is_finished=False,
            ),
            bgcolor=colors.PRIMARY,
            color=colors.ON_PRIMARY,
        )
        self.current_orders_column = Column()
        if cards:
            self.current_orders_column.controls = [
                SubTitle(value=await self.client.session.gtv(key='requisite_currently_orders_title')),
                *cards,
            ]
        if update:
            await self.current_orders_column.update_async()

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
                wrap=True,
            ),
            Divider(),
            Row(
                controls=state_chips,
                wrap=True,
            ),
        ]

    async def get_requisite_history_cards(self, requisites: list) -> list[StandardButton]:
        cards: list[StandardButton] = []
        for requisite in requisites:
            currency = requisite.currency
            method = requisite.input_method if requisite.type == 'input' else requisite.output_method
            type_ = await self.client.session.gtv(key=f'requisite_type_{requisite.type}')
            method_str = await self.client.session.gtv(key=method.name_text)
            type_str = f'{type_} ({method_str})'
            state_str = await self.client.session.gtv(key=f'requisite_state_{requisite.state}')
            currency_value = value_to_float(value=requisite.currency_value, decimal=currency.decimal)
            total_currency_value = value_to_float(value=requisite.total_currency_value, decimal=currency.decimal)
            currency_value_str = f'{currency_value}/{total_currency_value} {currency.id_str.upper()} '
            cards.append(
                StandardButton(
                    content=Row(
                        controls=[
                            Column(
                                controls=[
                                    Text(
                                        value=f'#{requisite.id:08}',
                                        size=10,
                                        font_family=Fonts.SEMIBOLD,
                                        color=colors.ON_PRIMARY_CONTAINER,
                                    ),
                                    Row(
                                        controls=[
                                            Text(
                                                value=type_str,
                                                size=12,
                                                font_family=Fonts.SEMIBOLD,
                                                color=colors.ON_PRIMARY_CONTAINER,
                                            ),
                                            Text(
                                                value='|',
                                                size=12,
                                                font_family=Fonts.SEMIBOLD,
                                                color=colors.ON_PRIMARY_CONTAINER,
                                            ),
                                            Text(
                                                value=state_str,
                                                size=12,
                                                font_family=Fonts.SEMIBOLD,
                                                color=colors.ON_PRIMARY_CONTAINER,
                                            ),
                                        ],
                                    ),
                                    Row(
                                        controls=[
                                            Text(
                                                value=currency_value_str,
                                                size=14,
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
                    on_click=partial(self.requisite_view, requisite.id),
                    bgcolor=colors.PRIMARY_CONTAINER,
                    horizontal=16,
                    vertical=12,
                )
            )
        return cards

    async def update_history_requisites_column(self, update: bool = True):
        history_requisites = await self.client.session.api.client.requisites.search(
            is_type_input=self.selected_type_chip in [TypeChips.INPUT, TypeChips.ALL],
            is_type_output=self.selected_type_chip in [TypeChips.OUTPUT, TypeChips.ALL],
            is_state_enable=self.selected_state_chip in [StateChips.ENABLE, StateChips.ALL],
            is_state_stop=self.selected_state_chip in [StateChips.STOP, StateChips.ALL],
            is_state_disable=self.selected_state_chip in [StateChips.DISABLE, StateChips.ALL],
            page=self.page_requisites,
        )
        self.history_requisites_column = Column(
            controls=[
                SubTitle(value=await self.client.session.gtv(key='requisite_history_title')),
                *await self.get_requisite_history_chips(),
                *await self.get_requisite_history_cards(requisites=history_requisites.requisites),
                PaginationWidget(
                    current_page=self.page_requisites,
                    total_pages=self.total_pages,
                    on_next=self.next_page,
                    on_back=self.previous_page,
                    text_next=await self.client.session.gtv(key='next'),
                    text_back=await self.client.session.gtv(key='back'),
                ),
            ],
        )
        if update:
            await self.history_requisites_column.update_async()

    """
    ORDERS
    """

    async def update_orders_column(self, update: bool = True):
        cards = await self.get_orders_cards(
            orders=await self.client.session.api.client.orders.list_get.main(
                by_request=False,
                by_requisite=True,
                is_active=False,
                is_finished=True,
            ),
        )
        self.orders_column = Column()
        if cards:
            self.orders_column.controls = [
                SubTitle(value=await self.client.session.gtv(key='requisite_orders_title')),
                *cards,
            ]
        if update:
            await self.orders_column.update_async()

    async def construct(self):
        await self.update_current_orders_column(update=False)
        await self.update_history_requisites_column(update=False)
        await self.update_orders_column(update=False)
        self.scroll = ScrollMode.AUTO
        create_disable = False
        if 'requisite_no' in self.client.session.account.permissions:
            create_disable = True
        self.controls = [
            Container(
                content=Column(
                    controls=[
                        Title(
                            value=await self.client.session.gtv(key='requisite_tab_title'),
                            create_name_text=await self.client.session.gtv(key='create'),
                            on_create=self.requisite_create,
                            disabled_create=create_disable,
                        ),
                        self.current_orders_column,
                        self.history_requisites_column,
                        self.orders_column,
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
