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

from flet_core import Column, Container, Row, Divider, MainAxisAlignment, \
    padding, Image, colors, ScrollMode, AlertDialog

from app.controls.button import StandardButton
from app.controls.information import Text, SubTitle, InformationContainer
from app.controls.input import TextField
from app.controls.layout import ClientBaseView
from app.utils import Fonts, value_to_float, Icons, Error, value_to_int
from app.utils.updater import UpdateChecker
from app.utils.updater.schemes import get_order_scheme
from app.utils.value import value_to_str, requisite_value_to_str
from app.views.main.tabs.acoount import open_support
from fexps_api_client.utils import ApiException


class RequestOrderView(ClientBaseView):
    route = '/client/request/order/get'
    order = dict
    order_request = dict
    request = dict
    method = dict
    currency = dict

    info_card: InformationContainer
    help_column: Column
    input_payment_button: StandardButton
    output_confirmation_button: StandardButton
    chat_button: StandardButton
    update_value_button: StandardButton
    cancel_button: StandardButton
    recreate_button: StandardButton
    order_request_completed_button: StandardButton
    order_request_canceled_button: StandardButton

    dialog: AlertDialog
    # order request update value
    tf_value: TextField

    def __init__(self, order_id: int):
        super().__init__()
        self.reload_bool = False
        self.reload_stop = False
        self.order_id = order_id
        self.dialog = AlertDialog()
        self.tf_value = TextField()

    async def update_info_card(self, update: bool = True) -> None:
        currency_value = value_to_float(
            value=self.order.currency_value,
            decimal=self.currency.decimal,
        )
        currency_value_str = f'{value_to_str(currency_value)} {self.currency.id_str.upper()}'
        field_controls = []
        for scheme_field in self.order.requisite_scheme_fields:
            field_info_str = requisite_value_to_str(value=self.order.requisite_fields.get(scheme_field.get('key')))
            field_controls.append(
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
                                    value=field_info_str,
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
            )
        self.info_card = InformationContainer(
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
                    *field_controls,
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
        if update:
            await self.info_card.update_async()

    async def update_help_column(self, update: bool = True) -> None:
        self.help_column = Column(
            controls=[
                SubTitle(value=await self.client.session.gtv(key='request_order_help_title')),
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
                    on_click=self.chat_open,
                ),
            ],
        )
        if update:
            await self.info_card.update_async()

    """
    INPUT PAYMENT
    """

    async def update_input_payment_button(self, update: bool = True) -> None:
        currency_value = value_to_float(
            value=self.order.currency_value,
            decimal=self.currency.decimal,
        )
        currency_value_str = f'{value_to_str(currency_value)} {self.currency.id_str.upper()}'
        input_payment_confirm = await self.client.session.gtv(key='request_order_input_payment_button')
        self.input_payment_button = StandardButton(
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
        if update:
            await self.input_payment_button.update_async()

    """
    OUTPUT CONFIRMATION
    """

    async def update_output_confirmation_button(self, update: bool = True) -> None:
        currency_value = value_to_float(
            value=self.order.currency_value,
            decimal=self.currency.decimal,
        )
        currency_value_str = f'{value_to_str(currency_value)} {self.currency.id_str.upper()}'
        output_confirmation = await self.client.session.gtv(key='request_order_output_confirmation_button')
        self.output_confirmation_button = StandardButton(
            content=Text(
                value=f'{output_confirmation} {currency_value_str}',
                size=20,
                font_family=Fonts.SEMIBOLD,
                color=colors.ON_PRIMARY,
            ),
            bgcolor=colors.PRIMARY,
            on_click=self.output_confirmation_confirm,
            expand=2,
        )
        if update:
            await self.output_confirmation_button.update_async()

    """
    CHAT
    """

    async def update_chat_button(self, update: bool = True) -> None:
        self.chat_button = StandardButton(
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
        if update:
            await self.chat_button.update_async()

    async def update_order_request_completed_button(self, update: bool = True) -> None:
        controls = [
            Text(
                value=await self.client.session.gtv(key=f'order_request_{self.order_request.type}_completed'),
                size=20,
                font_family=Fonts.SEMIBOLD,
                color=colors.ON_PRIMARY,
            )
        ]
        if self.order_request.type == 'update_value':
            value_str = value_to_float(value=self.order_request.data['value'], decimal=self.currency.decimal)
            value_str = value_to_str(value=value_str)
            controls += [
                Text(
                    value=f'({value_str})',
                    size=20,
                    font_family=Fonts.SEMIBOLD,
                    color=colors.ON_PRIMARY,
                ),
            ]
        self.order_request_completed_button = StandardButton(
            content=Row(
                controls=controls,
                alignment=MainAxisAlignment.CENTER,
            ),
            bgcolor=colors.PRIMARY,
            on_click=partial(self.order_request_update, 'completed'),
            expand=1,
        )
        if update:
            await self.order_request_completed_button.update_async()

    async def update_order_request_canceled_button(self, update: bool = True) -> None:
        controls = [
            Text(
                value=await self.client.session.gtv(key=f'order_request_{self.order_request.type}_canceled'),
                size=20,
                font_family=Fonts.SEMIBOLD,
                color=colors.ON_PRIMARY,
            ),
        ]
        if self.order_request.type == 'update_value':
            value_str = value_to_float(value=self.order_request.data['value'], decimal=self.currency.decimal)
            value_str = value_to_str(value=value_str)
            controls += [
                Text(
                    value=f'({value_str})',
                    size=20,
                    font_family=Fonts.SEMIBOLD,
                    color=colors.ON_PRIMARY,
                ),
            ]
        self.order_request_canceled_button = StandardButton(
            content=Row(
                controls=controls,
                alignment=MainAxisAlignment.CENTER,
            ),
            bgcolor=colors.PRIMARY,
            on_click=partial(self.order_request_update, 'canceled'),
            expand=1,
        )
        if update:
            await self.order_request_canceled_button.update_async()

    """
    UPDATES
    """

    async def update_update_value_button(self, update: bool = True) -> None:
        self.update_value_button = StandardButton(
            content=Row(
                controls=[
                    Text(
                        value=await self.client.session.gtv(key='request_order_update_value_button'),
                        size=20,
                        font_family=Fonts.SEMIBOLD,
                        color=colors.ON_PRIMARY_CONTAINER,
                    ),
                ],
                alignment=MainAxisAlignment.CENTER,
            ),
            bgcolor=colors.PRIMARY_CONTAINER,
            on_click=self.order_request_update_value_open,
            expand=1,
        )
        if update:
            await self.update_value_button.update_async()

    async def update_cancel_button(self, update: bool = True) -> None:
        self.cancel_button = StandardButton(
            content=Row(
                controls=[
                    Text(
                        value=await self.client.session.gtv(key='request_order_cancel_button'),
                        size=20,
                        font_family=Fonts.SEMIBOLD,
                        color=colors.ON_PRIMARY_CONTAINER,
                    ),
                ],
                alignment=MainAxisAlignment.CENTER,
            ),
            bgcolor=colors.PRIMARY_CONTAINER,
            on_click=self.order_request_cancel,
            expand=1,
        )
        if update:
            await self.chat_button.update_async()

    async def update_recreate_button(self, update: bool = True) -> None:
        self.recreate_button = StandardButton(
            content=Row(
                controls=[
                    Text(
                        value=await self.client.session.gtv(key='request_order_recreate_button'),
                        size=20,
                        font_family=Fonts.SEMIBOLD,
                        color=colors.ON_PRIMARY_CONTAINER,
                    ),
                ],
                alignment=MainAxisAlignment.CENTER,
            ),
            bgcolor=colors.PRIMARY_CONTAINER,
            on_click=self.order_request_recreate,
            expand=1,
        )
        if update:
            await self.recreate_button.update_async()

    async def construct(self):
        self.dialog = AlertDialog()
        controls, buttons = [], []
        asyncio.create_task(self.auto_reloader())
        await self.set_type(loading=True)
        self.order = await self.client.session.api.client.orders.get(id_=self.order_id)
        self.order_request = self.order.order_request
        self.currency = self.order.currency
        self.request = self.order.request
        self.method = self.order.method
        await self.set_type(loading=False)
        await self.update_info_card(update=False)
        await self.update_help_column(update=False)
        controls += [
            self.info_card,
            self.help_column,
        ]
        if self.order_request:
            if self.client.session.current_wallet.id != self.order_request.wallet.id:
                await self.update_order_request_completed_button(update=False)
                await self.update_order_request_canceled_button(update=False)
                buttons += [
                    Row(
                        controls=[
                            self.order_request_completed_button,
                            self.order_request_canceled_button,
                        ]
                    ),
                ]
            await self.update_chat_button(update=False)
            buttons += [
                Row(
                    controls=[
                        self.chat_button,
                    ]
                ),
            ]
        elif self.order.type == 'input':
            if self.order.state == 'waiting':
                pass
            elif self.order.state == 'payment':
                await self.update_update_value_button(update=False)
                await self.update_cancel_button(update=False)
                await self.update_recreate_button(update=False)
                await self.update_input_payment_button(update=False)
                await self.update_chat_button(update=False)
                buttons += [
                    Row(
                        controls=[
                            self.update_value_button,
                            self.cancel_button,
                            self.recreate_button,
                        ]
                    ),
                    Row(
                        controls=[
                            self.input_payment_button,
                            self.chat_button,
                        ]
                    ),
                ]
            elif self.order.state == 'confirmation':
                await self.update_chat_button(update=False)
                buttons += [
                    Row(
                        controls=[
                            self.chat_button,
                        ]
                    ),
                ]
            else:  # completed, canceled
                pass
        elif self.order.type == 'output':
            if self.order.state == 'waiting':
                pass
            elif self.order.state == 'payment':
                await self.update_update_value_button(update=False)
                await self.update_cancel_button(update=False)
                await self.update_recreate_button(update=False)
                await self.update_chat_button(update=False)
                buttons += [
                    Row(
                        controls=[
                            self.update_value_button,
                            self.cancel_button,
                            self.recreate_button,
                        ]
                    ),
                    Row(
                        controls=[
                            self.chat_button,
                        ]
                    ),
                ]
            elif self.order.state == 'confirmation':
                await self.update_output_confirmation_button(update=False),
                await self.update_chat_button(update=False),
                buttons += [
                    Row(
                        controls=[
                            self.output_confirmation_button,
                            self.chat_button,
                        ]
                    ),
                ]
            else:  # completed, canceled
                pass
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

    async def copy_to_clipboard(self, data, _):
        await self.client.page.set_clipboard_async(str(data))

    async def chat_open(self, _):
        from app.views.client.chat import ChatView
        await self.client.change_view(view=ChatView(order_id=self.order_id))

    async def order_payment(self, _):
        from .payment import RequestOrderPaymentView
        await self.client.change_view(view=RequestOrderPaymentView(order_id=self.order_id))

    async def on_dev(self, _):
        await self.client.session.bs_info.open_(
            icon=Icons.CHILL,
            title=await self.client.session.gtv(key='in_dev_title'),
            description=await self.client.session.gtv(key='in_dev_description'),
        )

    async def order_request_update(self, state: str, _):
        try:
            await self.client.session.api.client.orders.requests.update(id_=self.order_id, state=state)
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

    async def order_request_update_value_open(self, _):
        self.tf_value = TextField(
            label=await self.client.session.gtv(key='order_request_update_value_value'),
        )
        self.dialog.content = Container(
            content=Column(
                controls=[
                    self.tf_value,
                ],
            ),
            height=100,
        )
        self.dialog.actions = [
            Row(
                controls=[
                    StandardButton(
                        text=await self.client.session.gtv(key='confirm'),
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

    async def output_confirmation_confirm(self, _):
        try:
            await self.client.session.api.client.orders.updates.completed(id_=self.order_id)
            await self.client.change_view(go_back=True, delete_current=True, with_restart=True)
        except ApiException as exception:
            return await self.client.session.error(exception=exception)

    async def auto_reloader(self):
        if self.reload_bool:
            return
        self.reload_bool = True
        await asyncio.sleep(10)
        while self.reload_bool:
            if self.client.page.route != self.route:
                self.reload_bool = False
                return
            if self.reload_stop:
                await asyncio.sleep(5)
                continue
            order = await self.client.session.api.client.orders.get(id_=self.order_id)
            order_check = UpdateChecker().check(
                scheme=get_order_scheme,
                obj_1=self.order,
                obj_2=order,
            )
            if order_check:
                await self.construct()
                await self.update_async()
            await asyncio.sleep(5)
