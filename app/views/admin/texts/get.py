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

from flet_core import Row, Column, ScrollMode
from fexps_api_client.utils import ApiException

from app.controls.button import FilledButton
from app.controls.information import Text
from app.controls.information.card import Card
from app.controls.information.snack_bar import SnackBar
from app.controls.input import TextField
from app.controls.layout import Section, AdminBaseView
from app.utils import Fonts
from .translations.create import TextTranslationCreateView
from .translations.get import TextTranslationView


class TextView(AdminBaseView):
    route = '/admin/text/get'
    text = dict
    tf_key = TextField
    tf_value_default = TextField
    snack_bar: SnackBar

    def __init__(self, key):
        super().__init__()
        self.key = key

    async def build(self):
        await self.set_type(loading=True)
        self.text = await self.client.session.api.admin.texts.get(
            key=self.key
        )
        await self.set_type(loading=False)

        self.snack_bar = SnackBar(
            content=Text(
                value=await self.client.session.gtv(key='successful'),
            ),
        )

        self.tf_key = TextField(
            label=await self.client.session.gtv(key='key'),
            value=self.text['key'],
        )
        self.tf_value_default = TextField(
            label=await self.client.session.gtv(key='value_default'),
            value=self.text['value_default'],
        )
        self.scroll = ScrollMode.AUTO
        self.controls = await self.get_controls(
            title=self.text['value_default'],
            main_section_controls=[
                Column(
                    controls=[
                        self.tf_key,
                        self.tf_value_default,
                        self.snack_bar,
                        Row(
                            controls=[
                                FilledButton(
                                    content=Text(
                                        value=await self.client.session.gtv(key='save'),
                                    ),
                                    on_click=self.update_text,
                                ),
                                FilledButton(
                                    content=Text(
                                        value=await self.client.session.gtv(key='delete'),
                                    ),
                                    on_click=self.delete_text,
                                ),
                            ],
                        ),
                    ],
                ),
            ],
            sections=[
                Section(
                    title=await self.client.session.gtv(key='translation'),
                    on_create_click=self.create_translation,
                    controls=[
                        Card(
                            controls=[
                                Text(
                                    value=language['language'],
                                    size=15,
                                    font_family=Fonts.REGULAR,
                                ),
                                Text(
                                    value=language['value'],
                                    size=10,
                                    font_family=Fonts.MEDIUM,
                                ),
                            ],
                            on_click=partial(self.translation_view, language),
                        )
                        for language in self.text['translations']
                    ],
                ),
            ],
         )

    async def delete_text(self, _):
        await self.client.session.api.admin.texts.delete(
            key=self.text['key'],
        )
        await self.client.change_view(go_back=True, with_restart=True)

    async def update_text(self, _):
        try:
            await self.client.session.api.admin.texts.update(
                key=self.text['key'],
                value_default=self.tf_value_default.value,
                new_key=self.tf_key.value
            )
            self.snack_bar.open = True
            await self.update_async()
        except ApiException as e:
            await self.set_type(loading=False)
            return await self.client.session.error(error=e)

    async def create_translation(self, _):
        await self.client.change_view(view=TextTranslationCreateView(key=self.key))

    async def translation_view(self, language, _):
        text_key = self.text['key']
        await self.client.change_view(TextTranslationView(language=language, text_key=text_key))
