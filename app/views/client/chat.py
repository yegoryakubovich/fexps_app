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
import datetime
import json
import os
from base64 import b64encode
from io import BytesIO

import aiohttp
from flet_core import Container, Row, Column, UserControl, Control, colors, MainAxisAlignment, padding, \
    Image, ScrollMode, FilePickerUploadFile, FilePickerUploadEvent, Stack, ImageFit, IconButton, icons

from app.controls.button import StandardButton
from app.controls.information import Text, InformationContainer
from app.controls.input import TextField
from app.controls.layout import ClientBaseView
from app.utils import Fonts, get_image_src, Icons
from config import settings
from fexps_api_client import FexpsApiClient


class Chat(UserControl):
    running: bool
    url: str = f'{settings.url}/messages/chat/ws'
    message_column: Column
    control_list: list

    @staticmethod
    async def create_message_card(
            api: FexpsApiClient,
            account_id: int,
            message: dict,
            positions: dict = None,
            deviation: int = 0,
    ) -> Control:
        if not positions:
            positions = {}
        position = message['account_position'].title()
        if int(message['account']) == account_id:
            position = 'You'
        position_str = positions.get(position.lower(), position)
        date = message['date']
        if isinstance(date, str):
            date = datetime.datetime.strptime(date, settings.datetime_format)
            date = date.replace(tzinfo=None) + datetime.timedelta(hours=deviation)
        column_controls = [
            Row(
                controls=[
                    Text(
                        value=position_str,
                        size=14,
                        font_family=Fonts.SEMIBOLD,
                        color=colors.ON_PRIMARY_CONTAINER,
                    ),
                    Text(
                        value=date.strftime(settings.datetime_format),
                        size=14,
                        font_family=Fonts.SEMIBOLD,
                        color=colors.ON_PRIMARY_CONTAINER,
                    ),
                ],
                spacing=16,
                alignment=MainAxisAlignment.SPACE_BETWEEN,
            ),
        ]
        if message['image']:
            column_controls += [
                Row(
                    controls=[
                        Image(
                            src=await get_image_src(
                                api=api,
                                id_str=message['image'],
                            ),
                            height=150,
                        ),
                    ],
                ),
            ]
        if message['text']:
            column_controls += [
                Row(
                    controls=[
                        Text(
                            value=message['text'],
                            size=28,
                            font_family=Fonts.SEMIBOLD,
                            color=colors.ON_PRIMARY_CONTAINER,
                        ),
                    ],
                ),
            ]
        return InformationContainer(
            content=Column(
                controls=column_controls,
                spacing=-50,
            ),
            bgcolor=colors.PRIMARY_CONTAINER,
            padding=padding.symmetric(vertical=16, horizontal=16),
        )

    def __init__(
            self,
            api: FexpsApiClient,
            account_id: int,
            token: str,
            order_id: int,
            controls: list = None,
            positions: dict = None,
            deviation: int = 0,
    ):
        super().__init__()
        self.api = api
        self.token = token
        self.account_id = account_id
        self.order_id = order_id
        self.control_list = controls
        self.deviation = deviation
        if controls is None:
            self.control_list = []
        self.positions = positions
        if not positions:
            self.positions = {}
        self.session = aiohttp.ClientSession()
        self.websocket: aiohttp.client_ws.ClientWebSocketResponse = None

    async def connect(self):
        self.websocket = await self.session.ws_connect(f'{self.url}?token={self.token}&order_id={self.order_id}')

    async def disconnect(self):
        await self.websocket.close()

    async def send(self, data: dict):
        await self.websocket.send_json(data=data)

    async def did_mount_async(self):
        self.running = True
        await self.connect()
        asyncio.create_task(self.update_chat())

    async def will_unmount_async(self):
        self.running = False

    async def update_chat(self):
        async for message in self.websocket:
            if not self.running:
                return
            self.control_list.append(
                await self.create_message_card(
                    api=self.api,
                    account_id=self.account_id,
                    message=json.loads(message.data),
                    positions=self.positions,
                    deviation=self.deviation,
                )
            )
            await self.update_async()

    def build(self):
        self.message_column = Column(
            controls=self.control_list,
            scroll=ScrollMode.AUTO,
            auto_scroll=True,
            expand=True,
            spacing=10,
        )
        return self.message_column


class ChatView(ClientBaseView):
    route = '/client/chat'
    chat: Chat
    order_id: int
    tf_message: TextField
    photo_row: Row

    def __init__(self, order_id: int):
        super().__init__()
        self.order_id = order_id
        self.positions = {}
        self.photo = None
        self.data_io = None

    async def build(self):
        account = self.client.session.account
        self.positions = {
            'you': await self.client.session.gtv(key='chat_you'),
            'unknown': await self.client.session.gtv(key='chat_unknown'),
            'sender': await self.client.session.gtv(key='chat_sender'),
            'receiver': await self.client.session.gtv(key='chat_receiver'),
        }
        await self.set_type(loading=True)
        old_messages = await self.client.session.api.client.messages.get_list(order_id=self.order_id)
        old_messages_controls = [
            await Chat.create_message_card(
                api=self.client.session.api,
                account_id=account.id,
                message=message,
                positions=self.positions,
            )
            for message in old_messages[::-1]
        ]
        await self.set_type(loading=False)
        self.chat = Chat(
            account_id=account.id,
            api=self.client.session.api,
            token=self.client.session.token,
            order_id=self.order_id,
            controls=old_messages_controls,
            positions=self.positions,
            deviation=self.client.session.timezone.deviation,
        )
        self.photo_row = Row()
        self.tf_message = TextField(
            label=await self.client.session.gtv(key='chat_write_message'),
            expand=True,
        )
        title_str = await self.client.session.gtv(key='chat_title')
        self.controls = await self.get_controls(
            title=f'{title_str} order.{self.order_id}',
            with_expand=True,
            go_back_func=self.go_back,
            main_section_controls=[
                Container(
                    content=self.chat,
                    expand=True,
                ),
                Container(
                    content=self.photo_row,
                ),
                Container(
                    content=Row(
                        controls=[
                            StandardButton(
                                content=Image(
                                    src=Icons.CLIP,
                                    width=48,
                                    height=48,
                                    color=colors.ON_BACKGROUND,
                                ),
                                on_click=self.add_photo,
                                color=colors.ON_BACKGROUND,
                                bgcolor=colors.BACKGROUND,
                            ),
                            self.tf_message,
                        ],
                    ),
                ),
                Container(
                    content=Row(
                        controls=[
                            StandardButton(
                                text=await self.client.session.gtv(key='chat_send'),
                                on_click=self.send,
                                expand=True,
                            ),
                        ],
                    ),
                ),
            ],
        )

    async def go_back(self, _):
        await self.chat.disconnect()
        await self.client.change_view(go_back=True, delete_current=True)

    async def send(self, _):
        image_id_str = None
        if self.data_io:
            image_id_str = await self.client.session.api.client.images.create(
                model='order',
                model_id=self.order_id,
                file=self.data_io.read(),
            )
        text = None
        if self.tf_message.value:
            text = self.tf_message.value
        if not image_id_str and not text:
            return

        await self.chat.send(
            data={
                'image_id_str': image_id_str,
                'text': text,
            },
        )
        self.photo = None
        self.data_io = None
        self.photo_row.controls = []
        self.tf_message.value = None
        await self.update_async()

    """PHOTO"""

    async def add_photo(self, _):
        await self.client.session.filepicker.open_(
            on_select=self.upload_files,
            on_upload=self.on_upload_progress,
            allowed_extensions=['svg', 'jpg'],
        )

    async def photo_delete(self, _):
        self.photo = None
        self.data_io = None
        self.photo_row.controls = []
        await self.photo_row.update_async()

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
            Container(
                content=Stack(
                    controls=[
                        Image(
                            src=f"data:image/jpeg;base64,{encoded_image_data}",
                            width=150,
                            height=150,
                            fit=ImageFit.CONTAIN,
                        ),
                        IconButton(
                            icon=icons.CLOSE,
                            on_click=self.photo_delete,
                            top=1,
                            right=0,
                            icon_color=colors.ON_SECONDARY,
                        ),
                    ],
                ),
                bgcolor=colors.SECONDARY,
            ),
        ]
        await self.photo_row.update_async()
