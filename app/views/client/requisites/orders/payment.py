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


import io
import os
from base64 import b64encode
from functools import partial

from flet_core import Control, Row, TextField, ControlEvent, FilePickerUploadFile, \
    FilePickerUploadEvent, Image, ScrollMode, Container, Column, ImageFit, colors, alignment, Stack, IconButton, icons, \
    ProgressRing

from app.controls.button import StandardButton
from app.controls.information import Text
from app.controls.input import FilePicker
from app.controls.layout import ClientBaseView
from app.utils import Icons, Error
from app.utils.crypto import create_id_str
from config import settings
from fexps_api_client.utils import ApiException


class RequisiteOrderPaymentView(ClientBaseView):
    route = '/client/requisite/order/payment'
    order = dict
    photo_row: Row
    filepicker: FilePicker

    text_error: Text
    input_scheme_fields: list
    input_fields: dict
    fields: dict

    def __init__(self, order_id: int):
        super().__init__()
        self.order_id = order_id
        self.photos = {}
        self.filepicker = FilePicker()

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
                self.photo_row = Row()
                self.text_error = Text()
                result += [
                    Text(value=' '.join(name_list)),
                    Column(
                        controls=[
                            Row(
                                controls=[
                                    StandardButton(
                                        icon=Icons.PAYMENT,
                                        text=await self.client.session.gtv(key='add_image'),
                                        on_click=self.add_photo,
                                    ),
                                ],
                                height=110,
                            ),
                        ],
                        scroll=ScrollMode.AUTO,
                        height=100,
                    ),
                    self.photo_row,
                    self.text_error,
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
        self.client.page.overlay.append(self.filepicker)
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
                    if input_scheme_field['type'] == 'image':
                        self.input_fields[input_scheme_field['key']] = [
                            {
                                'filename': value['filename'],
                                'data': io.BytesIO(value['data']).getvalue().decode('ISO-8859-1'),
                            }
                            for id_str, value in self.photos.items()
                        ]
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

    """PHOTO FIELD"""

    async def set_text_error(self, text_value: str = None):
        self.text_error.value = text_value
        await self.text_error.update_async()

    async def add_photo(self, _):
        await self.set_text_error()
        await self.filepicker.open_(
            on_select=self.upload_files,
            on_upload=self.on_upload_progress,
            allow_multiple=True,
        )

    async def update_photo_row(self):
        self.photo_row.controls = []
        for id_str, value in self.photos.items():
            stack_controls = []
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
            if value['extension'] in ['jpg', 'jpeg', 'png']:
                file_image = Container(
                    content=Image(
                        src=f"data:image/jpeg;base64,{b64encode(value['data']).decode()}",
                        width=150,
                        height=150,
                        fit=ImageFit.CONTAIN,
                    ),
                    alignment=alignment.center,
                )
            stack_controls += [
                file_image,
            ]
            if id_str == 'temp':
                stack_controls += [
                    Container(
                        content=ProgressRing(
                            value=value['progress'],
                            color=colors.PRIMARY_CONTAINER,
                            bgcolor=colors.SECONDARY_CONTAINER,
                            width=64,
                            height=64,
                        ),
                        alignment=alignment.center,
                    ),
                ]
            else:
                stack_controls += [
                    Container(
                        content=Text(
                            value=value['filename'],
                            color=colors.ON_SECONDARY
                        ),
                        alignment=alignment.bottom_center,
                    ),
                    IconButton(
                        icon=icons.CLOSE,
                        on_click=partial(
                            self.photo_delete,
                            id_str,
                        ),
                        top=1,
                        right=0,
                        icon_color=colors.ON_SECONDARY,
                    ),
                ]
            self.photo_row.controls += [
                Container(
                    content=Stack(
                        controls=stack_controls,
                    ),
                    bgcolor=colors.SECONDARY,
                    height=170,
                    width=150,
                )
            ]
        await self.photo_row.update_async()

    async def upload_files(self, _):
        uf = []
        await self.set_text_error()
        if not self.filepicker.result.files:
            return
        for f in self.filepicker.result.files:
            if len(f.name.split('.')) < 2:
                continue
            if f.size > 2097152:
                await self.set_text_error(text_value=await self.client.session.gtv(key='file_max_size_2mb'))
                continue
            if len(self.photos) > 3:
                await self.set_text_error(text_value=await self.client.session.gtv(key='files_max_count'))
                continue
            uf.append(
                FilePickerUploadFile(
                    f.name,
                    upload_url=await self.client.session.page.get_upload_url_async(f.name, 600),
                )
            )
            await self.filepicker.upload_async([uf[-1]])
            await self.on_upload_progress(e=FilePickerUploadEvent(file_name=f.name, progress=1.0, error=None))

    async def on_upload_progress(self, e: FilePickerUploadEvent):
        await self.set_text_error()
        if e.progress is not None and e.progress < 1.0:
            self.photos['temp'] = {
                'filename': '',
                'extension': '',
                'data': None,
                'size': 0,
                'progress': e.progress,
            }
            await self.update_photo_row()
            return
        if self.photos.get('temp'):
            del self.photos['temp']
        path = f'uploads/{e.file_name}'
        if not os.path.exists(path):
            return
        with open(path, 'rb') as f:
            file_data = f.read()
        self.photos[create_id_str()] = {
            'filename': e.file_name,
            'extension': e.file_name.split('.')[-1],
            'data': file_data,
            'size': len(file_data),
            'progress': e.progress,
        }
        os.remove(path)
        await self.update_photo_row()

    async def photo_delete(self, id_str, _):
        await self.set_text_error()
        del self.photos[id_str]
        await self.update_photo_row()

    """TEXT FIELD"""

    async def change_input_fields(self, key: str, event: ControlEvent):
        self.input_fields[key] = event.data
