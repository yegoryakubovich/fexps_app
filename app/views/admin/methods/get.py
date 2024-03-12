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
import logging
from copy import deepcopy

from flet_core import Row, Column, colors, Checkbox, ScrollMode
from flet_core.dropdown import Option

from app.controls.button import FilledButton
from app.controls.information import Text
from app.controls.information.snack_bar import SnackBar
from app.controls.input import TextField, Dropdown
from app.controls.layout import AdminBaseView
from app.utils import Fonts
from fexps_api_client.utils import ApiException


class MethodView(AdminBaseView):
    route = '/admin/method/get'
    method = dict
    tf_currency: TextField
    details: list[Column]
    schema: Column
    snack_bar: SnackBar

    def __init__(self, id_: int):
        super().__init__()
        self.method_id = id_

    async def build(self):
        await self.set_type(loading=True)
        self.method = await self.client.session.api.client.methods.get(id_=self.method_id)
        await self.set_type(loading=False)
        self.snack_bar = SnackBar(content=Text(value=await self.client.session.gtv(key='successful')))
        self.schema = Column(
            controls=[
                Text(
                    value=await self.client.session.gtv(key='parameter') + ' #0',
                    size=24,
                    font_family=Fonts.MEDIUM,
                    color=colors.ON_BACKGROUND,
                ),
                TextField(
                    label=await self.client.session.gtv(key='key'),
                ),
                TextField(
                    label=await self.client.session.gtv(key='name'),
                ),
                Dropdown(
                    label=await self.client.session.gtv(key='type'),
                    options=[
                        Option(key='int', text=await self.client.session.gtv(key='integer')),
                        Option(key='str', text=await self.client.session.gtv(key='string')),
                    ],
                ),
                Checkbox(
                    label=await self.client.session.gtv(key='optional'),
                    value=False,
                ),
            ],

        )
        self.tf_currency = TextField(
            label=await self.client.session.gtv(key='key'),
            value=self.method.currency,
        )
        self.details = []
        for i, field in enumerate(self.method.schema_fields):
            column = deepcopy(self.schema)
            column.controls[0].value = await self.client.session.gtv(key='parameter') + f' #{i + 1}'
            column.controls[1].value = field['key']
            column.controls[2].value = field['name']
            column.controls[3].value = field['type']
            column.controls[4].value = field['optional']
            self.details.append(column)
        self.scroll = ScrollMode.AUTO
        self.controls = await self.get_controls(
            title=await self.client.session.gtv(key=self.method.name_text),
            main_section_controls=[
                Column(
                    controls=[
                        Text(
                            value='\n'.join([
                                f'{await self.client.session.gtv(key="name")}: '
                                f'{await self.client.session.gtv(key=self.method.name_text)}',
                            ]),
                            size=24,
                            font_family=Fonts.MEDIUM,
                            color=colors.ON_BACKGROUND,
                        ),
                        self.tf_currency,
                        Column(controls=self.details),
                        Row(
                            controls=[
                                FilledButton(
                                    content=Text(
                                        value=await self.client.session.gtv(key='save'),
                                    ),
                                    on_click=self.update_method,
                                ),
                                FilledButton(
                                    content=Text(
                                        value=await self.client.session.gtv(key='add_line'),
                                    ),
                                    on_click=self.add_line,
                                ),
                                FilledButton(
                                    content=Text(
                                        value=await self.client.session.gtv(key='remove_line'),
                                    ),
                                    on_click=self.remove_line,
                                ),
                                FilledButton(
                                    content=Text(value=await self.client.session.gtv(key='delete')),
                                    on_click=self.delete_method,
                                ),
                            ],
                        ),
                    ],
                ),
            ],
        )

    async def delete_method(self, _):
        await self.client.session.api.admin.texts.delete(id_=self.method_id)
        await self.client.change_view(go_back=True, with_restart=True)

    async def add_line(self, _):
        self.details.append(deepcopy(self.schema))
        self.controls[1].content.controls[1].controls[2].controls = self.details
        await self.update_async()

    async def remove_line(self, _):
        self.details.pop()
        self.controls[1].content.controls[1].controls[2].controls = self.details
        await self.update_async()

    async def update_method(self, _):
        await self.set_type(loading=True)
        schema_fields = []
        for column in self.details:
            schema_fields.append({
                'key': column.controls[1].value,
                'name': column.controls[2].value,
                'type': column.controls[3].value,
                'optional': column.controls[4].value,
            })
        try:
            await self.client.session.api.admin.methods.update(
                id_=self.method_id,
                currency_id_str=self.tf_currency.value,
                schema_fields=schema_fields
            )
            await self.client.session.get_text_pack()
            await self.set_type(loading=False)
            self.snack_bar.open = True
            await self.update_async()
        except ApiException as exception:
            await self.set_type(loading=False)
            return await self.client.session.error(exception=exception)
