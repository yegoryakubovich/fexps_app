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


from app.controls.layout import ClientBaseView
from app.views.client.account.notification.get_link_telegram import AccountNotificationLinkTelegramView
from app.views.client.account.notification.get_setting import AccountNotificationSettingView


class AccountNotificationView(ClientBaseView):

    async def on_load(self):
        await self.set_type(loading=True)
        notification = await self.client.session.api.client.notifications.get()
        await self.set_type(loading=False)
        if not notification.telegram_id:
            await self.client.change_view(view=AccountNotificationLinkTelegramView(), delete_current=True)
            return
        await self.client.change_view(
            view=AccountNotificationSettingView(notification=notification),
            delete_current=True,
        )
