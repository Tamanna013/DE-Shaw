class LogParserError(Exception):
    pass

class PayloadTooLargeError(LogParserError):
    def __init__(self, size_bytes: int, limit_bytes: int):
        super().__init__(f"Payload size {size_bytes} exceeds limit of {limit_bytes}")
        self.size_bytes = size_bytes
        self.limit_bytes = limit_bytes

class MalformedLogError(LogParserError):
    pass
