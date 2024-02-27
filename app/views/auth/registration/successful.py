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


from flet_core import Text, Image, Container, Column, alignment, MainAxisAlignment, CrossAxisAlignment

from app import InitView
from app.controls.button import FilledButton
from app.controls.layout import AuthView
from app.utils import Fonts, Session, Icons


class RegistrationSuccessfulView(AuthView):
    async def init(self, _):
        await self.set_type(loading=True)
        self.client.session = Session(client=self.client)
        view = await self.client.session.init()
        await self.set_type(loading=False)
        await self.client.change_view(view=view)

    async def change_view(self, _):
        await self.set_type(loading=True)

        session = await self.client.session.api.client.sessions.create(
            username=self.client.session.registration.username,
            password=self.client.session.registration.password,
        )

        # Get result, set in CS
        token = session.token
        await self.client.session.set_cs(key='token', value=token)

        # Clean Registration
        self.client.session.registration = None

        # Change view
        await self.set_type(loading=False)
        await self.client.change_view(view=InitView())

    async def build(self):
        self.controls = await self.get_controls(
            controls=[
                Container(
                    content=Column(
                        controls=[
                            Text(
                                value=await self.client.session.gtv(key='successful'),
                                size=40,
                                font_family=Fonts.SEMIBOLD,
                            ),
                            Image(
                                src=Icons.SUCCESSFUL,
                                height=200,
                            ),
                            FilledButton(
                                content=Text(
                                    value=await self.client.session.gtv(key='next'),
                                    size=16,
                                ),
                                on_click=self.change_view,
                                horizontal_padding=54,
                            ),
                        ],
                        spacing=60,
                        alignment=MainAxisAlignment.CENTER,
                        horizontal_alignment=CrossAxisAlignment.CENTER,
                    ),
                    alignment=alignment.top_center,
                ),
            ],
        )
