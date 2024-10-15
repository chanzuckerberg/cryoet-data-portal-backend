

class TomogramNotFoundError(FileNotFoundError):
    def __init__(self, message: str = None) -> None:
        message = message or "No source tomogram found"
        super().__init__(message)
