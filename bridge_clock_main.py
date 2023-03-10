"""Bridge Clock re-write in python"""
import json
from enum import IntEnum
from pathlib import Path
from typing import Tuple, Optional

import wx

from clock_main_frame import RoundTimer, SetupDialog
import validators as vld


class GameSettings:

    # Settings that can be loaded/saved
    ELEMENTS = (
        'rounds', 'round_length',
        'breaks', 'break_length', 'break_visible',
        'sounds', 'manual_restart',
    )
    DEFAULT_SAVE = '_last_settings.json'

    @classmethod
    def settings_dict(cls) -> dict:
        """Provide a template empty dict for settings."""
        return {k: None for k in cls.ELEMENTS}

    def __init__(
        self,
        dict_: Optional[dict] = None,
        rounds: int = 9, round_length: int = 20,
        breaks: Tuple = (4,), break_length: int = 5,
        break_visible: bool = False,
        sounds: bool = False,
        manual_restart: bool = False,
        load_last: Optional[bool] = None,
    ):
        # start with defaults or user-supplied entries
        self.rounds = rounds
        self.round_length = round_length
        self.breaks = breaks
        self.break_length = break_length
        self.break_visible = break_visible
        self.sounds = sounds
        self.manual_restart = manual_restart

        # if load_last is True, use those values instead:
        if load_last is not None and load_last:
            self.load_from_file(Path(self.DEFAULT_SAVE))

        # finally, override with dict values if given
        if dict_ is not None:
            self.update_from_dict(dict_)

    def _save_as_last(self) -> None:
        """Save the current settings for next time."""
        self.save_to_file(Path(self.DEFAULT_SAVE))

    def to_dict(self) -> dict:
        return {k: getattr(self, k) for k in self.ELEMENTS}

    def load_from_file(self, f: Path) -> None:
        try:
            with f.open() as fh:
                data = json.load(fh)
            self.update_from_dict(data)
        except (OSError, json.JSONDecodeError) as e:
            if str(f) != self.DEFAULT_SAVE:  # last settings may not exist
                print(f'Failure to load data!: {e}')

    def save_to_file(self, of: Path) -> None:
        """Save current settings for load later"""

        data = self.to_dict()
        try:
            with of.open('w') as ofh:
                json.dump(data, ofh, indent=2)
        except OSError as e:
            print(f'failed to save data: {e}')

    def update_from_dict(self, new_values: dict) -> None:
        """Update from a dict of values.  Ignore each item if blank."""

        for k, v in new_values.items():
            if k in self.ELEMENTS and v is not None:
                setattr(self, k, v)

    def exit(self) -> None:
        """handle end of game"""

        self._save_as_last()


class StatusbarFields(IntEnum):
    """Constants for the statusbar field sections"""
    ROUND = 0
    MINUTES = 1
    CLOCK = 2


class BridgeTimer(RoundTimer):
    """handler code goes here."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.settings = GameSettings(load_last=True)
        # wxGlade doesn't do timers.  One every second to run the timer,
        # one every minute to update the wall clock on the statusbar.
        self.statusbar_timer = wx.Timer(self)
        self.statusbar_timer.Start(60000)
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_clock_tick)

        self.clock = None
        self.round = 1
        self._game_started = False
        self._game_finished = False
        self._in_break = False  # only True when in visible break

        self._initialize_game()

    def _initialize_game(self) -> None:
        self._game_started = False
        self._pause_game()
        self._round_1()
        self._reset_clock()
        self._update_statusbar()

    def _pause_game(self) -> None:
        """Programmatically "press the pause button"."""
        self.timer.Stop()
        self.button_start.SetLabelText('Start')
        self.button_start.SetValue(False)

    def _round_1(self) -> None:
        """Return to round 1."""
        self.round = 1
        self._update_round()

    def _break_this_round(self) -> bool:
        """if True, go to a break after this round"""
        return self.round in self.settings.breaks

    def _update_round(self) -> None:
        """Change the round label"""
        self.label_round.SetLabelText(f'Round {self.round}')
        self.panel_1.Layout()

    def _reset_clock(self) -> None:
        """reset clock to round_time"""
        self.clock = wx.TimeSpan(0, min=self.settings.round_length, sec=0)
        self._update_clock()

    def _update_clock(self) -> None:
        """Display the current countdown clock value"""
        self.label_clock.SetLabelText(self.clock.Format('%M:%S'))
        self.panel_1.Layout()

    def _update_statusbar(self) -> None:
        """Update the values in the status bar"""
        self.SetStatusText(
            f"Round {self.round} of {self.settings.rounds}",
            StatusbarFields.ROUND,
        )
        self.SetStatusText(
            f"Minutes Per Round: {self.settings.round_length}",
            StatusbarFields.MINUTES,
        )
        self.SetStatusText(
            f"{wx.DateTime.Now().Format('%R')}",
            StatusbarFields.CLOCK,
        )

    def _next_round(self) -> None:
        """Handle Round Change.

        This could:
        - start the next round
        - go to a shown break,
        - start the next round adding time for an invisible break,
        - waiting for a manual restart,
        - ending the game.

        I expect there will be much more logic to add here.
        """
        if self.round < self.settings.rounds:
            if (not self._in_break   # don't repeat break
                and self.settings.break_visible
                    and self._break_this_round()):
                print('Break now!')
                self._go_to_break()
            else:
                self.round += 1
                self._in_break = False
                self._update_round()
                self._reset_clock()
                if (not self.settings.break_visible
                        and self._break_this_round()):
                    self.clock.Add(
                        wx.TimeSpan.Minutes(self.settings.break_length)
                    )
                    self._update_clock()
                self._update_statusbar()
                if self.settings.manual_restart:
                    self._pause_game()
                print('next round!')
        else:  # last round done, game over
            self._game_over()
            self.timer.Stop()

    def _go_to_break(self) -> None:
        """Display a visible hospitality break, and count down."""

        self._in_break = True
        self.label_round.SetLabelText('TIME TO NEXT ROUND:')
        self.clock = wx.TimeSpan.Minutes(self.settings.break_length)
        self._update_clock()

    def _game_over(self) -> None:
        """Game is over."""

        self._pause_game()
        self.label_clock.SetLabelText('Done!')
        self._game_finished = True

    def on_menu_File_save(self, event) -> None:
        # TODO: trigger file dialog, get path
        dlg = wx.FileDialog(
            self,
            message='Save configuration to file',
            defaultDir=str(Path(__file__)),
            wildcard='*.json',
        )
        if dlg.ShowModal() == wx.ID_OK:
            pth = dlg.GetPath()
            self.settings.save_to_file(Path(pth))
        event.Skip()

    def on_menu_File_Load(self, event) -> None:
        dlg = wx.FileDialog(
            self,
            message='Load Configuration From:',
            defaultDir=str(Path(__file__)),
            wildcard='*.json',
        )
        if dlg.ShowModal() == wx.ID_OK:
            pth = Path(dlg.GetPath())
            self.settings.load_from_file(Path(pth))
        event.Skip()

    def on_menu_File_Exit(self, event) -> None:
        self.on_close(event)
        event.Skip()

    def on_menu_Settings_Customize(self, event) -> None:
        print("Event handler 'on_menu_Settings_Customize'")
        with PreferencesDialog(self) as dlg:
            dlg.load(self.settings, self._game_started)
            if dlg.ShowModal() == wx.ID_OK:
                new_values, restart = dlg.get_values()
                self.settings.update_from_dict(new_values)
                self._update_statusbar()
                if restart:
                    self._initialize_game()
        event.Skip()

    def on_menu_view_Buttons(self, event) -> None:
        print("Event handler 'on_menu_view_Buttons' not implemented!")
        event.Skip()

    def on_menu_view_Statusbar(self, event) -> None:
        print("Event handler 'on_menu_view_Statusbar' not implemented!")
        event.Skip()

    def on_menu_Help_About(self, event) -> None:
        print("Event handler 'on_menu_Help_About' not implemented!")
        event.Skip()

    def on_close(self, event) -> None:
        print('closing!')
        if event.CanVeto() and self._game_started and not self._game_finished:
            answer = wx.MessageBox(
                'The game is not over.  Do you really wish to close?',
                'Game not over',
                wx.YES_NO | wx.CANCEL | wx.ICON_WARNING,
                self,
                )
            if answer != wx.YES:
                event.Veto()
                event.Skip()
                return

        self.settings.exit()
        event.Skip()

    @staticmethod
    def _handle_resize(obj: wx.Control, scale_text: str) -> None:
        """Scale text to fit window."""
        # TODO: understand why this is one call behind on maximize.
        w, h = obj.GetSize().Get()
        tw, th = obj.GetTextExtent(scale_text).Get()
        scale = min(h/th, w/tw)
        # old_size = obj.GetFont().GetPointSize()
        new_font = obj.GetFont().Scaled(scale)
        obj.SetFont(new_font)
        # print(f"old: {old_size}, scale: {scale}, "
        #       f"new: {object.GetFont().GetPointSize()}")

    def on_resize(self, event) -> None:
        print("Event handler 'on_resize'")
        self._handle_resize(
            self.label_round,
            'ROUND 8' if self.settings.rounds < 10 else 'ROUND 88',
        )
        self._handle_resize(
            self.label_clock,
            '88:88' if self.settings.round_length < 100 else '888:88',
        )
        self.panel_1.Layout()
        event.Skip()

    def on_button_start(self, event) -> None:
        print("Event handler 'on_button_start', "
              f"clicked = {self.button_start.GetValue()}")

        if self.button_start.GetValue():
            if self._game_finished:
                answer = wx.MessageBox(
                    'The game has ended.  Do you want to start another session '
                    'with the same parameters?',
                    'Start another session',
                    wx.YES_NO | wx.CANCEL,
                    self,
                )
                if answer == wx.YES:
                    self._initialize_game()
            self._game_started = True  # provide "restart" option
            self.button_start.SetLabelText('Pause')
            self.timer.Start(1000)
        else:
            self.button_start.SetLabelText('Start')
            self.timer.Stop()
        event.Skip()

    def on_button_reset(self, event) -> None:
        self._reset_clock()
        event.Skip()

    def on_button_clock_plus(self, event) -> None:
        self.clock.Add(wx.TimeSpan.Minute())
        self._update_clock()
        event.Skip()

    def on_button_clock_minus(self, event) -> None:
        self.clock.Subtract(wx.TimeSpan.Minute())
        if not self.clock.IsPositive():   # took last minute off clock
            self.clock = wx.TimeSpan(0, sec=5)
        self._update_clock()
        event.Skip()

    def on_button_end_round(self, event) -> None:
        self.clock = wx.TimeSpan(0, sec=2)
        self._update_clock()
        event.Skip()

    def on_button_round_plus(self, event) -> None:
        if self.round < self.settings.rounds:
            self.round += 1
            self._update_round()
        event.Skip()

    def on_button_round_minus(self, event) -> None:
        if self.round > 1:
            self.round -= 1
            self._update_round()
        event.Skip()

    def on_clock_tick(self, event) -> None:
        """One of the timers tripped, call the appropriate reaction"""

        if event.Id == self.timer.Id:
            # print('second_tick')
            self.clock.Subtract(wx.TimeSpan.Second())
            self._update_clock()
            if self.clock.IsNegative():
                self._next_round()
        else:
            # print('minute_tick')
            self._update_statusbar()  # do this for all timers
        event.Skip()


class PreferencesDialog(SetupDialog):
    """event handling goes here."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # add validators - DNE in wxGlade
        self.text_round_count.SetValidator(vld.RoundCountValidator())
        self.text_round_length.SetValidator(vld.RoundLengthValidator())
        self.text_break_rounds.SetValidator(vld.BreakValidator())
        self.text_break_length.SetValidator(vld.BreakLengthValidator())

    def load(self, settings: GameSettings, game_started: bool) -> None:
        self.text_round_count.ChangeValue(str(settings.rounds))
        self.text_round_length.ChangeValue(str(settings.round_length))
        self.text_break_rounds.ChangeValue(
            ','.join([str(x) for x in settings.breaks])
        )
        self.text_break_length.ChangeValue(str(settings.break_length))
        self.check_invisible.SetValue(not settings.break_visible)
        self.check_manual.SetValue(settings.manual_restart)
        self.check_sounds.SetValue(settings.sounds)
        if game_started:  # show the restart button
            self.check_restart.Show()
            self.check_restart.SetValue(False)

    def get_values(self) -> Tuple[dict, bool]:

        ret = {
            'rounds': int(self.text_round_count.GetValue()),
            'round_length': int(self.text_round_length.GetValue()),
            'breaks': tuple(
                int(break_round.strip())
                for break_round in self.text_break_rounds.GetValue().split(',')
            ),
            'break_length': int(self.text_break_length.GetValue()),
            'break_visible': not self.check_invisible.GetValue(),
            'manual_restart': self.check_manual.GetValue(),
            'sounds': self.check_sounds.GetValue(),
        }
        return ret, self.check_restart.IsChecked()

    def on_restart_checked(self, event) -> None:
        """Ensure user really wants to restart the game"""

        if self.check_restart.IsChecked():
            answer = wx.MessageBox(
                message="Are you sure you want to restart the game?",
                caption="Game Restart",
                style=wx.YES_NO | wx.CANCEL | wx.ICON_WARNING,
            )
            if answer != wx.YES:
                self.check_restart.SetValue(False)
        event.Skip()


class MyApp(wx.App):
    def OnInit(self):
        self.frame = BridgeTimer(None, wx.ID_ANY, "")
        self.SetTopWindow(self.frame)
        self.frame.Show()
        return True


# end of class MyApp


if __name__ == "__main__":
    app = MyApp(0)
    app.MainLoop()
