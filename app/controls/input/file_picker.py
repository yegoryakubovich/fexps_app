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


from typing import Any

from flet_core import FilePicker as FilePickerFlet, FilePickerFileType


class FilePicker(FilePickerFlet):
    def __init__(self):
        super().__init__()

    async def open_(
            self,
            on_select: Any,
            on_upload: Any = None,
            allowed_extensions: list[str] = None,
            allow_multiple: bool = False,
            file_type: FilePickerFileType = FilePickerFileType.ANY,
            initial_directory: str = None,
    ):
        self.on_result = on_select
        self.on_upload = on_upload
        self.allowed_extensions = allowed_extensions
        self.allow_multiple = allow_multiple
        self.file_type = file_type
        self.initial_directory = initial_directory
        await self.pick_files_async()
