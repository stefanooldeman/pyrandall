INVALID_VERSION_MSG = (
    "Unsupported schema version for pyrandall. " "Please choose from: {}"
)


class Error(Exception):
    """Base class for exceptions in this module."""

    def __init__(self, message):
        super(Exception, self).__init__(message)
        self.message = message


class InvalidSchenarioVersion(Error):
    def __init__(self, correct_versions):
        message = INVALID_VERSION_MSG.format(", ".join(correct_versions))
        super(Error, self).__init__(message)
        self.message = message


class ZeroAssertions(Error):
    pass

class ZeroEvents(Error):
    pass


class KafkaSetupError(Error):
    pass

class KafkaTopicError(Error):
    pass
