# grblHAL error codes: https://github.com/terjeio/grblHAL/blob/master/doc/csv/error_codes_en_US.csv

class ErrorCodes:
    EXPECTED_COMMAND_LETTER = (1, "Expected command letter")
    BAD_NUMBER_FMT = (2, "Bad number format")
    UNSUPPORTED_CMD = (20, "Unsupported command")
    MODAL_GROUP_VIOLATION = (21, "Modal group violation")

    def fmt(code):
        return f"error:{code[0]} ({code[1]})\n"
