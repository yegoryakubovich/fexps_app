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
from flet_core import UserControl, Row

from config import settings


class FileWebSockets(UserControl):
    running: bool
    url: str = settings.get_file_url()
    file_row: Row
    files: list

    def __init__(
            self,
            get_key: callable,
            update_file_keys: callable,
            create_file_row_controls: callable,
    ):
        super().__init__()
        self.get_key = get_key
        self.update_file_keys = update_file_keys
        self.create_file_row_controls = create_file_row_controls
        self.session = aiohttp.ClientSession()
        self.websocket: aiohttp.client_ws.ClientWebSocketResponse = None

    async def connect(self):
        self.websocket = await self.session.ws_connect(f'{self.url}?key={self.key}')

    async def disconnect(self):
        await self.websocket.close()

    def did_mount(self):
        self.running = True
        asyncio.create_task(self.update_chat())

    def will_unmount(self):
        self.running = False
        asyncio.create_task(self.disconnect())

    async def update_chat(self):
        await self.connect()
        self.file_row.controls = await self.create_file_row_controls(files=[])
        await self.update_async()
        async for message in self.websocket:
            if not self.running:
                return
            message_json = json.loads(message.data)
            key = await self.get_key()
            if message_json['key'] != key:
                continue
            self.file_row.controls = await self.create_file_row_controls(files=message_json['files'])
            await self.update_async()
            await self.update_file_keys(key=key)

    async def rebuild(self):
        self.file_row.controls = await self.create_file_row_controls(files=[])
        await self.update_async()

    def build(self):
        self.file_row = Row(
            controls=[],
        )
        return self.file_row
