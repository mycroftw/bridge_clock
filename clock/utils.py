"""Utility functions used throughout clock."""

from pathlib import Path

from playsound3.playsound3 import PlaysoundException, playsound

DEBUG = True
BREAK_COLOUR = "#8C92AC"  # slate grey, on a break
RUN_COLOUR = "#B00FFF"  # purple, not on break
ERROR_COLOUR = "#FF0000"  # red, background for error in settings
SOUNDS_DIR = Path("sound")
DEFAULT_SOUND = SOUNDS_DIR / "default.mp3"


def bc_log(msg: str) -> None:
    """handle logging.  Currently: print if DEBUG True."""

    if DEBUG:
        print(msg)


def play_sound(file_name: str) -> None:
    """Play a sound."""
    bc_log(f"play sound [{file_name}]")
    f = SOUNDS_DIR / f"{file_name}.mp3"
    if not Path(f).exists():  # play default sound
        bc_log(f"[{f}] not found, using default sound.")
        f = DEFAULT_SOUND
    try:
        playsound(f, block=False)
    except PlaysoundException as e:
        bc_log(f"Could not play sound file {f}: {e}")
