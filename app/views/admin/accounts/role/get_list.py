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

from flet_core import ScrollMode, colors

from app.controls.information import Text
from app.controls.information.card import Card
from app.controls.layout import AdminBaseView
from app.utils import Fonts
from app.views.admin.accounts.role import AccountRoleView, AccountRoleCreateView


class AccountRoleListView(AdminBaseView):
    route = '/admin/account/roles/list/get'
    roles: list[dict]
    role: list

    def __init__(self, account_id):
        super().__init__()
        self.account_id = account_id

    async def build(self):
        await self.set_type(loading=True)
        self.roles = await self.client.session.api.admin.accounts.roles.get(
            account_id=self.account_id
        )
        await self.set_type(loading=False)
        self.role = []
        if self.roles:
            for item in self.roles:
                role_id = item['role_id']
                role = await self.client.session.api.admin.roles.get(
                    id_=role_id
                )
                self.role.append({'id': item['id'], 'role': role})

        self.scroll = ScrollMode.AUTO
        self.controls = await self.get_controls(
            title=await self.client.session.gtv(key='admin_account_role_get_list_view_title'),
            on_create_click=self.create_role,
            main_section_controls=[
                Card(
                    controls=[
                        Text(
                            value=await self.client.session.gtv(key=role['role']['name_text']),
                            size=18,
                            font_family=Fonts.SEMIBOLD,
                            color=colors.ON_PRIMARY_CONTAINER,
                        ),
                    ],
                    on_click=partial(self.role_view, role),
                    color=colors.PRIMARY_CONTAINER,
                )
                for role in self.role
            ],
        )

    async def role_view(self, role, _):
        await self.client.change_view(
            view=AccountRoleView(
                account_id=self.account_id,
                role=role['role'],
                role_id=role['id'],
            ),
        )

    async def create_role(self, _):
        await self.client.change_view(
            view=AccountRoleCreateView(
                account_id=self.account_id,
            ),
        )
