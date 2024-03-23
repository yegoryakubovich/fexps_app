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


from flet_core import Row, colors, MaterialState, Container, Image, padding, margin, InputBorder, TextStyle
from pyperclip import copy

from app.controls.button import StandardButton
from app.controls.information import Text
from app.controls.input import TextField
from app.controls.layout import AdminBaseView
from app.utils import Fonts, Icons
from app.views.admin.accounts.role import AccountRoleListView


class AccountView(AdminBaseView):
    route = '/admin/accounts/get'
    account: dict
    clipboard_text_field: TextField
    clipboard: Container

    def __init__(self, account_id):
        super().__init__()
        self.account_id = account_id

    async def build(self):
        await self.set_type(loading=True)
        self.account = await self.client.session.api.admin.accounts.get(
            id_=self.account_id
        )
        await self.set_type(loading=False)

        # FIXME
        surname = self.account['surname'] if self.account['surname'] else await self.client.session.gtv(key='absent')

        self.clipboard_text_field = TextField(
            value='new_password',
            label=await self.client.session.gtv(key='admin_new_user_password'),
            height=50,
            content_padding=padding.only(left=10),
            color=colors.ON_BACKGROUND,
            border=InputBorder.OUTLINE,
            label_style=TextStyle(
                color=colors.PRIMARY_CONTAINER,
            ),
            expand=True,
            focused_border_color=colors.PRIMARY_CONTAINER,
            border_color=colors.PRIMARY_CONTAINER,
            read_only=True
        )

        self.clipboard = Container(
            Row(
                controls=[
                    self.clipboard_text_field,
                    Container(
                        Container(
                            content=Image(
                                src=Icons.COPY,
                                height=40,
                                color=colors.ON_BACKGROUND,
                            ),
                            ink=True,
                            on_click=self.copy_password,
                            bgcolor=colors.BLUE,
                            border_radius=15,
                        )
                    )
                ],
            ),
            margin=margin.only(top=15),
            visible=False,
        )

        self.controls = await self.get_controls(
            title=await self.client.session.gtv(key='admin_account_get_view_title'),
            main_section_controls=[
                Text(
                    value=await self.client.session.gtv(key='basic_information'),
                    size=20,
                    font_family=Fonts.SEMIBOLD,
                    color=colors.ON_BACKGROUND,
                ),
                Text(
                    value=f"{await self.client.session.gtv(key='firstname')}: {self.account['firstname']}\n"
                          f"{await self.client.session.gtv(key='lastname')}: {self.account['lastname']}\n"
                          f"{await self.client.session.gtv(key='surname')}: "
                          f"{surname}",
                    size=15,
                    font_family=Fonts.MEDIUM,
                    color=colors.ON_BACKGROUND,
                ),
                Text(
                    value=await self.client.session.gtv(key='contact_details'),
                    size=20,
                    font_family=Fonts.SEMIBOLD,
                    color=colors.ON_BACKGROUND,
                ),
                Text(
                    value=f"{await self.client.session.gtv(key='country')}: {self.account['country']}\n"
                          f"{await self.client.session.gtv(key='language')}: {self.account['language']}\n",
                    size=15,
                    font_family=Fonts.MEDIUM,
                    color=colors.ON_BACKGROUND,
                ),
                Row(
                    controls=[
                        StandardButton(
                            content=Text(
                                value=await self.client.session.gtv(key='roles'),
                            ),
                            on_click=self.role_view,
                        ),
                        StandardButton(
                            content=Text(
                                value=await self.client.session.gtv(key='admin_reset_user_password'),
                            ),
                            on_click=self.reset_password,
                            data=0,
                        ),
                    ]
                ),
                self.clipboard,
            ],
        )

    async def role_view(self, _):
        await self.client.change_view(view=AccountRoleListView(account_id=self.account_id))

    async def reset_password(self, e):
        if e.control.data == 0:
            e.control.bgcolor = colors.RED
            e.control.content.value = await self.client.session.gtv(key='confirm')
            e.control.style.overlay_color = {
                MaterialState.DEFAULT: colors.RED_600,
                MaterialState.HOVERED: colors.RED_600,
            }
            e.control.data += 1
        elif e.control.data == 1:
            e.control.bgcolor = colors.SECONDARY
            e.control.style.overlay_color = {
                MaterialState.DEFAULT: colors.PRIMARY_CONTAINER,
                MaterialState.HOVERED: colors.PRIMARY_CONTAINER,
            }
            e.control.content.value = await self.client.session.gtv(key='admin_reset_user_password')
            e.control.data = 0
            new_password = await self.client.session.api.admin.accounts.change_password(account_id=self.account_id)
            self.clipboard_text_field.value = new_password
            self.clipboard.visible = True
        await self.update_async()

    async def copy_password(self, _):
        copy(self.clipboard_text_field.value)
