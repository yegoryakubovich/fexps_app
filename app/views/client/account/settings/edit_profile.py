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

from flet_core import Column, Container, ScrollMode, Row, Image, ImageFit, alignment, Control, colors, MainAxisAlignment

from app.controls.button import StandardButton
from app.controls.information import Text, SnackBar
from app.controls.input import TextField
from app.controls.layout import ClientBaseView
from app.utils import Fonts
from app.utils.websockets.file import FileWebSockets
from config import settings
from fexps_api_client.utils import ApiException


class AccountSettingsEdtProfileView(ClientBaseView):
    route = '/client/account/settings/edit/profile'

    account = dict
    file_keys = dict

    tf_firstname: TextField
    tf_lastname: TextField
    file_row: [Row, FileWebSockets]
    btn_edit_photo: StandardButton

    snack_bar: SnackBar

    def __init__(self):
        super().__init__()
        self.file_key = None

    async def construct(self):
        await self.set_type(loading=True)
        self.account = self.client.session.account
        self.file_keys = await self.client.session.api.client.files.keys.create()
        await self.set_type(loading=False)
        self.tf_firstname = TextField(
            label=await self.client.session.gtv(key='account_settings_edit_profile_firstname'),
            value=self.account.firstname,
        )
        self.tf_lastname = TextField(
            label=await self.client.session.gtv(key='account_settings_edit_profile_lastname'),
            value=self.account.lastname,
        )
        self.file_row = FileWebSockets(
            get_key=self.get_key,
            update_file_keys=self.update_file_keys,
            create_file_row_controls=self.create_file_row_controls,
        )
        self.btn_edit_photo = StandardButton(
            content=Text(
                value=await self.client.session.gtv(
                    key='account_settings_edit_profile_edit_photo'),
            ),
            url=self.file_keys.url,
        )
        self.snack_bar = SnackBar(
            content=Text(
                value=await self.client.session.gtv(key='successful'),
            ),
        )
        self.controls = await self.get_controls(
            title=await self.client.session.gtv(key='account_settings_edit_profile'),
            with_expand=True,
            main_section_controls=[
                self.snack_bar,
                Container(
                    content=Column(
                        controls=[
                            self.tf_firstname,
                            self.tf_lastname,
                            Row(
                                controls=[
                                    Text(
                                        value=await self.client.session.gtv(key='account_settings_edit_profile_photo'),
                                        size=settings.get_font_size(multiple=2),
                                        font_family=Fonts.BOLD,
                                        color=colors.ON_BACKGROUND,
                                    ),
                                    self.btn_edit_photo,
                                ],
                                alignment=MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            self.file_row,
                        ],
                        scroll=ScrollMode.AUTO
                    ),
                    expand=True,
                ),
                Container(
                    content=Row(
                        controls=[
                            StandardButton(
                                content=Text(
                                    value=await self.client.session.gtv(key='next'),
                                    size=15,
                                    font_family=Fonts.REGULAR,
                                ),
                                on_click=self.confirm,
                                expand=True,
                            ),
                        ],
                    ),
                ),
            ],
        )

    async def get_key(self):
        return self.file_keys.key

    async def update_file_keys(self, key: str):
        self.file_key = key
        self.file_keys = await self.client.session.api.client.files.keys.create()
        self.btn_edit_photo.url = self.file_keys.url
        await self.btn_edit_photo.update_async()

    async def create_file_row_controls(self, files: list) -> list[Control]:
        if not files and self.account['file']:
            files: list = [self.account['file']]
        for file in files:
            if file['extension'] not in ['jpg', 'jpeg', 'png']:
                continue
            file_byte = file['value'].encode('ISO-8859-1')
            return [
                Container(
                    content=Image(
                        src=f'data:image/jpeg;base64,{b64encode(file_byte).decode()}',
                        width=150,
                        height=150,
                        fit=ImageFit.CONTAIN,
                    ),
                    alignment=alignment.center,
                ),
            ]

    async def confirm(self, _):
        try:
            await self.set_type(loading=True)
            await self.client.session.api.client.accounts.update(
                firstname=self.tf_firstname.value,
                lastname=self.tf_lastname.value,
                file_key=self.file_key,
            )
            self.account = self.client.session.account = await self.client.session.api.client.accounts.get()
            await self.set_type(loading=False)
            self.snack_bar.open = True
            await self.update_async()
        except ApiException as exception:
            await self.set_type(loading=False)
            return await self.client.session.error(exception=exception)
