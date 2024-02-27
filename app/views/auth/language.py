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


from flet_core.dropdown import Option

from app.controls.button import FilledButton
from app.controls.input import Dropdown
from app.controls.layout import AuthView
from config import settings


class LanguageView(AuthView):
    dropdown: Dropdown
    languages: list
    is_go_back: bool

    async def get_text_pack(self, language: str):
        self.client.session.text_pack = await self.client.session.api.client.texts.packs.get(language=language)
        await self.client.session.set_cs(key='text_pack', value=self.client.session.text_pack)

    def __init__(self, go_back: bool = False):
        super().__init__()
        self.is_go_back = go_back

    async def select(self, _):
        language = self.dropdown.value

        # If user not selected language
        if not language:
            self.dropdown.error_text = await self.client.session.gtv(key='error_language_select')
            await self.update_async()
            await self.dropdown.focus_async()
            return

        await self.client.session.set_cs(key='language', value=language)
        from .init import InitView
        await self.client.change_view(view=InitView())

    async def build(self):
        self.languages = await self.client.session.api.client.languages.get_list()
        await self.get_text_pack(language=settings.language_default)

        options = [
            Option(
                text=language.get('name'),
                key=language.get('id_str'),
            ) for language in self.languages
        ]
        self.dropdown = Dropdown(
            label=await self.client.session.gtv(key='language'),
            options=options,
        )

        self.controls = await self.get_controls(
            title=await self.client.session.gtv(key='set_language_view_title'),
            is_go_back=self.is_go_back,
            controls=[
                self.dropdown,
                FilledButton(
                    text=await self.client.session.gtv(key='next'),
                    on_click=self.select,
                    horizontal_padding=54,
                ),
            ],
        )
