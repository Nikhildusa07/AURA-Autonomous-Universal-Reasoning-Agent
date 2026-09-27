from datetime import datetime
from typing import Any


class ExecutionTrace:

    def __init__(self):
        self.events: list[dict[str, Any]] = []

    def record(self, event: str, details: Any = None):
        self.events.append({
            "timestamp": datetime.utcnow().isoformat(),
            "event": event,
            "details": details
        })

    def get_events(self):
        return self.events

    def clear(self):
        self.events.clear()


trace = ExecutionTrace()