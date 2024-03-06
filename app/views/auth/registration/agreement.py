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

from flet_core import Column

from app.controls.button import FilledButton, ListItemButton
from app.controls.information import Text
from app.controls.layout import AuthView
from app.utils import Fonts, Icons
from app.views.auth.registration.successful import RegistrationSuccessfulView


class AgreementRegistrationView(AuthView):

    async def build(self):
        self.controls = await self.get_controls(
            title=await self.client.session.gtv(key='registration_account_create_view_title'),
            controls=[
                Column(
                    controls=[
                        ListItemButton(
                            icon=Icons.PRIVACY_POLICY,
                            name=await self.client.session.gtv(key='privacy_policy'),
                            on_click=self.privacy_policy,
                        ),
                        Text(
                            value=await self.client.session.gtv(key='agreement_info'),
                            font_family=Fonts.REGULAR,
                            size=16,
                        ),
                        FilledButton(
                            content=Text(
                                value=await self.client.session.gtv(key='account_create'),
                            ),
                            on_click=self.change_view,
                        ),
                    ],
                    spacing=20,
                ),
            ],
        )

    async def change_view(self, _):
        await self.set_type(loading=True)
        await self.client.session.api.client.accounts.create(
            username=self.client.session.registration.username,
            password=self.client.session.registration.password,
            firstname=self.client.session.registration.firstname,
            lastname=self.client.session.registration.lastname,
            surname=self.client.session.registration.surname or None,
            country=self.client.session.registration.country,
            language=self.client.session.language,
            timezone=self.client.session.registration.timezone,
            currency=self.client.session.registration.currency,
        )
        await self.client.change_view(view=RegistrationSuccessfulView())
        await self.set_type(loading=False)

    async def privacy_policy(self, _):
        webbrowser.open('')
