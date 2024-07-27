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


import datetime
from typing import Any, Optional

from flet_core import Column, Container, CrossAxisAlignment, Image, MainAxisAlignment, Row, Text, \
    padding, BoxShadow, colors, margin

from app.controls.information.avatar import Avatar
from app.utils import Fonts
from config import settings


class BottomNavigationTab(Container):
    on_click_tab: Any
    account_change_func: callable
    controls: list
    dt_account_click: Optional[datetime.datetime]

    async def click(self, _):
        await self.on_click_tab(tab=self)
        if self.key != 'tab_account':
            return
        now = datetime.datetime.now()
        if not self.dt_account_click:
            self.dt_account_click = now
            return
        delta = now - self.dt_account_click
        if delta > datetime.timedelta(seconds=0.5):
            self.dt_account_click = now
            return
        await self.account_change_func(
            change_view=self.change_view,
            account_next=True,
        )

    async def set_state(self, activated: bool, key: str):
        if key == 'tab_account':
            return
        color = colors.ON_SECONDARY if activated else colors.SECONDARY
        self.text.color = color
        self.icon.color = color

        try:
            await self.text.update_async()
            await self.icon.update_async()
        except AssertionError:
            pass

    def __init__(
            self,
            key: str,
            name: str,
            account_change_func: callable,
            change_view: callable,
            icon_src: Optional[str] = None,
            icon_src_base64: Optional[str] = None,
            control=None,
    ):
        super().__init__()
        self.expand = True

        self.on_click = self.click
        self.key = key
        self.name = name
        self.control = control
        self.dt_account_click = None
        self.account_change_func = account_change_func
        self.change_view = change_view

        if icon_src:
            self.icon = Image(
                src=icon_src,
                color=colors.SECONDARY,
                height=30,
            )
        else:
            self.icon = Avatar(
                src_base64=icon_src_base64,
                width=30,
                height=30,
            )
        self.text = Text(
            font_family=Fonts.MEDIUM,
            value=self.name,
            size=settings.get_font_size(multiple=1.5),
            color=colors.SECONDARY,
        )

        self.content = Container(
            content=Column(
                controls=[
                    self.icon,
                    self.text,
                ],
                spacing=4,
                alignment=MainAxisAlignment.CENTER,
                horizontal_alignment=CrossAxisAlignment.CENTER,
            ),
            margin=margin.only(bottom=10, top=5)
        )


class BottomNavigation(Container):
    async def click_tab(
            self,
            tab: BottomNavigationTab,
    ):
        await self.on_click_tab(tab)

    def __init__(
            self,
            on_click_tab,
            tabs: list[BottomNavigationTab],
    ):
        super().__init__()
        self.tabs = tabs
        self.on_click_tab = on_click_tab

        for tab in self.tabs:
            tab.on_click_tab = self.click_tab

        self.bgcolor = colors.BACKGROUND
        self.padding = padding.symmetric(vertical=10)
        self.content = Row(
            controls=self.tabs,
            spacing=0,
            vertical_alignment=CrossAxisAlignment.CENTER,
            alignment=MainAxisAlignment.CENTER,
        )

        # FIXME
        self.shadow = BoxShadow(
            color=colors.SHADOW,
            spread_radius=1,
            blur_radius=20,
        )
