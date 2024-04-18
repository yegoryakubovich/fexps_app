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


import os
from base64 import b64encode
from functools import partial
from io import BytesIO

from flet_core import Control, Row, TextField, ControlEvent, FilePickerUploadFile, \
    FilePickerUploadEvent, Image, ScrollMode, Container, Column

from app.controls.button import StandardButton
from app.controls.information import Text
from app.controls.layout import ClientBaseView
from app.utils import Icons
from fexps_api_client.utils import ApiException


class RequisiteOrderPaymentView(ClientBaseView):
    route = '/client/requisite/order/payment'
    order = dict
    photo_row: Row
    input_scheme_fields: list
    input_fields: dict

    def __init__(self, order_id: int):
        super().__init__()
        self.order_id = order_id
        self.photo = None
        self.data_io = None

    async def get_field_controls(self) -> list[Control]:
        result = []
        for input_scheme_field in self.order.input_scheme_fields:
            type_ = input_scheme_field["type"]
            type_str = await self.client.session.gtv(key=type_)
            name_list = [await self.client.session.gtv(key=input_scheme_field['name_text_key']), f'({type_str})']
            if not input_scheme_field['optional']:
                name_list.append('*')
            if type_ == 'image':
                self.photo_row = Row()
                result += [
                    Text(value=' '.join(name_list)),
                    Row(
                        controls=[
                            StandardButton(
                                icon=Icons.PAYMENT,
                                text=await self.client.session.gtv(key='add_image'),
                                on_click=self.add_photo,
                                disabled=self.photo is not None,
                            ),
                        ],
                    ),
                    self.photo_row,
                ]
            else:
                result += [
                    TextField(
                        label=' '.join(name_list),
                        on_change=partial(self.change_input_fields, input_scheme_field['key']),
                    )
                ]

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

    async def order_confirm(self, _):
        await self.set_type(loading=True)
        try:
            for input_scheme_field in self.order.input_scheme_fields:
                if not self.input_fields.get(input_scheme_field['key']):
                    if input_scheme_field['type'] == 'image' and self.data_io:
                        id_str = await self.client.session.api.client.images.create(
                            model='order',
                            model_id=self.order_id,
                            file=self.data_io.read(),
                        )
                        self.input_fields[input_scheme_field['key']] = id_str
                    continue
                if input_scheme_field['type'] == 'int':
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

    """PHOTO FIELD"""

    async def add_photo(self, _):
        await self.client.session.filepicker.open_(
            on_select=self.upload_files,
            on_upload=self.on_upload_progress,
            allowed_extensions=['svg', 'jpg'],
        )

    async def upload_files(self, _):
        uf = []
        if not self.client.session.filepicker.result.files:
            return
        for f in self.client.session.filepicker.result.files:
            uf.append(
                FilePickerUploadFile(
                    f.name,
                    upload_url=await self.client.session.page.get_upload_url_async(f.name, 600),
                )
            )
            await self.client.session.filepicker.upload_async([uf[-1]])
            await self.on_upload_progress(e=FilePickerUploadEvent(file_name=f.name, progress=1.0, error=None))

    async def on_upload_progress(self, e: FilePickerUploadEvent):
        if e.progress is not None and e.progress < 1.0:
            return
        path = f'uploads/{e.file_name}'
        if not os.path.exists(path):
            return
        with open(path, 'rb') as f:
            image_data = f.read()
        self.data_io = BytesIO(image_data)
        encoded_image_data = b64encode(image_data).decode()
        self.photo_row.controls = [
            Image(src=f"data:image/jpeg;base64,{encoded_image_data}", width=150, height=150),
        ]
        await self.photo_row.update_async()

    """TEXT FIELD"""

    async def change_input_fields(self, key: str, event: ControlEvent):
        self.input_fields[key] = event.data
