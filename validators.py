"""Validators for the clock settings.

Separate from everything else, because they don't exist in wxGlade,  so
kept here to avoid cluttering up the main flow.

"""
# because this is a wxPython class, it uses wxWidgets C-Style function names.
# supress the complaint throughout.
# pylint: disable=invalid-name

import wx

from utils import bc_log, ERROR_COLOUR

# LIMITS SET HERE
MIN_ROUNDS = 1
MAX_ROUNDS = 20
WARN_ROUNDS = 14  # almost never will we want more than 13 rounds

MIN_LENGTH = 1
MAX_LENGTH = 210
WARN_LENGTH = 80  # almost never will we want round length > 12 boards.

MIN_BREAK_LENGTH = 0
MAX_BREAK_LENGTH = 100
WARN_BREAK_LENGTH = 7  # almost never will we want a long break


class BridgeClockValidateError(ValueError):
    """Raised when the value of a text box is wrong or out of bounds."""


class RoundCountValidator(wx.Validator):
    """Round count: range(1, 21)"""

    def __init__(self):
        """bind EVT_TEXT to validate while typing."""

        super().__init__()
        self.Bind(wx.EVT_TEXT, self.on_char)

    def Clone(self):
        """Clone the validator.  Required by wx."""

        return RoundCountValidator()

    def TransferToWindow(self):
        """Return False if data transfer to the window fails."""

        return True

    def TransferFromWindow(self):
        """Return False if data transfer from the window fails."""

        return True

    def _validate(self, value: str) -> None:
        """Do the validation. Throws BridgeClockValidationError on fail."""

        try:
            count = int(value)
        except ValueError as e:
            raise BridgeClockValidateError("Round Count must be an integer") from e
        if count not in range(MIN_ROUNDS, MAX_ROUNDS + 1):
            raise BridgeClockValidateError(
                f"Please select between {MIN_ROUNDS} and {MAX_ROUNDS} rounds."
            )

    # pylint: disable=unused-argument
    def Validate(self, parent):
        """Number of rounds: int, between 1 and MAX, warn if excessive."""

        ctrl = self.GetWindow()
        text = ctrl.GetValue()
        try:
            self._validate(text)
        except BridgeClockValidateError as e:
            wx.MessageBox(str(e))
            return False

        # valid, see if we want to warn
        if int(text) > WARN_ROUNDS:
            wx.MessageBox(f"Confirming: Your game has {text.strip()} rounds.")
        return True

    def on_char(self, event):
        """value changed, light up background if invalid."""

        ctrl = self.GetWindow()
        text = ctrl.GetValue()
        try:
            self._validate(text)
            ctrl.SetBackgroundColour(wx.NullColour)
            ctrl.Refresh()
        except BridgeClockValidateError:
            ctrl.SetBackgroundColour(ERROR_COLOUR)
            ctrl.Refresh()

        # changing round count can invalidate the breaks list, trigger that event
        # doing it by setting its value unchanged.
        text_breaks = ctrl.TopLevelParent.text_break_rounds
        text_breaks.SetValue(text_breaks.GetValue())

        event.Skip()


class RoundLengthValidator(wx.Validator):
    """Round length: int"""

    def __init__(self):
        """bind EVT_TEXT to validate while typing."""

        super().__init__()
        self.Bind(wx.EVT_TEXT, self.on_char)

    def Clone(self):
        """Clone the validator.  Required by wx."""

        return RoundLengthValidator()

    def TransferToWindow(self):
        """Return False if data transfer to the window fails."""

        return True

    def TransferFromWindow(self):
        """Return False if data transfer from the window fails."""

        return True

    def _validate(self, value: str):
        """Do validation. Throw BridgeClockValidateError on error (not warn)."""
        try:
            count = int(value)
        except ValueError as e:
            raise BridgeClockValidateError("Round Length must be an integer") from e
        if count not in range(MIN_LENGTH, MAX_LENGTH + 1):
            raise BridgeClockValidateError(
                "Round length must be between" f"{MIN_LENGTH} and {MAX_LENGTH} rounds"
            )

    # pylint: disable=unused-argument
    def Validate(self, parent):
        """Round length: int, between 1 and MAX, warn if excessive."""

        ctrl = self.GetWindow()
        text = ctrl.GetValue()

        try:
            self._validate(text)
        except BridgeClockValidateError as e:
            wx.MessageBox(str(e))
            return False

        # we're good, but check for excessive length rounds
        if int(text) > WARN_LENGTH:
            wx.MessageBox(f"Confirming: your rounds are {text.strip()} minutes long.")
        return True

    def on_char(self, event):
        """value changed, light up background if invalid."""

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


class BreakValidator(wx.Validator):
    """Breaks: blank, or int, or comma-separated ints, all in 1..rounds"""

    def __init__(self):
        """bind EVT_TEXT to validate while typing."""

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

    def _validate(self, value: str, parent: wx.TextCtrl) -> None:
        """Do the validation. Throws BridgeClockValidationError on fail."""

        if not value:  # no breaks is valid
            return

        try:
            breaks = [int(x) for x in value.split(",")]
        except ValueError as e:
            raise BridgeClockValidateError(
                "break rounds must all be integers. Separate "
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
        """value changed, light up background if invalid."""

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


class BreakLengthValidator(wx.Validator):
    """Break length: int, in minutes."""

    def __init__(self):
        """bind EVT_TEXT to validate while typing."""

        super().__init__()
        self.Bind(wx.EVT_TEXT, self.on_char)

    def Clone(self):
        """Clone the validator.  Required by wx."""

        return BreakLengthValidator()

    def TransferToWindow(self):
        """Return False if data transfer to the window fails."""

        return True

    def TransferFromWindow(self):
        """Return False if data transfer from the window fails."""

        return True

    def _validate(self, value: str):
        """Do validation. Throw BridgeClockValidateError on error (not warn)."""
        try:
            count = int(value)
        except ValueError as e:
            raise BridgeClockValidateError("Break Length must be an integer.") from e
        if count not in range(MIN_BREAK_LENGTH, MAX_BREAK_LENGTH + 1):
            raise BridgeClockValidateError(
                f"Break length must be between {MIN_BREAK_LENGTH}"
                f" and {MAX_BREAK_LENGTH} minutes."
            )

    # pylint: disable=unused-argument
    def Validate(self, parent):
        """Break Length int, between MIN and MAX, warn if large."""

        bc_log("in break length validator")
        ctrl = self.GetWindow()
        text = ctrl.GetValue()
        try:
            self._validate(text)
        except BridgeClockValidateError as e:
            wx.MessageBox(str(e))
            return False

        if int(text) > WARN_BREAK_LENGTH:
            wx.MessageBox(
                f"Confirming: your breaks are each {text.strip()} minutes long."
            )
        return True

    def on_char(self, event):
        """value changed, light up background if invalid."""

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
