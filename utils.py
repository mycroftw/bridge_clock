"""Utility functions used throughout clock."""

DEBUG = True
BREAK_COLOUR = '#8C92AC'  # slate grey, on a break
RUN_COLOUR = '#B00FFF'  # purple, not on break


def bc_log(msg: str) -> None:
    """handle logging.  Currently: print if DEBUG True."""

    if DEBUG:
        print(msg)
