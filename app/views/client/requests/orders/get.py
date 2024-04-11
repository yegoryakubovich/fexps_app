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
import os
from base64 import b64encode
from functools import partial
from io import BytesIO

from flet_core import SnackBar, Control, Column, Container, Row, Divider, MainAxisAlignment, \
    padding, Image, colors, alignment, AlertDialog, TextField, KeyboardType, ControlEvent, FilePickerUploadFile, \
    FilePickerUploadEvent, FilledButton

from app.controls.button import StandardButton
from app.controls.information import Text, SubTitle, InformationContainer
from app.controls.layout import ClientBaseView
from app.utils import Fonts, value_to_float, Icons
from app.utils.value import value_to_str
from fexps_api_client.utils import ApiException


class RequestOrderView(ClientBaseView):
    route = '/client/request/order/get'
    order = dict
    request = dict
    method = dict
    currency = dict
    snack_bar: SnackBar
    custom_info: list
    custom_controls: list[Control]
    dialog: AlertDialog
    input_scheme_fields: list
    input_fields: dict

    file_name: str = None

    def __init__(self, order_id: int):
        super().__init__()
        self.order_id = order_id
        self.photos = []
        self.data_io = None

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

    """ INPUT PAYMENT"""

    async def create_input_payment_dialog(self):
        self.input_scheme_fields = []
        for input_scheme_field in self.order.input_scheme_fields:
            type_ = input_scheme_field["type"]
            type_str = await self.client.session.gtv(key=type_)
            name_list = [await self.client.session.gtv(key=input_scheme_field['name_text_key']), f'({type_str})']
            if not input_scheme_field['optional']:
                name_list.append('*')
            if type_ == 'image':
                self.input_scheme_fields.append(
                    FilledButton(
                        content=Text(
                            value=await self.client.session.gtv(key='add_image'),
                        ),
                        on_click=self.add_photo,
                        disabled=len(self.photos) > 1,
                    )
                )
            else:
                self.input_scheme_fields.append(
                    TextField(
                        label=' '.join(name_list),
                        on_change=partial(self.change_input_fields, input_scheme_field['key']),
                        keyboard_type=KeyboardType.NUMBER if type_ == 'int' else None,
                    )
                )
        self.dialog = AlertDialog(
            content=Container(
                content=Column(
                    controls=self.input_scheme_fields,
                ),
                height=220,
            ),
            actions=[
                Row(
                    controls=[
                        StandardButton(
                            content=Text(
                                value=await self.client.session.gtv(key="confirm"),
                                size=16,
                            ),
                            on_click=self.input_field_dialog_confirm,
                            expand=True
                        ),
                    ],
                ),
            ],
            modal=False,
        )

    async def get_input_payment_button(self) -> StandardButton:
        currency_value = value_to_float(
            value=self.order.currency_value,
            decimal=self.currency.decimal,
        )
        currency_value_str = f'{value_to_str(currency_value)} {self.currency.id_str.upper()}'
        input_payment_confirm = await self.client.session.gtv(key='request_order_input_payment_button')
        return StandardButton(
            content=Text(
                value=f'{input_payment_confirm} {currency_value_str}',
                size=20,
                font_family=Fonts.SEMIBOLD,
                color=colors.ON_PRIMARY,
            ),
            bgcolor=colors.PRIMARY,
            on_click=self.input_field_dialog_open,
            expand=2,
        )

    async def get_output_confirmation_button(self) -> StandardButton:
        currency_value = value_to_float(
            value=self.order.currency_value,
            decimal=self.currency.decimal,
        )
        currency_value_str = f'{value_to_str(currency_value)} {self.currency.id_str.upper()}'
        output_confirmation = await self.client.session.gtv(key='request_order_output_confirmation_button')
        return StandardButton(
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
                        value=await self.client.session.gtv(key='request_order_value_edit_button'),
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
                        value=await self.client.session.gtv(key='request_order_cancel_button'),
                        size=20,
                        font_family=Fonts.SEMIBOLD,
                        color=colors.ON_PRIMARY_CONTAINER,
                    ),
                ],
                alignment=MainAxisAlignment.CENTER,
            ),
            bgcolor=colors.PRIMARY_CONTAINER,
            on_click=self.request_order_cancel,
            expand=1,
        )

    async def build(self):
        self.input_fields = {}
        self.dialog = AlertDialog()
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
                await self.create_input_payment_dialog()
                buttons += [
                    await self.get_cancel_button(),
                    await self.get_value_edit_button(),
                    await self.get_input_payment_button(),
                    await self.get_chat_button(),
                ]
            elif self.order.state == 'confirmation':
                buttons += [
                    await self.get_chat_button(),
                ]
            else:  # completed, canceled
                pass
        elif self.order.type == 'output':
            if self.order.state == 'waiting':
                pass
            elif self.order.state == 'payment':
                buttons += [
                    await self.get_chat_button(),
                ]
            elif self.order.state == 'confirmation':
                buttons += [
                    await self.get_output_confirmation_button(),
                    await self.get_chat_button(),
                ]
            else:  # completed, canceled
                pass
        if buttons:
            controls += [
                self.dialog,
                Container(
                    content=Row(
                        controls=buttons,
                    ),
                    expand=True,
                    alignment=alignment.bottom_center,
                )
            ]
        self.controls = await self.get_controls(
            title=await self.client.session.gtv(key='request_order_title'),
            with_expand=True,
            main_section_controls=controls,
        )

    async def payment_confirm(self, _):
        pass

    async def copy_to_clipboard(self, data, _):
        await self.client.page.set_clipboard_async(str(data))

    async def chat_open(self, _):
        from app.views.client.chat import ChatView
        await self.client.change_view(view=ChatView(order_id=self.order_id))

    """
    INPUT
    """

    async def input_field_dialog_open(self, _):
        self.dialog.open = True
        await self.dialog.update_async()

    async def upload_file(self, _):
        logging.critical(_)
        logging.critical(type(_))

    async def change_input_fields(self, key: str, event: ControlEvent):
        self.input_fields[key] = event.data

    async def input_field_dialog_confirm(self, _):
        self.dialog.open = False
        await self.update_async()
        await asyncio.sleep(0.1)
        await self.set_type(loading=True)
        for input_scheme_field in self.order.input_scheme_fields:
            if not self.input_fields.get(input_scheme_field['key']):
                continue
            if input_scheme_field['type'] == 'int':
                self.input_fields[input_scheme_field['key']] = int(self.input_fields[input_scheme_field['key']])
        try:
            await self.client.session.api.client.orders.updates.confirmation(
                id_=self.order_id,
                input_fields=self.input_fields,
            )
            await self.set_type(loading=False)
            await self.client.change_view(go_back=True, delete_current=True, with_restart=True)
        except ApiException as exception:
            await self.set_type(loading=False)
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

    async def request_order_cancel(self, _):
        try:
            await self.client.session.api.client.orders.requests.create(order_id=self.order_id, type_='cancel')
            await asyncio.sleep(0.05)
            await self.client.change_view(go_back=True, with_restart=True, delete_current=True)
        except ApiException as exception:
            return await self.client.session.error(exception=exception)

    async def on_dev(self, _):
        await self.client.session.bs_info.open_(
            icon=Icons.CHILL,
            title=await self.client.session.gtv(key='in_dev_title'),
            description=await self.client.session.gtv(key='in_dev_description'),
        )

    """FILES"""

    async def on_upload_progress(self, e: FilePickerUploadEvent):
        if e.progress is not None and e.progress < 1.0:
            pass
        else:
            path = f'upload/{e.file_name}'
            if os.path.exists(path):
                with open(path, 'rb') as f:
                    image_data = f.read()
                self.data_io = BytesIO(image_data)
                encoded_image_data = b64encode(image_data).decode()
                self.file_name = e.file_name
                self.photos.append(encoded_image_data)
                await self.restart()
            else:
                pass

    async def upload_files(self, _):
        uf = []
        if self.client.session.filepicker.result.files:
            for f in self.client.session.filepicker.result.files:
                uf.append(
                    FilePickerUploadFile(
                        f.name,
                        upload_url=await self.client.session.page.get_upload_url_async(f.name, 600),
                    )
                )
                await self.client.session.filepicker.upload_async([uf[-1]])
                await self.on_upload_progress(e=FilePickerUploadEvent(file_name=f.name, progress=1.0, error=None))

    async def add_photo(self, _):
        await self.client.session.filepicker.open_(
            on_select=self.upload_files,
            on_upload=self.on_upload_progress,
            allowed_extensions=['svg', 'jpg'],
        )
