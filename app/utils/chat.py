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
import webbrowser
from base64 import b64encode
from functools import partial

import aiohttp
from flet_core import Row, Column, UserControl, Control, colors, MainAxisAlignment, padding, \
    Image, ScrollMode, ImageFit

from app.controls.button import StandardButton
from app.controls.information import Text, InformationContainer
from app.utils import Fonts, Icons
from config import settings
from fexps_api_client import FexpsApiClient


class Chat(UserControl):
    running: bool
    url: str = settings.get_chat_url()
    message_column: Column
    control_list: list

    @staticmethod
    async def create_message_card(
            account_id: int,
            message: dict,
            positions: dict = None,
            deviation: int = 0,
    ) -> Control:
        async def open_file(url: str, _):
            webbrowser.open(url)

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
        if message['files']:
            image_row = Row(controls=[])
            for file in message['files']:
                if file['extension'] in ['jpg', 'jpeg', 'png']:
                    file_byte = file['value'].encode('ISO-8859-1')
                    file_container = StandardButton(
                        content=Image(
                            src=f'data:image/jpeg;base64,{b64encode(file_byte).decode()}',
                            width=150,
                            height=150,
                            fit=ImageFit.CONTAIN,
                        ),
                        on_click=partial(open_file, file['url']),
                        bgcolor=colors.PRIMARY_CONTAINER,
                        color=colors.ON_PRIMARY_CONTAINER,
                    )
                else:
                    file_container = StandardButton(
                        content=Image(
                            src=Icons.FILE,
                            width=100,
                            height=100,
                            fit=ImageFit.CONTAIN,
                        ),
                        on_click=partial(open_file, file['url']),
                        bgcolor=colors.PRIMARY_CONTAINER,
                        color=colors.ON_PRIMARY_CONTAINER,
                    )
                image_row.controls.append(file_container)

            column_controls.append(image_row)
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
