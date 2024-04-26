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
import logging
import os
from base64 import b64encode
from functools import partial

from flet_core import Container, Row, colors, Image, FilePickerUploadEvent, Stack, ImageFit, \
    IconButton, icons, alignment, FilePickerUploadFile

from app.controls.button import StandardButton
from app.controls.information import Text
from app.controls.input import TextField
from app.controls.layout import ClientBaseView
from app.utils import Icons
from app.utils.chat import Chat
from app.utils.crypto import create_id_str


class ChatView(ClientBaseView):
    route = '/client/chat'

    chat: Chat
    order_id: int
    photos: dict
    photo_dict: dict

    tf_message: TextField
    photo_row: Row
    text_error: Text
    sb_files: StandardButton

    def __init__(self, order_id: int):
        super().__init__()
        self.order_id = order_id
        self.positions = {}
        self.photo_dict = {}
        self.photos = {}
        self.photo_size = 0
        self.photo_row = Row(controls=[])
        self.text_error = Text(value=None)

    async def construct(self):
        account = self.client.session.account
        self.positions = {
            'you': await self.client.session.gtv(key='chat_you'),
            'unknown': await self.client.session.gtv(key='chat_unknown'),
            'sender': await self.client.session.gtv(key='chat_sender'),
            'receiver': await self.client.session.gtv(key='chat_receiver'),
        }
        # await self.set_type(loading=True)
        old_messages = await self.client.session.api.client.messages.get_list(order_id=self.order_id)
        old_messages_controls = [
            await Chat.create_message_card(
                account_id=account.id,
                message=message,
                positions=self.positions,
            )
            for message in old_messages[::-1]
        ]
        # await self.set_type(loading=False)
        self.chat = Chat(
            account_id=account.id,
            api=self.client.session.api,
            token=self.client.session.token,
            order_id=self.order_id,
            controls=old_messages_controls,
            positions=self.positions,
            deviation=self.client.session.timezone.deviation,
        )
        self.sb_files = StandardButton(
            content=Image(
                src=Icons.CLIP,
                width=48,
                height=48,
                color=colors.ON_BACKGROUND,
            ),
            on_click=self.add_photo,
            color=colors.ON_BACKGROUND,
            bgcolor=colors.BACKGROUND,
        )
        self.tf_message = TextField(
            label=await self.client.session.gtv(key='chat_write_message'),
            on_submit=self.send,
            expand=True,
        )
        title_str = await self.client.session.gtv(key='chat_title')
        self.controls = await self.get_controls(
            title=f'{title_str} order.{self.order_id}',
            with_expand=True,
            main_section_controls=[
                Container(
                    content=self.chat,
                    expand=True,
                ),
                Container(
                    content=self.photo_row,
                ),
                Container(
                    content=self.text_error,
                ),
                Container(
                    content=Row(
                        controls=[
                            self.sb_files,
                            self.tf_message,
                            StandardButton(
                                content=Image(
                                    src=Icons.PAYMENT,
                                    color=colors.ON_BACKGROUND,
                                    height=32,
                                    width=32,
                                ),
                                horizontal=0,
                                vertical=0,
                                on_click=self.send,
                                bgcolor=colors.BACKGROUND,
                            ),
                        ],
                    ),
                ),
            ],
        )


    async def send(self, _):
        text = None
        if self.tf_message.value:
            text = self.tf_message.value
        if not self.photos and not text:
            return
        await self.chat.send(
            data={
                'text': text,
                'files': [
                    {
                        'filename': value['filename'],
                        'data': io.BytesIO(value['data']).getvalue().decode('ISO-8859-1'),
                    }
                    for id_str, value in self.photos.items()
                ],
            },
        )
        self.photos = {}
        self.tf_message.value = None
        await self.set_text_error()
        await self.update_photo_row()

    """PHOTO"""

    async def set_text_error(self, text_value: str = None):
        logging.critical(id(self.text_error))
        self.text_error.value = text_value
        # await self.text_error.update_async()
        await self.client.session.page.update_async()

    async def add_photo(self, _):
        await self.set_text_error()
        await self.client.session.filepicker.open_(
            on_select=self.upload_files,
            on_upload=self.on_upload_progress,
        )

    async def update_photo_row(self):
        self.photo_row.controls = []
        for id_str, value in self.photos.items():
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
            self.photo_row.controls += [
                Container(
                    content=Stack(
                        controls=[
                            file_image,
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
                        ],
                    ),
                    bgcolor=colors.SECONDARY,
                    height=170,
                    width=150,
                )
            ]
        await self.photo_row.update_async()

    async def upload_files(self, _):
        uf = []
        # logging.critical(self.page)
        # logging.critical(self.client.session.page.update_async())
        # logging.critical(id(self.text_error))
        self.text_error.value = None
        await self.text_error.update_async()
        if not self.client.session.filepicker.result.files:
            return
        for f in self.client.session.filepicker.result.files:
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
            await self.client.session.filepicker.upload_async([uf[-1]])
            await self.on_upload_progress(e=FilePickerUploadEvent(file_name=f.name, progress=1.0, error=None))

    async def on_upload_progress(self, e: FilePickerUploadEvent):
        logging.critical(id(self.text_error))
        self.text_error.value = None
        await self.text_error.update_async()
        # await self.set_text_error()
        if e.progress is not None and e.progress < 1.0:
            return
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
        }
        os.remove(path)
        await self.update_photo_row()

    async def photo_delete(self, id_str, _):
        await self.set_text_error()
        del self.photos[id_str]
        await self.update_photo_row()
