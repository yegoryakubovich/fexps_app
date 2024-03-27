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

from flet_core import SnackBar, Control, Column, colors, Container, Row, Divider, MainAxisAlignment, \
    padding, Image, ControlEvent

from app.controls.button import StandardButton
from app.controls.information import Text
from app.controls.layout import ClientBaseView
from app.utils import Fonts, value_to_float, Icons
from app.utils.value import value_to_str


class OrderView(ClientBaseView):
    route = '/client/request/order/get'
    order = dict
    request = dict
    method = dict
    snack_bar: SnackBar
    custom_info: list
    custom_controls: list[Control]

    def __init__(self, order_id: int):
        super().__init__()
        self.order_id = order_id

    async def get_info_card(self):
        currency = await self.client.session.api.client.currencies.get(id_str=self.order.currency)
        currency_value = value_to_float(
            value=self.order.currency_value,
            decimal=currency.decimal,
        ) if self.order.currency_value else None
        currency_value_str = f'{value_to_str(currency_value)} {currency.id_str.upper()}'
        color = self.method.color

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

    async def build(self):
        await self.set_type(loading=True)
        self.order = await self.client.session.api.client.orders.get(id_=self.order_id)
        self.request = await self.client.session.api.client.requests.get(id_=self.order.request)
        self.method = await self.client.session.api.client.methods.get(id_=self.order.method)
        await self.set_type(loading=False)
        logging.critical(self.order)
        controls = [
            await self.get_info_card(),
        ]
        if self.request.state == 'loading':
            pass
        elif self.request.state == 'waiting':
            pass
        else:
            pass
        self.controls = await self.get_controls(
            title=await self.client.session.gtv(key='order'),
            with_expand=True,
            main_section_controls=controls,
        )

    async def payment_confirm(self, _):
        pass

    async def copy_to_clipboard(self, data, _):
        await self.client.page.set_clipboard_async(str(data))
