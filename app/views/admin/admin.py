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


from typing import Any

from flet_core import ScrollMode, Column

from app.controls.layout import AdminBaseView
from .accounts.get_list import AccountListView
from .commissions_packs.get_list import CommissionPackListView
from .countries.get_list import CountryListView
from .currencies.get_list import CurrencyListView
from .languages.get_list import LanguageListView
from .methods import MethodListView
from .permissions import PermissionListView
from .roles import RoleListView
from .texts.get_list import TextListView
from .timezones.get_list import TimezoneListView
from ...controls.button import ListItemButton
from ...utils import Icons


class Setting:
    name: str
    icon: str
    on_click: Any

    def __init__(self, name: str, icon: str, on_click: Any):
        self.name = name
        self.icon = icon
        self.on_click = on_click


class Section:
    settings: list[Setting]

    def __init__(self, settings: list[Setting]):
        self.settings = settings


class AdminView(AdminBaseView):
    route = '/admin'

    async def build(self):
        self.scroll = ScrollMode.AUTO
        parts = [
            Setting(
                name='admin_account_get_list_view_title',
                icon=Icons.ADMIN_ACCOUNTS,
                on_click=self.get_accounts,
            ),
            Setting(
                name='admin_commissions_packs_get_list_view_title',
                icon=Icons.ERROR,
                on_click=self.get_commissions_packs,
            ),
            Setting(
                name='admin_country_get_list_view_title',
                icon=Icons.COUNTRY,
                on_click=self.get_countries,
            ),
            Setting(
                name='admin_currency_get_list_view_title',
                icon=Icons.CURRENCY,
                on_click=self.get_currencies,
            ),
            Setting(
                name='admin_language_get_list_view_title',
                icon=Icons.LANGUAGE,
                on_click=self.get_languages,
            ),
            Setting(
                name='admin_method_get_list_view_title',
                icon=Icons.ERROR,
                on_click=self.get_methods,
            ),
            Setting(
                name='admin_permission_get_list_view_title',
                icon=Icons.ADMIN_PERMISSIONS,
                on_click=self.get_permissions,
            ),
            Setting(
                name='admin_role_get_list_view_title',
                icon=Icons.ADMIN_ROLES,
                on_click=self.get_roles,
            ),
            Setting(
                name='admin_text_get_list_view_title',
                icon=Icons.ADMIN_TEXTS,
                on_click=self.get_texts,
            ),
            Setting(
                name='admin_timezone_get_list_view_title',
                icon=Icons.TIMEZONE,
                on_click=self.get_timezones,
            ),

        ]

        main_sections_controls = [
            Column(
                controls=[
                    ListItemButton(
                        icon=setting.icon,
                        name=await self.client.session.gtv(key=setting.name),
                        on_click=setting.on_click,
                    )
                    for setting in parts
                ],
                spacing=4,
            ),
        ]

        self.controls = await self.get_controls(
            title=await self.client.session.gtv(key='admin_view_title'),
            main_section_controls=main_sections_controls,
        )

    async def coming_soon(self):
        pass

    async def go_back(self, _):
        await self.client.change_view(go_back=True)

    async def get_accounts(self, _):
        await self.client.change_view(view=AccountListView())

    async def get_commissions_packs(self, _):
        await self.client.change_view(view=CommissionPackListView())

    async def get_countries(self, _):
        await self.client.change_view(view=CountryListView())

    async def get_currencies(self, _):
        await self.client.change_view(view=CurrencyListView())

    async def get_languages(self, _):
        await self.client.change_view(view=LanguageListView())

    async def get_methods(self, _):
        await self.client.change_view(view=MethodListView())

    async def get_permissions(self, _):
        await self.client.change_view(view=PermissionListView())

    async def get_roles(self, _):
        await self.client.change_view(view=RoleListView())

    async def get_texts(self, _):
        await self.client.change_view(view=TextListView())

    async def get_timezones(self, _):
        await self.client.change_view(view=TimezoneListView())
