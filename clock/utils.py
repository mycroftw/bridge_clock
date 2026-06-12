"""Utility functions used throughout clock."""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import wx
from playsound3.playsound3 import PlaysoundException, playsound

DEBUG = True  # added error messages to stdout


@dataclass(slots=True)
class Palette:
    """Colour themes for clock."""

    break_: str | wx.Colour
    clock: str | wx.Colour
    run: str | wx.Colour
    text: str | wx.Colour


COLOURS = {
    "Default": Palette(
        break_="SLATE GREY", run="DARK ORCHID", clock="YELLOW", text="WHITE"
    ),
    "Blue": Palette(break_="SLATE GREY", run="ROYAL BLUE", clock="CYAN", text="WHITE"),
    "Flash": Palette(break_="DEEP PINK", run="MAROON", clock="GOLD", text="BLACK"),
    "Boring": Palette(
        break_="SLATE GREY", run="BLACK", clock="OLD LACE", text="OLD LACE"
    ),
}

ERROR_COLOUR = "RED"

SOUNDS_DIR = Path("sound")
DEFAULT_SOUND = "default"  # required sound, used if other sound file DNE
NO_SOUND = "silence"  # required sound, used for testing


def bc_log(msg: str) -> None:
    """handle logging.  Currently: print if DEBUG True."""

    if DEBUG:
        print(msg)


def sound_name_to_file(file_name: str) -> Optional[Path]:
    """Convert a barename ("round_end") to path to mp3 in SOUNDS_DIR or None if DNE"""
    f = SOUNDS_DIR / f"{file_name}.mp3"
    return f if f.exists() else None


def play_sound(file_name: str) -> None:
    """Play a sound."""
    bc_log(f"play sound [{file_name}]")
    f = sound_name_to_file(file_name)
    if f is None:
        bc_log(f"[{file_name}] not found, using default sound.")
        f = sound_name_to_file(DEFAULT_SOUND)
    try:
        playsound(f, block=False)
    except PlaysoundException as e:
        bc_log(f"Could not play sound file {f}: {e}")
