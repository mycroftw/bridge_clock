"""Utility functions used throughout clock."""

DEBUG = True


def bc_log(msg: str) -> None:
    """handle logging.  Currently: print if DEBUG True."""

    if DEBUG:
        print(msg)
