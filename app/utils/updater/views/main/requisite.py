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
from app.utils.updater.schemes import get_order_list_scheme, get_requisite_list_scheme
from app.views.main.tabs import RequisiteTab


class TypeChips:
    INPUT = 'input'
    OUTPUT = 'output'
    ALL = 'all'


class StateChips:
    ENABLE = 'enable'
    STOP = 'stop'
    DISABLE = 'disable'
    ALL = 'all'


async def check_update_main_requisite_view(view: RequisiteTab, update: bool = True):
    check_list = []
    # currency_orders
    currency_orders = await view.client.session.api.client.orders.list_get.main(
        by_request=False,
        by_requisite=True,
        is_active=True,
        is_finished=False,
    )
    check_list += [
        update_check(
            scheme=get_order_list_scheme,
            obj_1=view.currency_orders,
            obj_2=currency_orders,
        ),
    ]
    # history_requisites
    history_requisites = await view.client.session.api.client.requisites.search(
        is_type_input=view.selected_type_chip in [TypeChips.INPUT, TypeChips.ALL],
        is_type_output=view.selected_type_chip in [TypeChips.OUTPUT, TypeChips.ALL],
        is_state_enable=view.selected_state_chip in [StateChips.ENABLE, StateChips.ALL],
        is_state_stop=view.selected_state_chip in [StateChips.STOP, StateChips.ALL],
        is_state_disable=view.selected_state_chip in [StateChips.DISABLE, StateChips.ALL],
        page=view.page_requisites,
    )
    check_list += [
        update_check(
            scheme=get_requisite_list_scheme,
            obj_1=view.history_requisites_column,
            obj_2=history_requisites.requisites,
        ),
    ]
    if True not in check_list:
        return
    await view.construct()
    if update:
        await view.update_async()
