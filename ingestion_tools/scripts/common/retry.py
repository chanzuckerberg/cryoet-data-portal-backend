"""Retry utilities for S3 operations."""

import logging

from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential_jitter,
)

# Retry configuration for S3 operations
RETRY_MAX_ATTEMPTS = 5
RETRY_INITIAL_WAIT_SECONDS = 30.0
RETRY_MAX_WAIT_SECONDS = 300.0
RETRY_JITTER_SECONDS = 15.0

logger = logging.getLogger(__name__)


def is_s3_throttling(exception: BaseException) -> bool:
    """Check if exception is an S3 throttling/SlowDown error."""
    error_str = str(exception).lower()
    throttle_indicators = (
        "slowdown",
        "503",
        "service unavailable",  # Catches "OSError: [Errno 16] Service Unavailable"
        "throttl",
        "reduce your request rate",  # s3fs converts SlowDown to OSError with this message
    )
    return any(indicator in error_str for indicator in throttle_indicators)


def s3_retry_decorator(func):
    """Decorator that adds S3 throttling retry logic to a function."""
    return retry(
        stop=stop_after_attempt(RETRY_MAX_ATTEMPTS),
        wait=wait_exponential_jitter(
            initial=RETRY_INITIAL_WAIT_SECONDS,
            max=RETRY_MAX_WAIT_SECONDS,
            jitter=RETRY_JITTER_SECONDS,
        ),
        retry=retry_if_exception(is_s3_throttling),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )(func)
