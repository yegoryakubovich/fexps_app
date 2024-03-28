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


from flet_core import ListView, padding

from app.controls.layout.view import View
from app.controls.navigation import BottomNavigation, BottomNavigationTab
from .tabs import HomeTab, RequestTab, AccountTab, RequisiteTab
from ...utils import Icons


class Tab:
    def __init__(self, name: str, icon: str, control):
        self.name = name
        self.icon = icon
        self.control = control


TABS = [
    Tab(
        name='tab_home',
        icon=Icons.HOME,
        control=HomeTab,
    ),
    Tab(
        name='tab_request',
        icon=Icons.EXCHANGE,
        control=RequestTab,
    ),
    Tab(
        name='tab_requisite',
        icon=Icons.REQUISITE,
        control=RequisiteTab,
    ),
    Tab(
        name='tab_account',
        icon=Icons.ACCOUNT,
        control=AccountTab,
    ),
]


class MainView(View):
    tabs: list[BottomNavigationTab]
    tab_selected: BottomNavigationTab = None
    tab_default: BottomNavigationTab
    body: ListView

    async def change_tab(self, tab: BottomNavigationTab):
        if not tab.name != self.tab_selected.name:
            return
        await self.tab_selected.set_state(activated=False)
        self.tab_selected = tab
        await self.tab_selected.set_state(activated=True)
        await self.set_body(controls=self.tab_selected.controls)

    async def set_body(self, controls):
        self.body.controls = controls
        await self.body.update_async()

    async def build(self):
        self.body = ListView(expand=True, padding=padding.only(bottom=36))
        self.tabs = [
            BottomNavigationTab(
                name=await self.client.session.gtv(key=tab.name),
                icon=tab.icon,
                control=tab.control,
            )
            for tab in TABS
        ]
        self.tab_default = self.tabs[0] if not self.tab_selected else self.tab_selected

        self.controls = [
            # Header
            await self.get_header(),

            # Body
            self.body,

            # Bottom Navigation
            BottomNavigation(
                on_click_tab=self.change_tab,
                tabs=self.tabs,
            ),
        ]

        for tab in self.tabs:
            control = tab.control(client=self.client, view=self)
            await control.build()
            await control.on_load()
            tab.controls = [await control.get()]

        self.tab_selected = self.tab_default
        await self.tab_default.set_state(activated=True)
        await self.set_body(controls=self.tab_selected.controls)
