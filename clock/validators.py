"""Validators for the clock settings.

Separate from everything else, because they don't exist in wxGlade,  so
kept here to avoid cluttering up the main flow.

"""

import dataclasses
from typing import Optional

import wx

from utils import DEFAULT_SOUND, ERROR_COLOUR, bc_log

# because this is a wxPython class, it uses wxWidgets C-Style function names.
# supress the complaint throughout.
# pylint: disable=invalid-name


@dataclasses.dataclass(slots=True)
class ValidatorLimits:
    """Limits for a validator that requires an int."""

    min: int  # fail if less
    max: int  # fail if greater
    warn: int  # confirm if greater (could be desired, could be 115/155 instead of 15)


# SET LIMITS HERE
ROUND_LIMITS = ValidatorLimits(min=1, max=20, warn=14)  # 13x2 board rounds + 1
ROUND_LENGTH_LIMITS = ValidatorLimits(min=1, max=210, warn=85)  # 12x7 minutes/board
BREAK_LENGTH_LIMITS = ValidatorLimits(min=0, max=100, warn=7)  # minutes


class BridgeClockValidateError(ValueError):
    """Raised when the value of a text box is wrong or out of bounds."""


class BaseValidator(wx.Validator):
    """Base class for validators with common functionality."""

    def __init__(
        self,
        limits: ValidatorLimits,
        validator_name: str = "Value",
        error_message: str = "{name} must be an integer.",
    ):
        super().__init__()
        self.limits = limits
        self.validator_name = validator_name
        self.error_message = error_message.format(name=validator_name)
        self.Bind(wx.EVT_TEXT, self.on_char)

    def Clone(self):
        """Clone the validator. Required by wx."""
        return self.__class__(self.limits)

    def TransferToWindow(self):
        """Return False if data transfer to the window fails."""
        return True

    def TransferFromWindow(self):
        """Return False if data transfer from the window fails."""
        return True

    def _validate(self, value: str):
        """Do the validation. Throws BridgeClockValidationError on fail."""
        try:
            count = int(value)
        except ValueError as e:
            raise BridgeClockValidateError(self.error_message) from e
        if count not in range(self.limits.min, self.limits.max + 1):
            raise BridgeClockValidateError(
                f"{self.validator_name} must be between "
                f"{self.limits.min} and {self.limits.max}."
            )

    # pylint: disable=unused-argument
    def Validate(self, parent):
        """Validate field: int, between min and max, warn if large but possible.

        Because we do validation "as the user types", most of the actual validation
        is pushed to an internal function, also used by the wx.EVT_TEXT callback.
        """
        ctrl = self.GetWindow()
        text = ctrl.GetValue()
        try:
            self._validate(text)
        except BridgeClockValidateError as e:
            wx.MessageBox(str(e))
            return False

        if self.limits.warn and int(text) > self.limits.warn:
            wx.MessageBox(
                f"Confirming: your {self.validator_name} value is {text.strip()}."
            )
        return True

    def on_char(self, event):
        """Value changed, light up background if invalid."""
        ctrl = self.GetWindow()
        text = ctrl.GetValue()
        try:
            self._validate(text)
            ctrl.SetBackgroundColour(wx.NullColour)
            ctrl.Refresh()
        except BridgeClockValidateError:
            ctrl.SetBackgroundColour(ERROR_COLOUR)
            ctrl.Refresh()
        event.Skip()


class RoundCountValidator(BaseValidator):
    """Round count: positive int."""

    def __init__(self, limits: Optional[ValidatorLimits] = ROUND_LIMITS):
        super().__init__(limits=limits, validator_name="Round Count")

    def on_char(self, event):
        """value changed, confirm still valid.

        Changing the round count can invalidate the breaks list (say going from 10
        rounds to 5 with breaks set at 3 and 6), so this triggers the breaks validator
        as well as the round validator.
        """

        text_breaks = self.GetWindow().TopLevelParent.text_break_rounds
        text_breaks.SetValue(text_breaks.GetValue())
        super().on_char(event)


class RoundLengthValidator(BaseValidator):
    """Round length: int, in minutes."""

    def __init__(self, limits: Optional[ValidatorLimits] = ROUND_LENGTH_LIMITS):
        super().__init__(limits=limits, validator_name="Round Length")


class BreakValidator(wx.Validator):
    """Breaks: blank, or int, or comma-separated ints, all between 1..num rounds"""

    def __init__(self):

        super().__init__()
        self.Bind(wx.EVT_TEXT, self.on_char)

    def Clone(self):
        """Clone the validator.  Required by wx."""

        return BreakValidator()

    def TransferToWindow(self):
        """Return False if data transfer to the window fails."""

        return True

    def TransferFromWindow(self):
        """Return False if data transfer from the window fails."""

        return True

    @staticmethod
    def _validate(value: str, parent: wx.TextCtrl) -> None:
        """Do the validation. Throws BridgeClockValidationError on fail."""

        if not value:  # "no breaks" is valid
            return

        try:
            breaks = [int(x) for x in value.split(",")]
        except ValueError as e:
            raise BridgeClockValidateError(
                "Break rounds must all be integers. Separate "
                "multiple break rounds with commas (e.g. '4,9')"
            ) from e

        try:
            num_rounds = int(parent.TopLevelParent.text_round_count.GetValue())
        except ValueError:
            # fake for validation; this will trigger validation failure in
            # Round Count, so not worrying about it
            num_rounds = 1
        break_in_range = [break_round in range(1, num_rounds) for break_round in breaks]
        if not all(break_in_range):
            raise BridgeClockValidateError(
                f"Break rounds must be between round 1 and {num_rounds-1}"
            )

    def Validate(self, parent):
        """Break Rounds cs-ints, between 1 and Rounds, or blank (no breaks)."""
        bc_log("in break validator")
        ctrl = self.GetWindow()
        value = ctrl.GetValue().strip()
        ctrl.SetValue(value)

        try:
            self._validate(value, parent)
        except BridgeClockValidateError as e:
            wx.MessageBox(str(e))
            return False

        return True

    def on_char(self, event):
        """Value changed, light up background if invalid."""
        ctrl = self.GetWindow()
        text = ctrl.GetValue().strip()
        try:
            self._validate(text, ctrl.GetParent())
            ctrl.SetBackgroundColour(wx.NullColour)
            ctrl.Refresh()
        except BridgeClockValidateError:
            ctrl.SetBackgroundColour(ERROR_COLOUR)
            ctrl.Refresh()
        event.Skip()


class BreakLengthValidator(BaseValidator):
    """Break length: int, in minutes."""

    def __init__(self, limits: Optional[ValidatorLimits] = BREAK_LENGTH_LIMITS):
        super().__init__(limits=limits, validator_name="Break Length")


class SoundValidator(wx.Validator):
    """Check if sounds can be played."""

    def __init__(self):
        super().__init__()
        self.Bind(wx.EVT_CHECKBOX, self.on_checked)

    def Clone(self):
        return self.__class__()

    def TransferToWindow(self):
        return True

    def TransferFromWindow(self):
        return True

    def Validate(self, parent):
        return self._validate()

    def _validate(self):
        ctrl = self.GetWindow()
        checked = ctrl.IsChecked()
        if not checked or Path(DEFAULT_SOUND).exists():
            return True

        wx.MessageBox("Can not find default sound, assuming no sounds exist.")
        ctrl.SetValue(False)
        return False

    def on_checked(self, event):
        return self._validate()
