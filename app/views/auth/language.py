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


from flet_core import Row, ScrollMode
from flet_core.dropdown import Option

from app.controls.button import StandardButton
from app.controls.information import Text
from app.controls.input import Dropdown
from app.controls.layout import AuthView
from config import settings


class LanguageView(AuthView):
    dd_language: Dropdown
    languages: list
    is_go_back: bool

    def __init__(self, go_back: bool = False):
        super().__init__()
        self.is_go_back = go_back

    async def construct(self):
        self.languages = await self.client.session.api.client.languages.get_list()
        await self.client.session.get_text_pack(language=settings.language_default)
        options = [
            Option(
                text=language.get('name'),
                key=language.get('id_str'),
            ) for language in self.languages
        ]
        language_value = None
        for language in self.languages:
            if not language.get('is_default'):
                continue
            language_value = language.get('id_str')
        self.dd_language = Dropdown(
            label=await self.client.session.gtv(key='language'),
            options=options,
            value=language_value,
        )
        self.scroll = ScrollMode.AUTO
        self.controls = await self.get_controls(
            title=await self.client.session.gtv(key='set_language_view_title'),
            go_back=self.is_go_back,
            controls=[
                self.dd_language,
                Row(
                    controls=[
                        StandardButton(
                            content=Text(
                                value=await self.client.session.gtv(key='next'),
                                size=settings.get_font_size(multiple=1.5),
                            ),
                            on_click=self.select,
                            horizontal=54,
                            expand=True,
                        ),
                    ]
                ),
            ],
        )

    async def select(self, _=None):
        language = self.dd_language.value
        # If user not selected language
        if not language:
            self.dd_language.error_text = await self.client.session.gtv(key='error_language_select')
            await self.update_async()
            return
        await self.client.session.set_cs(key='language', value=language)
        await self.client.session.get_text_pack(language=language)
        from .init import InitView
        await self.client.change_view(view=InitView(), delete_current=True)
