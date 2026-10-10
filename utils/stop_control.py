"""Helpers for cooperative cancellation of the background bot thread."""

import builtins
import time

class StopRequested(Exception):
    """Raised when the user asks the running bot to stop."""

def stop_requested() -> bool:
    return bool(getattr(builtins, "STOP_BOT", False))

def raise_if_stop_requested() -> None:
    if stop_requested():
        raise StopRequested("Bot stop requested")

def interruptible_sleep(seconds: float, interval: float = 0.2) -> None:
    """Sleep in short intervals so a stop request is handled promptly."""
    end_time = time.monotonic() + max(0, seconds)
    while True:
        raise_if_stop_requested()
        remaining = end_time - time.monotonic()
        if remaining <= 0:
            return
        time.sleep(min(interval, remaining))

def stop_aware_condition(condition):
    """Wrap a Selenium wait condition with a cooperative stop check."""
    def check(driver):
        raise_if_stop_requested()
        return condition(driver)

    return check
