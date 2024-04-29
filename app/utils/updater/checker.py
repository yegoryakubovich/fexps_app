import logging


class UpdateChecker:
    @staticmethod
    def check(
            scheme: callable,
            obj_1: dict,
            obj_2: dict,
    ) -> bool:
        scheme_obj_1 = scheme(obj_1)
        scheme_obj_2 = scheme(obj_2)
        if scheme_obj_1 == scheme_obj_2:
            return False
        return True
