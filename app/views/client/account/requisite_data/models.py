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

from flet_core import Column, Control, Row, ControlEvent, KeyboardType
from flet_core.dropdown import Option

from app.controls.button import StandardButton
from app.controls.information import Text
from app.controls.input import TextField, Dropdown
from app.utils import Session, Fonts
from config import settings
from fexps_api_client.utils import ApiException


class RequisiteDataCreateModel:
    controls: list[Control]
    buttons: list[Control]
    requisite_data_id: int = None

    methods = list
    method: dict

    title: str
    optional: Column
    error_field: Text
    tf_name: TextField
    dd_currency: Dropdown
    dd_method: Dropdown
    fields: dict

    def __init__(
            self,
            session: Session,
            update_async: callable,
            after_close: callable = None,
            currency_id_str: str = None,
            method_id: int = None,
    ):
        self.title = ''
        self.session = session
        self.update_async = update_async
        self.after_close = after_close
        self.currency_id_str = currency_id_str
        self.method_id = method_id

    async def construct(self):
        self.title = await self.session.gtv(key='requisite_data_create_view_title')
        self.fields, self.fields_keys = {}, {}
        self.methods = await self.session.api.client.methods.get_list()
        currency_options = [
            Option(text=currency.id_str.upper(), key=currency.id_str)
            for currency in await self.session.api.client.currencies.get_list()
        ]
        method_options = []
        if self.currency_id_str:
            for method in self.methods:
                if method.currency.id_str.lower() != self.currency_id_str.lower():
                    continue
                method_str = await self.session.gtv(key=method.name_text)
                if settings.debug:
                    method_str = f'{method_str} ({method.id})'
                method_options += [
                    Option(text=method_str, key=method.id),
                ]
        self.error_field = Text(value='', size=15, font_family=Fonts.REGULAR)
        self.tf_name = TextField(label=await self.session.gtv(key='name'))
        self.dd_currency = Dropdown(
            label=await self.session.gtv(key='currency'),
            options=currency_options,
            on_change=self.change_currency,
            value=self.currency_id_str,
        )
        self.dd_method = Dropdown(
            label=await self.session.gtv(key='method'),
            options=method_options,
            on_change=self.change_method,
        )
        self.optional = Column(controls=[])
        if self.currency_id_str:
            await self.change_currency('')
        self.controls = [
            self.error_field,
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

    async def change_currency(self, _):
        self.currency_id_str = self.dd_currency.value
        method_options = []
        for method in self.methods:
            if method.currency.id_str.lower() != self.dd_currency.value.lower():
                continue
            method_str = await self.session.gtv(key=method.name_text)
            if settings.debug:
                method_str = f'{method_str} ({method.id})'
            method_options += [
                Option(text=method_str, key=method.id),
            ]
        self.dd_method.change_options(options=method_options)
        self.optional.controls = []
        await self.update_async()
        if self.method_id:
            self.dd_method.value = self.method_id
            self.method_id = None
            await self.change_method('')

    async def change_method(self, _):
        self.method = await self.session.api.client.methods.get(id_=self.dd_method.value)
        self.method_id = self.method['id']
        controls = [
            self.error_field,
        ]
        for field in self.method['schema_fields']:
            type_ = field["type"]
            name_list = [await self.session.gtv(key=field[f'name_text_key'])]
            if settings.debug:
                type_str = await self.session.gtv(key=type_)
                name_list += [f'({type_str})']
            if not field['optional']:
                name_list += ['*']
            controls += [
                TextField(
                    label=' '.join(name_list),
                    on_change=partial(self.change_fields, field['key']),
                    keyboard_type=KeyboardType.NUMBER if type_ == 'int' else None,
                ),
            ]
        self.optional.controls = controls
        await self.update_async()

    async def change_fields(self, key: str, event: ControlEvent):
        self.fields[key] = event.data

    async def create_requisite_data(self, _):
        for field in self.method['schema_fields']:
            if not self.fields.get(field['key']):
                continue
            if field['type'] == 'int':
                self.fields[field['key']] = int(self.fields.get(field['key']))
        try:
            self.requisite_data_id = await self.session.api.client.requisites_datas.create(
                name=self.tf_name.value,
                method_id=int(self.dd_method.value),
                fields=self.fields,
            )
        except ApiException as exception:
            return await self.session.error(exception=exception)
        if self.after_close:
            await self.after_close()
