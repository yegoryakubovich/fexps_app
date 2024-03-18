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
from typing import Any

from flet_core import Page
from flet_manager.utils import Client

from app.utils import Icons
from app.utils.registration import Registration
from config import settings
from fexps_api_client import FexpsApiClient
from fexps_api_client.utils import ApiException


class Session:
    client: Client
    page: Page
    token: str | None
    language: str | None
    text_pack_id: int | None
    text_pack_language: str | None
    text_pack: dict | None
    api: FexpsApiClient
    registration: Registration
    current_wallet: None
    wallets: list | None
    bs_error: Any
    bs_info: Any
    datepicker: Any
    filepicker: Any
    answers: dict | None

    def __init__(self, client: Client):
        self.client = client
        self.page = client.page
        self.account = None

    async def error(self, exception: ApiException):
        title = await self.client.session.gtv(key=f'error_{exception.code}')
        await self.bs_error.open_(
            title=title.format(**exception.kwargs),
            icon=Icons.ERROR,
        )

    async def init_bs(self):
        from app.controls.information.bottom_sheet import BottomSheet
        from app.controls.input.file_picker import FilePicker
        from app.controls.input.date_picker import DatePicker
        self.bs_error = BottomSheet()
        self.bs_info = BottomSheet()
        self.filepicker = FilePicker()
        self.datepicker = DatePicker()

        self.page.overlay.append(self.bs_error)
        self.page.overlay.append(self.bs_info)
        self.page.overlay.append(self.filepicker)
        self.page.overlay.append(self.datepicker)
        await self.page.update_async()

    async def init(self):
        self.token = await self.get_cs(key='token')
        self.language = await self.get_cs(key='language')
        self.text_pack = await self.get_cs(key='text_pack')

        self.api = FexpsApiClient(url=settings.url, token=self.token)
        try:
            self.account = await self.api.client.accounts.get()
            self.language = self.account.language
            if self.language != self.account.language:
                await self.set_cs(key='language', value=self.language)
            self.wallets = await self.api.client.wallets.get_list()
            if not self.wallets:
                await self.api.client.wallets.create(name='Default')
                self.wallets = await self.api.client.wallets.get_list()
            logging.critical(self.wallets)
            self.current_wallet = self.wallets[0]
        except ApiException:
            await self.set_cs(key='token', value=None)
            self.token = None
        await self.init_bs()

    # Client storage
    async def get_cs(self, key: str) -> Any:
        try:
            value = await self.page.client_storage.get_async(key=f'fexps.{key}')
            if value == 'null':
                value = None
            return value
        except RecursionError:
            return None

    async def set_cs(self, key: str, value: Any) -> None:
        if value is None:
            value = 'null'
        return await self.page.client_storage.set_async(key=f'fexps.{key}', value=value)

    # Texts
    async def get_text_value(self, key):
        if key:
            return self.text_pack.get(key, f'404 {key}')
        else:
            return None

    async def gtv(self, key):
        return await self.get_text_value(key=key)

    async def get_text_pack(self, language: str = None):
        if not language:
            language = self.language
        self.text_pack = await self.api.client.texts.packs.get(language=language)
        await self.set_cs(key='text_pack', value=self.text_pack)
