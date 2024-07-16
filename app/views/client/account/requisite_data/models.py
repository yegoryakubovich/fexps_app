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

from flet_core import Column, Control, Row, ControlEvent
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
    tf_name: TextField
    dd_currency: Dropdown
    dd_method: Dropdown
    fields: dict
    is_disposable: bool

    def __init__(
            self,
            session: Session,
            update_async: callable,
            after_close: callable = None,
            currency_id_str: str = None,
            method_id: int = None,
            is_disposable: bool = False,
    ):
        self.title = ''
        self.session = session
        self.update_async = update_async
        self.after_close = after_close
        self.currency_id_str = currency_id_str
        self.method_id = method_id
        self.is_disposable = is_disposable

    async def construct(self):
        self.title = await self.session.gtv(key='requisite_data_create_view_title')
        self.fields = {}
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
                if self.session.debug:
                    method_str = f'{method_str} ({method.id})'
                method_options += [
                    Option(text=method_str, key=method.id),
                ]
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
            self.tf_name,
        ]
        if not self.currency_id_str:
            self.controls += [
                self.dd_currency,
            ]
        if not self.method_id:
            self.controls += [
                self.dd_method,
            ]
        self.controls += [
            self.optional,
        ]
        self.buttons = [
            Row(
                controls=[
                    StandardButton(
                        content=Text(
                            value=await self.session.gtv(key='create'),
                            size=settings.get_font_size(multiple=1.5),
                            font_family=Fonts.REGULAR,
                        ),
                        on_click=self.create_requisite_data,
                        expand=True,
                    ),
                ],
            )
        ]

    async def change_currency(self, _=None):
        self.currency_id_str = self.dd_currency.value
        method_options = []
        for method in self.methods:
            if method.currency.id_str.lower() != self.dd_currency.value.lower():
                continue
            method_str = await self.session.gtv(key=method.name_text)
            if self.session.debug:
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

    async def change_method(self, _=None):
        self.method = await self.session.api.client.methods.get(id_=self.dd_method.value)
        self.method_id = self.method['id']
        controls = []
        for field in self.method['schema_fields']:
            type_ = field["type"]
            name_list = [await self.session.gtv(key=field[f'name_text_key'])]
            if self.session.debug:
                type_str = await self.session.gtv(key=type_)
                name_list += [f'({type_str})']
            if not field['optional']:
                name_list += ['*']
            controls += [
                TextField(
                    label=' '.join(name_list),
                    on_change=partial(self.change_fields, field['key']),
                ),
            ]
        self.optional.controls = controls
        await self.update_async()

    async def change_fields(self, key: str, event: ControlEvent):
        self.fields[key] = event.data

    async def create_requisite_data(self, _=None):
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
                is_disposable=self.is_disposable,
            )
        except ApiException as exception:
            await self.session.error(exception=exception)
            return
        if self.after_close:
            await self.after_close()
        return True
