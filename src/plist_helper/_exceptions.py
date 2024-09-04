class PlistHelperError(Exception):
    pass

class PlistHelperIndexError(PlistHelperError, IndexError):
    pass

class PlistHelperKeyError(PlistHelperError, KeyError):
    pass

class PlistHelperOverflowError(PlistHelperError, OverflowError):
    pass

class PlistHelperRuntimeError(PlistHelperError, RuntimeError):
    pass

class PlistHelperTypeError(PlistHelperError, TypeError):
    pass

class PlistHelperValueError(PlistHelperError, ValueError):
    pass
