"""Send actual bot stage updates to the UI when a GUI callback is installed."""

import builtins

def report_progress(percent, message, letter_number="", title=""):
    callback = getattr(builtins, "BOT_PROGRESS_CALLBACK", None)
    if callable(callback):
        callback(percent, message, letter_number, title)
