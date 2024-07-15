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
from typing import Optional

from flet_core import Column, Container, Row, Divider, MainAxisAlignment, padding, Image, colors, ScrollMode, \
    AlertDialog, IconButton, icons

from app.controls.button import StandardButton
from app.controls.information import Text, InformationContainer
from app.controls.input import TextField
from app.controls.layout import ClientBaseView
from app.utils import Fonts, value_to_float, Icons, Error, value_to_int
from app.utils.constants.order import OrderStates, OrderTypes
from app.utils.value import value_to_str
from config import settings
from fexps_api_client.utils import ApiException


class RequestOrderView(ClientBaseView):
    route = '/client/request/order/get'

    order = dict
    order_request = dict
    request = dict
    method = dict
    currency = dict

    info_card: InformationContainer
    inactive: Optional[bool]

    chat_button: StandardButton
    back_button: StandardButton
    payment_payment_button: StandardButton
    payment_confirmation_confirm_button: StandardButton
    payment_confirmation_cancel_button: StandardButton
    order_request_create_update_value_button: StandardButton
    order_request_create_cancel_button: StandardButton
    order_request_create_recreate_button: StandardButton
    order_request_completed_button: StandardButton
    order_request_canceled_button: StandardButton

    dialog: AlertDialog
    # order request update value
    tf_value: TextField

    def __init__(self, order_id: int):
        super().__init__()
        self.order_id = order_id
        self.dialog = AlertDialog()
        self.tf_value = TextField()
        self.inactive = None

    async def update_info_card(self, update: bool = True) -> None:
        currency_value = value_to_float(value=self.order.currency_value, decimal=self.currency.decimal)
        state_str = await self.client.session.gtv(key=f'request_order_{self.order.type}_{self.order.state}')
        info_controls = [
            Row(
                controls=[
                    Text(
                        value=await self.client.session.gtv(key=self.method.name_text),
                        size=settings.get_font_size(multiple=3),
                        font_family=Fonts.SEMIBOLD,
                        color=self.method.color,
                    ),
                ],
            ),
            Row(
                controls=[
                    Text(
                        value=await self.client.session.gtv(key='state'),
                        size=settings.get_font_size(multiple=1.6),
                        font_family=Fonts.SEMIBOLD,
                        color=self.method.color,
                    ),
                    Text(
                        value=state_str,
                        size=settings.get_font_size(multiple=1.6),
                        font_family=Fonts.SEMIBOLD,
                        color=self.method.color,
                    ),
                ],
                alignment=MainAxisAlignment.SPACE_BETWEEN,
            ),
            Divider(color=self.method.color),
        ]
        for scheme_field in self.order.requisite_scheme_fields:
            info_controls += [
                Row(
                    controls=[
                        TextField(
                            label=await self.client.session.gtv(key=scheme_field.get('name_text_key')),
                            value=self.order.requisite_fields.get(scheme_field.get('key')),
                            color=self.method.color,
                            bgcolor=self.method.bgcolor,
                            expand=True,
                            read_only=True,
                        ),
                        StandardButton(
                            content=Image(src=Icons.COPY, width=18, color=self.method.color),
                            on_click=partial(
                                self.copy_to_clipboard,
                                self.order.requisite_fields.get(scheme_field.get('key')),
                            ),
                            bgcolor=self.method.bgcolor,
                            horizontal=4,
                            vertical=4,
                        ),
                    ],
                    spacing=8,
                ),
            ]
        info_controls += [
            Row(
                controls=[
                    TextField(
                        label=await self.client.session.gtv(key='sum'),
                        value=currency_value,
                        suffix_text=self.currency.id_str.upper(),
                        color=self.method.color,
                        bgcolor=self.method.bgcolor,
                        expand=True,
                        read_only=True,
                    ),
                    StandardButton(
                        content=Image(src=Icons.COPY, width=18, color=self.method.color),
                        on_click=partial(self.copy_to_clipboard, currency_value),
                        bgcolor=self.method.bgcolor,
                        horizontal=0,
                        vertical=0,
                    ),
                ],
                spacing=8,
            ),
        ]
        self.info_card = InformationContainer(
            content=Column(
                controls=info_controls,
            ),
            bgcolor=self.method.bgcolor,
            padding=padding.symmetric(vertical=32, horizontal=32),
        )
        if update:
            await self.info_card.update_async()

    """
    INPUT PAYMENT
    """

    async def update_payment_payment_button(self, update: bool = True) -> None:
        currency_value = value_to_float(value=self.order.currency_value, decimal=self.currency.decimal)
        self.payment_payment_button = StandardButton(
            content=Text(
                value=await self.client.session.gtv(
                    key='request_order_payment_payment_button',
                    value=value_to_str(currency_value),
                    currency=self.currency.id_str.upper(),
                ),
                size=settings.get_font_size(multiple=1.5),
                font_family=Fonts.SEMIBOLD,
                color=colors.WHITE,
            ),
            bgcolor=colors.GREEN,
            on_click=self.payment,
            expand=1,
        )
        if update:
            await self.payment_payment_button.update_async()

    """
    OUTPUT CONFIRMATION
    """

    async def update_payment_confirmation_confirm_button(self, update: bool = True) -> None:
        currency_value = value_to_float(value=self.order.currency_value, decimal=self.currency.decimal)
        self.payment_confirmation_confirm_button = StandardButton(
            content=Text(
                value=await self.client.session.gtv(
                    key='request_order_payment_confirmation_confirm_button',
                    value=value_to_str(currency_value),
                    currency=self.currency.id_str.upper(),
                ),
                size=settings.get_font_size(multiple=1.5),
                font_family=Fonts.SEMIBOLD,
                color=colors.BLACK,
            ),
            bgcolor=colors.GREEN,
            on_click=self.payment_confirmation_confirm,
            expand=2,
        )
        if update:
            await self.payment_confirmation_confirm_button.update_async()

    async def update_payment_confirmation_cancel_button(self, update: bool = True) -> None:
        self.payment_confirmation_cancel_button = StandardButton(
            content=Text(
                value=await self.client.session.gtv(key='request_order_payment_confirmation_cancel_button'),
                size=settings.get_font_size(multiple=1.5),
                font_family=Fonts.SEMIBOLD,
                color=colors.BLACK,
            ),
            bgcolor=colors.RED,
            on_click=self.payment_confirmation_cancel,
            expand=2,
        )
        if update:
            await self.payment_confirmation_cancel_button.update_async()

    """
    CHAT
    """

    async def update_chat_button(self, update: bool = True) -> None:
        self.chat_button = StandardButton(
            content=Row(
                controls=[
                    Image(
                        src=Icons.CHAT,
                        width=14,
                        color=colors.ON_PRIMARY_CONTAINER,
                    ),
                    Text(
                        value=await self.client.session.gtv(key='chat_button'),
                        size=settings.get_font_size(multiple=1.5),
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
        if update:
            await self.chat_button.update_async()

    """
    UPDATES
    """

    async def update_order_request_create_update_value_button(self, update: bool = True) -> None:
        self.order_request_create_update_value_button = StandardButton(
            content=Row(
                controls=[
                    Text(
                        value=await self.client.session.gtv(key='request_order_order_request_update_value_button'),
                        size=settings.get_font_size(multiple=1.5),
                        font_family=Fonts.SEMIBOLD,
                        color=colors.ON_PRIMARY_CONTAINER,
                    ),
                ],
                alignment=MainAxisAlignment.CENTER,
            ),
            bgcolor=colors.PRIMARY_CONTAINER,
            on_click=self.order_request_update_value_open,
            horizontal=12,
            vertical=8,
            expand=1,
        )
        if update:
            await self.order_request_create_update_value_button.update_async()

    async def update_order_request_create_recreate_button(self, update: bool = True) -> None:
        self.order_request_create_recreate_button = StandardButton(
            content=Row(
                controls=[
                    Text(
                        value=await self.client.session.gtv(key='request_order_order_request_recreate_button'),
                        size=settings.get_font_size(multiple=1.5),
                        font_family=Fonts.SEMIBOLD,
                        color=colors.ON_PRIMARY_CONTAINER,
                    ),
                ],
                alignment=MainAxisAlignment.CENTER,
            ),
            bgcolor=colors.PRIMARY_CONTAINER,
            on_click=self.order_request_recreate,
            horizontal=12,
            vertical=8,
            expand=1,
        )
        if update:
            await self.order_request_create_recreate_button.update_async()

    async def update_order_request_create_cancel_button(self, update: bool = True) -> None:
        self.order_request_create_cancel_button = StandardButton(
            content=Row(
                controls=[
                    Text(
                        value=await self.client.session.gtv(key='request_order_order_request_cancel_button'),
                        size=settings.get_font_size(multiple=1.5),
                        font_family=Fonts.SEMIBOLD,
                        color=colors.WHITE,
                    ),
                ],
                alignment=MainAxisAlignment.CENTER,
            ),
            bgcolor=colors.RED,
            on_click=self.order_request_cancel,
            horizontal=12,
            vertical=8,
            expand=1,
        )
        if update:
            await self.chat_button.update_async()

    async def update_back_button(self, update: bool = True) -> None:
        self.back_button = StandardButton(
            content=Row(
                controls=[
                    Text(
                        value=await self.client.session.gtv(key='request_order_back_button'),
                        size=settings.get_font_size(multiple=1.5),
                        font_family=Fonts.SEMIBOLD,
                        color=colors.ON_PRIMARY_CONTAINER,
                    ),
                ],
                alignment=MainAxisAlignment.CENTER,
            ),
            bgcolor=colors.PRIMARY_CONTAINER,
            on_click=self.back,
            expand=1,
        )
        if update:
            await self.back_button.update_async()

    async def construct(self):
        self.dialog = AlertDialog(modal=True)
        await self.set_type(loading=True)
        self.order = await self.client.session.api.client.orders.get(id_=self.order_id)
        if self.inactive is not None:
            if not self.inactive and self.order.state in [OrderStates.COMPLETED, OrderStates.CANCELED]:
                await self.set_type(loading=False)
                await self.client.change_view(go_back=True, delete_current=True)
                return
        self.order_request = self.order.order_request
        self.currency = self.order.currency
        self.request = self.order.request
        self.method = self.order.method
        await self.set_type(loading=False)
        await self.update_info_card(update=False)
        controls = [
            self.info_card,
        ]
        await self.update_back_button(update=False)
        buttons = [
            Row(
                controls=[
                    self.back_button,
                ]
            ),
        ]
        await self.update_chat_button(update=False)
        self.inactive = False
        if self.order_request:
            pass
        elif self.order.type == OrderTypes.INPUT:
            if self.order.state == OrderStates.WAITING:
                pass
            elif self.order.state == OrderStates.PAYMENT:
                await self.update_order_request_create_update_value_button(update=False)
                await self.update_order_request_create_recreate_button(update=False)
                await self.update_order_request_create_cancel_button(update=False)
                await self.update_payment_payment_button(update=False)
                buttons += [
                    Row(
                        controls=[
                            self.order_request_create_update_value_button,
                            self.order_request_create_recreate_button,
                            self.order_request_create_cancel_button,
                        ],
                        spacing=6,
                    ),
                    Row(
                        controls=[
                            self.payment_payment_button,
                        ],
                    ),
                ]
            elif self.order.state == OrderStates.CONFIRMATION:
                pass
            elif self.order.state in [OrderStates.COMPLETED, OrderStates.CANCELED]:
                self.inactive = True
        elif self.order.type == OrderTypes.OUTPUT:
            if self.order.state == OrderStates.WAITING:
                pass
            elif self.order.state == OrderStates.PAYMENT:
                await self.update_order_request_create_update_value_button(update=False)
                await self.update_order_request_create_recreate_button(update=False)
                await self.update_order_request_create_cancel_button(update=False)
                buttons += [
                    Row(
                        controls=[
                            self.order_request_create_update_value_button,
                            self.order_request_create_recreate_button,
                            self.order_request_create_cancel_button,
                        ],
                        spacing=6,
                    ),
                ]
            elif self.order.state == OrderStates.CONFIRMATION:
                await self.update_payment_confirmation_cancel_button(update=False)
                await self.update_payment_confirmation_confirm_button(update=False)
                buttons += [
                    Row(
                        controls=[
                            self.payment_confirmation_cancel_button,
                            self.payment_confirmation_confirm_button,
                        ]
                    ),
                ]
            elif self.order.state in [OrderStates.COMPLETED, OrderStates.CANCELED]:
                self.inactive = True
        buttons += [
            Row(
                controls=[
                    self.chat_button,
                ]
            ),
        ]
        title_str = await self.client.session.gtv(key='request_order_title')
        self.controls = await self.get_controls(
            title=f'{title_str} #{self.order.id:08}',
            with_expand=True,
            main_section_controls=[
                self.dialog,
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

    async def back(self, _):
        await self.client.change_view(
            go_back=True,
            delete_current=True,
        )

    async def copy_to_clipboard(self, data, _):
        await self.client.session.page.set_clipboard(str(data))

    async def chat_open(self, _):
        from app.views.client.chat import ChatView
        await self.client.change_view(view=ChatView(order_id=self.order_id))

    async def payment(self, _):
        from .payment import RequestOrderPaymentView
        await self.client.change_view(view=RequestOrderPaymentView(order_id=self.order_id))

    async def order_request_update(self, state: str, _):
        try:
            await self.client.session.api.client.orders.requests.update(id_=self.order_request.id, state=state)
            await self.construct()
            await self.update_async()
        except ApiException as exception:
            return await self.client.session.error(exception=exception)

    async def order_request_cancel(self, _):
        try:
            await self.client.session.api.client.orders.requests.create(order_id=self.order_id, type_='cancel')
        except ApiException as exception:
            return await self.client.session.error(exception=exception)

    async def order_request_recreate(self, _):
        try:
            await self.client.session.api.client.orders.requests.create(order_id=self.order_id, type_='recreate')
            await self.construct()
            await self.update_async()
        except ApiException as exception:
            return await self.client.session.error(exception=exception)

    async def dialog_close(self, _):
        self.dialog.open = False
        await self.dialog.update_async()

    async def order_request_update_value_open(self, _):
        self.tf_value = TextField(
            label=await self.client.session.gtv(key='order_request_update_value_value'),
        )
        self.dialog.content = Container(
            content=Column(
                controls=[
                    Row(
                        controls=[
                            Text(
                                value=await self.client.session.gtv(key='request_order_update_value_button'),
                                size=settings.get_font_size(multiple=1.5),
                                font_family=Fonts.BOLD,
                                color=colors.ON_BACKGROUND,
                            ),
                            IconButton(
                                icon=icons.CLOSE,
                                on_click=self.dialog_close,
                                icon_color=colors.ON_BACKGROUND,
                            ),
                        ],
                        alignment=MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    self.tf_value,
                ],
                scroll=ScrollMode.AUTO,
            ),
            width=400,
        )
        self.dialog.actions = [
            Row(
                controls=[
                    StandardButton(
                        content=Text(
                            value=await self.client.session.gtv(key='confirm'),
                            size=settings.get_font_size(multiple=1.5),
                        ),
                        on_click=self.order_request_update_value,
                        expand=True,
                    ),
                ],
            ),
        ]
        self.dialog.open = True
        await self.dialog.update_async()

    async def order_request_update_value(self, _):
        if not await Error.check_field(self, field=self.tf_value, check_float=True):
            return
        self.dialog.open = False
        await self.dialog.update_async()
        try:
            await self.client.session.api.client.orders.requests.create(
                order_id=self.order_id,
                type_='update_value',
                value=value_to_int(value=self.tf_value.value, decimal=self.currency.decimal),
            )
        except ApiException as exception:
            return await self.client.session.error(exception=exception)

    """
    OUTPUT
    """

    async def payment_confirmation_confirm(self, _):
        try:
            await self.client.session.api.client.orders.updates.completed(id_=self.order_id)
            await self.construct()
            await self.update_async()
        except ApiException as exception:
            return await self.client.session.error(exception=exception)

    async def payment_confirmation_cancel(self, _):
        try:
            await self.client.session.api.client.orders.updates.payment(id_=self.order_id)
            await self.construct()
            await self.update_async()
        except ApiException as exception:
            return await self.client.session.error(exception=exception)
