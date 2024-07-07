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

from app.controls.input import Dropdown, TextField
from config import settings
from fexps_api_client.utils import ApiException

from app.controls.button import StandardButton
from app.controls.information import Text
from app.controls.information.snack_bar import SnackBar
from app.controls.layout import AdminBaseView


class CountryView(AdminBaseView):
    route = '/admin/country/get'
    country = dict
    languages = list[dict]
    timezones = list[dict]
    currencies = list[dict]
    tf_name = TextField
    dd_language = Dropdown
    dd_timezone = Dropdown
    dd_currency = Dropdown
    snack_bar = SnackBar

    def __init__(self, country_id_str):
        super().__init__()
        self.country_id_str = country_id_str

    async def construct(self):
        await self.set_type(loading=True)
        self.country = await self.client.session.api.client.countries.get(
            id_str=self.country_id_str,
        )
        self.languages = await self.client.session.api.client.languages.get_list()
        self.timezones = await self.client.session.api.client.timezones.get_list()
        self.currencies = await self.client.session.api.client.currencies.get_list()
        await self.set_type(loading=False)

        language_options = [
            Option(
                text=language.get('name'),
                key=language.get('id_str'),
            ) for language in self.languages
        ]
        timezone_options = [
            Option(
                text=timezone.get('id_str'),
                key=timezone.get('id_str'),
            ) for timezone in self.timezones
        ]
        currency_options = [
            Option(
                text=currency.get('name_text'),
                key=currency.get('id_str'),
            ) for currency in self.currencies
        ]

        self.snack_bar = SnackBar(
            content=Text(
                value=await self.client.session.gtv(key='successful'),
            ),
        )
        self.tf_name = TextField(
            label=await self.client.session.gtv(key='name'),
            value=self.country['name'],
        )
        self.dd_language = Dropdown(
            label=await self.client.session.gtv(key='language'),
            value=self.country['language'],
            options=language_options,
        )
        self.dd_timezone = Dropdown(
            label=await self.client.session.gtv(key='timezone'),
            value=self.country['timezone'],
            options=timezone_options,
        )
        self.dd_currency = Dropdown(
            label=await self.client.session.gtv(key='currency'),
            value=self.country['currency'],
            options=currency_options,
        )
        self.scroll = ScrollMode.AUTO
        self.controls = await self.get_controls(
            title=self.country['name'],
            main_section_controls=[
                self.tf_name,
                self.dd_language,
                self.dd_currency,
                self.dd_timezone,
                self.snack_bar,
                Row(
                    controls=[
                        StandardButton(
                            content=Text(
                                value=await self.client.session.gtv(key='save'),
                                size=settings.get_font_size(multiple=1.5),
                            ),
                            on_click=self.update_country,
                            expand=True,
                        ),
                        StandardButton(
                            content=Text(
                                value=await self.client.session.gtv(key='delete'),
                                size=settings.get_font_size(multiple=1.5),
                            ),
                            on_click=self.delete_country,
                            expand=True,
                        ),
                    ],
                ),
            ],
        )

    async def delete_country(self, _):
        await self.client.session.api.admin.countries.delete(
            id_str=self.country_id_str,
        )
        await self.client.change_view(go_back=True, with_restart=True)

    async def update_country(self, _):
        await self.set_type(loading=True)
        try:
            await self.client.session.api.admin.countries.update(
                id_str=self.country_id_str,
                name=self.tf_name.value,
                language_default=self.dd_language.value,
                currency_default=self.dd_currency.value,
                timezone_default=self.dd_timezone.value,
            )
            await self.set_type(loading=False)
            self.snack_bar.open = True
            await self.update_async()
        except ApiException as exception:
            await self.set_type(loading=False)
            return await self.client.session.error(exception=exception)
