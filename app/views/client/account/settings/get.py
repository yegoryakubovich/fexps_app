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


from flet_core import Column

from app.controls.button import ListItemButton
from app.controls.layout import ClientBaseView
from app.utils import Icons
from config import settings


class AccountSettingsView(ClientBaseView):
    route = '/client/account/settings/get'

    async def construct(self):
        self.controls = await self.get_controls(
            title=await self.client.session.gtv(key='account_settings_title'),
            with_expand=True,
            main_section_controls=[
                Column(
                    controls=[
                        ListItemButton(
                            icon=Icons.NOTIFICATIONS,
                            name=await self.client.session.gtv(key='account_settings_edit_profile'),
                            font_size=settings.get_font_size(multiple=2),
                            on_click=self.edit_profile,
                        ),
                        ListItemButton(
                            icon=Icons.SECURITY,
                            name=await self.client.session.gtv(key='account_settings_change_password'),
                            font_size=settings.get_font_size(multiple=2),
                            on_click=self.change_password,
                        ),
                        ListItemButton(
                            icon=Icons.ADMIN_TEXTS,
                            name=await self.client.session.gtv(key='account_settings_account_client_text'),
                            font_size=settings.get_font_size(multiple=2),
                            on_click=self.account_client_text,
                        ),
                        ListItemButton(
                            icon=Icons.CONTACT,
                            name=await self.client.session.gtv(key='account_settings_account_contact'),
                            font_size=settings.get_font_size(multiple=2),
                            on_click=self.account_contact,
                        ),

                    ],
                    spacing=4,
                ),
            ],
        )

    async def edit_profile(self, _):
        from app.views.client.account.settings.edit_profile import AccountSettingsEdtProfileView
        await self.client.change_view(view=AccountSettingsEdtProfileView())

    async def change_password(self, _):
        from app.views.client.account.settings.change_password import AccountSettingsChangePasswordView
        await self.client.change_view(view=AccountSettingsChangePasswordView())

    async def account_client_text(self, _):
        from app.views.client.account.settings.account_client_text import AccountSettingsAccountClientTextView
        await self.client.change_view(view=AccountSettingsAccountClientTextView(go_back=True))

    async def account_contact(self, _):
        from app.views.client.account.settings.account_contact import AccountSettingsAccountContactView
        await self.client.change_view(view=AccountSettingsAccountContactView(go_back=True))
