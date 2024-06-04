"""Helper functions for use in plist_helper modules."""
def verify(
    condition: bool,
    failure_exception: Exception,
) -> None:
    """Make sure a condition is met before continuing execution.

    TODO(@jlyle)
    """
    if condition:
        return

    raise failure_exception
