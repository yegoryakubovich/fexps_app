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


from flet_manager.utils import get_svg as fm_get_svg


def get_svg(icon_name):
    return fm_get_svg(f'assets/icons/app/{icon_name}.svg')


class Icons:
    NOT_FOUNT = get_svg('404')
    SUCCESSFUL = get_svg('successful')
    PHONE = get_svg('phone')
    TELEGRAM = get_svg('telegram')
    EMAIL = get_svg('email')
    BACK = get_svg('back')
    DOC = get_svg('doc')
    PROTEIN = get_svg('protein')
    FATS = get_svg('fats')
    CARBOHYDRATES = get_svg('carbohydrates')
    CHILL = get_svg('chill')
    COPY = get_svg('copy')
    RELOAD = get_svg('reload')
    PLAN = get_svg('plan')
    STATS = get_svg('stats')
    ACCOUNT = get_svg('account')
    TRAINING = get_svg('training')
    NOTIFICATIONS = get_svg('notifications')
    SECURITY = get_svg('security')
    LANGUAGE = get_svg('language')
    CURRENCY = get_svg('currency')
    TIMEZONE = get_svg('timezone')
    COUNTRY = get_svg('country')
    LOGOUT = get_svg('logout')
    CREATE = get_svg('create')
    ARTICLES = get_svg('articles')
    ADMIN_ACCOUNTS = get_svg('admin_accounts')
    ADMIN_TEXTS = get_svg('admin_texts')
    ADMIN_PRODUCTS = get_svg('admin_products')
    ADMIN_EXERCISES = get_svg('admin_exercises')
    ADMIN_PERMISSIONS = get_svg('admin_permissions')
    ADMIN_ROLES = get_svg('admin_roles')
    ADMIN_SERVICES = get_svg('admin_services')
    PRIVACY_POLICY = get_svg('privacy_policy')
    FAQ = get_svg('faq')
    ABOUT = get_svg('about')
    SUPPORT = get_svg('support')
    NEXT = get_svg('next')
    LIGHT = get_svg('light')
    DARK = get_svg('dark')
    ERROR = get_svg('error')
    FILE = get_svg('file')
    WALLET_MENU = get_svg('wallet_menu')
    HOME = get_svg('home')
    COIN = get_svg('coin')
    EXCHANGE = get_svg('exchange')
    CHAT = get_svg('chat')
    OPEN = get_svg('open')
    REQUISITE = get_svg('requisite')
    MAKE_EXCHANGE = get_svg('make_exchange')
    PAYMENT = get_svg('payment')
    DEV = get_svg('dev')
    EDIT = get_svg('edit')
    CLIP = get_svg('clip')
    WALLET = get_svg('wallet')
    METHOD = get_svg('method')
    COMMISSION_PACK = get_svg('commission_pack')
    CONTACT = get_svg('contact')
    REVERSE = get_svg('reverse')
    SETTINGS = get_svg('settings')
    SEARCH = get_svg('search')
