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
from functools import partial

from flet_core import Column, Container, ScrollMode, Row, colors, ExpansionTile, border, ControlEvent

from app.controls.button import StandardButton, SwitchButton
from app.controls.information import Text, SnackBar
from app.controls.layout import ClientBaseView
from app.utils import Fonts
from config import settings
from fexps_api_client import FexpsApiClient
from fexps_api_client.utils import ApiException


class AccountNotificationSettingView(ClientBaseView):
    route = '/client/account/settings/notification/get/setting'

    notification = dict
    settings: dict
    snack_bar: SnackBar

    def __init__(self, notification):
        super().__init__()
        self.notification = notification

    async def construct(self):
        self.settings = {
            'is_active': self.notification.is_active,
            'is_system': self.notification.is_system,
            'is_system_email': self.notification.is_system_email,
            'is_system_telegram': self.notification.is_system_telegram,
            'is_system_push': self.notification.is_system_push,
            'is_request': self.notification.is_request,
            'is_request_email': self.notification.is_request_email,
            'is_request_telegram': self.notification.is_request_telegram,
            'is_request_push': self.notification.is_request_push,
            'is_requisite': self.notification.is_requisite,
            'is_requisite_email': self.notification.is_requisite_email,
            'is_requisite_telegram': self.notification.is_requisite_telegram,
            'is_requisite_push': self.notification.is_requisite_push,
            'is_chat': self.notification.is_chat,
            'is_chat_email': self.notification.is_chat_email,
            'is_chat_telegram': self.notification.is_chat_telegram,
            'is_chat_push': self.notification.is_chat_push,
            'is_transfer': self.notification.is_transfer,
            'is_transfer_email': self.notification.is_transfer_email,
            'is_transfer_telegram': self.notification.is_transfer_telegram,
            'is_transfer_push': self.notification.is_transfer_push,
        }
        self.snack_bar = SnackBar(
            content=Text(
                value=await self.client.session.gtv(key='successful'),
            ),
        )
        controls = [
            SwitchButton(
                label=await self.client.session.gtv(key='notification_setting_active'),
                value=self.notification.is_system,
                on_change=partial(self.notification_setting_change, 'is_system')
            ),
            *[
                Container(
                    content=ExpansionTile(
                        title=SwitchButton(
                            label=await self.client.session.gtv(key=f'notification_setting_{key}'),
                            value=self.settings[f'is_{key}'],
                            on_change=partial(self.notification_setting_change, f'is_{key}'),
                        ),
                        subtitle=Text(
                            value=await self.client.session.gtv(key=f'notification_setting_{key}_description'),
                            size=settings.get_font_size(multiple=1.5),
                            font_family=Fonts.REGULAR,
                            color=colors.ON_BACKGROUND,
                        ),
                        controls=[
                            SwitchButton(
                                label=await self.client.session.gtv(key=f'notification_setting_email'),
                                value=self.settings[f'is_{key}_email'],
                                on_change=partial(self.notification_setting_change, f'is_{key}_email'),
                            ),
                            SwitchButton(
                                label=await self.client.session.gtv(key=f'notification_setting_telegram'),
                                value=self.settings[f'is_{key}_telegram'],
                                on_change=partial(self.notification_setting_change, f'is_{key}_telegram'),
                            ),
                            SwitchButton(
                                label=await self.client.session.gtv(key=f'notification_setting_push'),
                                value=self.settings[f'is_{key}_push'],
                                on_change=partial(self.notification_setting_change, f'is_{key}_push'),
                            ),
                        ],
                        maintain_state=True,
                        bgcolor=colors.BACKGROUND,
                        collapsed_bgcolor=colors.BACKGROUND,
                        icon_color=colors.ON_BACKGROUND,
                        collapsed_icon_color=colors.ON_BACKGROUND,
                        initially_expanded=self.client.session.debug,
                        controls_padding=5,
                    ),
                    border=border.all(color=colors.ON_BACKGROUND, width=1),
                )
                for key in ['system', 'request', 'requisite', 'chat', 'transfer']
            ],
        ]
        self.controls = await self.get_controls(
            title=await self.client.session.gtv(key='notification_setting_title'),
            with_expand=True,
            main_section_controls=[
                self.snack_bar,
                Container(
                    content=Column(
                        controls=controls,
                        scroll=ScrollMode.AUTO,
                        spacing=10,
                    ),
                    expand=True,
                ),
                Container(
                    content=Row(
                        controls=[
                            StandardButton(
                                content=Text(
                                    value=await self.client.session.gtv(key='confirm'),
                                    size=settings.get_font_size(multiple=2),
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

    async def notification_setting_change(self, key: str, event: ControlEvent):
        self.settings[key] = True if event.data == 'true' else False
        logging.critical(self.settings)

    async def notification_confirm(self, _):
        try:
            await self.set_type(loading=True)
            await self.client.session.api.client.notifications.updates.settings(**self.settings)
            await self.set_type(loading=False)
            self.snack_bar.open = True
            await self.update_async()
        except ApiException as exception:
            await self.set_type(loading=False)
            return await self.client.session.error(exception=exception)
