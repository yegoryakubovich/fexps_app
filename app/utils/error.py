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


from flet_core import Control


class Error:

    @staticmethod
    async def check_field(
            self,
            field,
            check_int=False,
            check_float=False,
            min_len=None,
            max_len=None,
            error_text_key='error_count_letter'
    ) -> bool:
        field.error_text = None
        if check_int:
            try:
                int(str(field.value))
            except:
                field.error_text = await self.client.session.gtv(key='error_not_int')
                await self.update_async()
                return False
        if not check_int and check_float:
            try:
                float(str(field.value))
            except:
                field.error_text = await self.client.session.gtv(key='error_not_float')
                await self.update_async()
                return False
        if not check_int and not check_float and (min_len or max_len):
            len_value = len(field.value)
            if (min_len and len_value < min_len) or (max_len and len_value > max_len):
                field.error_text = await self.client.session.gtv(key=error_text_key) + ' ' + f'{min_len}-{max_len}'
                await self.update_async()
                return False
        return True

    @staticmethod
    async def field_error_set(
            fields: list[Control],
            text: str,
            update: bool = True,
    ) -> None:
        for field in fields:
            field.error_text = text
            if update:
                await field.update_async()

    @staticmethod
    async def field_error_reset(
            fields: list[Control],
            update: bool = True,
    ) -> None:
        for field in fields:
            field.error_text = None
            if update:
                await field.update_async()
