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


from base64 import b64encode

from flet_core import Container, Row, colors, Image, Column, ScrollMode, ImageFit, Control, alignment, Stack

from app.controls.button import StandardButton
from app.controls.information import Text
from app.controls.input import TextField
from app.controls.layout import ClientBaseView
from app.utils import Icons
from app.utils.websockets.chat import ChatWebSockets
from app.utils.websockets.file import FileWebSockets


class ChatView(ClientBaseView):
    route = '/client/chat'

    file_keys = dict
    chat: ChatWebSockets
    file_row: [Row, FileWebSockets]
    order_id: int

    tf_message: TextField
    attach_file_btn: StandardButton

    def __init__(self, order_id: int):
        super().__init__()
        self.order_id = order_id
        self.send_key = None

    async def construct(self):
        account = self.client.session.account
        await self.set_type(loading=True)
        old_messages = await self.client.session.api.client.messages.get_list(order_id=self.order_id)
        self.file_keys = await self.client.session.api.client.files.keys.create()
        await self.set_type(loading=False)
        old_messages_controls = [
            await ChatWebSockets.create_message_card(
                gtv=self.client.session.gtv,
                open_link=self.open_link,
                account_id=account.id,
                message=message,
            )
            for message in old_messages[::-1]
        ]
        self.chat = ChatWebSockets(
            account_id=account.id,
            open_link=self.open_link,
            gtv=self.client.session.gtv,
            token=self.client.session.token,
            order_id=self.order_id,
            controls=old_messages_controls,
            deviation=self.client.session.timezone.deviation,
        )
        self.file_row = FileWebSockets(
            get_key=self.get_key,
            update_file_keys=self.update_file_keys,
            create_file_row_controls=self.create_file_row_controls,
        )
        self.attach_file_btn = StandardButton(
            content=Image(
                src=Icons.CLIP,
                width=48,
                height=48,
                color=colors.ON_BACKGROUND,
            ),
            url=self.file_keys.url,
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

    async def get_key(self):
        return self.file_keys.key

    async def update_file_keys(self, key: str):
        self.send_key = key
        self.file_keys = await self.client.session.api.client.files.keys.create()
        self.attach_file_btn.url = self.file_keys.url
        self.attach_file_btn.update()

    @staticmethod
    async def create_file_row_controls(files: list) -> list[Control]:
        controls = []
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
            if file['extension'] in ['jpg', 'jpeg', 'png']:
                file_byte = file['value'].encode('ISO-8859-1')
                file_image = Container(
                    content=Image(
                        src=f'data:image/jpeg;base64,{b64encode(file_byte).decode()}',
                        width=150,
                        height=150,
                        fit=ImageFit.CONTAIN,
                    ),
                    alignment=alignment.center,
                )
            controls += [
                Container(
                    content=Stack(
                        controls=[
                            file_image,
                            Container(
                                content=Text(
                                    value=file['filename'],
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
        return controls

    async def send(self, _):
        text = None
        if self.tf_message.value:
            text = self.tf_message.value
        if not self.send_key and not text:
            return
        await self.chat.send(
            data={
                'role': 'user',
                'text': text,
                'files_key': self.send_key,
            },
        )
        self.send_key = None
        self.tf_message.value = None
        await self.file_row.rebuild()
        await self.tf_message.update_async()

    async def open_link(self, url: str, _=None):
        self.client.page.launch_url(url=url)
