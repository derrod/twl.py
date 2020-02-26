# Warning

This project is some 2-3 years old (though has been updated to the latest APIs) and is *very* incomplete since I never had time/motivation to really finish it. There's a lot of legacy code that should be rewritten and ripped out because I didn't know what I was doing.

The main executable (`twl.py`) is a mess that was meant to only be temporary until I finish writing a proper CLI... That's not going to happen at this rate.

That being said it *does* kinda work.

(You have to `set PYTHONPATH=..` on Windows or the Linux equivalent first).

Authenticate with Twitch (follow on-screen instructions)
```
$ py -3.6 twl.py --auth
```

List games:
```
$ py -3.6 twl.py --list --sort

```

Create aria2c file to download a game
```
$ py -3.6 twl.py -v --install --install-base-dir "twitch" --aria2c --aria2c-file "/tmp/dllist.txt" --game-id <ID>
```
This will also print the aria2c command to download the game.

I left some debug/test code in there that shows how updating/patching works in theory. But I never got around to implementing that.

---------------------------------------------------
# Old README before I gave up

# twl.py (Twitch Launcher.py)

A lightweight, multiplatform downloader/installer/updater for games available through the Twitch App.

## Motivation

I wanted to have a simple, fairly lightweight way of downloading and running the (free) games I got through Twitch Prime without the Twitch App.

Why?
- Twitch App is Windows only
- Twitch App is bloated (Twitch player, Discord clone, WoW/minecraft mod manager, and game distribution platform)
- Twitch App is slow and requires an update nearly every launch (yay Electron)
- Most Games are DRM free and don't require the App

## Features, Scope and ToDo

Already implemented:
 * Login through Twitch directly (no browser required*)
 * Amazon SDS APIs
 * Parsing v1/v2 manifests
 * Download list exporter for aria2c
 * Delta Patching **(untested)**

*Unless manual CAPTCHA solving is required.

Missing features:
 * Downloader
 * Updater
 * Installer (creating shortcuts, running redist installers, etc.)

Out-of-scope/Not planned:
 * FuelPump stuff for DRM and online play

**ToDo**
 * Rewrite main twl.py file (currently hacked together so it kinda works but pretty ugly)
 * Tests
 * pipenv file
 * setup.py file
 * more testing
   + Linux
   + Updating (v1 normal, v2 normal and delta)

