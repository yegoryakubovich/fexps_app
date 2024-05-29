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
    cb_request_change: Checkbox
    cb_requisite_change: Checkbox
    cb_order_change: Checkbox
    cb_chat_change: Checkbox

    def __init__(self, notification):
        super().__init__()
        self.notification = notification

    async def construct(self):
        self.cb_active = Checkbox(
            label=await self.client.session.gtv(key='notification_setting_active'),
            value=self.notification.is_active,
        )
        self.cb_request_change = Checkbox(
            label=await self.client.session.gtv(key='notification_setting_request_change'),
            value=self.notification.is_request_change,
        )
        self.cb_requisite_change = Checkbox(
            label=await self.client.session.gtv(key='notification_setting_requisite_change'),
            value=self.notification.is_requisite_change,
        )
        self.cb_order_change = Checkbox(
            label=await self.client.session.gtv(key='notification_setting_order_change'),
            value=self.notification.is_order_change,
        )
        self.cb_chat_change = Checkbox(
            label=await self.client.session.gtv(key='notification_setting_chat_change'),
            value=self.notification.is_chat_change,
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
                            self.cb_request_change,
                            self.cb_requisite_change,
                            self.cb_order_change,
                            self.cb_chat_change,
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
                is_request_change=self.cb_request_change.value,
                is_requisite_change=self.cb_requisite_change.value,
                is_order_change=self.cb_order_change.value,
                is_chat_change=self.cb_chat_change.value,
            )
            await self.client.session.get_text_pack()
            await self.set_type(loading=False)
            self.snack_bar.open = True
            await self.update_async()
        except ApiException as exception:
            await self.set_type(loading=False)
            return await self.client.session.error(exception=exception)
