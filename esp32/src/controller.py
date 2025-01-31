from gcode import COORINATE_SYSTEM, Code


class Units:
    """
    The units of measurement.
    """
    INCHES = 0
    MILLIMETERS = 1


class Controller:
    """
    A G-Code controller.
    """

    def __init__(self):
        # Absolute position of each axis
        self.axis = {'A': 0, 'B': 0, 'C': 0, 'X': 0, 'Y': 0, 'Z': 0} 

        # Relative position of each coordinate system
        self.home_positions = {}

        # Iterate over all coordinate systems
        for i in range(1, 10):
            # Set all axes relative position to 0
            self.home_positions[i] = {'A': 0, 'B': 0, 'C': 0, 'X': 0, 'Y': 0, 'Z': 0} 

        self.coordinate_system = 1  # Default to P1/G54
        self.units = Units.MILLIMETERS


    async def execute(self, cmds: list[Code]):
        """
        Execute a group of G-code commands.

        Args:
            cmds (list[Code]): The G-code command group to execute
        """
        for cmd in cmds:
            if cmd.command == 'G21':
                self.units = Units.MILLIMETERS
            elif cmd.command == 'G20':
                self.units = Units.INCHES
            elif cmd.command in ['G54', 'G55', 'G56', 'G57', 'G58', 'G59', 'G59.1', 'G59.2', 'G59.3']:
                self.coordinate_system = COORINATE_SYSTEM[cmd.command]
            else:
                raise ValueError(f"Unsupported command: {cmd.command}")
