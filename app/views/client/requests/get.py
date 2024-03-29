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

from flet_core import Column, colors, Control, ScrollMode, Row, MainAxisAlignment, Container, \
    padding, alignment, Image, Divider

from app.controls.button import StandardButton
from app.controls.information import Text, SubTitle
from app.controls.layout import ClientBaseView
from app.utils import Fonts, value_to_float, Icons
from app.views.client.requests.orders.get import OrderView


class RequestView(ClientBaseView):
    route = '/client/request/get'
    request = dict
    orders: list
    custom_info: list
    custom_controls: list[Control]

    def __init__(self, request_id: int):
        super().__init__()
        self.request_id = request_id

    async def get_info_card(self):
        rate = value_to_float(
            value=self.request.rate, decimal=self.request.rate_decimal
        )
        if self.request.type == 'input':
            input_currency = await self.client.session.api.client.currencies.get(id_str=self.request.input_currency)
            input_currency_value = value_to_float(
                value=self.request.input_currency_value_raw,
                decimal=input_currency.decimal,
            )
            input_value = value_to_float(
                value=self.request.input_value_raw,
                decimal=input_currency.decimal,
            )
            value_str = f'{input_currency_value} {input_currency.id_str.upper()} -> {input_value}'
            rate_str = f'{rate} {input_currency.id_str.upper()} / 1'
        elif self.request.type == 'output':
            output_currency = await self.client.session.api.client.currencies.get(
                id_str=self.request.output_currency,
            )
            output_currency_value = value_to_float(
                value=self.request.output_currency_value_raw,
                decimal=output_currency.decimal,
            )
            output_value = value_to_float(
                value=self.request.output_raw,
                decimal=output_currency.decimal,
            )
            value_str = f'{output_value} -> {output_currency_value} {output_currency.id_str.upper()}'
            rate_str = f'{rate} {output_currency.id_str.upper()} / 1'
        else:
            input_currency = await self.client.session.api.client.currencies.get(id_str=self.request.input_currency)
            output_currency = await self.client.session.api.client.currencies.get(
                id_str=self.request.output_currency,
            )
            input_currency_value = value_to_float(
                value=self.request.input_currency_value_raw,
                decimal=input_currency.decimal,
            )
            output_currency_value = value_to_float(
                value=self.request.output_currency_value_raw,
                decimal=output_currency.decimal,
            )
            value_str = (
                f'{input_currency_value} {input_currency.id_str.upper()}'
                f' -> '
                f'{output_currency_value} {output_currency.id_str.upper()}'
            )
            rate_str = f'{rate} {input_currency.id_str.upper()} / 1 {output_currency.id_str.upper()}'
        return Container(
            content=Column(
                controls=[
                    Row(
                        controls=[
                            Text(
                                value=value_str,
                                size=28,
                                font_family=Fonts.SEMIBOLD,
                                color=colors.ON_PRIMARY_CONTAINER,
                            ),
                        ],
                    ),
                    Divider(color=colors.ON_PRIMARY_CONTAINER),
                    Row(
                        controls=[
                            Text(
                                value=await self.client.session.gtv(key='request_id'),
                                size=14,
                                font_family=Fonts.SEMIBOLD,
                                color=colors.ON_PRIMARY_CONTAINER,
                            ),
                            Text(
                                value=f'{self.request.id:08}',
                                size=14,
                                font_family=Fonts.SEMIBOLD,
                                color=colors.ON_PRIMARY_CONTAINER,
                            ),
                        ],
                        alignment=MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    Row(
                        controls=[
                            Text(
                                value=await self.client.session.gtv(key='state'),
                                size=14,
                                font_family=Fonts.SEMIBOLD,
                                color=colors.ON_PRIMARY_CONTAINER,
                            ),
                            Text(
                                value=await self.client.session.gtv(key=f'request_state_{self.request.state}'),
                                size=14,
                                font_family=Fonts.SEMIBOLD,
                                color=colors.ON_PRIMARY_CONTAINER,
                            ),
                        ],
                        alignment=MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    Row(
                        controls=[
                            Text(
                                value=await self.client.session.gtv(key='rate'),
                                size=14,
                                font_family=Fonts.SEMIBOLD,
                                color=colors.ON_PRIMARY_CONTAINER,
                            ),
                            Text(
                                value=rate_str,
                                size=14,
                                font_family=Fonts.SEMIBOLD,
                                color=colors.ON_PRIMARY_CONTAINER,
                            ),
                        ],
                        alignment=MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    Row(
                        controls=[
                            Text(
                                value=await self.client.session.gtv(key='request_output_method'),
                                size=14,
                                font_family=Fonts.SEMIBOLD,
                                color=colors.ON_PRIMARY_CONTAINER,
                            ),
                            Text(
                                value='404',
                                size=14,
                                font_family=Fonts.SEMIBOLD,
                                color=colors.ON_PRIMARY_CONTAINER,
                            ),
                        ],
                        alignment=MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    Row(
                        controls=[
                            Text(
                                value=await self.client.session.gtv(key='date'),
                                size=14,
                                font_family=Fonts.SEMIBOLD,
                                color=colors.ON_PRIMARY_CONTAINER,
                            ),
                            Text(
                                value=self.request.date.strftime('%Y-%m-%d, %H:%M:%S'),
                                size=14,
                                font_family=Fonts.SEMIBOLD,
                                color=colors.ON_PRIMARY_CONTAINER,
                            ),
                        ],
                        alignment=MainAxisAlignment.SPACE_BETWEEN,
                    ),
                ],
            ),
            bgcolor=colors.PRIMARY_CONTAINER,
            padding=padding.symmetric(vertical=32, horizontal=32),
        )

    async def get_controls_waiting(self):
        return [
            Container(
                content=Row(
                    controls=[
                        StandardButton(
                            text=await self.client.session.gtv(key='confirm'),
                            on_click=self.waiting_confirm,
                            expand=True,
                        )
                    ],
                ),
                expand=True,
                alignment=alignment.bottom_center,
            ),
        ]

    """
    ORDERS SEND
    """

    async def get_orders_send_cards(self):
        cards: list = []
        for order in self.orders:
            currency = await self.client.session.api.client.currencies.get(id_str=order.currency)
            state_str = await self.client.session.gtv(key=f'request_order_state_{order.state}')
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
                                                color=colors.ON_PRIMARY_CONTAINER,
                                            ),
                                        ],
                                    ),
                                    Row(
                                        controls=[
                                            Text(
                                                value=f'404 CARD NUMBER',
                                                size=28,
                                                font_family=Fonts.SEMIBOLD,
                                                color=colors.ON_PRIMARY_CONTAINER,
                                            ),
                                        ],
                                    ),
                                    Row(
                                        controls=[
                                            Text(
                                                value=value_str,
                                                size=16,
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
                                color=colors.ON_PRIMARY_CONTAINER,
                            ),
                        ],
                        alignment=MainAxisAlignment.SPACE_BETWEEN,
                        spacing=2,
                    ),
                    on_click=partial(self.order_view, order.id),
                    bgcolor=colors.PRIMARY_CONTAINER,
                ),
            )
        return cards

    async def get_orders_send(self) -> Row:
        return Row(
            scroll=ScrollMode.AUTO,
            controls=[
                SubTitle(value=await self.client.session.gtv(key='request_order_input_title')),
                *await self.get_orders_send_cards(),
            ],
            wrap=True,
        )

    async def get_help_cards(self) -> list[Control]:
        return [
            SubTitle(value=await self.client.session.gtv(key='request_order_help_title')),
            StandardButton(
                content=Row(
                    controls=[
                        Row(
                            controls=[
                                Text(
                                    value=await self.client.session.gtv(key='faq'),
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
                on_click=None,
            ),
        ]

    async def get_controls_other(self) -> list[Control]:
        return [
            await self.get_orders_send(),
            *await self.get_help_cards(),
        ]

    async def build(self):
        await self.set_type(loading=True)
        self.request = await self.client.session.api.client.requests.get(id_=self.request_id)
        self.orders = await self.client.session.api.client.orders.list_get.by_request(request_id=self.request_id)
        await self.set_type(loading=False)
        controls = [
            await self.get_info_card(),
        ]
        if self.request.state == 'loading':
            pass
        elif self.request.state == 'waiting':
            controls += await self.get_controls_waiting()
        else:
            controls += await self.get_controls_other()
        self.controls = await self.get_controls(
            with_expand=True,
            title=f'{await self.client.session.gtv(key='request_get_title')} #{self.request.id:08}',
            main_section_controls=controls,
        )

    async def order_view(self, order_id: int, _):
        await self.client.change_view(view=OrderView(order_id=order_id))

    async def waiting_confirm(self, _):
        await self.client.session.api.client.requests.update_confirmation(id_=self.request_id)
        await self.client.change_view(go_back=True, delete_current=True, with_restart=True)
