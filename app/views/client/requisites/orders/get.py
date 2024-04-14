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
import logging
from functools import partial

from flet_core import Control, Column, Container, Row, Divider, MainAxisAlignment, \
    padding, Image, colors, alignment, ScrollMode

from app.controls.button import StandardButton
from app.controls.information import Text, SubTitle, InformationContainer
from app.controls.layout import ClientBaseView
from app.utils import Fonts, value_to_float, Icons
from app.utils.value import value_to_str
from fexps_api_client.utils import ApiException


class RequisiteOrderView(ClientBaseView):
    route = '/client/requisite/order/get'
    order = dict
    requisite = dict
    method = dict
    currency = dict

    def __init__(self, order_id: int):
        super().__init__()
        self.reload_bool = False
        self.reload_stop = False
        self.order_id = order_id

    async def get_info_card(self):
        currency_value = value_to_float(
            value=self.order.currency_value,
            decimal=self.currency.decimal,
        )
        currency_value_str = f'{value_to_str(currency_value)} {self.currency.id_str.upper()}'
        return InformationContainer(
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
                                value=await self.client.session.gtv(key='sum'),
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
                spacing=-50,
            ),
            bgcolor=self.method.bgcolor,
            padding=padding.symmetric(vertical=32, horizontal=32),
        )

    async def get_help_cards(self) -> list[Control]:
        return [
            SubTitle(value=await self.client.session.gtv(key='requisite_order_help_title')),
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

    """
    INPUT
    """

    async def get_input_confirmation_button(self) -> StandardButton:
        currency_value = value_to_float(
            value=self.order.currency_value,
            decimal=self.currency.decimal,
        )
        currency_value_str = f'{value_to_str(currency_value)} {self.currency.id_str.upper()}'
        output_confirmation = await self.client.session.gtv(key='requisite_order_input_confirmation_button')
        return StandardButton(
            content=Text(
                value=f'{output_confirmation} {currency_value_str}',
                size=20,
                font_family=Fonts.SEMIBOLD,
                color=colors.ON_PRIMARY,
            ),
            bgcolor=colors.PRIMARY,
            on_click=self.input_confirmation_confirm,
            expand=2,
        )

    """
    OUTPUT
    """

    async def get_output_payment_button(self) -> StandardButton:
        currency_value = value_to_float(
            value=self.order.currency_value,
            decimal=self.currency.decimal,
        )
        currency_value_str = f'{value_to_str(currency_value)} {self.currency.id_str.upper()}'
        input_payment_confirm = await self.client.session.gtv(key='requisite_order_output_payment_button')
        return StandardButton(
            content=Text(
                value=f'{input_payment_confirm} {currency_value_str}',
                size=20,
                font_family=Fonts.SEMIBOLD,
                color=colors.ON_PRIMARY,
            ),
            bgcolor=colors.PRIMARY,
            on_click=self.order_payment,
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
                        size=20,
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

    async def get_value_edit_button(self) -> StandardButton:
        return StandardButton(
            content=Row(
                controls=[
                    Text(
                        value=await self.client.session.gtv(key='requisite_order_value_edit_button'),
                        size=20,
                        font_family=Fonts.SEMIBOLD,
                        color=colors.ON_PRIMARY_CONTAINER,
                    ),
                ],
                alignment=MainAxisAlignment.CENTER,
            ),
            bgcolor=colors.PRIMARY_CONTAINER,
            on_click=self.on_dev,
            expand=1,
        )

    async def get_cancel_button(self) -> StandardButton:
        return StandardButton(
            content=Row(
                controls=[
                    Text(
                        value=await self.client.session.gtv(key='requisite_order_cancel_button'),
                        size=20,
                        font_family=Fonts.SEMIBOLD,
                        color=colors.ON_PRIMARY_CONTAINER,
                    ),
                ],
                alignment=MainAxisAlignment.CENTER,
            ),
            bgcolor=colors.PRIMARY_CONTAINER,
            on_click=self.on_dev,
            expand=1,
        )

    async def build(self):
        await self.set_type(loading=True)
        self.order = await self.client.session.api.client.orders.get(id_=self.order_id)
        self.currency = await self.client.session.api.client.currencies.get(id_str=self.order.currency)
        self.requisite = await self.client.session.api.client.requisites.get(id_=self.order.requisite)
        self.method = await self.client.session.api.client.methods.get(id_=self.order.method)
        await self.set_type(loading=False)
        asyncio.create_task(self.auto_reloader())
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
                    await self.get_chat_button(),
                ]
            elif self.order.state == 'confirmation':
                buttons += [
                    await self.get_input_confirmation_button(),
                    await self.get_chat_button(),
                ]
            else:  # completed, canceled
                pass
        elif self.order.type == 'output':
            if self.order.state == 'waiting':
                pass
            elif self.order.state == 'payment':
                buttons += [
                    await self.get_cancel_button(),
                    await self.get_value_edit_button(),
                    await self.get_output_payment_button(),
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
                )
            ]
        self.scroll = ScrollMode.AUTO
        self.controls = await self.get_controls(
            title=await self.client.session.gtv(key='requisite_order_title'),
            main_section_controls=controls,
        )

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

    async def copy_to_clipboard(self, data, _):
        await self.client.page.set_clipboard_async(str(data))

    async def chat_open(self, _):
        from app.views.client.chat import ChatView
        await self.client.change_view(view=ChatView(order_id=self.order_id))

    async def order_payment(self, _):
        from .payment import RequisiteOrderPaymentView
        await self.client.change_view(view=RequisiteOrderPaymentView(order_id=self.order_id))

    async def on_dev(self, _):
        await self.client.session.bs_info.open_(
            icon=Icons.CHILL,
            title=await self.client.session.gtv(key='in_dev_title'),
            description=await self.client.session.gtv(key='in_dev_description'),
        )

    """INPUT"""

    async def input_confirmation_confirm(self, _):
        try:
            await self.client.session.api.client.orders.updates.completed(id_=self.order_id)
            await self.client.change_view(go_back=True, delete_current=True, with_restart=True)
        except ApiException as exception:
            return await self.client.session.error(exception=exception)
