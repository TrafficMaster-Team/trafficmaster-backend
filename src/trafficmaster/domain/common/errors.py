class AppError(Exception):
    pass


class DomainError(AppError):
    pass


class DomainFieldError(DomainError):
    pass


class InconsistentTimeError(DomainFieldError):
    pass
