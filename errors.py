class OutOfFieldError(Exception):
    """Raised when we try to get some tile outside of 9x9 field"""


class NewNumberDiscoveredError(Exception):
    """Raised when new number located on field. Breaks the loop"""


class WrongNumberOfOptionsError(Exception):
    """Raised when number of new offered options is invalid"""


class BrokenAssumption(Exception):
    """Raised when duplicated number appears in group or none of the options left for the tile"""


class Solved(Exception):
    """Raised when solution is ready"""


