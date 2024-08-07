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


from app.utils.updater import update_check
from app.utils.updater.schemes import get_wallet_list_scheme, get_request_list_scheme, get_transfer_list_scheme, \
    get_wallet_scheme
from app.views.main.tabs import HomeTab


class Chips:
    input = 'input'
    output = 'output'
    all = 'all'


async def check_update_main_home_view(view: HomeTab, update: bool = True):
    # wallets
    wallets = await view.client.session.api.client.wallets.get_list()
    if update_check(scheme=get_wallet_list_scheme, obj_1=view.client.session.wallets, obj_2=wallets):
        view.client.session.wallets = wallets
    # current_wallet
    current_wallet = await view.client.session.api.client.wallets.get(id_=view.client.session.current_wallet['id'])
    if update_check(scheme=get_wallet_scheme, obj_1=view.client.session.current_wallet, obj_2=current_wallet):
        view.client.session.current_wallet = current_wallet
        await view.update_balance_stack(update=update)
    if update:
        await view.balance_stack.update_async()
    # current_requests
    currently_request = await view.client.session.api.client.requests.search(is_active=True)
    if update_check(scheme=get_request_list_scheme, obj_1=view.currently_request, obj_2=currently_request.requests):
        view.currently_request = currently_request.requests
        await view.update_currently_request_row(update=update)
    if update:
        await view.currently_request_row.update_async()
    # transfers
    transfer_history = await view.client.session.api.client.transfers.search(
        wallet_id=view.client.session.current_wallet['id'],
        is_sender=view.selected_chip in [Chips.output, Chips.all],
        is_receiver=view.selected_chip in [Chips.input, Chips.all],
        page=view.page_transfer,
    )
    if update_check(scheme=get_transfer_list_scheme, obj_1=view.transfer_history, obj_2=transfer_history.transfers):
        view.transfer_history = transfer_history.transfers
        await view.update_transfer_history_row(update=update)
    if update:
        await view.transfer_history_row.update_async()
