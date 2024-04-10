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


from flet_core import Column, Control, Row, ControlEvent, KeyboardType
from flet_core.dropdown import Option

from app.controls.button import StandardButton
from app.controls.information import Text
from app.controls.input import TextField, Dropdown
from app.utils import Session, Fonts
from fexps_api_client.utils import ApiException


class RequisiteDataCreateModel:
    controls: list[Control]
    buttons: list[Control]
    requisite_data_id: int = None
    height: int = 450

    methods: list
    method: dict

    optional: Column
    tf_name: TextField
    dd_currency: Dropdown
    dd_method: Dropdown
    fields: dict
    fields_keys: dict

    def __init__(
            self,
            session: Session,
            update_async: callable,
            after_clise: callable = None,
            before_clise: callable = None,
    ):
        self.session = session
        self.update_async = update_async
        self.after_clise = after_clise
        self.before_clise = before_clise

    async def build(self):
        self.fields, self.fields_keys = {}, {}
        method_options = []
        self.methods = await self.session.api.client.methods.get_list()
        currency_options = [
            Option(text=currency.id_str.upper(), key=currency.id_str)
            for currency in await self.session.api.client.currencies.get_list()
        ]
        self.tf_name = TextField(label=await self.session.gtv(key='name'))
        self.dd_currency = Dropdown(
            label=await self.session.gtv(key='currency'),
            options=currency_options,
            on_change=self.change_currency,
        )
        self.dd_method = Dropdown(
            label=await self.session.gtv(key='method'),
            options=method_options,
            on_change=self.change_method,
        )
        self.optional = Column(controls=[])
        self.controls = [
            self.tf_name,
            self.dd_currency,
            self.dd_method,
            self.optional,
        ]
        self.buttons = [
            Row(
                controls=[
                    StandardButton(
                        content=Text(
                            value=await self.session.gtv(key='create'),
                            size=15,
                            font_family=Fonts.REGULAR,
                        ),
                        on_click=self.create_requisite_data,
                        expand=True,
                    ),
                ],
            )
        ]

    async def change_currency(self, event: ControlEvent):
        method_options = []
        for method in self.methods:
            if method.currency.lower() != event.data.lower():
                continue
            name = await self.session.gtv(key=method.name_text)
            method_options.append(Option(
                text=f'{name} ({method.id})',
                key=method.id,
            ))
        self.dd_method.options = method_options
        self.optional.controls = []
        await self.update_async()

    async def change_method(self, event: ControlEvent):
        self.method = await self.session.api.client.methods.get(id_=event.data)
        controls = []
        for field in self.method['schema_fields']:
            type_ = field["type"]
            type_str = await self.session.gtv(key=type_)
            name_list = [await self.session.gtv(key=field[f'name_text_key']), f'({type_str})']
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

    async def create_requisite_data(self, _):
        if self.after_clise:
            await self.after_clise()
        for field in self.method['schema_fields']:
            if not self.fields.get(field['key']):
                continue
            if field['type'] == 'int':
                self.fields[field['key']] = int(self.fields.get(field['key']))
        try:
            self.requisite_data_id = await self.session.api.client.requisites_datas.create(
                name=self.tf_name.value,
                method_id=self.dd_method.value,
                fields=self.fields,
            )
        except ApiException as exception:
            return await self.session.error(exception=exception)
        if self.before_clise:
            await self.before_clise()
