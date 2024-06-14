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


from flet_core import Row, Column, Container, padding, colors, border_radius, ScrollMode

from app.controls.button import StandardButton
from app.controls.information import Text
from app.controls.input import TextField
from app.controls.layout import AuthView
from app.utils import Fonts, Error
from app.utils.registration import Registration
from app.views.auth.signup.second import RegistrationSecondView
from fexps_api_client.utils import ApiException


class RegistrationFirstView(AuthView):
    tf_username: TextField
    tf_password: TextField

    async def construct(self):
        self.tf_username = TextField(
            label=await self.client.session.gtv(key='username'),
            password=False,
        )
        self.tf_password = TextField(
            label=await self.client.session.gtv(key='password'),
            password=True,
            can_reveal_password=True,
        )
        self.scroll = ScrollMode.AUTO
        self.controls = await self.get_controls(
            title=await self.client.session.gtv(key='registration_account_create_view_title'),
            controls=[
                Column(
                    controls=[
                        self.tf_username,
                        self.tf_password,
                        Row(
                            controls=[
                                StandardButton(
                                    content=Text(
                                        value=await self.client.session.gtv(key='next_step'),
                                        size=16,
                                    ),
                                    on_click=self.change_view,
                                    expand=True,
                                ),
                            ]
                        ),
                        Container(
                            content=Row(
                                controls=[
                                    Text(
                                        value=await self.client.session.gtv(
                                            key='registration_account_create_view_question'
                                        ),
                                        size=16,
                                        font_family=Fonts.REGULAR,
                                        color=colors.ON_BACKGROUND,
                                    ),
                                    Text(
                                        value=await self.client.session.gtv(key='sign_in'),
                                        size=16,
                                        font_family=Fonts.SEMIBOLD,
                                        color=colors.ON_BACKGROUND,
                                    ),
                                ],
                                spacing=4,
                            ),
                            on_click=self.go_authentication,
                            ink=True,
                            padding=padding.symmetric(vertical=4),
                            border_radius=border_radius.all(6),
                        ),
                    ],
                    spacing=20,
                ),
            ]
        )

    async def change_view(self, _):
        await self.set_type(loading=True)
        fields = [(self.tf_username, 6, 32), (self.tf_password, 7, 32)]
        for field, min_len, max_len in fields:
            if not await Error.check_field(self, field, min_len=min_len, max_len=max_len):
                await self.set_type(loading=False)
                return
        try:
            await self.client.session.api.client.accounts.check_username(username=self.tf_username.value)
        except ApiException as exception:
            await self.set_type(loading=False)
            return await self.client.session.error(exception=exception)

        try:
            await self.client.session.api.client.accounts.check_password(password=self.tf_password.value)
        except ApiException as exception:
            await self.set_type(loading=False)
            return await self.client.session.error(exception=exception)

        # Save in Registration
        self.client.session.registration = Registration()
        self.client.session.registration.contacts = []
        self.client.session.registration.username = self.tf_username.value
        self.client.session.registration.password = self.tf_password.value

        await self.set_type(loading=False)
        await self.client.change_view(view=RegistrationSecondView())

    async def go_authentication(self, _):
        from app.views.auth.signin import AuthenticationView
        await self.client.change_view(view=AuthenticationView(), delete_current=True)
