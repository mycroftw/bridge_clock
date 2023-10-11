"""Validators for the clock settings.

Separate from everything else, because they don't exist in wxGlade,  so
kept here to avoid cluttering up the main flow.

"""
# because this is a wxPython class, it uses wxWidgets C-Style function names.
# supress the complaint throughout.
# pylint: disable=invalid-name

import wx

from utils import bc_log

# TODO: figure out how to trigger validators while entering.
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


class RoundCountValidator(wx.Validator):
    """Round count: range(1, 21)"""

    def Clone(self):
        """Clone the validator.  Required by wx."""

        return RoundCountValidator()

    def TransferToWindow(self):
        """Return False if data transfer to the window fails."""

        return True

    def TransferFromWindow(self):
        """Return False if data transfer from the window fails."""

        return True

    # pylint: disable=unused-argument
    def Validate(self, parent):
        """Number of rounds: int, between 1 and MAX, warn if excessive."""

        bc_log('in round count validator')
        ctrl = self.GetWindow()
        try:
            count = int(ctrl.GetValue())
        except ValueError:
            wx.MessageBox('Round Count must be an integer')
            return False
        if count not in range(MIN_ROUNDS, MAX_ROUNDS+1):
            wx.MessageBox(f'Please select between {MIN_ROUNDS}'
                          f' and {MAX_ROUNDS} rounds.')
            return False

        # valid, see if we want to warn
        if count > WARN_ROUNDS:
            wx.MessageBox(f'Confirming: Your game has {count} rounds.')
        return True


class RoundLengthValidator(wx.Validator):
    """Round length: int"""

    def Clone(self):
        """Clone the validator.  Required by wx."""

        return RoundLengthValidator()

    def TransferToWindow(self):
        """Return False if data transfer to the window fails."""

        return True

    def TransferFromWindow(self):
        """Return False if data transfer from the window fails."""

        return True

    # pylint: disable=unused-argument
    def Validate(self, parent):
        """Round length: int, between 1 and MAX, warn if excessive."""

        print('in round length validator')
        ctrl = self.GetWindow()
        try:
            count = int(ctrl.GetValue())
        except ValueError:
            wx.MessageBox('Round Length must be an integer')
            return False
        if count not in range(MIN_LENGTH, MAX_LENGTH+1):
            wx.MessageBox('Round Length must be between '
                          f'{MIN_LENGTH} and {MAX_LENGTH} minutes.')
            return False

        # we're good, but check for excessive length rounds
        if count > WARN_LENGTH:
            wx.MessageBox(f'Confirming: your rounds are {count} minutes long.')
        return True


class BreakValidator(wx.Validator):
    """Breaks: blank, or int, or comma-separated ints, all in 1..rounds"""

    def Clone(self):
        """Clone the validator.  Required by wx."""

        return BreakValidator()

    def TransferToWindow(self):
        """Return False if data transfer to the window fails."""

        return True

    def TransferFromWindow(self):
        """Return False if data transfer from the window fails."""

        return True

    def Validate(self, parent):
        """Break Rounds cs-ints, between 1 and Rounds, or blank (no breaks)."""

        bc_log('in break validator')
        ctrl = self.GetWindow()
        value = ctrl.GetValue()
        if not value:  # no breaks
            return True
        try:
            breaks = [int(x) for x in value.split(',')]
        except ValueError:
            wx.MessageBox('break rounds must all be integers. Separate '
                          "multiple break rounds with commas (e.g. '4,9')")
            return False

        num_rounds = int(parent.TopLevelParent.text_round_count.GetValue())
        break_in_range = [break_round in range(1, num_rounds)
                          for break_round in breaks]
        if not all(break_in_range):
            wx.MessageBox('Break rounds must be between round 1 '
                          f'and {num_rounds-1}')
            return False

        return True


class BreakLengthValidator(wx.Validator):
    """Break length: int, in minutes."""

    def Clone(self):
        """Clone the validator.  Required by wx."""

        return BreakLengthValidator()

    def TransferToWindow(self):
        """Return False if data transfer to the window fails."""

        return True

    def TransferFromWindow(self):
        """Return False if data transfer from the window fails."""

        return True

    # pylint: disable=unused-argument
    def Validate(self, parent):
        """Break Length int, between MIN and MAX, warn if large."""

        bc_log('in break length validator')
        ctrl = self.GetWindow()
        try:
            count = int(ctrl.GetValue())
        except ValueError:
            wx.MessageBox('Break Length must be an integer.')
            return False
        if count not in range(MIN_BREAK_LENGTH, MAX_BREAK_LENGTH+1):
            wx.MessageBox(f'Break length must be between {MIN_BREAK_LENGTH}'
                          f' and {MAX_BREAK_LENGTH} minutes.')
            return False

        if count > WARN_BREAK_LENGTH:
            wx.MessageBox(f'Confirming: your breaks are each {count} '
                          'minutes long.')
        return True
