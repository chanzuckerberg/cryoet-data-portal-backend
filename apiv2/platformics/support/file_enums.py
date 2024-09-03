import enum

import strawberry


@strawberry.enum
class FileStatus(enum.Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    PENDING = "PENDING"


@strawberry.enum
class FileAccessProtocol(enum.Enum):
    s3 = "s3"
    https = "https"


@strawberry.enum
class FileUploadClient(enum.Enum):
    browser = "browser"
    cli = "cli"
    s3 = "s3"
    basespace = "basespace"
