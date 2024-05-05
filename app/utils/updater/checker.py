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


def update_check(
        scheme: callable,
        obj_1: dict,
        obj_2: dict,
) -> bool:
    scheme_obj_1 = scheme(obj_1)
    scheme_obj_2 = scheme(obj_2)
    if scheme_obj_1 == scheme_obj_2:
        return False
    return True
