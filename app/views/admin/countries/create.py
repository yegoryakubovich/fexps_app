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


from flet_core import ScrollMode
from flet_core.dropdown import Option
from fexps_api_client.utils import ApiException

from app.controls.button import StandardButton
from app.controls.information import Text
from app.controls.input import TextField, Dropdown
from app.controls.layout import AdminBaseView
from app.utils import Error


class CountryCreateView(AdminBaseView):
    route = '/admin/country/create'
    tf_name: TextField
    tf_id_str: TextField
    languages = list[dict]
    timezones = list[dict]
    currencies = list[dict]
    dd_language = Dropdown
    dd_timezone = Dropdown
    dd_currency = Dropdown

    async def build(self):
        await self.set_type(loading=True)
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

        self.dd_language = Dropdown(
            label=await self.client.session.gtv(key='language'),
            value=self.languages[0]['id_str'],
            options=language_options,
        )
        self.dd_timezone = Dropdown(
            label=await self.client.session.gtv(key='timezone'),
            value=self.timezones[0]['id_str'],
            options=timezone_options,
        )
        self.dd_currency = Dropdown(
            label=await self.client.session.gtv(key='currency'),
            value=self.currencies[0]['id_str'],
            options=currency_options,
        )
        self.tf_id_str, self.tf_name = [
            TextField(
                label=await self.client.session.gtv(key=key),
            )
            for key in ['key', 'name']
        ]

        self.scroll = ScrollMode.AUTO
        self.controls = await self.get_controls(
            title=await self.client.session.gtv(key='admin_country_create_view_title'),
            main_section_controls=[
                self.tf_id_str,
                self.tf_name,
                self.dd_language,
                self.dd_timezone,
                self.dd_currency,
                StandardButton(
                    content=Text(
                        value=await self.client.session.gtv(key='create'),
                        size=16,
                    ),
                    on_click=self.create_country,
                    expand=True,
                ),
            ],
        )

    async def create_country(self, _):
        await self.set_type(loading=True)
        fields = [(self.tf_id_str, 2, 16), (self.tf_name, 1, 1024)]
        for field, min_len, max_len in fields:
            if not await Error.check_field(self, field, min_len=min_len, max_len=max_len):
                await self.set_type(loading=False)
                return
        try:
            await self.client.session.api.admin.countries.create(
                id_str=self.tf_id_str.value,
                name=self.tf_name.value,
                language=self.dd_language.value,
                timezone=self.dd_timezone.value,
                currency=self.dd_currency.value,
            )
            await self.set_type(loading=False)
            await self.client.change_view(go_back=True, with_restart=True, delete_current=True)
        except ApiException as exception:
            await self.set_type(loading=False)
            return await self.client.session.error(exception=exception)
