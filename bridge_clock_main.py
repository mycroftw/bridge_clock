"""Bridge Clock re-write in python"""

import dataclasses
import json
from dataclasses import dataclass, InitVar
from enum import IntEnum
from pathlib import Path
from typing import Tuple, ClassVar, Callable

import wx
import wx.adv

import validators as vld
from clock_main_frame import RoundTimer, SetupDialog
from utils import bc_log, BREAK_COLOUR, RUN_COLOUR


@dataclass(slots=True)
class GameSettings:
    """Settings for the current timer."""

    dict_: InitVar[dict | None] = None
    rounds: int = 9
    round_length: int = 20
    scheduled_breaks: tuple[int] = (4,)
    unscheduled_breaks: list[int] = dataclasses.field(default_factory=list)
    break_length: int = 5
    break_visible: bool = False
    sounds: bool = False
    manual_restart: bool = False
    load_last: InitVar[bool] = False

    DEFAULT_SAVE: ClassVar[str] = "_last_settings.json"
    NO_SAVE_SETTINGS: ClassVar[tuple] = ("unscheduled_breaks",)

    def __post_init__(self, dict_: dict, load_last: bool) -> None:
        """Load from database if provided or last settings if set."""

        if load_last:
            self.load_from_file(Path(self.DEFAULT_SAVE))
        if dict_ is not None:
            self.update_from_dict(dict_)
        self.unscheduled_breaks = []

    # As far as "go to break" is concerned, doesn't matter if scheduled or
    # requested on the fly
    @property
    def breaks(self) -> tuple:
        """Which rounds have breaks after.

        Includes scheduled breaks or ones manually selected with "go to break" button.
        """

        return tuple(set(list(self.scheduled_breaks) + self.unscheduled_breaks))

    def _save_as_last(self) -> None:
        """Save the current settings for next time."""

        self.save_to_file(Path(self.DEFAULT_SAVE))

    def load_from_file(self, f: Path) -> None:
        """Load settings from json file."""

        try:
            with f.open() as fh:
                data = json.load(fh)
            self.update_from_dict(data)
        except (OSError, json.JSONDecodeError) as e:
            if str(f) != self.DEFAULT_SAVE:  # last settings may not exist
                print(f"Failure to load data!: {e}")

    def save_to_file(self, of: Path) -> None:
        """Save current settings for load later"""

        data = dataclasses.asdict(self)
        for k in self.NO_SAVE_SETTINGS:
            data.pop(k, None)
        try:
            with of.open("w") as ofh:
                json.dump(data, ofh, indent=2)
        except OSError as e:
            print(f"failed to save data: {e}")

    def update_from_dict(self, new_values: dict) -> None:
        """Update from a dict of values.  Ignore each item if blank."""

        for k, v in new_values.items():
            if v is not None:
                try:
                    setattr(self, k, v)
                except AttributeError as e:  # k not in class
                    bc_log(f"Attribute {k} not allowed in Settings: {e}")

    def exit(self) -> None:
        """Save last settings on exit"""

        self._save_as_last()


class StatusbarFields(IntEnum):
    """Constants for the statusbar field sections"""

    ROUND = 0
    MINUTES = 1
    CLOCK = 2


@dataclass
class Accelerator:
    """Information for an accelerator/context menu item."""

    source: wx.Control
    cmd: Callable
    text: str
    keycode: int
    flags: int = wx.ACCEL_NORMAL
    make_menu_item: bool = True
    make_keycode: bool = True


class BridgeTimer(RoundTimer):  # pylint: disable=too-many-ancestors
    """handler code goes here."""

    def __init__(self, *args, **kwargs):

        def _get_accelerators() -> tuple[Accelerator, ...]:
            """Put the accelerators in a space they can be found, out of main init."""

            return (
                Accelerator(
                    self.button_start,
                    self.fire_button_start,
                    "Start/Pause",
                    ord("s"),
                ),
                Accelerator(
                    self.button_clock_plus,
                    self.on_button_clock_plus,
                    "+1 minute",
                    ord("="),
                    flags=wx.ACCEL_SHIFT,  # Shift-= is the "+" key
                ),
                Accelerator(
                    self.button_clock_minus,
                    self.on_button_clock_minus,
                    "-1 minute",
                    ord("-"),
                ),
                Accelerator(
                    self.button_end_round,
                    self.on_button_end_round,
                    "End Round",
                    ord("R"),
                    flags=wx.ACCEL_NORMAL,
                ),
                Accelerator(
                    self.button_end_round,
                    self.on_button_end_round,
                    "",
                    ord("R"),
                    flags=wx.ACCEL_SHIFT,
                    make_menu_item=False,
                ),
                Accelerator(
                    self.button_break,
                    self.on_goto_break,
                    "Go To Break",
                    ord("B"),
                    flags=wx.ACCEL_NORMAL,
                ),
                Accelerator(
                    self.button_break,
                    self.on_goto_break,
                    "Go To Break",
                    ord("B"),
                    flags=wx.ACCEL_SHIFT,
                    make_menu_item=False,
                ),
            )

        super().__init__(*args, **kwargs)
        self.settings = GameSettings(load_last=True)
        # wxGlade doesn't do timers.  One every second to run the timer,
        # one every minute to update the wall clock on the statusbar.
        self.statusbar_timer = wx.Timer(self)
        self.statusbar_timer.Start(60000)
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_clock_tick)

        self.accelerators = _get_accelerators()
        self._context_menu_start = None  # special: the "start/pause" context menu item
        self._create_shortcuts()

        self.round_end = None  # end of round or break
        self.time_left_on_pause = None  # if paused, time left in round or break
        self.round = 1
        self._game_started = False
        self._game_finished = False
        self._in_break = False  # only True when in visible break

        self._initialize_game()

    def _create_shortcuts(self) -> None:
        """Create and bind the context menu items.  Not in wxGlade."""

        self.context_menu = wx.Menu()
        entries = []

        for accelerator in self.accelerators:
            if accelerator.make_menu_item:
                item = self.context_menu.Append(wx.ID_ANY, accelerator.text, "")
                self.Bind(wx.EVT_MENU, accelerator.cmd, item, accelerator.source)
                # special case: start button, store for label change
                if accelerator.source == self.button_start:
                    self._context_menu_start = item
            if accelerator.make_keycode:
                entries.append(
                    wx.AcceleratorEntry(
                        accelerator.flags,
                        accelerator.keycode,
                        accelerator.source.GetId(),
                    )
                )

        self.Bind(wx.EVT_CONTEXT_MENU, self.on_context_menu)
        accelerator_table = wx.AcceleratorTable(entries)
        self.SetAcceleratorTable(accelerator_table)

    def _initialize_game(self) -> None:
        """Put clock in "game ready to start" mode."""

        self._game_started = False
        self._game_finished = False
        self._round_1()
        self._reset_clock()
        self._pause_game()
        self._update_statusbar()

    def _pause_game(self) -> None:
        """Programmatically "press the pause button"."""

        self.timer.Stop()
        self.time_left_on_pause = self.round_end - wx.DateTime.Now()
        self.button_start.SetLabelText("Start")
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

        self.label_round.SetLabelText(f"Round {self.round}")
        self.label_clock.SetBackgroundColour(RUN_COLOUR)
        self.label_round.SetBackgroundColour(RUN_COLOUR)
        self.panel_1.Layout()

    def _reset_clock(self) -> None:
        """reset clock to round_time"""

        minutes = (
            self.settings.break_length if self._in_break else self.settings.round_length
        )
        self.round_end = wx.DateTime.Now() + wx.TimeSpan.Minutes(minutes)
        self._update_clock()

    def _update_clock(self) -> None:
        """Display the current countdown clock value"""

        time_left = self.round_end - wx.DateTime.Now()
        self.label_clock.SetLabelText(time_left.Format("%M:%S"))
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
            if (
                not self._in_break  # don't repeat break
                and self.settings.break_visible
                and self._break_this_round()
            ):
                bc_log("Break now!")
                self._go_to_break()
            else:
                self.round += 1
                self._in_break = False
                self._update_round()
                self._reset_clock()
                if not self.settings.break_visible and self._break_this_round():
                    self.round_end.Add(wx.TimeSpan.Minutes(self.settings.break_length))
                    self._update_clock()
                self._update_statusbar()
                if self.settings.manual_restart:
                    self._pause_game()
                bc_log("next round!")
        else:  # last round done, game over
            self._game_over()
            self.timer.Stop()

    def _go_to_break(self) -> None:
        """Display a visible hospitality break, and count down."""

        self._in_break = True
        self.label_clock.SetBackgroundColour(BREAK_COLOUR)
        self.label_round.SetBackgroundColour(BREAK_COLOUR)
        self.label_round.SetLabelText("TIME TO NEXT ROUND:")
        self.round_end = wx.DateTime.Now() + wx.TimeSpan.Minutes(
            self.settings.break_length
        )
        self._update_clock()

    def _game_over(self) -> None:
        """Game is over."""

        self._pause_game()
        self.label_clock.SetLabelText("Done! ")
        self._handle_resize(self.label_clock, "Done! ")
        self.panel_1.Layout()
        self._game_finished = True
        bc_log(f"End of Game, {wx.DateTime.UNow().Format('%H:%M:%S.%l')}")

    def on_menu_file_save(self, event) -> None:
        dlg = wx.FileDialog(
            self,
            message="Save configuration to file",
            defaultDir=str(Path(__file__)),
            wildcard="*.json",
        )
        if dlg.ShowModal() == wx.ID_OK:
            pth = dlg.GetPath()
            self.settings.save_to_file(Path(pth))
        event.Skip()

    def on_menu_file_load(self, event) -> None:
        dlg = wx.FileDialog(
            self,
            message="Load Configuration From:",
            defaultDir=str(Path(__file__)),
            wildcard="*.json",
        )
        if dlg.ShowModal() == wx.ID_OK:
            pth = Path(dlg.GetPath())
            self.settings.load_from_file(Path(pth))
            if not self._game_started:
                self._initialize_game()
        event.Skip()

    def on_menu_file_exit(self, event) -> None:
        self.Close()
        event.Skip()

    def on_menu_settings_customize(self, event) -> None:
        bc_log("Event handler 'on_menu_settings_customize'")
        with PreferencesDialog(self) as dlg:
            dlg.load(self.settings, self._game_started)
            if dlg.ShowModal() == wx.ID_OK:
                new_values, restart = dlg.get_values()
                self.settings.update_from_dict(new_values)
                self._update_statusbar()
                if not self._game_started or restart:  # reset game
                    self._initialize_game()
        event.Skip()

    def on_menu_view_buttons(self, event) -> None:
        """Hide or show buttons on bottom of clock."""

        show = not event.IsChecked()
        self.sizer_1.Show(self.sizer_2, show=show, recursive=True)
        self.panel_1.Layout()
        event.Skip()

    def on_menu_view_statusbar(self, event) -> None:
        """Hide or show the status bar on bottom of clock."""

        # TODO: currently breaks resizing (#23)
        statusbar = None if event.IsChecked() else self.frame_statusbar
        self.SetStatusBar(statusbar)
        self.Layout()
        self.panel_1.Layout()
        event.Skip()

    def on_menu_help_about(self, event) -> None:
        bc_log("showing About.")
        about_info = wx.adv.AboutDialogInfo()
        about_info.SetVersion("0.1", "Alpha release 0.1, Dec 2 2023")
        about_info.SetName("BridgeTimer")
        about_info.SetCopyright("(C) Michael Farebrother 2023")
        about_info.SetDescription(
            "\nAvailable from https://github.com/mycroftw/bridge_clock\n"
            "Licenced under the GPL v3.\n"
            "\nThanks to Rich Waugh for 20 years of his clock and the inspiration.\n"
            '\n"Next round, please; slow players pass a board"',
        )
        wx.adv.AboutBox(about_info)
        event.Skip()

    def on_context_menu(self, event: wx.ContextMenuEvent) -> None:
        """right click, bring up context menu."""

        pos = event.GetPosition()
        bc_log(f"context menu requested at {pos}, {self.ScreenToClient(pos)}")
        point = (50, 50) if pos == wx.DefaultPosition else self.ScreenToClient(pos)

        # special: set the value of "Start" menu item to the value of the togglebutton
        self._context_menu_start.SetItemLabel(self.button_start.GetLabelText())
        self.PopupMenu(self.context_menu, point)

    def on_close(self, event) -> None:
        bc_log("closing!")
        if event.CanVeto() and self._game_started and not self._game_finished:
            answer = wx.MessageBox(
                "The game is not over.  Do you really wish to close?",
                "Game not over",
                wx.YES_NO | wx.CANCEL | wx.ICON_WARNING,
                self,
            )
            if answer != wx.YES:
                event.Veto()
                return

        self.timer.Stop()
        self.statusbar_timer.Stop()
        self.settings.exit()
        event.Skip()

    @staticmethod
    def _handle_resize(obj: wx.Control, scale_text: str) -> None:
        """Scale text to fit window."""
        w, h = obj.GetSize()
        tw, th = obj.GetTextExtent(scale_text).Get()
        scale = min(h / th, w / tw)
        new_font = obj.GetFont().Scaled(scale)
        obj.SetFont(new_font)

    def on_resize(self, event) -> None:
        # Hack to resolve sizer not auto-sizing with panel on maximize/unmaximize
        self.Layout()
        self.sizer_1.SetDimension(self.panel_1.GetPosition(), self.panel_1.GetSize())
        self._handle_resize(
            self.label_round,
            "ROUND 8" if self.settings.rounds < 10 else "ROUND 88",
        )
        self._handle_resize(
            self.label_clock,
            "88:88" if self.settings.round_length < 100 else "888:88",
        )
        self.panel_1.Layout()
        event.Skip()

    def fire_button_start(self, event) -> None:
        """Convert a menu or keyboard "Start/pause" trigger to togglebutton event."""

        bc_log("toggle start/pause from popupmenu or space key")
        # manually toggle button (wx.EVT_TOGGLEBUTTON does not do this)
        self.button_start.SetValue(not self.button_start.GetValue())

        toggle_event = wx.CommandEvent(
            wx.EVT_TOGGLEBUTTON.typeId, self.button_start.GetId()
        )
        wx.PostEvent(self.button_start.GetEventHandler(), toggle_event)
        event.Skip()

    def on_button_start(self, event) -> None:
        bc_log(
            "Event handler 'on_button_start', "
            f"clicked = {self.button_start.GetValue()}"
        )

        if self.button_start.GetValue():
            if self._game_finished:
                answer = wx.MessageBox(
                    "The game has ended.  Do you want to start another "
                    "session with the same parameters?",
                    "Start another session",
                    wx.YES_NO | wx.CANCEL,
                    self,
                )
                if answer == wx.YES:
                    self._initialize_game()
            self._game_started = True  # provide "restart" option
            self.button_start.SetLabelText("Pause")
            if self.time_left_on_pause:
                self.round_end = wx.DateTime.Now() + self.time_left_on_pause
                self.time_left_on_pause = None
            self.timer.Start(250)
        else:
            self._pause_game()
        event.Skip()

    def on_button_reset(self, event) -> None:
        self._reset_clock()
        event.Skip()

    def on_button_clock_plus(self, event) -> None:
        self.round_end.Add(wx.TimeSpan.Minute())
        self._update_clock()
        event.Skip()

    def on_button_clock_minus(self, event) -> None:
        self.round_end.Subtract(wx.TimeSpan.Minute())
        if self.round_end <= wx.DateTime.Now():
            self.round_end = wx.DateTime.Now() + wx.TimeSpan(0, sec=5)
        self._update_clock()
        event.Skip()

    def on_goto_break(self, event):
        """Add an unscheduled break after this round."""

        # if we're breaking this round already, ignore
        if not self._break_this_round():
            self.settings.unscheduled_breaks.append(self.round)
            if not self.settings.break_visible:  # treat as "add break minutes to clock"
                self.round_end.Add(wx.TimeSpan.Minutes(self.settings.break_length))
                self._update_clock()
        event.Skip()

    def on_button_end_round(self, event) -> None:
        self.round_end = wx.DateTime.Now() + wx.TimeSpan(0, sec=2)
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

        if event.Id == self.timer.GetId():
            # bc_log('second_tick')
            self._update_clock()
            if self.round_end <= wx.DateTime.Now():
                bc_log(
                    "End of Round: clock time: "
                    f"{wx.DateTime.UNow().Format('%H:%M:%S.%l')}"
                )
                self._next_round()
        # otherwise it's the minute tick
        elif self.GetStatusBar():
            self._update_statusbar()  # do this for all timers
        event.Skip()


class PreferencesDialog(SetupDialog):  # pylint: disable=too-many-ancestors
    """event handling goes here."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # add validators - DNE in wxGlade
        self.text_round_count.SetValidator(vld.RoundCountValidator())
        self.text_round_length.SetValidator(vld.RoundLengthValidator())
        self.text_break_rounds.SetValidator(vld.BreakValidator())
        self.text_break_length.SetValidator(vld.BreakLengthValidator())

    def load(self, settings: GameSettings, game_started: bool) -> None:
        """Load Dialog with game's current settings."""

        self.text_round_count.ChangeValue(str(settings.rounds))
        self.text_round_length.ChangeValue(str(settings.round_length))
        self.text_break_rounds.ChangeValue(
            ",".join([str(x) for x in settings.scheduled_breaks])
        )
        self.text_break_length.ChangeValue(str(settings.break_length))
        self.check_invisible.SetValue(not settings.break_visible)
        self.check_manual.SetValue(settings.manual_restart)
        self.check_sounds.SetValue(settings.sounds)
        if game_started:  # show the restart button
            self.check_restart.Show()
            self.check_restart.SetValue(False)
            self.GetSizer().SetSizeHints(self)

    def get_values(self) -> Tuple[dict, bool]:
        """Pull values from dialog.

        Returns a dict containing the settings,
            and a boolean that answers "Shall we restart the game?"

        """

        breaks_raw = self.text_break_rounds.GetValue()
        breaks = breaks_raw.split(",") if breaks_raw else ()

        ret = {
            "rounds": int(self.text_round_count.GetValue()),
            "round_length": int(self.text_round_length.GetValue()),
            "scheduled_breaks": tuple(int(b) for b in breaks),
            "break_length": int(self.text_break_length.GetValue()),
            "break_visible": not self.check_invisible.GetValue(),
            "manual_restart": self.check_manual.GetValue(),
            "sounds": self.check_sounds.GetValue(),
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
    """Run the clock."""

    def OnInit(self):  # pylint: disable=invalid-name
        """Init callback from wx.  Set stuff up and show the clock.

        Because this is an "init-alike", we should ignore "attribute defined
        outside init".

        """

        # pylint: disable-next=attribute-defined-outside-init
        self.frame = BridgeTimer(None, wx.ID_ANY, "")
        self.SetTopWindow(self.frame)
        self.frame.Show()
        return True


# end of class MyApp


if __name__ == "__main__":
    app = MyApp(0)
    app.MainLoop()
