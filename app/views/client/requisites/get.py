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


import asyncio
from functools import partial

from flet_core import Row, colors, MainAxisAlignment, Image, Column, Control, ScrollMode, Container

from app.controls.button import StandardButton
from app.controls.information import SubTitle, Text
from app.controls.layout import ClientBaseView
from app.utils import Icons, Fonts, value_to_float
from app.utils.value import requisite_value_to_str
from app.views.client.requisites.orders.get import RequisiteOrderView
from app.views.main.tabs.acoount import open_support
from fexps_api_client.utils import ApiException


class RequisiteView(ClientBaseView):
    route = '/client/requisite/get'
    requisite = dict
    orders = list[dict]

    def __init__(self, requisite_id: int):
        super().__init__()
        self.reload_bool = False
        self.reload_stop = False
        self.requisite_id = requisite_id

    """
    ORDERS
    """

    async def get_orders_cards(self):
        cards: list = []
        for order in self.orders:
            currency = order.currency
            state_str = await self.client.session.gtv(key=f'requisite_order_{order.type}_{order.state}')
            value = value_to_float(value=order.currency_value, decimal=currency.decimal)
            value_str = f'{value} {currency.id_str.upper()}'
            color, bgcolor = colors.ON_PRIMARY, colors.PRIMARY
            if order.state in ['completed', 'canceled']:
                color, bgcolor = colors.ON_PRIMARY_CONTAINER, colors.PRIMARY_CONTAINER
            order_info_str = ''
            if order.requisite_scheme_fields:
                order_info_key = order.requisite_scheme_fields[0]['key']
                order_info_str = requisite_value_to_str(
                    value=order.requisite_fields[order_info_key],
                    card_number_replaces=True,
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
                                                value=state_str,
                                                size=8,
                                                font_family=Fonts.SEMIBOLD,
                                                color=color,
                                            ),
                                        ],
                                    ),
                                    Row(
                                        controls=[
                                            Text(
                                                value=order_info_str,
                                                size=28,
                                                font_family=Fonts.SEMIBOLD,
                                                color=color,
                                            ),
                                        ],
                                    ),
                                    Row(
                                        controls=[
                                            Text(
                                                value=value_str,
                                                size=16,
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
                                height=32,
                                color=color,
                            ),
                        ],
                        alignment=MainAxisAlignment.SPACE_BETWEEN,
                        spacing=2,
                    ),
                    on_click=partial(self.order_view, order.id),
                    bgcolor=bgcolor,
                ),
            )
        return cards

    async def get_order_row(self) -> Row:
        return Row(
            controls=[
                SubTitle(value=await self.client.session.gtv(key='requisite_orders_title')),
                *await self.get_orders_cards(),
            ],
            wrap=True,
        )

    async def get_help_cards(self) -> list[Control]:
        return [
            SubTitle(value=await self.client.session.gtv(key='requisite_help_title')),
            StandardButton(
                content=Row(
                    controls=[
                        Row(
                            controls=[
                                Text(
                                    value=await self.client.session.gtv(key='help_faq'),
                                    size=28,
                                    font_family=Fonts.SEMIBOLD,
                                    color=colors.ON_BACKGROUND,
                                ),
                            ],
                            expand=True,
                        ),
                        Image(
                            src=Icons.OPEN,
                            height=28,
                            color=colors.ON_BACKGROUND,
                        ),
                    ],
                ),
                bgcolor=colors.BACKGROUND,
                horizontal=0,
                vertical=0,
                on_click=None,
            ),
            StandardButton(
                content=Row(
                    controls=[
                        Row(
                            controls=[
                                Text(
                                    value=await self.client.session.gtv(key='help_telegram_contact_title'),
                                    size=28,
                                    font_family=Fonts.SEMIBOLD,
                                    color=colors.ON_BACKGROUND,
                                ),
                            ],
                            expand=True,
                        ),
                        Image(
                            src=Icons.OPEN,
                            height=28,
                            color=colors.ON_BACKGROUND,
                        ),
                    ]
                ),
                bgcolor=colors.BACKGROUND,
                horizontal=0,
                vertical=0,
                on_click=open_support,
            ),
        ]

    """
    INPUT
    """

    async def get_controls_input(self) -> list[Control]:
        return [
            *await self.get_help_cards(),
        ]

    """
    OUTPUT
    """

    async def get_controls_output(self) -> list[Control]:
        return [
            *await self.get_help_cards(),
        ]

    """
    BUTTON
    """

    async def get_stop_button(self):
        return StandardButton(
            content=Text(
                value=await self.client.session.gtv(key='requisite_stop_button'),
                size=20,
                font_family=Fonts.SEMIBOLD,
                color=colors.ON_PRIMARY,
            ),
            bgcolor=colors.PRIMARY,
            on_click=self.requisite_state_stop,
            expand=1,
        )

    async def get_enable_button(self):
        return StandardButton(
            content=Text(
                value=await self.client.session.gtv(key='requisite_enable_button'),
                size=20,
                font_family=Fonts.SEMIBOLD,
                color=colors.ON_PRIMARY,
            ),
            bgcolor=colors.PRIMARY,
            on_click=self.requisite_state_enable,
            expand=1,
        )

    async def get_disable_button(self):
        return StandardButton(
            content=Text(
                value=await self.client.session.gtv(key='requisite_disable_button'),
                size=20,
                font_family=Fonts.SEMIBOLD,
                color=colors.ON_PRIMARY,
            ),
            bgcolor=colors.PRIMARY,
            on_click=self.requisite_state_disable,
            expand=1,
        )

    async def build(self):
        await self.set_type(loading=True)
        self.requisite = await self.client.session.api.client.requisites.get(id_=self.requisite_id)
        self.orders = await self.client.session.api.client.orders.list_get.by_requisite(requisite_id=self.requisite_id)
        await self.set_type(loading=False)
        asyncio.create_task(self.auto_reloader())
        controls = [
            await self.get_order_row(),
        ]
        buttons = []
        if self.requisite.type == 'input':
            controls += await self.get_controls_input()
        elif self.requisite.type == 'output':
            controls += await self.get_controls_output()
        if self.requisite.state == 'enable':
            buttons += [
                Row(
                    controls=[
                        await self.get_stop_button(),
                    ],
                ),
            ]
        elif self.requisite.state == 'stop':
            buttons += [
                Row(
                    controls=[
                        await self.get_enable_button(),
                        await self.get_disable_button(),
                    ],
                ),
            ]
        title_str = await self.client.session.gtv(key='requisite_get_title')
        self.controls = await self.get_controls(
            title=f'{title_str} #{self.requisite.id:08}',
            with_expand=True,
            back_with_restart=True,
            main_section_controls=[
                Container(
                    content=Column(
                        controls=controls,
                        scroll=ScrollMode.AUTO,
                    ),
                    expand=True,
                ),
                *[
                    Container(content=button)
                    for button in buttons
                ],
            ],
        )

    async def order_view(self, order_id: int, _):
        await self.client.change_view(view=RequisiteOrderView(order_id=order_id))

    async def requisite_state_stop(self, _):
        await self.set_type(loading=True)
        try:
            await self.client.session.api.client.requisites.updates.stop(id_=self.requisite_id)
            await self.set_type(loading=False)
            await self.build()
            await self.update_async()
        except ApiException as exception:
            await self.set_type(loading=False)
            return await self.client.session.error(exception=exception)

    async def requisite_state_enable(self, _):
        await self.set_type(loading=True)
        try:
            await self.client.session.api.client.requisites.updates.enable(id_=self.requisite_id)
            await self.set_type(loading=False)
            await self.build()
            await self.update_async()
        except ApiException as exception:
            await self.set_type(loading=False)
            return await self.client.session.error(exception=exception)

    async def requisite_state_disable(self, _):
        await self.set_type(loading=True)
        try:
            await self.client.session.api.client.requisites.updates.disable(id_=self.requisite_id)
            await self.set_type(loading=False)
            await self.build()
            await self.update_async()
        except ApiException as exception:
            await self.set_type(loading=False)
            return await self.client.session.error(exception=exception)

    async def auto_reloader(self):
        if self.reload_bool:
            return
        self.reload_bool = True
        await asyncio.sleep(5)
        while self.reload_bool:
            if self.client.page.route != self.route:
                self.reload_bool = False
                return
            if self.reload_stop:
                continue
            await self.build()
            await self.update_async()
            await asyncio.sleep(5)
