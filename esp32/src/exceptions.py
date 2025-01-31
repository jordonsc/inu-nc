from error_codes import ErrorCodes


class GCodeException(Exception):
    """
    Base exception for G-code errors.
    """

    def __init__(self, message, error_code):
        self.error_code = error_code
        super().__init__(message)


class UnsupportedCommandError(GCodeException):
    """
    Unsupported G-code command.

    eg: "G9999"
    """

    def __init__(self, command):
        self.command = command
        self.message = f"Unsupported command: {command}"
        super().__init__(self.message, ErrorCodes.UNSUPPORTED_CMD)


class MissingValueError(GCodeException):
    """
    Value is absent from the G-code.

    eg: "L" instead of "L20"
    """

    def __init__(self, command):
        self.command = command
        self.message = f"Missing value for command: {command}"
        super().__init__(self.message, ErrorCodes.EXPECTED_COMMAND_LETTER)


class BadNumberError(GCodeException):
    """
    Value is not a number.

    eg: "LX"
    """

    def __init__(self, command):
        self.command = command
        self.message = f"Value is not a number: {command}"
        super().__init__(self.message, ErrorCodes.BAD_NUMBER_FMT)


class ModalGroupViolationError(GCodeException):
    """
    Conflicting modal commands in the same block.

    eg: "G90 G91"
    """

    def __init__(self, command):
        self.command = command
        self.message = f"Conflicting modal commands in same block: {command}"
        super().__init__(self.message, ErrorCodes.MODAL_GROUP_VIOLATION)
