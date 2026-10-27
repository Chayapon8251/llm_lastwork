"""Single-process request budgets for an optionally public demo.

No IP addresses are persisted. Limits reset on restart; this is not a
distributed rate limiter and the deployment intentionally runs one worker.
"""
import threading
import time
from collections import deque


class DemoLimiter:
    def __init__(self, clock=time.monotonic):
        self.clock = clock
        self.lock = threading.Lock()
        self.clients = {}
        self.global_calls = deque()

    def allow(self, client):
        now = self.clock()
        with self.lock:
            while self.global_calls and self.global_calls[0] <= now - 86400:
                self.global_calls.popleft()
            self.clients = {key: q for key, q in self.clients.items() if q and q[-1] > now - 60}
            recent = self.clients.get(client, deque())
            while recent and recent[0] <= now - 60:
                recent.popleft()
            if len(recent) >= 6:
                return False, max(1, int(recent[0] + 60 - now) + 1)
            hour = [t for t in self.global_calls if t > now - 3600]
            if len(hour) >= 40:
                return False, max(1, int(hour[0] + 3600 - now) + 1)
            if len(self.global_calls) >= 120:
                return False, max(1, int(self.global_calls[0] + 86400 - now) + 1)
            recent.append(now)
            self.clients[client] = recent
            self.global_calls.append(now)
            return True, 0
