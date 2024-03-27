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

from flet_core import SnackBar, Control, Column, Container, Row, Divider, MainAxisAlignment, \
    padding, Image, colors, alignment

from app.controls.button import StandardButton
from app.controls.information import Text, SubTitle
from app.controls.layout import ClientBaseView
from app.utils import Fonts, value_to_float, Icons
from app.utils.value import value_to_str


class OrderView(ClientBaseView):
    route = '/client/request/order/get'
    order = dict
    request = dict
    method = dict
    currency = dict
    snack_bar: SnackBar
    custom_info: list
    custom_controls: list[Control]

    def __init__(self, order_id: int):
        super().__init__()
        self.order_id = order_id

    async def get_info_card(self):
        currency_value = value_to_float(
            value=self.order.currency_value,
            decimal=self.currency.decimal,
        ) if self.order.currency_value else None
        currency_value_str = f'{value_to_str(currency_value)} {self.currency.id_str.upper()}'
        return Container(
            content=Column(
                controls=[
                    Row(
                        controls=[
                            Text(
                                value=await self.client.session.gtv(key=self.method.name_text),
                                size=28,
                                font_family=Fonts.SEMIBOLD,
                                color=self.method.color,
                            ),
                        ],
                    ),
                    Divider(color=self.method.color),
                    *[
                        Row(
                            controls=[
                                Text(
                                    value=await self.client.session.gtv(key=scheme_field.get('name_text_key')),
                                    size=14,
                                    font_family=Fonts.SEMIBOLD,
                                    color=self.method.color,
                                ),
                                Row(
                                    controls=[
                                        Text(
                                            value=self.order.requisite_fields.get(scheme_field.get('key'), 'None'),
                                            size=14,
                                            font_family=Fonts.SEMIBOLD,
                                            color=self.method.color,
                                        ),
                                        StandardButton(
                                            content=Image(
                                                src=Icons.COPY,
                                                width=18,
                                                color=self.method.color,
                                            ),
                                            on_click=partial(
                                                self.copy_to_clipboard,
                                                self.order.requisite_fields.get(scheme_field.get('key')),
                                            ),
                                            bgcolor=self.method.bgcolor,
                                            horizontal=0,
                                            vertical=0,
                                        ),
                                    ],
                                    spacing=0,
                                ),
                            ],
                            alignment=MainAxisAlignment.SPACE_BETWEEN,
                        )
                        for scheme_field in self.order.requisite_scheme_fields
                    ],
                    Row(
                        controls=[
                            Text(
                                value=await self.client.session.gtv(key='order_sum'),
                                size=14,
                                font_family=Fonts.SEMIBOLD,
                                color=self.method.color,
                            ),
                            Row(
                                controls=[
                                    Text(
                                        value=currency_value_str,
                                        size=14,
                                        font_family=Fonts.SEMIBOLD,
                                        color=self.method.color,
                                    ),
                                    StandardButton(
                                        content=Image(
                                            src=Icons.COPY,
                                            width=18,
                                            color=self.method.color,
                                        ),
                                        on_click=partial(
                                            self.copy_to_clipboard,
                                            currency_value,
                                        ),
                                        bgcolor=self.method.bgcolor,
                                        horizontal=0,
                                        vertical=0,
                                    ),
                                ],
                                spacing=0,
                            ),
                        ],
                        alignment=MainAxisAlignment.SPACE_BETWEEN,
                    ),
                ],
            ),
            bgcolor=self.method.bgcolor,
            padding=padding.symmetric(vertical=32, horizontal=32),
        )

    async def get_help_cards(self) -> list[Control]:
        return [
            SubTitle(value=await self.client.session.gtv(key='help_card_title')),
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
                on_click=None,
            ),
            StandardButton(
                content=Row(
                    controls=[
                        Row(
                            controls=[
                                Text(
                                    value=await self.client.session.gtv(key='help_chat_title'),
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

    async def get_input_payment_button(self) -> StandardButton:
        currency_value = value_to_float(
            value=self.order.currency_value,
            decimal=self.currency.decimal,
        ) if self.order.currency_value else None
        currency_value_str = f'{value_to_str(currency_value)} {self.currency.id_str.upper()}'
        return StandardButton(
            content=Text(
                value=f'{await self.client.session.gtv(key='order_payment_confirm')} {currency_value_str}',
                size=28,
                font_family=Fonts.SEMIBOLD,
                color=colors.ON_PRIMARY,
            ),
            bgcolor=colors.PRIMARY,
            on_click=self.input_payment_confirm,
            expand=2,
        )

    async def get_chat_button(self) -> StandardButton:
        return StandardButton(
            content=Row(
                controls=[
                    Image(
                        src=Icons.CHAT,
                        width=28,
                        color=colors.ON_PRIMARY_CONTAINER,
                    ),
                    Text(
                        value=await self.client.session.gtv(key='chat_button'),
                        size=28,
                        font_family=Fonts.SEMIBOLD,
                        color=colors.ON_PRIMARY_CONTAINER,
                    ),
                ],
                alignment=MainAxisAlignment.CENTER,
            ),
            bgcolor=colors.PRIMARY_CONTAINER,
            on_click=self.chat_open,
            expand=1,
        )

    async def build(self):
        await self.set_type(loading=True)
        self.order = await self.client.session.api.client.orders.get(id_=self.order_id)
        self.currency = await self.client.session.api.client.currencies.get(id_str=self.order.currency)
        self.request = await self.client.session.api.client.requests.get(id_=self.order.request)
        self.method = await self.client.session.api.client.methods.get(id_=self.order.method)
        await self.set_type(loading=False)
        logging.critical(self.order)
        controls = [
            await self.get_info_card(),
            *await self.get_help_cards(),
        ]
        buttons = []
        if self.order.type == 'input':
            if self.order.state == 'waiting':
                pass
            elif self.order.state == 'payment':
                buttons += [
                    await self.get_input_payment_button(),
                    await self.get_chat_button(),
                ]
            elif self.order.state == 'confirmation':
                buttons += [
                    await self.get_chat_button(),
                ]
            else:  # completed, canceled
                pass
        elif self.order.state == 'output':
            if self.order.state == 'waiting':
                pass
            elif self.order.state == 'payment':
                buttons += [
                    await self.get_chat_button(),
                ]
            elif self.order.state == 'confirmation':
                buttons += [
                    await self.get_chat_button(),
                ]
            else:  # completed, canceled
                pass
        if buttons:
            controls += [
                Container(
                    content=Row(
                        controls=buttons,
                    ),
                    expand=True,
                    alignment=alignment.bottom_center,
                )
            ]
        self.controls = await self.get_controls(
            title=await self.client.session.gtv(key='order'),
            with_expand=True,
            main_section_controls=controls,
        )

    async def payment_confirm(self, _):
        pass

    async def copy_to_clipboard(self, data, _):
        await self.client.page.set_clipboard_async(str(data))

    async def chat_open(self, _):
        pass

    async def input_payment_confirm(self, _):
        pass
