"""Library exceptions."""


class EnedisException(Exception):
    pass


class EnedisAccessException(EnedisException):
    pass


class EnedisMaintenanceException(EnedisException):
    pass


class EnedisWrongLoginException(EnedisException):
    pass
