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
import logging

from flet_core import Row, Column, Container, padding, colors
from fexps_api_client.utils import ApiException

from app.controls.button import FilledButton
from app.controls.information import Text
from app.controls.input import TextField
from app.controls.layout import AuthView
from app.utils import Fonts, Error
from app.utils.registration import Registration
from app.views.auth.registration.second import RegistrationSecondView


class RegistrationFirstView(AuthView):
    tf_username: TextField
    tf_password: TextField

    async def build(self):
        self.tf_username = TextField(
            label=await self.client.session.gtv(key='username'),
            password=False,
        )
        self.tf_password = TextField(
            label=await self.client.session.gtv(key='password'),
            password=True,
            can_reveal_password=True,
        )
        self.controls = await self.get_controls(
            title=await self.client.session.gtv(key='registration_account_create_view_title'),
            controls=[
                Column(
                    controls=[
                        self.tf_username,
                        self.tf_password,
                        FilledButton(
                            content=Text(
                                value=await self.client.session.gtv(key='next'),
                                size=16,
                            ),
                            on_click=self.change_view,
                            horizontal_padding=54,
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
                                        color=colors.PRIMARY,
                                    ),
                                ],
                                spacing=4,
                            ),
                            on_click=self.go_authentication,
                            ink=True,
                            padding=padding.symmetric(vertical=4),
                        ),
                    ],
                    spacing=20,
                ),
            ]
        )

    async def change_view(self, _):
        check_username_error = await self.client.session.gtv(key='error_check_username')
        # check_password_error = await self.client.session.gtv(key='error_check_password')

        fields = [(self.tf_username, 6, 32), (self.tf_password, 8, 32)]
        for field, min_len, max_len in fields:
            if not await Error.check_field(self, field, min_len=min_len, max_len=max_len):
                return

        try:
            await self.client.session.api.client.accounts.check_username(username=self.tf_username.value)
            logging.critical(2)
        except ApiException as e:
            self.tf_username.error_text = e.message
            await self.update_async()
            return

        try:
            await self.client.session.api.client.accounts.check_password(password=self.tf_password.value)
        except ApiException as e:
            self.tf_password.error_text = e.message
            await self.update_async()
            return

        # Save in Registration
        self.client.session.registration = Registration()
        self.client.session.registration.username = self.tf_username.value
        self.client.session.registration.password = self.tf_password.value

        currencies = await self.client.session.api.client.currencies.get_list()
        countries = await self.client.session.api.client.countries.get_list()
        timezones = await self.client.session.api.client.timezones.get_list()

        await self.client.change_view(
            view=RegistrationSecondView(
                currencies=currencies,
                countries=countries,
                timezones=timezones,
            ),
        )
        await self.update_async()

    async def go_authentication(self, _):
        from app.views.auth.authentication import AuthenticationView
        await self.client.change_view(view=AuthenticationView(), delete_current=True)
