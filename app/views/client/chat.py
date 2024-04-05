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
import json

import aiohttp
from flet_core import Container, Row, alignment, Column, UserControl, Control, colors, MainAxisAlignment, padding, \
    ListView

from app.controls.button import StandardButton
from app.controls.information import Text, InformationContainer
from app.controls.input import TextField
from app.controls.layout import ClientBaseView
from app.utils import Fonts
from config import settings
from fexps_api_client import FexpsApiClient


class Chat(UserControl):
    running: bool
    url: str = f'{settings.url}/messages/chat/ws'
    message_column: ListView
    control_list: list

    @staticmethod
    def create_message_card(account_id: int, message: dict) -> Control:
        position = message['account_position']
        if int(message['account']) == account_id:
            position = 'You'
        return InformationContainer(
            content=Column(
                controls=[
                    Row(
                        controls=[
                            Text(
                                value=position,
                                size=14,
                                font_family=Fonts.SEMIBOLD,
                                color=colors.ON_PRIMARY_CONTAINER,
                            ),
                            Text(
                                value=message['date'].strftime(settings.datetime_format),
                                size=14,
                                font_family=Fonts.SEMIBOLD,
                                color=colors.ON_PRIMARY_CONTAINER,
                            ),
                        ],
                        spacing=16,
                        alignment=MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    Row(
                        controls=[
                            Text(
                                value=message['text'],
                                size=28,
                                font_family=Fonts.SEMIBOLD,
                                color=colors.ON_PRIMARY_CONTAINER,
                            ),
                        ],
                        alignment=MainAxisAlignment.SPACE_BETWEEN,
                    ),
                ],
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
            controls: list = None
    ):
        super().__init__()
        self.api = api
        self.token = token
        self.account_id = account_id
        self.order_id = order_id
        self.control_list = controls
        if controls is None:
            self.control_list = []
        self.session = aiohttp.ClientSession()
        self.websocket: aiohttp.client_ws.ClientWebSocketResponse = None

    async def connect(self):
        self.websocket = await self.session.ws_connect(f'{self.url}?token={self.token}&order_id={self.order_id}')

    async def disconnect(self):
        await self.websocket.close()

    async def send(self, text: str):
        await self.websocket.send_str(data=text)

    async def did_mount_async(self):
        self.running = True
        await self.connect()
        asyncio.create_task(self.update_chat())

    async def will_unmount_async(self):
        self.running = False

    async def update_chat(self):
        async for message in self.websocket:
            if message.type == aiohttp.WSMsgType.TEXT:
                json_data = json.loads(message.data)
                message = await self.api.client.messages.get(id_=json_data['id'])
                self.control_list.append(
                    self.create_message_card(account_id=self.account_id, message=message)
                )
                await self.update_async()

    def build(self):
        self.message_column = ListView(
            controls=self.control_list,
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

    def __init__(self, order_id: int):
        super().__init__()
        self.order_id = order_id

    async def build(self):
        account = self.client.session.account
        await self.set_type(loading=True)
        old_messages = await self.client.session.api.client.messages.get_list(order_id=self.order_id)
        old_messages_controls = [
            Chat.create_message_card(account_id=account.id, message=message)
            for message in old_messages[::-1]
        ]
        await self.set_type(loading=False)
        title_str = await self.client.session.gtv(key='chat_title')
        title_str = f'{title_str} order.{self.order_id}'
        self.chat = Chat(
            account_id=account.id,
            api=self.client.session.api,
            token=self.client.session.token,
            order_id=self.order_id,
            controls=old_messages_controls,
        )
        self.tf_message = TextField(
            label=await self.client.session.gtv(key='chat_write_message'),
            expand=True,
        )
        self.controls = await self.get_controls(
            title=title_str,
            go_back_func=self.go_back,
            main_section_controls=[
                Container(
                    content=self.chat,
                    height=self.client.page.height - 300,
                ),
                Container(
                    content=Row(
                        controls=[
                            self.tf_message,
                        ],
                    ),
                    alignment=alignment.bottom_center,
                ),
                Container(
                    content=Row(
                        controls=[
                            StandardButton(
                                text=await self.client.session.gtv(key='send'),
                                on_click=self.send_message,
                                expand=True,
                            ),
                        ],
                    ),
                    alignment=alignment.bottom_center,
                ),
            ],
        )

    async def go_back(self, _):
        await self.chat.disconnect()
        await self.client.change_view(go_back=True, delete_current=True)

    async def send_message(self, _):
        if not self.tf_message.value:
            return
        await self.chat.send(text=self.tf_message.value)
        self.tf_message.value = None
        await self.update_async()
