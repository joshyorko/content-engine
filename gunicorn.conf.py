# Gunicorn configuration
# Adjusted to accommodate larger request headers when hitting Gunicorn directly.

# Increase per-header field size (default is ~8190 bytes). Set to 64 KiB.
limit_request_field_size = 65536

# Increase request line limit to handle long URLs and cookies in the request line.
limit_request_line = 16384

# Keep existing worker model but ensure it is explicit and consistent with entrypoint.
workers = 3
worker_class = "sync"

# Bind matches the container port exposed by Dockerfile and docker-compose.
bind = "0.0.0.0:8000"

# Optional: reasonable timeouts (kept default-ish; uncomment if needed)
# timeout = 30
# keepalive = 2

# Access/error logs can help during verification (inherit Docker stdout/err by default)
# accesslog = "-"
# errorlog = "-"