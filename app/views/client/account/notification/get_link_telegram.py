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


from flet_core import Column, colors, Container, ScrollMode, Row, MainAxisAlignment

from app.controls.button import StandardButton
from app.controls.information import Text
from app.controls.layout import ClientBaseView
from app.utils import Fonts


class AccountNotificationLinkTelegramView(ClientBaseView):
    route = '/client/account/notification/get/link/telegram'

    async def construct(self):
        await self.set_type(loading=True)
        notification_link = await self.client.session.api.client.notifications.updates.code()
        await self.set_type(loading=False)
        controls = [
            Row(
                controls=[
                    StandardButton(
                        content=Text(
                            value=await self.client.session.gtv(key='notification_link_telegram_link_button'),
                            size=20,
                            font_family=Fonts.SEMIBOLD,
                            color=colors.ON_PRIMARY,
                        ),
                        bgcolor=colors.PRIMARY,
                        url=notification_link.url,
                        on_click=self.go_back,
                        expand=2,
                    ),
                ],
                alignment=MainAxisAlignment.SPACE_BETWEEN,
            )
        ]
        self.controls = await self.get_controls(
            title=await self.client.session.gtv(key='notification_link_telegram_title'),
            with_expand=True,
            main_section_controls=[
                Container(
                    content=Column(
                        controls=controls,
                        scroll=ScrollMode.AUTO,
                    ),
                    expand=True,
                ),
            ],
        )

    async def go_back(self, _):
        await self.client.change_view(go_back=True, delete_current=True)
