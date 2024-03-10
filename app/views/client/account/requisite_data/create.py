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

from flet_core import Column, ControlEvent, KeyboardType
from flet_core.dropdown import Option

from app.controls.button import FilledButton
from app.controls.information import Text
from app.controls.input import TextField, Dropdown
from app.controls.layout import AdminBaseView
from app.utils import Fonts
from app.views.client.account.requisite_data.get import RequisiteDataView
from fexps_api_client.utils import ApiException


class RequisiteDataCreateView(AdminBaseView):
    route = '/admin/text/create'
    methods: list
    method: dict

    optional: Column
    tf_name: TextField
    dd_currency: Dropdown
    dd_method: Dropdown
    fields: dict
    fields_keys: dict

    async def build(self):
        self.fields, self.fields_keys = {}, {}
        self.methods = await self.client.session.api.client.methods.get_list()

        currency_options = [Option(
            text=currency.id_str.upper(),
            key=currency.id_str,
        ) for currency in await self.client.session.api.client.currencies.get_list()]
        method_options = []

        self.tf_name = TextField(label=await self.client.session.gtv(key='name'))
        self.dd_currency = Dropdown(
            label=await self.client.session.gtv(key='currency'),
            options=currency_options,
            on_change=self.change_currency,
        )
        self.dd_method = Dropdown(
            label=await self.client.session.gtv(key='method'),
            options=method_options,
            on_change=self.change_method,
        )
        self.optional = Column(controls=[])

        self.controls = await self.get_controls(
            title=await self.client.session.gtv(key='requisite_data_create_view_title'),
            main_section_controls=[
                self.tf_name,
                self.dd_currency,
                self.dd_method,
                self.optional,
                FilledButton(
                    content=Text(
                        value=await self.client.session.gtv(key='create'),
                        size=15,
                        font_family=Fonts.REGULAR,
                    ),
                    on_click=self.create_text,
                ),
            ],
        )

    async def change_currency(self, event: ControlEvent):
        method_options = []
        for method in self.methods:
            if method.currency.lower() != event.data.lower():
                continue
            name = await self.client.session.gtv(key=method.name_text)
            method_options.append(Option(
                text=f'{name} ({method.id})',
                key=method.id,
            ))
        self.dd_method.options = method_options
        self.optional.controls = []
        await self.update_async()

    async def change_method(self, event: ControlEvent):
        self.method = await self.client.session.api.client.methods.get(id_=event.data)

        controls = []
        for field in self.method['schema_fields']:
            type_ = await self.client.session.gtv(key=f'method_type_{field["type"]}')
            name_list = [
                await self.client.session.gtv(key=field[f'name_text_key']),
                f'({type_})',
            ]
            if not field['optional']:
                name_list.append('*')
            controls.append(TextField(
                label=' '.join(name_list),
                on_change=self.change_fields,
                keyboard_type=KeyboardType.NUMBER if type_ == 'int' else None,
            ))
            self.fields_keys[' '.join(name_list)] = field['key']
        self.optional.controls = controls
        await self.update_async()

    async def change_fields(self, event: ControlEvent):
        self.fields[self.fields_keys[event.control.label]] = event.data

    async def create_text(self, _):
        await self.set_type(loading=True)
        for field in self.method['schema_fields']:
            if not self.fields.get(field['key']):
                continue
            if field['type'] == 'int':
                self.fields[field['key']] = int(self.fields.get(field['key']))

        try:
            requisite_data_id = await self.client.session.api.client.requisite_data.create(
                name=self.tf_name.value,
                method_id=self.dd_method.value,
                fields=self.fields,
            )
            await self.set_type(loading=False)
            await self.client.change_view(
                view=RequisiteDataView(requisite_data_id=requisite_data_id),
                delete_current=True,
            )
        except ApiException as exception:
            await self.set_type(loading=False)
            logging.critical(exception.code)
            logging.critical(exception.kwargs)
            return await self.client.session.error(exception=exception)
