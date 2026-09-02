"""Event queue management for workflow progress tracking"""

import queue
import threading
from typing import Optional

_event_queue: Optional[queue.Queue] = None
_queue_lock = threading.Lock()


def get_event_queue() -> Optional[queue.Queue]:
    """Get the current event queue for this thread's workflow"""
    with _queue_lock:
        return _event_queue


def set_event_queue(q: Optional[queue.Queue]) -> None:
    """Set the event queue for this thread's workflow"""
    global _event_queue
    with _queue_lock:
        _event_queue = q


def emit_event(event: dict) -> None:
    """Emit an event to the current event queue if one is set"""
    q = get_event_queue()
    if q is not None:
        try:
            q.put(event)
        except Exception as e:
            print(f"Warning: Failed to emit event: {e}")
