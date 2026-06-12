import wx.lib.colourdb

from clock.bridge_clock_main import MyApp

app = MyApp(0)
# need an app before you can play with TheColourDatabase
wx.lib.colourdb.updateColourDB()
app.MainLoop()
