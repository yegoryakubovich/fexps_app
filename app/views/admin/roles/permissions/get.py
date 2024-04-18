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


from app.controls.button import StandardButton
from app.controls.information import Text
from app.controls.layout import AdminBaseView


class RolePermissionView(AdminBaseView):
    route = '/admin/role/permission/get'
    permission = dict

    def __init__(self, permission_id):
        super().__init__()
        self.permission_id = permission_id

    async def construct(self):
        await self.set_type(loading=True)
        self.permission = await self.client.session.api.admin.roles.permissions.get(
            id_=self.permission_id
        )
        await self.set_type(loading=False)

        self.controls = await self.get_controls(
            title=await self.client.session.gtv(key=self.permission['permission']),
            main_section_controls=[
                StandardButton(
                    content=Text(
                        value=await self.client.session.gtv(key='delete'),
                    ),
                    on_click=self.delete_permission,
                    expand=True,
                ),
            ],
        )

    async def delete_permission(self, _):
        await self.client.session.api.admin.roles.permissions.delete(
            id_=self.permission_id,
        )
        await self.client.change_view(go_back=True, with_restart=True)
