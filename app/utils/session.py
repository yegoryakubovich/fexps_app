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


import asyncio
import logging
from typing import Any

from flet_core import Page
from flet_manager.utils import Client

from app.utils import Icons
from app.utils.registration import Registration
from app.utils.value import value_replace
from config import settings
from fexps_api_client import FexpsApiClient
from fexps_api_client.utils import ApiException


class Session:
    client: Client
    page: Page
    tokens: list[str]
    token: str | None
    language: str | None
    text_pack_id: int | None
    text_pack_language: str | None
    text_pack: dict | None
    api: FexpsApiClient | None
    registration: Registration
    current_wallet: None
    wallets: list | None
    debug: bool
    bs_error: Any
    bs_info: Any
    datepicker: Any
    filepicker: Any
    answers: dict | None

    def __init__(self, client: Client):
        self.client = client
        self.page = client.page
        self.accounts: list[dict] = []
        self.account = None
        self.timezone = None
        self.updater = True

    async def error(self, exception: ApiException):
        title = await self.gtv(key=f'error_{exception.code}', **exception.kwargs)
        await self.bs_error.open_(title=title, icon=Icons.ERROR)

    async def init_bs(self):
        from app.controls.information.bottom_sheet import BottomSheet
        from app.controls.input.file_picker import FilePicker
        from app.controls.input.date_picker import DatePicker
        self.bs_error = BottomSheet()
        self.bs_info = BottomSheet()
        self.filepicker = FilePicker()
        self.datepicker = DatePicker()

        self.page.overlay.clear()
        self.page.overlay.append(self.bs_error)
        self.page.overlay.append(self.bs_info)
        self.page.overlay.append(self.filepicker)
        self.page.overlay.append(self.datepicker)
        await self.page.update_async()

    async def change_account(
            self,
            change_view: callable,
            account_id: int = None,
            account_next: bool = False,
    ) -> bool:
        from app.views.auth.init import InitView
        if len(self.accounts) == 1:
            return False
        if account_id:
            if account_id == self.account.id:
                return False
            for account_dict in self.accounts:
                if account_id != account_dict['id']:
                    continue
                await self.set_cs(key='token', value=account_dict['token'])
        elif account_next:
            i = None
            for i, account_dict in enumerate(self.accounts):
                if self.account.id != account_dict['id']:
                    continue
                i = i
                break
            i += 1
            if i >= len(self.accounts):
                i -= len(self.accounts)
            await self.set_cs(key='token', value=self.accounts[i]['token'])
        await self.set_cs(key='current_wallet', value=None)
        await change_view(view=InitView(), delete_current=True)

    async def init(self):
        self.token = await self.get_cs(key='token')
        self.accounts = await self.get_cs(key='accounts') or []
        self.language = await self.get_cs(key='language')
        self.text_pack = await self.get_cs(key='text_pack')
        self.current_wallet = await self.get_cs(key='current_wallet')
        self.api = FexpsApiClient(url=settings.get_url(), token=self.token)
        asyncio.create_task(self.start_updater())
        try:
            self.account = await self.api.client.accounts.get()
            account_index = None
            for account_dict in self.accounts:
                if account_dict['id'] != self.account.id:
                    continue
                account_index = self.accounts.index(account_dict)
                break
            current_account_dict = {'id': self.account.id, 'username': self.account.username, 'token': self.token}
            if account_index is None:
                self.accounts.append(current_account_dict)
            else:
                self.accounts[account_index] = current_account_dict
            await self.set_cs(key='accounts', value=self.accounts)
            self.timezone = await self.api.client.timezones.get(id_str=self.account.timezone)
            self.api = FexpsApiClient(url=settings.get_url(), token=self.token, deviation=self.timezone.deviation)
            if self.language != self.account.language:
                await self.set_cs(key='language', value=self.language)
            self.wallets = await self.api.client.wallets.get_list()
            if not self.current_wallet:
                self.current_wallet = self.wallets[0]
                await self.set_cs(key='current_wallet', value=self.current_wallet)
            self.debug = await self.get_cs(key='debug')
            if not self.debug:
                await self.set_cs(key='debug', value=False)
                self.debug = False
        except ApiException:
            await self.set_cs(key='token', value=None)
            await self.set_cs(key='current_wallet', value=None)
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
        while True:
            try:
                await self.page.client_storage.set_async(key=f'fexps.{key}', value=value)
                break
            except:
                pass

    # Texts
    async def get_text_value(self, key):
        if key:
            return self.text_pack.get(key, f'404 {key}')
        else:
            return None

    async def gtv(self, key, **kwargs):
        return value_replace(await self.get_text_value(key=key), **kwargs)

    async def get_text_pack(self, language: str = None):
        if not language:
            language = self.language
        self.text_pack = await self.api.client.texts.packs.get(language=language)
        await self.set_cs(key='text_pack', value=self.text_pack)

    async def start_updater(self):
        from app.utils.updater.views.main import check_update_main_view
        from app.utils.updater.views.request import check_update_request_view
        from app.utils.updater.views.request.order import check_update_request_order_view
        from app.utils.updater.views.requisite import check_update_requisite_view
        from app.utils.updater.views.requisite.order import check_update_requisite_order_view

        from app.views.client.requests import RequestView
        from app.views.client.requests.orders import RequestOrderView
        from app.views.client.requisites import RequisiteView
        from app.views.client.requisites.orders import RequisiteOrderView
        from app.views.main.main import MainView

        await asyncio.sleep(3)
        self.page.on_disconnect = self.on_disconnect
        methods = [
            (MainView, check_update_main_view),
            (RequestView, check_update_request_view),
            (RequestOrderView, check_update_request_order_view),
            (RequisiteView, check_update_requisite_view),
            (RequisiteOrderView, check_update_requisite_order_view),
        ]
        while self.updater:
            last_view = self.page.views[-1]
            for type_, func in methods:
                if not isinstance(last_view, type_):
                    continue
                # await func(view=last_view)
                try:
                    await func(view=last_view)
                except Exception as exception:
                    logging.critical(f'Updater pass {type_} | {exception}')
            await asyncio.sleep(settings.update_interval)

    async def on_disconnect(self, _):
        self.updater = False
