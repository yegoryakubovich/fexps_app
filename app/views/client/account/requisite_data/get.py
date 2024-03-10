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


from flet_core import Row, Column, colors

from app.controls.button import FilledButton
from app.controls.information import Text
from app.controls.layout import AdminBaseView
from app.utils import Fonts


class RequisiteDataView(AdminBaseView):
    route = '/admin/text/get'
    requisite_data = dict
    method = dict

    def __init__(self, requisite_data_id: int):
        super().__init__()
        self.requisite_data_id = requisite_data_id

    async def build(self):
        await self.set_type(loading=True)
        self.requisite_data = await self.client.session.api.client.requisite_data.get(id_=self.requisite_data_id)
        self.method = await self.client.session.api.client.methods.get(id_=self.requisite_data.method)
        await self.set_type(loading=False)
        data = [
            f'{await self.client.session.gtv(key="name")}: {self.requisite_data.name}',
            f'{await self.client.session.gtv(key="method")}: '
            f'{await self.client.session.gtv(key=self.method.name_text)} ({self.method.id})',
        ]
        details = []
        for field in self.method.schema_fields:
            field_name = await self.client.session.gtv(key=field["name_text_key"])
            field_result = self.requisite_data.fields.get(field['key'])
            details.append(f'{field_name}: {field_result}')
        self.controls = await self.get_controls(
            title=self.requisite_data['name'],
            main_section_controls=[Column(controls=[
                Text(
                    value='\n'.join(data),
                    size=15,
                    font_family=Fonts.MEDIUM,
                    color=colors.ON_BACKGROUND,
                ),
                Text(
                    value=await self.client.session.gtv(key='details'),
                    size=20,
                    font_family=Fonts.SEMIBOLD,
                    color=colors.ON_BACKGROUND,
                ),
                Text(
                    value=f'\n'.join(details),
                    size=15,
                    font_family=Fonts.MEDIUM,
                    color=colors.ON_BACKGROUND,
                ),
                Row(controls=[FilledButton(
                    content=Text(value=await self.client.session.gtv(key='delete')),
                    on_click=self.delete_requisite_data,
                )]),
            ])],
        )

    async def delete_requisite_data(self, _):
        await self.client.session.api.client.requisite_data.delete(id_=self.requisite_data_id)
        await self.client.change_view(go_back=True, delete_current=True, with_restart=True)
