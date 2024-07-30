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

from app.utils.updater import update_check
from app.utils.updater.schemes import get_request_list_scheme
from app.views.main.tabs import RequestTab


class Chips:
    ACTIVE = 'active'
    COMPLETED = 'completed'
    CANCELED = 'canceled'
    ALL = 'all'
    PARTNERS = 'partners'


async def check_update_main_request_view(view: RequestTab, update: bool = True):
    # current_requests
    current_requests = await view.client.session.api.client.requests.search(is_active=True)
    if update_check(scheme=get_request_list_scheme, obj_1=view.currently_request, obj_2=current_requests.requests):
        view.currently_request = current_requests.requests
        await view.update_currently_request_row(update=update)
    if update:
        await view.currently_request_row.update_async()
    # history_requests
    history_requests = await view.client.session.api.client.requests.search(
        id_=view.search_value,
        is_active=view.selected_chip in [Chips.ACTIVE, Chips.ALL],
        is_completed=view.selected_chip in [Chips.COMPLETED, Chips.ALL],
        is_canceled=view.selected_chip in [Chips.CANCELED, Chips.ALL],
        is_partner=view.partner_chip,
        page=view.page_request,
    )
    if update_check(scheme=get_request_list_scheme, obj_1=view.history_requests, obj_2=history_requests.requests):
        view.history_requests = history_requests.requests
        view.total_pages = history_requests.pages
        await view.update_history_requests_column(update=update)
    if update:
        await view.history_requests_column.update_async()
