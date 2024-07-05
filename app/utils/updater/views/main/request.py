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
from app.utils.updater.schemes import get_request_list_scheme
from app.views.main.tabs import RequestTab


class Chips:
    COMPLETED = 'completed'
    CANCELED = 'canceled'
    ALL = 'all'


async def check_update_main_request_view(view: RequestTab, update: bool = True):
    check_list = []
    # current_requests
    current_requests = await view.client.session.api.client.requests.search()
    check_list += [
        update_check(
            scheme=get_request_list_scheme,
            obj_1=view.current_requests,
            obj_2=current_requests.requests,
        ),
    ]
    # history_requests
    history_requests = await view.client.session.api.client.requests.search(
        is_completed=view.selected_chip in [Chips.COMPLETED, Chips.ALL],
        is_canceled=view.selected_chip in [Chips.CANCELED, Chips.ALL],
        is_partner=view.partner_chip,
        page=view.page_request,
    )
    check_list += [
        update_check(
            scheme=get_request_list_scheme,
            obj_1=view.history_requests,
            obj_2=history_requests.requests,
        ),
    ]
    if True not in check_list:
        return
    await view.construct()
    if update:
        await view.update_async()
