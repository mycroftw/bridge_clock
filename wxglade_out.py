#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
#
# generated by wxGlade 1.0.5 on Thu Oct 12 20:44:24 2023
#

import wx

# begin wxGlade: dependencies
# end wxGlade

# begin wxGlade: extracode
# end wxGlade


class RoundTimer(wx.Frame):
    def __init__(self, *args, **kwds):
        # begin wxGlade: RoundTimer.__init__
        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.SetSize((800, 600))
        self.SetTitle("Bridge Clock")

        # Menu Bar
        self.frame_menubar = wx.MenuBar()
        wxglade_tmp_menu = wx.Menu()
        item = wxglade_tmp_menu.Append(wx.ID_ANY, "Save Current Profile", "")
        self.Bind(wx.EVT_MENU, self.on_menu_file_save, item)
        item = wxglade_tmp_menu.Append(wx.ID_ANY, "Load Profile", "")
        self.Bind(wx.EVT_MENU, self.on_menu_file_load, item)
        item = wxglade_tmp_menu.Append(wx.ID_ANY, "Exit", "")
        self.Bind(wx.EVT_MENU, self.on_menu_file_exit, item)
        self.frame_menubar.Append(wxglade_tmp_menu, "File")
        wxglade_tmp_menu = wx.Menu()
        item = wxglade_tmp_menu.Append(wx.ID_ANY, "Parameters", "")
        self.Bind(wx.EVT_MENU, self.on_menu_settings_customize, item)
        self.frame_menubar.Append(wxglade_tmp_menu, "Settings")
        wxglade_tmp_menu = wx.Menu()
        self.frame_menubar.i_view_buttons = wxglade_tmp_menu.Append(wx.ID_ANY, "Hide_Buttons", "")
        self.Bind(wx.EVT_MENU, self.on_menu_view_buttons, self.frame_menubar.i_view_buttons)
        self.frame_menubar.i_view_statusbar = wxglade_tmp_menu.Append(wx.ID_ANY, "Hide Statusbar", "")
        self.Bind(wx.EVT_MENU, self.on_menu_view_statusbar, self.frame_menubar.i_view_statusbar)
        self.frame_menubar.Append(wxglade_tmp_menu, "View")
        wxglade_tmp_menu = wx.Menu()
        item = wxglade_tmp_menu.Append(wx.ID_ANY, "About", "")
        self.Bind(wx.EVT_MENU, self.on_menu_help_about, item)
        self.frame_menubar.Append(wxglade_tmp_menu, "Help")
        self.SetMenuBar(self.frame_menubar)
        # Menu Bar end

        self.frame_statusbar = self.CreateStatusBar(3)
        self.frame_statusbar.SetStatusWidths([-1, 200, 50])
        # statusbar fields
        frame_statusbar_fields = ["Round Number:", "Minutes Per Round:", "Time:"]
        for i in range(len(frame_statusbar_fields)):
            self.frame_statusbar.SetStatusText(frame_statusbar_fields[i], i)

        self.panel_1 = wx.Panel(self, wx.ID_ANY)

        self.sizer_1 = wx.BoxSizer(wx.VERTICAL)

        self.label_round = wx.StaticText(self.panel_1, wx.ID_ANY, "Round 1", style=wx.ALIGN_CENTER_HORIZONTAL)
        self.label_round.SetBackgroundColour(wx.Colour(176, 0, 255))
        self.label_round.SetForegroundColour(wx.Colour(255, 255, 255))
        self.label_round.SetFont(wx.Font(36, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 0, "Copperplate Gothic Bold"))
        self.sizer_1.Add(self.label_round, 1, wx.EXPAND, 0)

        self.label_clock = wx.StaticText(self.panel_1, wx.ID_ANY, "20:00", style=wx.ALIGN_CENTER_HORIZONTAL)
        self.label_clock.SetBackgroundColour(wx.Colour(176, 15, 255))
        self.label_clock.SetForegroundColour(wx.Colour(255, 255, 0))
        self.label_clock.SetFont(wx.Font(256, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
        self.sizer_1.Add(self.label_clock, 8, wx.EXPAND, 0)

        sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer_1.Add(sizer_2, 0, wx.EXPAND, 0)

        self.button_start = wx.ToggleButton(self.panel_1, wx.ID_ANY, "Start")
        self.button_start.SetToolTip("Run or pause the clock.")
        sizer_2.Add(self.button_start, 0, 0, 0)

        self.button_reset = wx.Button(self.panel_1, wx.ID_ANY, "Reset")
        self.button_reset.SetToolTip("Reset current round to full round length.")
        sizer_2.Add(self.button_reset, 0, 0, 0)

        self.button_clock_plus = wx.Button(self.panel_1, wx.ID_ANY, "+1 min")
        sizer_2.Add(self.button_clock_plus, 0, 0, 0)

        self.button_clock_minus = wx.Button(self.panel_1, wx.ID_ANY, "-1 min")
        sizer_2.Add(self.button_clock_minus, 0, 0, 0)

        self.button_break = wx.Button(self.panel_1, wx.ID_ANY, "Go To Break")
        self.button_break.SetToolTip("Add an unscheduled break after this round.")
        sizer_2.Add(self.button_break, 0, 0, 0)

        sizer_2.Add((40, 0), 1, wx.ALL, 0)

        self.button_end_round = wx.Button(self.panel_1, wx.ID_ANY, "End Round")
        sizer_2.Add(self.button_end_round, 0, 0, 0)

        self.button_round_plus = wx.Button(self.panel_1, wx.ID_ANY, "+1 Round")
        sizer_2.Add(self.button_round_plus, 0, 0, 0)

        self.button_round_minus = wx.Button(self.panel_1, wx.ID_ANY, "-1 Round")
        sizer_2.Add(self.button_round_minus, 0, 0, 0)

        self.panel_1.SetSizer(self.sizer_1)

        self.Layout()

        self.Bind(wx.EVT_TOGGLEBUTTON, self.on_button_start, self.button_start)
        self.Bind(wx.EVT_BUTTON, self.on_button_reset, self.button_reset)
        self.Bind(wx.EVT_BUTTON, self.on_button_clock_plus, self.button_clock_plus)
        self.Bind(wx.EVT_BUTTON, self.on_button_clock_minus, self.button_clock_minus)
        self.Bind(wx.EVT_BUTTON, self.on_goto_break, self.button_break)
        self.Bind(wx.EVT_BUTTON, self.on_button_end_round, self.button_end_round)
        self.Bind(wx.EVT_BUTTON, self.on_button_round_plus, self.button_round_plus)
        self.Bind(wx.EVT_BUTTON, self.on_button_round_minus, self.button_round_minus)
        self.Bind(wx.EVT_CLOSE, self.on_close, self)
        self.Bind(wx.EVT_SIZE, self.on_resize, self)
        # end wxGlade

    def on_menu_file_save(self, event):  # wxGlade: RoundTimer.<event_handler>
        print("Event handler 'on_menu_file_save' not implemented!")
        event.Skip()

    def on_menu_file_load(self, event):  # wxGlade: RoundTimer.<event_handler>
        print("Event handler 'on_menu_file_load' not implemented!")
        event.Skip()

    def on_menu_file_exit(self, event):  # wxGlade: RoundTimer.<event_handler>
        print("Event handler 'on_menu_file_exit' not implemented!")
        event.Skip()

    def on_menu_settings_customize(self, event):  # wxGlade: RoundTimer.<event_handler>
        print("Event handler 'on_menu_settings_customize' not implemented!")
        event.Skip()

    def on_menu_view_buttons(self, event):  # wxGlade: RoundTimer.<event_handler>
        print("Event handler 'on_menu_view_buttons' not implemented!")
        event.Skip()

    def on_menu_view_statusbar(self, event):  # wxGlade: RoundTimer.<event_handler>
        print("Event handler 'on_menu_view_statusbar' not implemented!")
        event.Skip()

    def on_menu_help_about(self, event):  # wxGlade: RoundTimer.<event_handler>
        print("Event handler 'on_menu_help_about' not implemented!")
        event.Skip()

    def on_button_start(self, event):  # wxGlade: RoundTimer.<event_handler>
        print("Event handler 'on_button_start' not implemented!")
        event.Skip()

    def on_button_reset(self, event):  # wxGlade: RoundTimer.<event_handler>
        print("Event handler 'on_button_reset' not implemented!")
        event.Skip()

    def on_button_clock_plus(self, event):  # wxGlade: RoundTimer.<event_handler>
        print("Event handler 'on_button_clock_plus' not implemented!")
        event.Skip()

    def on_button_clock_minus(self, event):  # wxGlade: RoundTimer.<event_handler>
        print("Event handler 'on_button_clock_minus' not implemented!")
        event.Skip()

    def on_goto_break(self, event):  # wxGlade: RoundTimer.<event_handler>
        print("Event handler 'on_goto_break' not implemented!")
        event.Skip()

    def on_button_end_round(self, event):  # wxGlade: RoundTimer.<event_handler>
        print("Event handler 'on_button_end_round' not implemented!")
        event.Skip()

    def on_button_round_plus(self, event):  # wxGlade: RoundTimer.<event_handler>
        print("Event handler 'on_button_round_plus' not implemented!")
        event.Skip()

    def on_button_round_minus(self, event):  # wxGlade: RoundTimer.<event_handler>
        print("Event handler 'on_button_round_minus' not implemented!")
        event.Skip()

    def on_close(self, event):  # wxGlade: RoundTimer.<event_handler>
        print("Event handler 'on_close' not implemented!")
        event.Skip()

    def on_resize(self, event):  # wxGlade: RoundTimer.<event_handler>
        print("Event handler 'on_resize' not implemented!")
        event.Skip()

# end of class RoundTimer

class SetupDialog(wx.Dialog):
    def __init__(self, *args, **kwds):
        # begin wxGlade: SetupDialog.__init__
        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_DIALOG_STYLE
        wx.Dialog.__init__(self, *args, **kwds)
        self.SetTitle("dialog")

        sizer_1 = wx.BoxSizer(wx.VERTICAL)

        self.panel_1 = wx.Panel(self, wx.ID_ANY)
        sizer_1.Add(self.panel_1, 1, wx.EXPAND, 0)

        sizer_3 = wx.BoxSizer(wx.VERTICAL)

        label_1 = wx.StaticText(self.panel_1, wx.ID_ANY, "Setup Game")
        sizer_3.Add(label_1, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)

        grid_sizer_1 = wx.FlexGridSizer(2, 2, 0, 50)
        sizer_3.Add(grid_sizer_1, 2, wx.ALIGN_CENTER_HORIZONTAL, 0)

        label_2 = wx.StaticText(self.panel_1, wx.ID_ANY, "Number of Rounds:")
        grid_sizer_1.Add(label_2, 0, wx.ALIGN_CENTER_VERTICAL, 0)

        label_3 = wx.StaticText(self.panel_1, wx.ID_ANY, "Minutes per Round:")
        grid_sizer_1.Add(label_3, 0, wx.ALIGN_CENTER_VERTICAL, 0)

        self.text_round_count = wx.TextCtrl(self.panel_1, wx.ID_ANY, "", style=wx.TE_CENTRE)
        self.text_round_count.SetMinSize((50, -1))
        self.text_round_count.SetToolTip("Number of rounds to count (9, 13, ...)")
        grid_sizer_1.Add(self.text_round_count, 0, wx.ALIGN_CENTER, 0)

        self.text_round_length = wx.TextCtrl(self.panel_1, wx.ID_ANY, "", style=wx.TE_CENTRE)
        self.text_round_length.SetMinSize((50, -1))
        self.text_round_length.SetToolTip("Length of each round (minutes).  Include time for round change!")
        grid_sizer_1.Add(self.text_round_length, 0, wx.ALIGN_CENTER, 0)

        label_4 = wx.StaticText(self.panel_1, wx.ID_ANY, "Hospitality Breaks")
        sizer_3.Add(label_4, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)

        grid_sizer_2 = wx.FlexGridSizer(2, 3, 0, 20)
        sizer_3.Add(grid_sizer_2, 2, wx.ALIGN_CENTER_HORIZONTAL, 0)

        label_5 = wx.StaticText(self.panel_1, wx.ID_ANY, "After Rounds (e.g. \"4,9\")")
        grid_sizer_2.Add(label_5, 0, 0, 0)

        label_6 = wx.StaticText(self.panel_1, wx.ID_ANY, "Break Length")
        grid_sizer_2.Add(label_6, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)

        label_7 = wx.StaticText(self.panel_1, wx.ID_ANY, "Invisible?")
        grid_sizer_2.Add(label_7, 0, 0, 0)

        self.text_break_rounds = wx.TextCtrl(self.panel_1, wx.ID_ANY, "", style=wx.TE_CENTRE)
        self.text_break_rounds.SetMinSize((80, -1))
        self.text_break_rounds.SetToolTip("Rounds to give a break after.  If more than one, separate by commas (e.g. 4, 9)")
        grid_sizer_2.Add(self.text_break_rounds, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)

        self.text_break_length = wx.TextCtrl(self.panel_1, wx.ID_ANY, "", style=wx.TE_CENTRE)
        self.text_break_length.SetMinSize((50, -1))
        self.text_break_length.SetToolTip("Minutes to pause for the break.")
        grid_sizer_2.Add(self.text_break_length, 0, wx.ALIGN_CENTER, 0)

        self.check_invisible = wx.CheckBox(self.panel_1, wx.ID_ANY, "")
        self.check_invisible.SetToolTip("If checked, rather than showing a break explicitly, just add the time to the current round.")
        grid_sizer_2.Add(self.check_invisible, 0, wx.ALIGN_CENTER, 0)

        sizer_4 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_3.Add(sizer_4, 1, wx.ALIGN_CENTER_HORIZONTAL, 0)

        self.check_sounds = wx.CheckBox(self.panel_1, wx.ID_ANY, "Sounds:", style=wx.ALIGN_RIGHT)
        self.check_sounds.SetToolTip("Play sounds")
        sizer_4.Add(self.check_sounds, 0, wx.ALIGN_CENTER_VERTICAL, 0)

        self.check_manual = wx.CheckBox(self.panel_1, wx.ID_ANY, "Manually Start Rounds:", style=wx.ALIGN_RIGHT)
        self.check_manual.SetToolTip("If checked, will not automatically start each next round.")
        sizer_4.Add(self.check_manual, 0, wx.EXPAND | wx.LEFT, 30)

        self.check_restart = wx.CheckBox(self.panel_1, wx.ID_ANY, "Restart Game", style=wx.ALIGN_RIGHT)
        self.check_restart.Hide()
        sizer_4.Add(self.check_restart, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 30)

        sizer_2 = wx.StdDialogButtonSizer()
        sizer_1.Add(sizer_2, 0, wx.ALIGN_RIGHT | wx.ALL, 4)

        self.button_ok = wx.Button(self, wx.ID_OK, "")
        self.button_ok.SetDefault()
        sizer_2.AddButton(self.button_ok)

        sizer_2.Add((50, 0), 1, wx.EXPAND, 0)

        self.button_cancel = wx.Button(self, wx.ID_CANCEL, "")
        sizer_2.AddButton(self.button_cancel)

        sizer_2.Realize()

        self.panel_1.SetSizer(sizer_3)

        self.SetSizer(sizer_1)
        sizer_1.Fit(self)

        self.SetAffirmativeId(self.button_ok.GetId())
        self.SetEscapeId(self.button_cancel.GetId())

        self.Layout()

        self.Bind(wx.EVT_CHECKBOX, self.on_restart_checked, self.check_restart)
        # end wxGlade

    def on_restart_checked(self, event):  # wxGlade: SetupDialog.<event_handler>
        print("Event handler 'on_restart_checked' not implemented!")
        event.Skip()

# end of class SetupDialog

class MyApp(wx.App):
    def OnInit(self):
        self.round_timer = RoundTimer(None, wx.ID_ANY, "")
        self.SetTopWindow(self.round_timer)
        self.round_timer.Show()
        return True

# end of class MyApp

if __name__ == "__main__":
    app = MyApp(0)
    app.MainLoop()
