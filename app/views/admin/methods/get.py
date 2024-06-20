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

from flet_core import Row, Column, colors, Checkbox, ScrollMode, Divider, KeyboardType
from flet_core.dropdown import Option

from app.controls.button import StandardButton
from app.controls.information import Text
from app.controls.information.snack_bar import SnackBar
from app.controls.input import TextField, Dropdown
from app.controls.layout import AdminBaseView
from app.utils import Fonts, Error, value_to_int, value_to_float
from fexps_api_client.utils import ApiException


class MethodView(AdminBaseView):
    route = '/admin/method/get'
    method = dict
    currency = dict

    currency_options: list[Option]
    schema_type_options: list[Option]
    schema_input_type_options: list[Option]

    dd_currency: Dropdown
    tf_name = TextField
    schema: Column
    schema_fields: list[Column]
    schema_input_fields: list[Column]
    tf_input_rate_default = TextField
    tf_output_rate_default = TextField
    tf_input_rate_percent = TextField
    tf_output_rate_percent = TextField
    tf_color: TextField
    tf_bgcolor: TextField
    cb_is_rate_default: Checkbox

    snack_bar: SnackBar

    def __init__(self, method_id: int):
        super().__init__()
        self.method_id = method_id

    async def construct(self):
        await self.set_type(loading=True)
        self.method = await self.client.session.api.client.methods.get(id_=self.method_id)
        self.currency = self.method.currency
        self.currency_options = [
            Option(text=currency.id_str.upper(), key=currency.id_str)
            for currency in await self.client.session.api.client.currencies.get_list()
        ]
        await self.set_type(loading=False)
        self.snack_bar = SnackBar(content=Text(value=await self.client.session.gtv(key='successful')))
        self.schema_type_options = [
            Option(key='int', text=await self.client.session.gtv(key='int')),
            Option(key='str', text=await self.client.session.gtv(key='str')),
        ]
        self.schema_input_type_options = [
            Option(key='int', text=await self.client.session.gtv(key='int')),
            Option(key='str', text=await self.client.session.gtv(key='str')),
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
            value=self.method.currency.id_str,
        )
        self.tf_name = TextField(
            label=await self.client.session.gtv(key='name'),
            value=await self.client.session.gtv(key=self.method.name_text),
        )
        self.tf_input_rate_default = TextField(
            label=await self.client.session.gtv(key='admin_method_input_rate_default'),
            keyboard_type=KeyboardType.NUMBER,
            value=value_to_float(value=self.method.input_rate_default, decimal=self.currency.rate_decimal),
        )
        self.tf_output_rate_default = TextField(
            label=await self.client.session.gtv(key='admin_method_output_rate_default'),
            keyboard_type=KeyboardType.NUMBER,
            value=value_to_float(value=self.method.output_rate_default, decimal=self.currency.rate_decimal),
        )
        self.tf_input_rate_percent = TextField(
            label=await self.client.session.gtv(key='admin_method_input_rate_percent'),
            keyboard_type=KeyboardType.NUMBER,
            value=value_to_float(value=self.method.input_rate_percent, decimal=self.currency.rate_decimal),
        )
        self.tf_output_rate_percent = TextField(
            label=await self.client.session.gtv(key='admin_method_output_rate_percent'),
            keyboard_type=KeyboardType.NUMBER,
            value=value_to_float(value=self.method.output_rate_percent, decimal=self.currency.rate_decimal),
        )
        self.tf_color = TextField(
            label=await self.client.session.gtv(key='admin_method_color'),
            value=self.method.color,
        )
        self.tf_bgcolor = TextField(
            label=await self.client.session.gtv(key='admin_method_bgcolor'),
            value=self.method.bgcolor,
        )
        self.cb_is_rate_default = Checkbox(
            label=await self.client.session.gtv(key='admin_method_is_rate_default'),
            value=self.method.is_rate_default,
        )
        self.schema_fields = []
        for i, field in enumerate(self.method.schema_fields):
            column = deepcopy(self.schema)
            column.controls[1].value = field['key']
            column.controls[2].value = field['name']
            column.controls[3].options = deepcopy(self.schema_type_options)
            column.controls[3].value = field['type']
            column.controls[4].value = field['optional']
            self.schema_fields.append(column)
        self.schema_input_fields = []
        for i, field in enumerate(self.method.schema_input_fields):
            column = deepcopy(self.schema)
            column.controls[1].value = field['key']
            column.controls[2].value = field['name']
            column.controls[3].options = deepcopy(self.schema_input_type_options)
            column.controls[3].value = field['type']
            column.controls[4].value = field['optional']
            self.schema_input_fields.append(column)
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
                        self.dd_currency,
                        self.tf_name,
                        self.tf_input_rate_default,
                        self.tf_output_rate_default,
                        self.tf_input_rate_percent,
                        self.tf_output_rate_percent,
                        self.tf_color,
                        self.tf_bgcolor,
                        self.cb_is_rate_default,
                        Row(controls=[
                            Text(
                                value=await self.client.session.gtv(key="admin_method_schema_fields"),
                                size=24,
                                font_family=Fonts.MEDIUM,
                                color=colors.ON_BACKGROUND,
                            ),
                            StandardButton(
                                content=Text(value=await self.client.session.gtv(key='add_line')),
                                on_click=self.schema_fields_add_line,
                            ),
                            StandardButton(
                                content=Text(value=await self.client.session.gtv(key='remove_line')),
                                on_click=self.schema_fields_remove_line,
                            ),
                        ]),
                        Column(controls=self.schema_fields),
                        Row(controls=[
                            Text(
                                value=await self.client.session.gtv(key="admin_method_input_schema_fields"),
                                size=24,
                                font_family=Fonts.MEDIUM,
                                color=colors.ON_BACKGROUND,
                            ),
                            StandardButton(
                                content=Text(value=await self.client.session.gtv(key='add_line')),
                                on_click=self.schema_input_fields_add_line,
                            ),
                            StandardButton(
                                content=Text(value=await self.client.session.gtv(key='remove_line')),
                                on_click=self.schema_input_fields_remove_line,
                            ),
                        ]),
                        Column(controls=self.schema_input_fields),
                        Row(controls=[
                            StandardButton(
                                content=Text(value=await self.client.session.gtv(key='save')),
                                on_click=self.update_method,
                                expand=True,
                            ),
                            StandardButton(
                                content=Text(value=await self.client.session.gtv(key='delete')),
                                on_click=self.delete_method,
                                expand=True,
                            ),
                        ]),
                    ],
                ),
            ],
        )

    async def delete_method(self, _):
        await self.client.session.api.admin.methods.delete(id_=self.method_id)
        await self.client.change_view(go_back=True, with_restart=True)

    async def schema_fields_add_line(self, _):
        column = deepcopy(self.schema)
        column.controls[3].options = deepcopy(self.schema_type_options)
        self.schema_fields.append(column)
        await self.update_async()

    async def schema_fields_remove_line(self, _):
        self.schema_fields.pop()
        await self.update_async()

    async def schema_input_fields_add_line(self, _):
        column = deepcopy(self.schema)
        column.controls[3].options = deepcopy(self.schema_input_type_options)
        self.schema_input_fields.append(column)
        await self.update_async()

    async def schema_input_fields_remove_line(self, _):
        self.schema_input_fields.pop()
        await self.update_async()

    async def update_method(self, _):
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
            custom_field_list = [
                ('input_rate_default', self.tf_input_rate_default, self.method.input_rate_default),
                ('output_rate_default', self.tf_output_rate_default, self.method.output_rate_default),
                ('input_rate_percent', self.tf_input_rate_percent, self.method.input_rate_percent),
                ('output_rate_percent', self.tf_output_rate_percent, self.method.output_rate_percent),
            ]
            updates = {
                'fields': fields,
                'input_fields': input_fields,
            }
            if self.method.currency.id_str.lower() != self.dd_currency.value.lower():
                updates['currency'] = self.dd_currency.value
            if await self.client.session.gtv(key=self.method.name_text) != self.tf_name.value:
                updates['name'] = self.tf_name.value
            if self.method.color != self.tf_color.value:
                updates['color'] = self.tf_color.value
            if self.method.bgcolor != self.tf_bgcolor.value:
                updates['bgcolor'] = self.tf_bgcolor.value
            if self.method.is_rate_default != self.cb_is_rate_default.value:
                updates['is_rate_default'] = self.cb_is_rate_default.value
            for field_key, field, model_value in custom_field_list:
                if not await Error.check_field(self, field=field, check_float=True):
                    return
                field_value = value_to_int(value=field.value, decimal=self.currency.rate_decimal)
                if model_value == field_value:
                    continue
                updates[field_key] = field_value
            await self.client.session.api.admin.methods.update(
                id_=self.method_id,
                **updates,
            )
            await self.client.session.get_text_pack()
            await self.set_type(loading=False)
            self.snack_bar.open = True
            await self.update_async()
        except ApiException as exception:
            await self.set_type(loading=False)
            return await self.client.session.error(exception=exception)
