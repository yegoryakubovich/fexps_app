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


def get_file_list_scheme(files: list[dict] = None) -> list:
    if files is None:
        return []
    return [
        get_file_scheme(file=file)
        for file in files
    ]


def get_file_scheme(file: dict = None) -> list:
    if file is None:
        return []
    return [
        file['id'],
        file['id_str'],
        file['filename'],
        file['extension'],
        file['open_url'],
        file['download_url'],
        file['value'],
    ]
