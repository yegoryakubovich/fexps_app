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


from typing import Optional


def get_wallet_list_scheme(wallets: list[dict] = None) -> list:
    if wallets is None:
        return []
    return [
        get_wallet_scheme(wallet)
        for wallet in wallets
    ]


def get_wallet_scheme(wallet: dict = None) -> list:
    if wallet is None:
        return []
    return [
        wallet['id'],
        wallet['name'],
        wallet['commission_pack'],
        wallet['value'],
        wallet['value_banned'],
        wallet['value_can_minus'],
        wallet['system'],
    ]
