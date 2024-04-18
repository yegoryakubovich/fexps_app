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


from flet_core import Row
from fexps_api_client.utils import ApiException

from app.controls.button import StandardButton
from app.controls.information import Text
from app.controls.information.snack_bar import SnackBar
from app.controls.input import TextField
from app.controls.layout import AdminBaseView
from app.utils import Error


class TextTranslationView(AdminBaseView):
    route = '/admin/text/translation/get'
    tf_value = TextField
    snack_bar: SnackBar

    def __init__(self, language, text_key):
        super().__init__()
        self.text_key = text_key
        self.language = language

    async def construct(self):
        self.snack_bar = SnackBar(
            content=Text(
                value=await self.client.session.gtv(key='successful'),
            ),
        )
        self.tf_value = TextField(
            label=await self.client.session.gtv(key='translation'),
            value=self.language['value']
        )
        self.controls = await self.get_controls(
            title=self.language['language'],
            main_section_controls=[
                self.tf_value,
                self.snack_bar,
                Row(
                    controls=[
                        StandardButton(
                            content=Text(
                                value=await self.client.session.gtv(key='save'),
                            ),
                            on_click=self.update_translation,
                            expand=True,
                        ),
                        StandardButton(
                            content=Text(
                                value=await self.client.session.gtv(key='delete'),
                            ),
                            on_click=self.delete_translation,
                            expand=True,
                        ),
                    ],
                ),
            ],
         )

    async def delete_translation(self, _):
        await self.client.session.api.admin.texts.translations.delete(
            text_key=self.text_key,
            language=self.language['language'],
        )
        await self.client.change_view(go_back=True, with_restart=True)

    async def update_translation(self, _):
        await self.set_type(loading=True)
        fields = [(self.tf_value, 1, 1024)]
        for field, min_len, max_len in fields:
            if not await Error.check_field(self, field, min_len=min_len, max_len=max_len):
                await self.set_type(loading=False)
                return
        try:
            await self.client.session.api.admin.texts.translations.update(
                text_key=self.text_key,
                language=self.language['language'],
                value=self.tf_value.value,
            )
            await self.client.session.get_text_pack()
            await self.set_type(loading=False)
            self.snack_bar.open = True
            await self.update_async()
        except ApiException as exception:
            await self.set_type(loading=False)
            return await self.client.session.error(exception=exception)
