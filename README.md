# bridge_clock
Python replacement for the old windows XP clock I've been using

## Purpose

Bridge round timers have existed for a long time, but standalone ones are still
very expensive and "user-hostile".  I've worked with other timers that try to 
work for purpose, but need to be restarted every round, or can't be easily changed,
or won't pause, or...

I've always liked Rich Waugh's timer, easy to use and flexible, but it has two issues that
limit it's lifespan:
   - Fixed window size of 800x600 - tiny on modern screens
   - Requires an ancient version of MSC controls, which are very hard to find for Windows 10 and
     do not work at all in Windows 11.

Of course, there are several webapp options, which can be very nice.  Most of the tournaments I 
run don't have enough wifi access for me, never mind a webapp.

So, I've written a new one.  It bears a strong resemblance to Rich Waugh's (at least for now), but with
more of the features I want as a tournament director, and avoiding as many of the annoyances as I can.

At this point, it's _very_ prerelease.  It works, but that's about all I'll vouch for.  It's a few days
mostly spent learning wxPython and wxGlade, having not written any GUI this century.  ~I haven't even tested the 
timer to see how far off it is.~  I've tested it now, and fixed the obvious problem.  Keeps reasonably correct time,
if you don't keep pausing it or letting the computer hibernate or...

I don't even guarantee that all the options work (I know sound doesn't).

I am now actively testing it in club games, but I know where the holes are :-)
If you're comfortable with VERY ALPHA release, go ahead and try it.
I expect the issues to pile up amazingly.

## Requirements
I intend to create a standalone executable at some point, but right now it requires Python (at least 3.8) and wxPython
(Phoenix).  If you don't know how to get those, this is too alpha for you, so I'm not providing instructions (yet).

Run `python .\bridge_clock_main.py` and enjoy.