class PlistHelperError(Exception):
    pass

class PlistHelperRuntimeError(PlistHelperError, RuntimeError):
    pass

class PlistHelperTypeError(PlistHelperError, TypeError):
    pass

class PlistHelperValueError(PlistHelperError, ValueError):
    pass

class PlistHelperKeyError(PlistHelperError, KeyError):
    pass
