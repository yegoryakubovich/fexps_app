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


from base64 import b64encode
from typing import Any

from flet_core import Column, ScrollMode, Container, padding, colors, alignment, CrossAxisAlignment

from app.controls.button import ListItemButton
from app.controls.information import Title, Text
from app.controls.information.avatar import Avatar
from app.utils import Fonts, Icons
from app.views import AdminView
from app.views.main.tabs.base import BaseTab
from config import settings


class Setting:
    name: str
    icon: str
    on_click: Any
    url: Any

    def __init__(self, name: str, icon: str, on_click: Any = None, url: Any = None):
        self.name = name
        self.icon = icon
        self.on_click = on_click
        self.url = url


class Section:
    name: str
    settings: list[Setting]

    def __init__(self, name: str, settings_: list[Setting]):
        self.name = name
        self.settings = settings_


class AccountTab(BaseTab):
    account_column: Column

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.account_column = Column(spacing=0, horizontal_alignment=CrossAxisAlignment.CENTER)

    async def update_account_column(self, update: bool = True):
        firstname = self.client.session.account.firstname
        lastname = self.client.session.account.lastname
        username = self.client.session.account.username
        account_icon_src, icon_src_base64 = Icons.ACCOUNT, None
        if self.client.session.account['file']:
            account_icon_src = None
            icon_src_base64 = b64encode(self.client.session.account['file']['value'].encode('ISO-8859-1')).decode()
        self.account_column.controls = [
            Avatar(
                src=account_icon_src,
                src_base64=icon_src_base64,
                width=100,
                height=100,
            ),
            Text(
                value=f'{firstname} {lastname}',
                font_family=Fonts.SEMIBOLD,
                size=settings.get_font_size(multiple=2.5),
                color=colors.ON_BACKGROUND,
            ),
            Text(
                value=f'@{username}',
                font_family=Fonts.SEMIBOLD,
                size=settings.get_font_size(multiple=1),
                color=colors.ON_BACKGROUND,
            ),
        ]
        if update:
            await self.account_column.update_async()

    async def construct(self):
        await self.update_account_column(update=False)
        sections = [
            Section(
                name='my_account',
                settings_=[
                    Setting(
                        name='account_settings',
                        icon=Icons.SETTINGS,
                        on_click=self.settings,
                    ),
                    Setting(
                        name='account_notifications',
                        icon=Icons.NOTIFICATIONS,
                        on_click=self.notification,
                    ),
                    Setting(
                        name='account_requisite_data',
                        icon=Icons.METHOD,
                        on_click=self.requisite_data,
                    ),
                    Setting(
                        name='account_language',
                        icon=Icons.LANGUAGE,
                        on_click=self.update_language,
                    ),
                    Setting(
                        name='account_change_account',
                        icon=Icons.ACCOUNT,
                        on_click=self.change_account,
                    ),
                ],
            ),
            Section(
                name='help',
                settings_=[
                    Setting(
                        name='about',
                        icon=Icons.ABOUT,
                        on_click=self.about_us,
                    ),
                    Setting(
                        name='support',
                        icon=Icons.SUPPORT,
                        url=settings.url_telegram,
                    ),
                    Setting(
                        name='faq',
                        icon=Icons.FAQ,
                        on_click=self.question_view,
                    ),
                    Setting(
                        name='privacy_policy',
                        icon=Icons.PRIVACY_POLICY,
                        # on_click=self.privacy_policy,
                    ),
                ],
            ),
        ]
        sections_controls = [
            Container(
                content=Column(
                    controls=[
                        Container(
                            content=Text(
                                value=await self.client.session.gtv(section.name),
                                font_family=Fonts.SEMIBOLD,
                                size=settings.get_font_size(multiple=2.5),
                                color=colors.ON_BACKGROUND,
                            ),
                        ),
                        Column(
                            controls=[
                                ListItemButton(
                                    icon=setting.icon,
                                    name=await self.client.session.gtv(key=setting.name),
                                    on_click=setting.on_click,
                                    url=setting.url,
                                )
                                for setting in section.settings
                            ],
                            spacing=4,
                        ),
                    ],
                ),
                padding=padding.only(top=12),
            )
            for section in sections
        ]
        self.scroll = ScrollMode.AUTO
        self.controls = [
            Container(
                content=Column(
                    controls=[
                        Title(value=await self.client.session.gtv(key='account_tab_title')),
                        Container(
                            content=self.account_column,
                            padding=padding.only(top=12),
                            alignment=alignment.center,
                        ),
                        *sections_controls,
                        Container(
                            content=Text(
                                value=f'{await self.client.session.gtv(key="version")} {settings.version}',
                                font_family=Fonts.REGULAR,
                                size=settings.get_font_size(multiple=2),
                                color=colors.ON_BACKGROUND,
                            ),
                            alignment=alignment.center,
                            on_click=self.go_admin,
                            padding=padding.symmetric(vertical=4),
                            ink=True,
                        ),
                    ],
                ),
                padding=10,
            )
        ]

    async def settings(self, _):
        from app.views.client.account.settings.get import AccountSettingsView
        await self.client.change_view(view=AccountSettingsView())

    async def notification(self, _):
        from app.views.client.account.notification import AccountNotificationView
        await self.client.change_view(view=AccountNotificationView())

    async def requisite_data(self, _):
        from app.views.client.account.requisite_data.get_list import RequisiteDataListView
        await self.client.change_view(view=RequisiteDataListView(go_back=True))

    async def update_language(self, _):
        from app.views.auth.language import LanguageView
        await self.client.change_view(view=LanguageView(go_back=True))

    async def change_account(self, _):
        from app.views.client.account.change_account import ChangeAccountView
        await self.client.change_view(view=ChangeAccountView(go_back=True))

    async def about_us(self, _):
        from app.views.client.account.about_us import AboutUsView
        await self.client.change_view(view=AboutUsView())

    async def question_view(self, _):
        from app.views.client.account.faq import FAQView
        await self.client.change_view(view=FAQView())

    async def go_admin(self, _):
        if 'admin' in self.client.session.account.permissions:
            await self.client.change_view(view=AdminView())
