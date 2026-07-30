# bridge_clock

Python replacement for the old Windows XP clock I've been using

## Purpose

Bridge round timers have existed for a long time, but standalone ones are still
very expensive and "user-hostile".  I've worked with other timers that try to 
work for purpose, but need to be restarted every round, or can't be easily changed,
or won't pause, or...

I've always liked
[Rich Waugh's timer (archive.org link)](https://web.archive.org/web/20101120153843/http://bridgeace.com/bridgeprograms.htm),
it's very easy to use and flexible, but it has two issues that limit its lifespan:
   - Fixed window size of 800x600 - tiny on modern screens
- Requires an ancient version of MSC controls
  which are very hard to find for Windows 10,
  and which do not work at all in Windows 11.

There are several webapp options, which can be very nice.
Of course, most of the tournaments I run don't have enough Wi-Fi access for me,
never mind a webapp.

So, I've written a new one.
It bears a strong resemblance to Rich Waugh's (at least for now), but with
more of the features I want as a tournament director,
and avoiding as many of the annoyances as I can.

At this point, it's beta. It works. 
I can run multiples on the same computer, and it's obvious which is which.
It keeps correct time (with a couple of bugs I haven't been able to reproduce).

I don't even guarantee that all the options work. 
Sound now works (but it's - idiosyncratic.  See the [README.md](bridge_clock/sound/README.md) 
  in the sound folder).

I use it in club games and have installed it on at least two computers for other people,
  including a dedicated laptop at my local unit, for use in tournaments.
But I know where the holes are :-)
If you're comfortable with BETA release, go ahead and try it.
I expect the issues to pile up amazingly.

## Requirements

I have tested a python packager, and it works well.
Unfortunately, with all the malware writers doing the same thing, it is very likely
to get flagged as malware by Microsoft.
Trust me (or check the code), it isn't; but this is a barrier to general release.

Right now it is best to install Python (at least 3.8) (optional: in a venv) and the dependencies:
  - `wxPython` (Phoenix)[^1]
  - `playsound3` (for sounds)
  - `pytest` (for automated unit testing - which is coming soon(tm)).  
      I'm going to figure out how to remove this necessity from release builds.

If you don't know how to get those from a `pyproject.toml` file, this is too alpha for you,
so I'm not providing instructions (yet).

Once you have these, download the project, and run `python -m bridge_clock` 
(or `venv/bin/activate && python -m bridge_clock`) and enjoy.

In `clock\utils.py`, there is a `DEBUG` constant.
Set it to False if you like, but if you're going to submit a bug, I'd like the DEBUG log.

Specifics for Windows:

I have created a shortcut on my desktop, with the following parameters:
 - **Target:** `C:\Windows\System32\cmd.exe /k .\venv\Scripts\activate.bat && python -m bridge_clock`
 - **Start in:** `[main folder of project]` (where this file is)

Specifics for Linux:
  - Installing wxPython for Linux is not easy. 
    If you can't use one of the prebuilt wheels and you don't do development on Linux, find someone who does.
  - For `systemd` distros (if you don't know, you probably have one), 
    the following .desktop file works on my machine:
    ```
    [Desktop Entry]
    Name=clock
    Exec=/path/to/clock.sh
    Terminal=True
    Icon=clock
    Type=Application
    ```
    where the clock.sh is
    ``` 
    #! /bin/bash
    source venv/bin/activate
    python -m bridge_clock
    ```
    
## Runtime notes:

1. There are some constants at the top of `clock\utils.py` file.
    - You can set `DEBUG` to `False` if you don't want the random noise being output;
    but if you are submitting a bug, I'd really like the debug output.
    - Feel free to change or add colour palettes - you can use 
    [the named colours](https://github.com/wxWidgets/Phoenix/blob/master/wx/lib/colourdb.py)
    (sorry, source code) or `"#FFFFFF"` style colour strings.
    - **Back up the file** and **Be careful** before changing anything - 
    any mistake will cause the clock to crash on start.
2. Current known "don't do this" bugs:
    - Don't use the `Hide Statusbar` option.
    It breaks the layout unrepairably (see 
    [Issue #24](https://github.com/mycroftw/bridge_clock/issues/24)).
    - Sometimes, especially with "maximize" or repeatedly alternating between 
    showing a description and hiding it, the layout resizing loses its mind.
    Frequently, maximizing and de-maximizing the window will help.
3. 