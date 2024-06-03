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


from flet_core import Column, Container, ScrollMode, Checkbox, Row, colors, Divider

from app.controls.button import StandardButton
from app.controls.information import Text, SnackBar
from app.controls.layout import ClientBaseView
from app.utils import Fonts
from fexps_api_client.utils import ApiException


class AccountNotificationSettingView(ClientBaseView):
    route = '/client/account/notification/get/setting'

    notification = dict
    snack_bar: SnackBar

    cb_active: Checkbox
    cb_global: Checkbox
    cb_request: Checkbox
    cb_requisite: Checkbox
    cb_order: Checkbox
    cb_chat: Checkbox
    cb_transfer: Checkbox

    def __init__(self, notification):
        super().__init__()
        self.notification = notification

    async def construct(self):
        self.cb_active = Checkbox(
            label=await self.client.session.gtv(key='notification_setting_active'),
            value=self.notification.is_active,
        )
        self.cb_global = Checkbox(
            label=await self.client.session.gtv(key='notification_setting_global'),
            value=self.notification.is_global,
        )
        self.cb_request = Checkbox(
            label=await self.client.session.gtv(key='notification_setting_request'),
            value=self.notification.is_request,
        )
        self.cb_requisite = Checkbox(
            label=await self.client.session.gtv(key='notification_setting_requisite'),
            value=self.notification.is_requisite,
        )
        self.cb_order = Checkbox(
            label=await self.client.session.gtv(key='notification_setting_order'),
            value=self.notification.is_order,
        )
        self.cb_chat = Checkbox(
            label=await self.client.session.gtv(key='notification_setting_chat'),
            value=self.notification.is_chat,
        )
        self.cb_transfer = Checkbox(
            label=await self.client.session.gtv(key='notification_setting_transfer'),
            value=self.notification.is_transfer,
        )
        self.snack_bar = SnackBar(content=Text(value=await self.client.session.gtv(key='successful')))
        self.controls = await self.get_controls(
            title=await self.client.session.gtv(key='notification_setting_title'),
            with_expand=True,
            main_section_controls=[
                Container(
                    content=Column(
                        controls=[
                            self.cb_active,
                            Divider(),
                            self.cb_global,
                            self.cb_request,
                            self.cb_requisite,
                            self.cb_order,
                            self.cb_chat,
                            self.cb_transfer,
                        ],
                        scroll=ScrollMode.AUTO,
                    ),
                    expand=True,
                ),
                Container(
                    content=Row(
                        controls=[
                            StandardButton(
                                content=Text(
                                    value=await self.client.session.gtv(key='confirm'),
                                    size=20,
                                    font_family=Fonts.SEMIBOLD,
                                    color=colors.ON_PRIMARY,
                                ),
                                bgcolor=colors.PRIMARY,
                                on_click=self.notification_confirm,
                                expand=2,
                            )
                        ],
                    ),
                )
            ],
        )

    async def notification_confirm(self, _):
        try:
            await self.set_type(loading=True)
            await self.client.session.api.client.notifications.updates.settings(
                is_active=self.cb_active.value,
                is_global=self.cb_global.value,
                is_request=self.cb_request.value,
                is_requisite=self.cb_requisite.value,
                is_order=self.cb_order.value,
                is_chat=self.cb_chat.value,
                is_transfer=self.cb_transfer.value,
            )
            await self.client.session.get_text_pack()
            await self.set_type(loading=False)
            self.snack_bar.open = True
            await self.update_async()
        except ApiException as exception:
            await self.set_type(loading=False)
            return await self.client.session.error(exception=exception)
