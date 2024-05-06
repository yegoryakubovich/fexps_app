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
from base64 import b64encode

import aiohttp
from flet_core import Column, UserControl, Control, colors, ScrollMode, Container, Row, padding, \
    Image, alignment

from app.controls.button import StandardButton
from app.controls.information import Text, InformationContainer
from app.utils import Fonts, Icons
from app.utils.value import size_value_to_str
from config import settings


class Chat(UserControl):
    running: bool
    url: str = settings.get_chat_url()
    message_column: Column
    control_list: list

    @staticmethod
    async def create_message_card(
            gtv: callable,
            account_id: int,
            message: dict,
            deviation: int = 0,
    ) -> Control:
        column_controls = []
        position = message['position'].lower()
        custom_alignment = alignment.center_right
        bgcolor = colors.PRIMARY_CONTAINER
        color = colors.ON_PRIMARY_CONTAINER
        text_str = message['text']
        if message['role'] == 'user':
            position = message['position'].lower()
            if int(message['account']) == account_id:
                position = 'you'
                custom_alignment = alignment.center_left
        elif message['role'] == 'moderator':
            position = 'moderator'
        elif message['role'] == 'system':
            custom_alignment = alignment.center
            bgcolor = colors.BACKGROUND
            color = colors.ON_BACKGROUND
        position_str = await gtv(key=f'chat_position_{position.lower()}')
        date = message['date']
        if isinstance(date, str):
            date = datetime.datetime.strptime(date, settings.datetime_format)
            date = date.replace(tzinfo=None) + datetime.timedelta(hours=deviation)
        # header
        if message['role'] == 'system':
            pass
        else:
            column_controls += [
                Row(
                    controls=[
                        Text(
                            value=position_str,
                            size=14,
                            font_family=Fonts.SEMIBOLD,
                            color=color,
                        ),
                        Text(
                            value=date.strftime(settings.datetime_format),
                            size=14,
                            font_family=Fonts.SEMIBOLD,
                            color=color,
                        ),
                    ],
                    spacing=16,
                    tight=True,
                ),
            ]
        # files
        if message['files']:
            file_column = Column(controls=[])
            for file in message['files']:
                filename_str = file['filename']
                size_str = size_value_to_str(value=len(file['value']))
                if file['extension'] in ['jpg', 'jpeg', 'png']:
                    file_byte = file['value'].encode('ISO-8859-1')
                    file_image = Image(
                        src=f'data:image/jpeg;base64,{b64encode(file_byte).decode()}',
                        width=30,
                        height=30,
                    )
                else:
                    file_image = Image(
                        src=Icons.FILE,
                        width=30,
                        height=30,
                    )
                file_column.controls += [
                    StandardButton(
                        content=Row(
                            controls=[
                                Container(
                                    content=file_image,
                                    height=50,
                                    width=50,
                                ),
                                Column(
                                    controls=[
                                        Text(value=filename_str),
                                        Text(value=size_str),
                                        Text(value=file['url']),
                                    ],
                                ),
                            ],
                            tight=True,
                        ),
                        url=file['url'],
                        bgcolor=colors.PRIMARY_CONTAINER,
                        color=color,
                    ),
                ]
            column_controls.append(file_column)
        # Text
        if text_str:
            if message['role'] == 'system':
                text_str = await gtv(key=text_str.lower())
                column_controls += [
                    Row(
                        controls=[
                            Text(
                                value=text_str,
                                size=16,
                                font_family=Fonts.SEMIBOLD,
                                color=color,
                            ),
                        ],
                        tight=True,
                    ),
                ]
            else:
                column_controls += [
                    Row(
                        controls=[
                            Text(
                                value=text_str,
                                size=16,
                                font_family=Fonts.SEMIBOLD,
                                color=color,
                            ),
                        ],
                        tight=True,
                    ),
                ]
        return Container(
            content=InformationContainer(
                content=Column(
                    controls=column_controls,
                ),
                bgcolor=bgcolor,
                padding=padding.symmetric(vertical=16, horizontal=16),

            ),
            alignment=custom_alignment,

        )

    def __init__(
            self,
            gtv: callable,
            account_id: int,
            token: str,
            order_id: int,
            controls: list = None,
            deviation: int = 0,
    ):
        super().__init__()
        self.gtv = gtv
        self.token = token
        self.account_id = account_id
        self.order_id = order_id
        self.control_list = controls
        self.deviation = deviation
        if controls is None:
            self.control_list = []
        self.session = aiohttp.ClientSession()
        self.websocket: aiohttp.client_ws.ClientWebSocketResponse = None

    async def connect(self):
        self.websocket = await self.session.ws_connect(f'{self.url}?token={self.token}&order_id={self.order_id}')

    async def disconnect(self):
        await self.websocket.close()

    async def send(self, data: dict):
        await self.websocket.send_json(data=data)

    def did_mount(self):
        self.running = True
        asyncio.create_task(self.update_chat())

    def will_unmount(self):
        self.running = False
        asyncio.create_task(self.disconnect())

    async def update_chat(self):
        await self.connect()
        async for message in self.websocket:
            if not self.running:
                return
            self.control_list.append(
                await self.create_message_card(
                    gtv=self.gtv,
                    account_id=self.account_id,
                    message=json.loads(message.data),
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
