from enum import Enum


class Operation(Enum):
    """
    Operations allowed in queries
    """

    EQ = '='
    UNEQ = '<>'
    LT = '<'
    LTE = '<='
    GT = '>'
    GTE = '>='
    LIKE = ' LIKE '
    ILIKE = ' ILIKE '
    IS = ' IS '
