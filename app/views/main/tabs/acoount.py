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


from functools import partial
from typing import Any

from flet_core import Column, ScrollMode, Container, padding, colors, alignment, CrossAxisAlignment, \
    CircleAvatar, Image

from app.controls.button import ListItemButton
from app.controls.information import Title, Text
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

    async def construct(self):
        firstname = self.client.session.account.firstname
        lastname = self.client.session.account.lastname
        username = self.client.session.account.username

        sections = [
            Section(
                name='my_account',
                settings_=[
                    Setting(
                        name='account_notifications',
                        icon=Icons.NOTIFICATIONS,
                        on_click=self.notification,
                    ),
                    Setting(
                        name='account_security',
                        icon=Icons.SECURITY,
                        on_click=self.change_password,
                    ),
                    Setting(
                        name='account_requisite_data',
                        icon=Icons.METHOD,
                        on_click=self.requisite_data,
                    ),
                    Setting(
                        name='account_account_contact',
                        icon=Icons.CONTACT,
                        on_click=self.account_contact,
                    ),
                    Setting(
                        name='account_language',
                        icon=Icons.LANGUAGE,
                        on_click=self.update_language,
                    ),
                    Setting(
                        name='account_logout',
                        icon=Icons.LOGOUT,
                        on_click=partial(
                            self.client.session.bs_info.open_,
                            icon=Icons.LOGOUT,
                            title=await self.client.session.gtv(key='logout_title'),
                            description=await self.client.session.gtv(key='logout_description'),
                            button_title=await self.client.session.gtv(key='confirm'),
                            button_on_click=self.logout,
                        ),
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
                                size=24,
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
                            content=Column(
                                controls=[
                                    CircleAvatar(
                                        content=Image(
                                            src=Icons.ACCOUNT,
                                            color=colors.SECONDARY,
                                        ),
                                        bgcolor=colors.ON_PRIMARY,
                                        radius=32,
                                    ),
                                    Text(
                                        value=f'{firstname} {lastname}',
                                        font_family=Fonts.SEMIBOLD,
                                        size=24,
                                        color=colors.ON_BACKGROUND,
                                    ),
                                    Text(
                                        value=f'@{username}',
                                        font_family=Fonts.SEMIBOLD,
                                        size=12,
                                        color=colors.ON_BACKGROUND,
                                    ),
                                ],
                                spacing=0,
                                horizontal_alignment=CrossAxisAlignment.CENTER,
                            ),
                            padding=padding.only(top=12),
                            alignment=alignment.center,
                        ),
                        *sections_controls,
                        Container(
                            content=Text(
                                value=f'{await self.client.session.gtv(key="version")} {settings.version}',
                                font_family=Fonts.REGULAR,
                                size=16,
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

    async def notification(self, _):
        from app.views.client.account.notification.get import AccountNotificationView
        await self.client.change_view(view=AccountNotificationView())

    async def change_password(self, _):
        from app.views.client.account.change_password import ChangePasswordView
        await self.client.change_view(view=ChangePasswordView())

    async def requisite_data(self, _):
        from app.views.client.account.requisite_data.get_list import RequisiteDataListView
        await self.client.change_view(view=RequisiteDataListView(go_back=True))

    async def account_contact(self, _):
        from app.views.client.account.account_contact.get import AccountContactView
        await self.client.change_view(view=AccountContactView(go_back=True))

    async def update_language(self, _):
        from app.views.auth.language import LanguageView
        await self.client.change_view(view=LanguageView(go_back=True))

    async def logout(self, _):
        await self.client.session.set_cs(key='token', value=None)
        from app.views.auth.init import InitView
        await self.client.change_view(view=InitView(), delete_current=True)

    async def about_us(self, _):
        from app.views.client.account.about_us import AboutUsView
        await self.client.change_view(view=AboutUsView())

    async def question_view(self, _):
        from app.views.client.account.faq import FAQView
        await self.client.change_view(view=FAQView())

    async def go_admin(self, _):
        if 'admin' in self.client.session.account.permissions:
            await self.client.change_view(view=AdminView())
