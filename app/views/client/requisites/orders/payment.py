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


import webbrowser
from base64 import b64encode
from functools import partial

from flet_core import Control, Row, TextField, ControlEvent, Image, ScrollMode, Container, Column, ImageFit, colors, \
    alignment, Stack

from app.controls.button import StandardButton
from app.controls.information import Text
from app.controls.layout import ClientBaseView
from app.utils import Icons, Error
from config import settings
from fexps_api_client.utils import ApiException


class RequisiteOrderPaymentView(ClientBaseView):
    route = '/client/requisite/order/payment'
    order = dict
    file_keys = dict
    file_row: Row
    attach_file_btn: StandardButton

    input_scheme_fields: list
    input_fields: dict
    fields: dict

    def __init__(self, order_id: int):
        super().__init__()
        self.order_id = order_id

    async def get_field_controls(self) -> list[Control]:
        result = []
        self.fields = {}
        for input_scheme_field in self.order.input_scheme_fields:
            type_ = input_scheme_field["type"]
            type_str = await self.client.session.gtv(key=type_)
            name_list = [await self.client.session.gtv(key=input_scheme_field['name_text_key'])]
            if settings.debug:
                name_list += [f'({type_str})']
            if not input_scheme_field['optional']:
                name_list += ['*']
            if type_ == 'image':
                self.file_row = Row()
                self.attach_file_btn = StandardButton(
                    text=await self.client.session.gtv(key='add_image'),
                    on_click=self.add_file,
                )
                result += [
                    Text(value=' '.join(name_list)),
                    Row(
                        controls=[
                            self.attach_file_btn,
                            StandardButton(
                                content=Image(
                                    src=Icons.RELOAD,
                                    width=32,
                                    height=32,
                                    color=colors.ON_BACKGROUND,
                                ),
                                on_click=self.reload_file,
                                color=colors.ON_BACKGROUND,
                                bgcolor=colors.BACKGROUND,
                            ),
                        ],
                    ),
                    self.file_row,
                ]
            else:
                self.fields[input_scheme_field['key']] = TextField(
                    label=' '.join(name_list),
                    on_change=partial(
                        self.change_input_fields,
                        input_scheme_field['key'],
                    ),
                )
                result.append(self.fields[input_scheme_field['key']])
        return result

    async def construct(self):
        self.input_fields = {}
        await self.set_type(loading=True)
        self.order = await self.client.session.api.client.orders.get(id_=self.order_id)
        await self.set_type(loading=False)
        self.controls = await self.get_controls(
            title=await self.client.session.gtv(key='request_order_title'),
            with_expand=True,
            main_section_controls=[
                Container(
                    content=Column(
                        controls=await self.get_field_controls(),
                        scroll=ScrollMode.AUTO,
                    ),
                    expand=True,
                ),
                Container(
                    content=Row(
                        controls=[
                            StandardButton(
                                content=Text(
                                    value=await self.client.session.gtv(key="confirm"),
                                    size=16,
                                ),
                                on_click=self.order_confirm,
                                expand=True
                            ),
                        ],
                    ),
                ),
            ],
        )

    """FILE FIELD"""

    async def add_file(self, _):
        self.file_keys = await self.client.session.api.client.files.keys.create()
        self.attach_file_btn.text = await self.client.session.gtv(key='order_open_file_upload')
        self.attach_file_btn.on_click = None
        self.attach_file_btn.url = self.file_keys.url
        await self.attach_file_btn.update_async()
        self.client.session.page.launch_url(self.file_keys.url)
        # webbrowser.open(url=self.file_keys.url)

    async def reload_file(self, _):
        if not self.file_keys:
            return
        self.attach_file_btn.text = await self.client.session.gtv(key='add_image')
        self.attach_file_btn.on_click = self.add_file
        self.attach_file_btn.url = None
        await self.attach_file_btn.update_async()
        files = await self.client.session.api.client.files.keys.get(key=self.file_keys.key)
        await self.update_file_row(files=files)

    async def update_file_row(self, files):
        self.file_row.controls = []
        for file in files:
            file_image = Container(
                content=Image(
                    src=Icons.FILE,
                    width=100,
                    height=100,
                    fit=ImageFit.CONTAIN,
                    color=colors.WHITE,
                ),
                alignment=alignment.center,
            )
            if file.extension in ['jpg', 'jpeg', 'png']:
                file_byte = file.value.encode('ISO-8859-1')
                file_image = Container(
                    content=Image(
                        src=f'data:image/jpeg;base64,{b64encode(file_byte).decode()}',
                        width=150,
                        height=150,
                        fit=ImageFit.CONTAIN,
                    ),
                    alignment=alignment.center,
                )
            self.file_row.controls += [
                Container(
                    content=Stack(
                        controls=[
                            file_image,
                            Container(
                                content=Text(
                                    value=file.filename,
                                    color=colors.ON_SECONDARY
                                ),
                                alignment=alignment.bottom_center,
                            ),
                        ],
                    ),
                    bgcolor=colors.SECONDARY,
                    height=170,
                    width=150,
                )
            ]
        await self.file_row.update_async()

    """TEXT FIELD"""

    async def change_input_fields(self, key: str, event: ControlEvent):
        self.input_fields[key] = event.data

    async def order_confirm(self, _):
        await self.set_type(loading=True)
        try:
            for input_scheme_field in self.order.input_scheme_fields:
                if not self.input_fields.get(input_scheme_field['key']):
                    if input_scheme_field['type'] == 'image' and self.file_keys:
                        self.input_fields[input_scheme_field['key']] = self.file_keys.key
                    continue
                if input_scheme_field['type'] == 'int':
                    if not await Error.check_field(self, self.fields[input_scheme_field['key']], check_int=True):
                        await self.set_type(loading=False)
                        return
                    self.input_fields[input_scheme_field['key']] = int(self.input_fields[input_scheme_field['key']])
            await self.client.session.api.client.orders.updates.confirmation(
                id_=self.order_id,
                input_fields=self.input_fields,
            )
            await self.set_type(loading=False)
            await self.client.change_view(go_back=True, delete_current=True, with_restart=True)
        except ApiException as exception:
            await self.set_type(loading=False)
            return await self.client.session.error(exception=exception)
