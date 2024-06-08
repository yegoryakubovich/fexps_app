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

from flet_core import Container, Row, colors, Image, Stack, ImageFit, alignment, ProgressRing, Column, ScrollMode

from app.controls.button import StandardButton
from app.controls.information import Text
from app.controls.input import TextField
from app.controls.layout import ClientBaseView
from app.utils import Icons
from app.utils.chat import Chat


class ChatView(ClientBaseView):
    route = '/client/chat'

    chat: Chat
    order_id: int

    tf_message: TextField
    file_row: Row
    attach_file_btn: StandardButton
    attach_reload_btn: StandardButton

    prog_bars: dict[str, ProgressRing] = {}

    def __init__(self, order_id: int):
        super().__init__()
        self.order_id = order_id
        self.file_row = Row(controls=[])

    async def construct(self):
        account = self.client.session.account
        old_messages = await self.client.session.api.client.messages.get_list(order_id=self.order_id)
        old_messages_controls = [
            await Chat.create_message_card(
                gtv=self.client.session.gtv,
                account_id=account.id,
                message=message,
            )
            for message in old_messages[::-1]
        ]
        self.chat = Chat(
            account_id=account.id,
            gtv=self.client.session.gtv,
            token=self.client.session.token,
            order_id=self.order_id,
            controls=old_messages_controls,
            deviation=self.client.session.timezone.deviation,
        )
        self.attach_file_btn = StandardButton(
            content=Image(
                src=Icons.CLIP,
                width=48,
                height=48,
                color=colors.ON_BACKGROUND,
            ),
            on_click=self.add_file,
            color=colors.ON_BACKGROUND,
            bgcolor=colors.BACKGROUND,
        )
        self.attach_reload_btn = StandardButton(
            content=Image(
                src=Icons.RELOAD,
                width=48,
                height=48,
                color=colors.ON_BACKGROUND,
            ),
            on_click=self.reload_file,
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
                    content=self.file_row,
                ),
                Container(
                    content=Column(
                        controls=[
                            Row(
                                controls=[
                                    self.attach_file_btn,
                                    self.attach_reload_btn,
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
                                height=110,
                            )
                        ],
                        scroll=ScrollMode.AUTO,
                        height=100,
                    ),
                ),
            ],
        )

    """FILE"""

    async def add_file(self, _):
        self.file_keys = await self.client.session.api.client.files.keys.create()
        self.attach_file_btn.on_click = None
        self.attach_file_btn.url = self.file_keys.url
        await self.attach_file_btn.update_async()
        webbrowser.open(url=self.file_keys.url)

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

    async def send(self, _):
        text = None
        if self.tf_message.value:
            text = self.tf_message.value
        if not self.file_keys and not text:
            return
        await self.chat.send(
            data={
                'role': 'user',
                'text': text,
                'files_key': self.file_keys.key if self.file_keys else None,
            },
        )
        await self.update_file_row(files=[])
        self.tf_message.value = None
        await self.tf_message.update_async()
