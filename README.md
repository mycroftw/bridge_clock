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

At this point, it's pre-release. It works, but that's about all I'll vouch for.
Keeps reasonably correct time, if you don't keep pausing it or letting the
computer hibernate or...

I don't even guarantee that all the options work (I know sound doesn't).

I am now actively testing it in club games, but I know where the holes are :-)
If you're comfortable with ALPHA release, go ahead and try it.
I expect the issues to pile up amazingly.

## Requirements

I have tested a python packager, and it works well.
Unfortunately, with all the malware writers doing the same thing, it is very likely
to get flagged as malware by Microsoft.
Trust me (or check the code), it isn't; but this is a barrier to general release.

Right now it is best to install Python (at least 3.8) and wxPython (Phoenix).
If you don't know how to get those, this is too alpha for you,
so I'm not providing instructions (yet).

Once you have these, download the scripts in the clock subfolder, 
run `python .\bridge_clock_main.py` and enjoy.