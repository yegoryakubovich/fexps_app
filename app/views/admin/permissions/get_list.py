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

from flet_core import Text, ScrollMode, colors

from app.controls.information.card import Card
from app.controls.layout import AdminBaseView
from app.utils import Fonts
from app.views.admin.permissions.create import PermissionCreateView
from app.views.admin.permissions.get import PermissionView


class PermissionListView(AdminBaseView):
    route = '/admin/permission/list/get'
    permissions: list[dict]

    async def construct(self):
        await self.set_type(loading=True)
        self.permissions = await self.client.session.api.admin.permissions.get_list()
        await self.set_type(loading=False)

        self.scroll = ScrollMode.AUTO
        self.controls = await self.get_controls(
            title=await self.client.session.gtv(key='admin_permission_get_list_view_title'),
            on_create_click=self.create_permission,
            main_section_controls=[
                Card(
                    controls=[
                        Text(
                            value=await self.client.session.gtv(key=permission['name_text']),
                            size=18,
                            font_family=Fonts.SEMIBOLD,
                            color=colors.ON_PRIMARY_CONTAINER,
                        ),
                    ],
                    on_click=partial(self.permission_view, permission['id_str']),
                    color=colors.PRIMARY_CONTAINER,
                )
                for permission in self.permissions

            ],
        )

    async def create_permission(self, _):
        await self.client.change_view(view=PermissionCreateView())

    async def permission_view(self, permission_id_str, _):
        await self.client.change_view(view=PermissionView(permission_id_str=permission_id_str))
