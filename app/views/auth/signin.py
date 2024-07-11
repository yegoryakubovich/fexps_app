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

from flet_core import Column, Row, Container, padding, colors, border_radius, ScrollMode

from app.controls.button import StandardButton
from app.controls.information import Text
from app.controls.input import TextField
from app.controls.layout import AuthView
from app.utils import Fonts, Error
from config import settings
from fexps_api_client.utils import ApiException


class AuthenticationView(AuthView):
    tf_username: TextField
    tf_password: TextField

    def __init__(self, new_login: bool = False):
        super().__init__()
        self.new_login = new_login

    async def construct(self):
        self.tf_username = TextField(
            label=await self.client.session.gtv(key='username'),
        )
        self.tf_password = TextField(
            label=await self.client.session.gtv(key='password'),
            password=True,
            can_reveal_password=True,
        )
        self.scroll = ScrollMode.AUTO
        self.controls = await self.get_controls(
            title=await self.client.session.gtv(key='sign_in'),
            go_back=self.go_back if self.new_login else None,
            controls=[
                Column(
                    controls=[
                        self.tf_username,
                        self.tf_password,
                        Row(
                            controls=[
                                StandardButton(
                                    content=Text(
                                        value=await self.client.session.gtv(key='sign_in'),
                                        size=settings.get_font_size(multiple=1.5),
                                    ),
                                    on_click=self.authenticate,
                                    horizontal=54,
                                    expand=True,
                                ),
                            ],
                        ),
                        Container(
                            content=Row(
                                controls=[
                                    Text(
                                        value=await self.client.session.gtv(key='authentication_view_question'),
                                        size=16,
                                        font_family=Fonts.REGULAR,
                                        color=colors.ON_BACKGROUND,
                                    ),
                                    Text(
                                        value=await self.client.session.gtv(key='sign_up'),
                                        size=16,
                                        font_family=Fonts.SEMIBOLD,
                                        color=colors.ON_BACKGROUND,
                                    ),
                                ],
                                spacing=4,
                            ),
                            on_click=self.go_registration,
                            ink=True,
                            padding=padding.symmetric(vertical=4),
                            border_radius=border_radius.all(6),
                        ),
                    ],
                    spacing=20,
                ),
            ],
        )

    async def go_back(self, _=None):
        await self.client.change_view(go_back=True)

    async def authenticate(self, _):
        await self.set_type(loading=True)
        fields = [(self.tf_username, 6, 32), (self.tf_password, 6, 32)]
        for field, min_len, max_len in fields:
            if not await Error.check_field(self, field, min_len=min_len, max_len=max_len):
                await self.set_type(loading=False)
                return
        # Create session
        try:
            session = await self.client.session.api.client.sessions.create(
                username=self.tf_username.value,
                password=self.tf_password.value,
            )
            await self.set_type(loading=False)
        except ApiException as exception:
            await self.set_type(loading=False)
            return await self.client.session.error(exception=exception)

        # Get result, set in CS
        tokens = await self.client.session.get_cs(key='tokens')
        if not tokens:
            tokens = []
        token = session.token
        await self.client.session.set_cs(key='tokens', value=tokens + [token])
        await self.client.session.set_cs(key='token', value=token)
        await self.client.session.set_cs(key='current_wallet', value=None)

        # Change view
        self.client.page.views.clear()
        await self.set_type(loading=False)
        from app.views.auth.init import InitView
        await self.client.change_view(view=InitView())

    async def go_registration(self, _):
        from app.views.auth.signup import RegistrationFirstView
        await self.client.change_view(
            view=RegistrationFirstView(new_login=self.new_login),
            delete_current=True,
        )
