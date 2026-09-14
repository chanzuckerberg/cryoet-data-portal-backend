import json
import logging
import os
import sys

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s[%(name)s.%(funcName)s:%(lineno)d] %(message)s",
    datefmt="%d/%b/%Y %H:%M:%S",
    stream=sys.stdout,
)

# Gunicorn config variables
loglevel = os.getenv("LOG_LEVEL", "info")
workers = os.getenv("WORKERS", 4)
bind = "unix:///var/run/fastapi.sock"
errorlog = "-"
worker_tmp_dir = "/dev/shm"
accesslog = "-"
graceful_timeout = int(os.getenv("GRACEFUL_TIMEOUT", "120"))
timeout = int(os.getenv("TIMEOUT", "120"))
keepalive = int(os.getenv("KEEP_ALIVE", "5"))
# Recycle workers periodically so memory from large responses is returned to the OS.
max_requests = int(os.getenv("MAX_REQUESTS", "200"))
max_requests_jitter = int(os.getenv("MAX_REQUESTS_JITTER", "20"))
# TODO - this is broken, per https://github.com/encode/uvicorn/issues/527
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# For debugging and testing
log_data = {
    "loglevel": loglevel,
    "access_log_format": access_log_format,
    "workers": workers,
    "bind": bind,
    "graceful_timeout": graceful_timeout,
    "timeout": timeout,
    "keepalive": keepalive,
    "max_requests": max_requests,
    "max_requests_jitter": max_requests_jitter,
    "errorlog": errorlog,
    "accesslog": accesslog,
}
print(json.dumps(log_data))
