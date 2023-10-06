"""Validators for the clock settings.

Separate from everything else, because they don't exist in wxGlade,  so
kept here to avoid cluttering up the main flow.

"""
import wx

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

    def __init__(self):
        super().__init__()

    def Clone(self):
        return RoundCountValidator()

    def TransferToWindow(self):
        return True

    def TransferFromWindow(self):
        return True

    def Validate(self, parent):
        print('in round count validator')
        ctrl = self.GetWindow()
        try:
            count = int(ctrl.GetValue())
        except ValueError:
            wx.MessageBox('Round Count must be an integer')
            return False
        if count in range(MIN_ROUNDS, MAX_ROUNDS+1):
            # implement warning
            if count > WARN_ROUNDS:
                wx.MessageBox(f'Confirming: Your game has {count} rounds.')
            return True
        else:
            wx.MessageBox(f'Please select between {MIN_ROUNDS}'
                          f' and {MAX_ROUNDS} rounds.')
            return False


class RoundLengthValidator(wx.Validator):
    """Round length: int"""

    def __init__(self):
        super().__init__()

    def Clone(self):
        return RoundLengthValidator()

    def TransferToWindow(self):
        return True

    def TransferFromWindow(self):
        return True

    def Validate(self, parent):
        print('in round length validator')
        ctrl = self.GetWindow()
        try:
            count = int(ctrl.GetValue())
        except ValueError:
            wx.MessageBox('Round Length must be an integer')
            return False
        if count in range(MIN_LENGTH, MAX_LENGTH+1):
            if count > WARN_LENGTH:
                wx.MessageBox(
                    f'Confirming: your rounds are {count} minutes long.'
                )
            return True
        else:
            wx.MessageBox('Round Length must be between '
                          f'{MIN_LENGTH} and {MAX_LENGTH} minutes.')
            return False


class BreakValidator(wx.Validator):
    """Breaks: blank, or int, or comma-separated ints, all in 1..rounds"""

    def __init__(self):
        super().__init__()

    def Clone(self):
        return BreakValidator()

    def TransferToWindow(self):
        return True

    def TransferFromWindow(self):
        return True

    def Validate(self, parent):
        print('in break validator')
        ctrl = self.GetWindow()
        value = ctrl.GetValue()
        if not len(value):  # no breaks
            return True
        try:
            breaks = [int(x) for x in value.split(',')]
        except ValueError:
            wx.MessageBox('break rounds must all be integers. Separate '
                          "multiple break rounds with commas (e.g. '4,9')")
            return False
        num_rounds = int(parent.TopLevelParent.text_round_count.GetValue())
        break_in_range = [
            break_round in range(1, num_rounds)
            for break_round in breaks
        ]
        if all(break_in_range):
            return True
        else:
            wx.MessageBox('Break rounds must be between round 1 '
                          f'and {num_rounds-1}')
            return False


class BreakLengthValidator(wx.Validator):
    """Round count: range(1, 21)"""

    def __init__(self):
        super().__init__()

    def Clone(self):
        return BreakLengthValidator()

    def TransferToWindow(self):
        return True

    def TransferFromWindow(self):
        return True

    def Validate(self, parent):
        print('in break length validator')
        ctrl = self.GetWindow()
        try:
            count = int(ctrl.GetValue())
        except ValueError:
            wx.MessageBox('Break Length must be an integer.')
            return False
        if count in range(MIN_BREAK_LENGTH, MAX_BREAK_LENGTH+1):
            if count > WARN_BREAK_LENGTH:
                wx.MessageBox(f'Confirming: your breaks are each {count} '
                              'minutes long.')
            return True
        else:
            wx.MessageBox(f'Break length must be between {MIN_BREAK_LENGTH}'
                          f' and {MAX_BREAK_LENGTH} minutes.')
            return False
