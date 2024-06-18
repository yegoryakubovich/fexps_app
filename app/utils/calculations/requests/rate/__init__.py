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


from .all import calculate_request_rate_all_by_output_currency_value, calculate_request_rate_all_by_input_currency_value
from .input import calculate_request_rate_input_by_input_currency_value, calculate_request_rate_input_by_input_value
from .output import calculate_request_rate_output_by_output_currency_value, \
    calculate_request_rate_output_by_output_value
