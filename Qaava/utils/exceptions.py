# Add application specific exception classes here


class QaavaDatabaseNotSetException(Exception):
    pass


class QaavaAuthConfigException(Exception):
    pass


class QaavaNetworkException(Exception):
    pass


class QaavaNotImplementedException(Exception):
    pass
