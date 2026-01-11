# filename: app/anti_spam.py

from fastapi import Request, HTTPException
import time


# TODO - CHILLIEMAN - This was a fun idea - But wont this eventually cause an OOM?
RATE_LIMIT = 10  # requests
WINDOW = 60  # seconds
requests_log = {}


def rate_limiter(request: Request):
    ip = request.client.host
    now = time.time()
    window_start = now - WINDOW
    requests_log.setdefault(ip, [])
    requests_log[ip] = [t for t in requests_log[ip] if t > window_start]
    if len(requests_log[ip]) >= RATE_LIMIT:
        raise HTTPException(status_code=429, detail="Too many requests")
    requests_log[ip].append(now)
