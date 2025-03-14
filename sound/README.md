# How to use the Sounds folder

First: you don't have to care about this:
  - the default installation has all the sounds you "need"
  - you don't have to turn sounds on at all

But if you do care, here's how to use it.

At the moment the following things will play a sound if "Sounds" are enabled:
  - `round_end`: played when the round changes
  - `go_to_break`: played when a (visible) break starts
  - `game_over`: played at the end of the last round

Others will be added 
  (biggest one would be a "do not start any new boards" one set for a specific time, 
  say 2 minutes before round end) 
  as people report a need for them.

**Note: All sounds must be in "mp3" format, 
  be in the main `sound` subdirectory, 
  and end in `.mp3`**

## How it works
- If sounds are enabled in settings,
  - and there is a sound file in the `sound` subdirectory for the trigger:
    it will be played when triggered.
  - if there is no named sound file for the trigger:
    the `default.mp3` sound file will be played.

## Required sound files
If there is no `default.mp3` sound file in the `sound` subdirectory, 
  or if it can't be played, then you will not be allowed to enable sounds for your game.

There is a second "required" sound file, `silence.mp3`. 
This is a second of silence, and is used for testing to ensure sounds work.
If you delete this, things will still work, 
  but you'll get a bunch of beeps you probably don't want when setting up.

## Prebuilt packages
There are subdirectories inside `sound` with pre-set sounds:
- `Beeps`: various beeps
- `SoundOfSilence`: copies of `silence.mp3` for each sound
  (so you can "ignore" specific sounds, or all of them 
  if you're worried "Sounds" might accidentally get turned on in settings)
- `Speech`: for people who want spoken (English) commands.

If you want to use one of those presets, 
  or mix-and-match, 
  or use most of a set and add your own, 
  just copy those files into the main `sound` subdirectory.

## Author note
The main author isn't a fan of automatic sounds, 
  so this will not get the live testing that other parts of the clock do.
But he knows that many people *rely* on automated sounds in their other clocks,
  so understands the need for the option.  
He will fix issues found with the same priority as other non-critical issues,
  but may rely on others to find them.

## License
All sounds here are licensed Free For Use, as follows:
- "Beeps", including the default.mp3, by [floraphonic](https://www.floraphonic.com),
- All the silences, including the main `silence.mp3`, 
  from [Anar Software](https://github.com/anars/blank-audio).
- The "Speech" package, by Anonymous.