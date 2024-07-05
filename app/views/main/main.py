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

from flet_core import ListView, padding

from app.controls.layout.view import View
from app.controls.navigation import BottomNavigation, BottomNavigationTab
from .tabs import HomeTab, RequestTab, AccountTab, RequisiteTab
from ...utils import Icons


class Tab:
    def __init__(self, name: str, control, icon_src: str = None, icon_src_base64: str = None):
        self.name = name
        self.icon_src = icon_src
        self.icon_src_base64 = icon_src_base64
        self.control = control


class MainView(View):
    tabs: list[BottomNavigationTab]
    tab_selected: BottomNavigationTab = None
    tab_default: BottomNavigationTab
    body: ListView

    async def change_tab(self, tab: BottomNavigationTab):
        if not tab.name != self.tab_selected.name:
            return
        await self.tab_selected.set_state(activated=False, key=self.tab_selected.key)
        self.tab_selected = tab
        await self.tab_selected.set_state(activated=True, key=self.tab_selected.key)
        await self.set_body(controls=self.tab_selected.controls)

    async def set_body(self, controls):
        self.body.controls = controls
        await self.body.update_async()

    async def construct(self):
        self.body = ListView(expand=True, padding=padding.only(bottom=36))
        account_icon_src, icon_src_base64 = Icons.ACCOUNT, None
        if self.client.session.account['file']:
            account_icon_src = None
            icon_src_base64 = b64encode(self.client.session.account['file']['value'].encode('ISO-8859-1')).decode()
        TABS = [
            Tab(
                name='tab_home',
                icon_src=Icons.HOME,
                control=HomeTab,
            ),
            Tab(
                name='tab_request',
                icon_src=Icons.EXCHANGE,
                control=RequestTab,
            ),
            Tab(
                name='tab_requisite',
                icon_src=Icons.REQUISITE,
                control=RequisiteTab,
            ),
            Tab(
                name='tab_account',
                icon_src=account_icon_src,
                icon_src_base64=icon_src_base64,
                control=AccountTab,
            ),
        ]
        self.tabs = [
            BottomNavigationTab(
                key=tab.name,
                name=await self.client.session.gtv(key=tab.name),
                icon_src=tab.icon_src,
                icon_src_base64=tab.icon_src_base64,
                control=tab.control,
            )
            for tab in TABS
        ]
        self.tab_default = self.tabs[0]
        if self.tab_selected:
            self.tab_default = next(tab for tab in self.tabs if tab.name == self.tab_selected.name)

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
            await control.construct()
            await control.on_load()
            tab.controls = [await control.get()]

        self.tab_selected = self.tab_default
        await self.tab_default.set_state(activated=True, key=self.tab_selected.key)
        await self.set_body(controls=self.tab_selected.controls)
