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


from copy import deepcopy

from flet_core import Checkbox, colors, Column, Row, ScrollMode, Divider
from flet_core.dropdown import Option

from app.controls.button import StandardButton
from app.controls.information import Text
from app.controls.input import TextField, Dropdown
from app.controls.layout import AdminBaseView
from app.utils import Fonts
from fexps_api_client.utils import ApiException
from .get import MethodView


class MethodCreateView(AdminBaseView):
    route = '/admin/method/create'
    currency_options: list[Option]
    schema_type_options: list[Option]
    schema_input_type_options: list[Option]
    schema: Column

    dd_currency: Dropdown
    tf_name: TextField
    schema_fields: list[Column]
    schema_input_fields: list[Column]
    tf_color: TextField
    tf_bgcolor: TextField

    async def build(self):
        await self.set_type(loading=True)
        self.currency_options = [Option(
            text=currency.id_str.upper(),
            key=currency.id_str,
        ) for currency in await self.client.session.api.client.currencies.get_list()]
        await self.set_type(loading=False)
        self.schema_type_options = [
            Option(key='int', text=await self.client.session.gtv(key='integer')),
            Option(key='str', text=await self.client.session.gtv(key='string')),
        ]
        self.schema_input_type_options = [
            Option(key='int', text=await self.client.session.gtv(key='integer')),
            Option(key='str', text=await self.client.session.gtv(key='string')),
            Option(key='image', text=await self.client.session.gtv(key='image')),
        ]
        self.schema = Column(
            controls=[
                Divider(color=colors.ON_BACKGROUND),
                TextField(label=await self.client.session.gtv(key='key')),
                TextField(label=await self.client.session.gtv(key='name')),
                Dropdown(label=await self.client.session.gtv(key='type')),
                Checkbox(label=await self.client.session.gtv(key='optional')),
            ],
        )
        self.dd_currency = Dropdown(
            label=await self.client.session.gtv(key='currency'),
            options=self.currency_options,
        )
        self.tf_name = TextField(
            label=await self.client.session.gtv(key='name'),
        )
        self.tf_color = TextField(
            label=await self.client.session.gtv(key='method_color'),
            value='#1D1D1D',
        )
        self.tf_bgcolor = TextField(
            label=await self.client.session.gtv(key='method_bgcolor'),
            value='#FFFCEF',
        )


        schema_field_column = deepcopy(self.schema)
        schema_field_column.controls[3].options = deepcopy(self.schema_type_options)
        self.schema_fields = [schema_field_column]
        schema_input_field_column = deepcopy(self.schema)
        schema_input_field_column.controls[3].options = deepcopy(self.schema_input_type_options)
        self.schema_input_fields = [schema_input_field_column]
        self.scroll = ScrollMode.AUTO
        self.controls = await self.get_controls(
            title=await self.client.session.gtv(key='admin_text_create_view_title'),
            main_section_controls=[
                self.dd_currency,
                self.tf_name,
                self.tf_color,
                self.tf_bgcolor,
                Row(controls=[
                    Text(
                        value=await self.client.session.gtv(key="schema_fields"),
                        size=24,
                        font_family=Fonts.MEDIUM,
                        color=colors.ON_BACKGROUND,
                    ),
                    StandardButton(
                        content=Text(value=await self.client.session.gtv(key='add_line')),
                        on_click=self.schema_fields_add_line,
                    ),
                    StandardButton(
                        content=Text(value=await self.client.session.gtv(key='delete_line')),
                        on_click=self.schema_fields_delete_line,
                    ),
                ]),
                Column(controls=self.schema_fields),
                Row(controls=[
                    Text(
                        value=await self.client.session.gtv(key="schema_input_fields"),
                        size=24,
                        font_family=Fonts.MEDIUM,
                        color=colors.ON_BACKGROUND,
                    ),
                    StandardButton(
                        content=Text(value=await self.client.session.gtv(key='add_line')),
                        on_click=self.schema_input_fields_add_line,
                    ),
                    StandardButton(
                        content=Text(value=await self.client.session.gtv(key='delete_line')),
                        on_click=self.schema_input_fields_delete_line,
                    ),
                ]),
                Column(controls=self.schema_input_fields),
                StandardButton(
                    content=Text(
                        value=await self.client.session.gtv(key='create'),
                        size=15,
                        font_family=Fonts.REGULAR,
                    ),
                    on_click=self.create_method,
                    expand=True,
                ),
            ],
        )

    async def schema_fields_add_line(self, _):
        column = deepcopy(self.schema)
        column.controls[3].options = deepcopy(self.schema_type_options)
        self.schema_fields.append(column)
        await self.update_async()

    async def schema_fields_delete_line(self, _):
        self.schema_fields.pop()
        await self.update_async()

    async def schema_input_fields_add_line(self, _):
        column = deepcopy(self.schema)
        column.controls[3].options = deepcopy(self.schema_input_type_options)
        self.schema_input_fields.append(column)
        await self.update_async()

    async def schema_input_fields_delete_line(self, _):
        self.schema_input_fields.pop()
        await self.update_async()

    async def create_method(self, _):
        await self.set_type(loading=True)
        fields = []
        for column in self.schema_fields:
            fields.append({
                'key': column.controls[1].value,
                'name': column.controls[2].value,
                'type': column.controls[3].value,
                'optional': column.controls[4].value,
            })
        input_fields = []
        for column in self.schema_input_fields:
            input_fields.append({
                'key': column.controls[1].value,
                'name': column.controls[2].value,
                'type': column.controls[3].value,
                'optional': column.controls[4].value,
            })
        try:
            method_id = await self.client.session.api.admin.methods.create(
                currency=self.dd_currency.value,
                name=self.tf_name.value,
                fields=fields,
                input_fields=input_fields,
                color=self.tf_color.value,
                bgcolor=self.tf_bgcolor.value,
            )
            await self.client.session.get_text_pack()
            await self.set_type(loading=False)
            await self.client.change_view(view=MethodView(id_=method_id), delete_current=True, with_restart=True)
        except ApiException as exception:
            await self.set_type(loading=False)
            return await self.client.session.error(exception=exception)
