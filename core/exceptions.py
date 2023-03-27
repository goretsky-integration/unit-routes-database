class ApplicationError(Exception):
    pass


class NotFoundError(ApplicationError):
    pass


class AlreadyExistsError(ApplicationError):
    pass
