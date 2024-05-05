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


def get_transfer_list_scheme(transfers: list[dict] = None) -> list:
    if transfers is None:
        return []
    return [
        get_transfer_scheme(transfer)
        for transfer in transfers
    ]


def get_transfer_scheme(transfer: dict = None) -> list:
    if transfer is None:
        return []
    return [
        transfer['id'],
        transfer['type'],
        transfer['operation'],
        transfer['wallet_from'],
        transfer['account_from'],
        transfer['wallet_to'],
        transfer['account_to'],
        transfer['order'],
        transfer['value'],
        transfer['date'],
    ]
