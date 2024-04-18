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


from flet_core import Row, Column, colors, SnackBar, Container, alignment, ScrollMode

from app.controls.button import StandardButton
from app.controls.information import Text
from app.controls.input import TextField
from app.controls.layout import ClientBaseView
from app.utils import Fonts
from fexps_api_client.utils import ApiException


class RequisiteDataView(ClientBaseView):
    route = '/client/requisite/data/get'
    requisite_data = dict
    method = dict
    details: list[TextField]
    snack_bar: SnackBar

    def __init__(self, requisite_data_id: int):
        super().__init__()
        self.requisite_data_id = requisite_data_id

    async def construct(self):
        await self.set_type(loading=True)
        self.requisite_data = await self.client.session.api.client.requisites_datas.get(id_=self.requisite_data_id)
        self.method = await self.client.session.api.client.methods.get(id_=self.requisite_data.method)
        await self.set_type(loading=False)
        self.snack_bar = SnackBar(content=Text(value=await self.client.session.gtv(key='successful')))
        self.details = []
        for field in self.method.schema_fields:
            value = self.requisite_data.fields.get(field['key'])
            self.details.append(
                TextField(
                    key_question=field['key'],
                    label=await self.client.session.gtv(key=field['name_text_key']),
                    value=value if value else '',
                )
            )
        self.controls = await self.get_controls(
            title=self.requisite_data['name'],
            with_expand=True,
            main_section_controls=[
                Container(
                    content=Column(
                        controls=[
                            Text(
                                value='\n'.join([
                                    f'{await self.client.session.gtv(key="name")}: {self.requisite_data.name}',
                                    f'{await self.client.session.gtv(key="currency")}: {self.method.currency.id_str.upper()}',
                                    f'{await self.client.session.gtv(key="method")}: '
                                    f'{await self.client.session.gtv(key=self.method.name_text)} ({self.method.id})',
                                ]),
                                size=24,
                                font_family=Fonts.MEDIUM,
                                color=colors.ON_BACKGROUND,
                            ),
                            *self.details,
                        ],
                        scroll=ScrollMode.AUTO,
                    ),
                    expand=True,
                ),
                Container(
                    content=Row(
                        controls=[
                            StandardButton(
                                content=Text(
                                    value=await self.client.session.gtv(key='save'),
                                ),
                                on_click=self.update_requisite_data,
                                expand=True,
                            ),
                            StandardButton(
                                content=Text(value=await self.client.session.gtv(key='delete')),
                                on_click=self.delete_requisite_data,
                                expand=True,
                            ),
                        ],
                    ),
                    alignment=alignment.bottom_center,
                ),
            ],
        )

    async def delete_requisite_data(self, _):
        await self.client.session.api.client.requisites_datas.delete(id_=self.requisite_data_id)
        await self.client.change_view(go_back=True, delete_current=True, with_restart=True)

    async def update_requisite_data(self, _):
        await self.set_type(loading=True)
        fields = {}
        for text_field in self.details:
            fields[text_field.key_question] = text_field.value
        try:
            await self.client.session.api.client.requisites_datas.update(
                id_=self.requisite_data_id,
                fields=fields,
            )
            await self.set_type(loading=False)
            self.snack_bar.open = True
            await self.update_async()
        except ApiException as exception:
            await self.set_type(loading=False)
            return await self.client.session.error(exception=exception)
