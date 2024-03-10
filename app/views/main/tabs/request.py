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


from flet_core import Column, Container, ControlEvent, colors

from app.controls.information.home.scope_row import HomeScopeRow
from app.controls.information.request.history_row import RequestHistoryChip, RequestHistoryRow, RequestInfo
from app.views.main.tabs.base import BaseTab
from config import settings


class Chips:
    is_input = 'is_input'
    is_output = 'is_output'
    is_all = 'is_all'
    is_finish = 'is_finish'


class RequestTab(BaseTab):
    exercise: list[dict] = None
    scopes: list[dict]
    is_input: bool
    is_output: bool
    is_all: bool
    is_finish: bool

    async def get_scope_row(self):
        self.scopes = [
            dict(
                name=await self.client.session.gtv(key=f'request_create'),
                on_click=self.go_create,
            ),
            dict(
                name=await self.client.session.gtv(key=f'request_test'),
            ),
        ]
        return HomeScopeRow(scopes=self.scopes)

    async def get_history(self):
        self.filter_chips = [
            RequestHistoryChip(
                name=await self.client.session.gtv(key=f'chip_{Chips.is_input}'),
                key=Chips.is_input,
                on_select=self.chip_select,
                selected=self.is_input,
            ),
            RequestHistoryChip(
                name=await self.client.session.gtv(key=f'chip_{Chips.is_output}'),
                key=Chips.is_output,
                on_select=self.chip_select,
                selected=self.is_output,
            ),
            RequestHistoryChip(
                name=await self.client.session.gtv(key=f'chip_{Chips.is_all}'),
                key=Chips.is_all,
                on_select=self.chip_select,
                selected=self.is_all,
            ),
            RequestHistoryChip(
                name=await self.client.session.gtv(key=f'chip_{Chips.is_finish}'),
                key=Chips.is_finish,
                on_select=self.chip_select,
                selected=self.is_finish,
            ),
        ]
        requests = await self.client.session.api.client.request.search(
            is_input=self.is_input,
            is_output=self.is_output,
            is_all=self.is_all,
            is_finish=self.is_finish,
            page=1,
        )
        requests_list: list[RequestInfo] = []
        for request in requests.requests:
            color, value = None, None
            if request.type == 'input':
                color, value = colors.GREEN, request.input_value / settings.default_decimal
            elif request.type == 'output':
                color, value = colors.RED, request.output_value / settings.default_decimal
            elif request.type == 'all':

                # input_method = await self.client.session.api.client.methods.get(id_=request.input_method)
                # output_method = await self.client.session.api.client.methods.get(id_=request.output_method)
                # input_currency = await self.client.session.api.client.currencies.get(id_str=input_method.currency)
                # output_currency = await self.client.session.api.client.currencies.get(id_str=output_method.currency)
                # input_value = request.input_currency_value * (10 ** input_currency.decimal)
                # output_value = request.output_currency_value * (10 ** output_currency.decimal)
                color, value = colors.GREY, f'{0} -> {0}'
            requests_list.append(RequestInfo(
                type_=await self.client.session.gtv(key=f'request_type_{request.type}'),
                state=await self.client.session.gtv(key=f'request_state_{request.state}'),
                value=value,
                color=color,
                date=request.date,
            ))

        return RequestHistoryRow(
            title_text=await self.client.session.gtv(key='transaction_history'),
            filter_chips=self.filter_chips,
            requests_list=requests_list,
        )

    async def build(self):
        self.is_input, self.is_output, self.is_all, self.is_finish = True, True, True, False
        self.client.session.wallets = await self.client.session.api.client.wallets.get_list()
        self.client.session.current_wallet = await self.client.session.api.client.wallets.get(
            id_=self.client.session.current_wallet.id,
        )
        self.controls = [
            Container(
                content=Column(
                    controls=[
                        await self.get_scope_row(),
                        await self.get_history(),
                    ],
                ),
                padding=10,
            ),
        ]

    async def go_create(self, _):
        from app.views.client.requests import RequestCreateView
        await self.client.change_view(view=RequestCreateView(current_wallet=self.client.session.current_wallet))

    async def chip_select(self, event: ControlEvent):
        if event.control.key == Chips.is_input:
            self.is_input = True if event.data == 'true' else False
        elif event.control.key == Chips.is_output:
            self.is_output = True if event.data == 'true' else False
        elif event.control.key == Chips.is_all:
            self.is_all = True if event.data == 'true' else False
        elif event.control.key == Chips.is_finish:
            self.is_finish = True if event.data == 'true' else False
        self.controls[0].content.controls[1] = await self.get_history()
        await self.update_async()
