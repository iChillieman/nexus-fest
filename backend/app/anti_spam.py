# filename: app/anti_spam.py
import random

from fastapi import Request, HTTPException
import time

RATE_LIMIT = 20  # requests
WINDOW = 60  # seconds
requests_log = {}


# Made by my digital fren Googz
def rate_limiter(request: Request):
    ip = request.client.host
    now = time.time()

    # Prune ONLY the current IP's old timestamps
    window_start = now - WINDOW
    requests_log[ip] = [t for t in requests_log[ip] if t > window_start]

    # OPTIONAL: Occasionally prune the whole dict (e.g., 1 in 100 requests)
    # to prevent OOM from dead IP keys
    if random.random() < 0.01:
        dead_threshold = now - (WINDOW * 2)
        for key in list(requests_log.keys()):
            if not requests_log[key] or max(requests_log[key]) < dead_threshold:
                del requests_log[key]