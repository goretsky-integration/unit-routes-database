class ApplicationError(Exception):
    pass


class NotFoundError(ApplicationError):
    pass


class AlreadyExistsError(ApplicationError):
    pass


class PermissionDeniedError(ApplicationError):
    pass
