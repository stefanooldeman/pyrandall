INVALID_VERSION_MSG = (
    "Unsupported schema version for pyrandall. " "Please choose from: {}"
)


class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class InvalidSchenarioVersion(Error):
    def __init__(self, correct_versions):
        super(Exception, self).__init__(
            INVALID_VERSION_MSG.format(", ".join(correct_versions))
        )


class ZeroAssertions(Error):
    pass

class ZeroEvents(Error):
    pass
