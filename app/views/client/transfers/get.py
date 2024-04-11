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
import logging

from flet_core import Column, colors, Row, MainAxisAlignment, Image, CircleAvatar

from app.controls.information import Text
from app.controls.layout import AdminBaseView
from app.utils import Fonts, Icons
from app.utils.value import value_to_float
from config import settings


class TransferView(AdminBaseView):
    route = '/client/transfers/get'
    transfer = dict

    def __init__(self, transfer_id: int):
        super().__init__()
        self.transfer_id = transfer_id

    async def build(self):
        await self.set_type(loading=True)
        self.transfer = await self.client.session.api.client.transfers.get(id_=self.transfer_id)
        await self.set_type(loading=False)
        logging.critical(self.transfer)
        value = value_to_float(value=self.transfer.value)
        short_name = ''
        if self.transfer.operation == 'send':
            short_name = self.transfer.account_to.short_name
            value = f'- {value}'
        elif self.transfer.operation == 'receive':
            short_name = self.transfer.account_from.short_name
            value = f'+ {value}'
        self.controls = await self.get_controls(
            title=await self.client.session.gtv(key='transfer_view_title'),
            back_with_restart=False,
            main_section_controls=[
                Column(
                    controls=[
                        Row(
                            controls=[
                                Text(
                                    value=self.transfer.date.strftime(settings.datetime_format),
                                    size=18,
                                    font_family=Fonts.SEMIBOLD,
                                    color=colors.ON_PRIMARY,
                                ),
                            ],
                            alignment=MainAxisAlignment.CENTER,
                        ),
                        Row(
                            controls=[
                                Column(
                                    controls=[
                                        CircleAvatar(
                                            content=Image(
                                                src=Icons.ACCOUNT,
                                                color=colors.SECONDARY,
                                            ),
                                            bgcolor=colors.ON_PRIMARY,
                                            radius=38,
                                        ),
                                        Text(
                                            value=short_name.upper(),
                                            font_family=Fonts.SEMIBOLD,
                                            size=30,
                                            color=colors.ON_BACKGROUND,
                                        ),
                                    ],
                                ),
                            ],
                            alignment=MainAxisAlignment.CENTER,
                        ),
                        Row(
                            controls=[
                                Text(
                                    value=value,
                                    size=64,
                                    font_family=Fonts.BOLD,
                                    color=colors.ON_PRIMARY,
                                ),
                            ],
                            alignment=MainAxisAlignment.CENTER,
                        ),
                    ],
                ),
            ],
        )
