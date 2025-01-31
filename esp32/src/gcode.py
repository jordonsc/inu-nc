from exceptions import *

COORINATE_SYSTEM = {'G54': 1, 'G55': 2, 'G56': 3, 'G57': 4, 'G58': 5, 'G59': 6, 'G59.1': 7, 'G59.2': 8, 'G59.3': 9}


class Code:
    """
    Represents a single G-code command with an optional value.

    The value would be the parameter for the command, e.g. 'X10' where 'X' is the command and '10' is the value. 

    G and M codes do not have values and are represented as a command in whole, e.g. 'G1' is a command.
    """

    def __init__(self, command, value=None):
        self.command = command
        self.value = value

    def __str__(self):
        if self.value is not None:
            return f"{self.command}{self.value}"
        else:
            return f"{self.command}"

    def is_parameter(self):
        """
        Check if the code is an argument (has a value) or if it is stand-alone command (G and M codes only).
        """
        return self.value is not None



class CodeGroup:
    """
    Represents a single G-code command, with a collection of parameters applied as part of a code group (a line of G-codes).
    """
    def __init__(self):
        self.command = None
        self.parameters = {}

    def add_code(self, code: Code):
        if code.is_parameter():
            # Don't add if already set
            if code.command in self.parameters:
                raise ModalGroupViolationError(f"Argument already set: {code.command}")
            
            # Set group paramater
            self.parameters[code.command] = code.value
        else:
            # Don't add if we've already got a modal command set
            if self.command is not None:
                raise ModalGroupViolationError("Command already set")
            
            # Set group primary command
            self.command = code.command

    def __str__(self):
        return f"{self.command} {' '.join([str(Code(k, v)) for k, v in self.parameters.items()])}"


class GCodeParser:
    """
    Parses G-code statements into `Code` objects.
    """

    # See grblHAL supported G-code: https://github.com/grblHAL/core?tab=readme-ov-file#supported-g-codes
    SUPPORTED_CODES = {
        'G0', 'G1',  # Rapid & linear movement
        'G4',  # Dwell (pause)
        'G10',  # Set coordinate system
        'G20', 'G21',  # Units: inches, millimeters
        'G28', 'G28.1'  # Home, set home
        'G54', 'G55', 'G56', 'G57', 'G58', 'G59', 'G59.1', 'G59.2', 'G59.3',  # Coordinate system
        'G90', 'G91',  # Absolute/relative positioning
        'M0', 'M1', 'M2',  # Stop
        'M3', 'M4', 'M5',  # Spindle control: forward, reverse, stop
        'M30',  # Program end
    }
    SUPPORTED_PARAMS = {
        'A', 'B', 'C', 'X', 'Y', 'Z',  # Axes
        'F',  # Feed rate
        'S',  # Spindle speed or laser intensity
        'P',  # Dwell (pause) time, workspace coordinate system
        'L',  # Used for G10 subcommands
    }

    @staticmethod
    def parse(data):
        """
        Parse the G-code data.

        Args:
            data (str): The G-code data to parse.

        Returns:
            list[Command]: The parsed commands.

        Raises:
            GCodeException
        """
        commands = data.strip().upper().split(' ')
        parsed_commands = []

        for command in commands:
            # G and M codes are standalone commands, all other values are parameters.
            if command.startswith('G') or command.startswith('M'):
                # Check if the command is supported
                if command in GCodeParser.SUPPORTED_CODES:
                    parsed_commands.append(Code(command))
                else:
                    raise UnsupportedCommandError(command)
            else:
                # Parameter code
                code = command[0]
                value = command[1:]

                # Check that the value isn't too long
                if len(value) > 5:
                    raise BadNumberError(command)

                # Check if the value is a number
                if value:
                    try:
                        _ = float(value)
                    except ValueError:
                        raise BadNumberError(command)
                
                
                if code in GCodeParser.SUPPORTED_PARAMS:
                    if value:
                        parsed_commands.append(Code(code, value))
                    else:
                        raise MissingValueError(command)
                else:
                    raise UnsupportedCommandError(command)

        return parsed_commands
