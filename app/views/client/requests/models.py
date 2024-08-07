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


from flet_core import Control, Row, IconButton, icons, colors, MainAxisAlignment

from app.controls.button import StandardButton
from app.controls.information import Text
from app.controls.input import TextField
from app.utils import Session, Fonts
from config import settings
from fexps_api_client.utils import ApiException


class RequestUpdateNameModel:
    controls: list[Control]
    buttons: list[Control]
    height: int = 150

    tf_name: TextField

    def __init__(
            self,
            session: Session,
            update_async: callable,
            request_id: int,
            request_name: str = None,
            after_close: callable = None,
            before_close: callable = None,
            close_func: callable = None,
    ):
        self.session = session
        self.update_async = update_async
        self.request_id = request_id
        self.request_name = request_name
        self.after_close = after_close
        self.before_close = before_close
        self.close_func = close_func

    async def construct(self):
        self.tf_name = TextField(
            label=await self.session.gtv(key='name'),
            value=self.request_name,
        )
        self.controls = [
            Row(
                controls=[
                    Text(
                        value=await self.session.gtv(key='request_change_name_title'),
                        size=settings.get_font_size(multiple=1.5),
                        font_family=Fonts.BOLD,
                        color=colors.ON_BACKGROUND,
                    ),
                    IconButton(
                        icon=icons.CLOSE,
                        on_click=self.close_func,
                        icon_color=colors.ON_BACKGROUND,
                    ),
                ],
                alignment=MainAxisAlignment.SPACE_BETWEEN,
            ),
            self.tf_name,
        ]
        self.buttons = [
            Row(
                controls=[
                    StandardButton(
                        content=Text(
                            value=await self.session.gtv(key='request_edit_name'),
                            size=settings.get_font_size(multiple=1.5),
                            font_family=Fonts.REGULAR,
                        ),
                        on_click=self.edit_name,
                        expand=True,
                    ),
                ],
            ),
        ]

    async def edit_name(self, _):
        request_name = None
        if self.tf_name.value:
            request_name = self.tf_name.value
        if self.before_close:
            await self.before_close()
        try:
            await self.session.api.client.requests.updates.name(
                id_=self.request_id,
                name=request_name,
            )
        except ApiException as exception:
            return await self.session.error(exception=exception)
        if self.after_close:
            await self.after_close()
