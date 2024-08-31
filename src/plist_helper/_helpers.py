"""Helper functions for use in plist_helper modules."""


def assert_(
    condition: bool,
    failure_exception: Exception,
) -> None:
    """Make sure a condition is met before continuing execution.

    TODO(@jlyle): Docstring
    """
    if condition:
        return

    raise failure_exception
