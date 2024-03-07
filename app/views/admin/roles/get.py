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

from flet_core import ScrollMode

from app.controls.button import FilledButton
from app.controls.information import Text
from app.controls.information.card import Card
from app.controls.layout import AdminBaseView, Section
from app.utils import Fonts
from app.views.admin.roles.permissions import RolePermissionView
from app.views.admin.roles.permissions.create import RolePermissionCreateView


class RoleView(AdminBaseView):
    route = '/admin/role/get'
    role = dict
    permissions = dict

    def __init__(self, role_id):
        super().__init__()
        self.role_id = role_id

    async def build(self):
        await self.set_type(loading=True)
        self.role = await self.client.session.api.admin.roles.get(
            id_=self.role_id
        )
        self.permissions = await self.client.session.api.admin.roles.permissions.get_list(
            role_id=self.role_id,
        )
        await self.set_type(loading=False)

        self.scroll = ScrollMode.AUTO
        self.controls = await self.get_controls(
            title=await self.client.session.gtv(key=self.role['name_text']),
            main_section_controls=[
                FilledButton(
                    content=Text(
                        value=await self.client.session.gtv(key='delete'),
                    ),
                    on_click=self.delete_role,
                ),
            ],
            sections=[
                Section(
                    title=await self.client.session.gtv(key='permissions'),
                    on_create_click=self.create_permission,
                    controls=[
                        Card(
                            controls=[
                                Text(
                                    value=await self.client.session.gtv(key=permission['permission']),
                                    size=15,
                                    font_family=Fonts.REGULAR,
                                ),
                            ],
                            on_click=partial(self.permission_view, permission['id']),
                        )
                        for permission in self.permissions
                    ],
                ),
            ],
         )

    async def delete_role(self, _):
        await self.client.session.api.admin.roles.delete(
            id_=self.role_id,
        )
        await self.client.change_view(go_back=True, with_restart=True)

    async def create_permission(self, _):
        await self.client.change_view(view=RolePermissionCreateView(role_id=self.role_id))

    async def permission_view(self, permission_id, _):
        await self.client.change_view(view=RolePermissionView(permission_id=permission_id))
