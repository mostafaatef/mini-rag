from enum import Enum

class ResponceMessagesEnum(Enum):
    FILE_TYPE_NOT_ALLOWAED = "file_type_not_allowed"
    FILE_SIZE_TOO_LARGE = "file_size_too_large"
    FILE_UPLOAD_SUCCESS = "file_upload_success"
    FILE_UPLOAD_FAILED = "file_upload_failed"
    FILE_PROCESSING_FAILED = "file_processing_failed"
    FILE_PROCESSING_SUCCESS = "file_processing_success"
    