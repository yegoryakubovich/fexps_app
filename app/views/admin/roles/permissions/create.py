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


from flet_core.dropdown import Option

from config import settings
from fexps_api_client.utils import ApiException

from app.controls.button import StandardButton
from app.controls.information import Text
from app.controls.input import Dropdown
from app.controls.layout import AdminBaseView
from app.utils import Fonts


class RolePermissionCreateView(AdminBaseView):
    route = '/admin/role/permission/create'
    dd_permission: Dropdown
    permissions = dict
    role = dict
    tf_not_permission: Text

    def __init__(self, role_id):
        super().__init__()
        self.role_id = role_id

    async def construct(self):
        await self.set_type(loading=True)
        self.role = await self.client.session.api.admin.roles.get(
            id_=self.role_id,
        )
        self.permissions = await self.client.session.api.admin.permissions.get_list()
        await self.set_type(loading=False)

        existing_permissions = [
            permission for permission in self.role.get('permissions', [])
        ]
        available_permissions = [
            permission for permission in self.permissions
            if permission.get('id_str') not in existing_permissions
        ]

        permissions_options = [
            Option(
                text=await self.client.session.gtv(key=language.get('name_text')),
                key=language.get('id_str'),
            ) for language in available_permissions
        ]
        if permissions_options:
            self.dd_permission = Dropdown(
                label=await self.client.session.gtv(key='permission'),
                value=permissions_options[0].key,
                options=permissions_options,
            )
            permission_control = self.dd_permission
            button = StandardButton(
                content=Text(
                    value=await self.client.session.gtv(key='create'),
                    size=settings.get_font_size(multiple=1.5),
                ),
                on_click=self.create_permission,
                expand=True,
            )
            controls = [permission_control, button]
        else:
            self.tf_not_permission = Text(
                value=await self.client.session.gtv(key='not_permission'),
                size=20,
                font_family=Fonts.MEDIUM,
            )
            permission_control = self.tf_not_permission
            controls = [permission_control]

        self.controls = await self.get_controls(
            title=await self.client.session.gtv(key='admin_role_permission_create_view_title'),
            main_section_controls=controls,
        )

    async def create_permission(self, _):
        await self.set_type(loading=True)
        try:
            await self.client.session.api.admin.roles.permissions.create(
                role_id=self.role_id,
                permission=self.dd_permission.value,
            )
            await self.set_type(loading=False)
            await self.client.change_view(go_back=True, with_restart=True, delete_current=True)
        except ApiException as exception:
            await self.set_type(loading=False)
            return await self.client.session.error(exception=exception)
