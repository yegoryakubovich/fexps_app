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


from fexps_api_client.utils import ApiException

from app.controls.button import StandardButton
from app.controls.information import Text
from app.controls.input import TextField
from app.controls.layout import AdminBaseView
from app.utils.error import Error


class RoleCreateView(AdminBaseView):
    route = '/admin/role/create'
    tf_name: TextField

    async def build(self):
        self.tf_name = TextField(
            label=await self.client.session.gtv(key='name'),
        )
        self.controls = await self.get_controls(
            title=await self.client.session.gtv(key='admin_role_create_view_title'),
            main_section_controls=[
                self.tf_name,
                StandardButton(
                    content=Text(
                        value=await self.client.session.gtv(key='create'),
                        size=16,
                    ),
                    on_click=self.create_role,
                    expand=True,
                ),
            ],
        )

    async def create_role(self, _):
        await self.set_type(loading=True)
        from app.views.admin.roles import RoleView
        fields = [(self.tf_name, 2, 1024)]
        for field, min_len, max_len in fields:
            if not await Error.check_field(self, field, min_len=min_len, max_len=max_len):
                await self.set_type(loading=False)
                return
        try:
            role_id = await self.client.session.api.admin.roles.create(
                name=self.tf_name.value,
            )
            await self.client.session.get_text_pack()
            await self.set_type(loading=False)
            await self.client.change_view(view=RoleView(role_id=role_id), delete_current=True)
        except ApiException as exception:
            await self.set_type(loading=False)
            return await self.client.session.error(exception=exception)
