import logging

from flet_core import SnackBar

from app.controls.layout import AdminBaseView


class OrderView(AdminBaseView):
    route = '/client/request/order/get'
    order = dict
    snack_bar: SnackBar

    def __init__(self, order_id: int):
        super().__init__()
        self.order_id = order_id

    async def build(self):
        await self.set_type(loading=True)
        self.order = await self.client.session.api.client.orders.get(id_=self.order_id)
        await self.set_type(loading=False)
        logging.critical(self.order)
