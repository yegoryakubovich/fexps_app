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


from flet_core import ScrollMode, Row
from flet_core.dropdown import Option

from app.controls.button import FilledButton, StandardButton
from app.controls.information import Text
from app.controls.input import Dropdown, TextField
from app.controls.layout import AuthView
from app.utils import Error
from app.views.auth.signup.agreement import AgreementRegistrationView


class RegistrationSecondView(AuthView):
    dd_country: Dropdown
    tf_firstname: TextField
    tf_lastname: TextField
    tf_surname: TextField
    countries = list[dict]

    def __init__(self, **kwargs):
        super().__init__(**kwargs, scroll=ScrollMode.AUTO)

    async def build(self):
        await self.set_type(loading=True)
        self.countries = await self.client.session.api.client.countries.get_list()
        await self.set_type(loading=False)
        country_options = [
            Option(
                text=country.name,
                key=country.id_str,
            ) for country in self.countries
        ]
        self.tf_firstname, self.tf_lastname, self.tf_surname = [
            TextField(
                label=await self.client.session.gtv(key=key),
            )
            for key in ['firstname', 'lastname', 'surname']
        ]
        self.dd_country = Dropdown(
            label=await self.client.session.gtv(key='country'),
            options=country_options,
            value=country_options[0].key,
        )
        self.controls = await self.get_controls(
            title=await self.client.session.gtv(key='registration_account_create_view_title'),
            controls=[
                self.tf_firstname,
                self.tf_lastname,
                self.tf_surname,
                self.dd_country,
                Row(
                    controls=[
                        StandardButton(
                            content=Text(
                                value=await self.client.session.gtv(key='next_step'),
                                size=16,
                            ),
                            on_click=self.change_view,
                            expand=True,
                        ),
                    ]
                ),
            ],
        )

    async def change_view(self, _):
        await self.set_type(loading=True)
        fields = [(self.tf_firstname, 2, 32), (self.tf_lastname, 2, 32)]
        for field, min_len, max_len in fields:
            if not await Error.check_field(self, field, min_len=min_len, max_len=max_len):
                await self.set_type(loading=False)
                return
        if self.tf_surname.value and (len(self.tf_surname.value) < 2 or len(self.tf_surname.value) > 32):
            self.tf_surname.error_text = await self.client.session.gtv(key='error_count_letter')
            await self.set_type(loading=False)
            await self.update_async()

        country = await self.client.session.api.client.countries.get(
            id_str=self.dd_country.value
        )

        self.client.session.registration.firstname = self.tf_firstname.value
        self.client.session.registration.lastname = self.tf_lastname.value
        self.client.session.registration.surname = self.tf_surname.value
        self.client.session.registration.country = self.dd_country.value
        self.client.session.registration.currency = country['currency']
        self.client.session.registration.timezone = country['timezone']
        await self.set_type(loading=False)
        await self.client.change_view(view=AgreementRegistrationView(), delete_current=True)
