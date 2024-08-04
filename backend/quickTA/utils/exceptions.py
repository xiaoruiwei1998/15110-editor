class BadRequestError(Exception): # 400
    pass


class ForbiddenError(Exception): # 403
    pass


class NotFoundError(Exception):
    pass