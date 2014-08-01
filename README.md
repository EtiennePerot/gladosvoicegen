GLaDOS voice generator GUI automation script
--------------------------------------------

**Disclaimer: This script was written years ago. It is extremely dirty. I did not plan to open source this but am doing so anyway due to repeated requests over the years. Use with care and caution.** Risk of sanity loss ahead.

This is the script that powers the Windows/Melodyne GUI automation side of the [GLaDOS voice generator].

It is extremely dirty and extremely brittle. It will assume the following (list may not be exhaustive):

  * All the files in this repo are extracted directly in `C:\` (who cares, it's a single-purpose VM)
  * Melodyne is installed at `C:\Program Files\Celemony\Melodyne.3.2\Melodyne.exe` and is already set up to start normally (no license prompt etc)
  * The following Melodyne keyboard shortcuts are set:
    * `Ctrl+E`: Open export dialog (default setting)
    * `Ctrl+O` Open file dialog (default setting)
    * `A`: Open pitch correction dialog (Edit commands -> Correction macros -> Correct Pitch)
    * `F`: Select formant tool
    * `I`: Invert selection
    * `M`: Change to Pitch Modulation tool
    * `P`: Switch to Pitch Tool
    * `Q`: Quit Melodyne
    * `S`: Select all
  * The folder `Z:\files` exists and contains at least one `.glados.wav` file.
  * You are using Windows XP
  * You are running with the default-color-scheme, non-Luna desktop theme (the Windows-2000-looking one). Check the provided `desktop.png` screenshot to confirm; the window borders and UI text size and font rendering algorithm need to be a pixel-perfect match.
  * You are running at 24-bit color depth (otherwise the provided screenshot bits won't match!)
  * You are extremely patient and dedicated to get this pile of hacks working somehow (if you've read up to this point, you're doing pretty good there)

It required Python 2.x with the following dependencies:

  * [win32all] to do mouse clicks
  * [SendKeys] to send keypresses
  * [PIL] to take screenshots
  * [psyco] to make the brute-force image matching a fair bit faster

You'll likely want the 32-bit version because of these dependencies.

Once you have all this set up, run `glados.py` and hopefully it will give its best shot at converting the `.glados.wav` file it finds in `Z:\files`. If all goes well, it will save the resulting file next to the original file, but with `ok-` in front of the filename and `.glados` replaced by `.done` (so the filename goes from `foo.glados.wav` to `ok-foo.done.wav`). Why? Just because.

The point of storing files in `Z:\files` is so that you can map a shared folder from the host to `Z:\` in the guest. Then you can just drop files in there from the host and have the results be written back to you, all without network connectivity down to the guest. That way you can also just remove all connectivity the guest may have. It's probably safer that way since Windows XP isn't going to get security patches anymore anyway. Then you just need to have something to run `glados.py` every once in a while. The Windows cron equivalent thing can probably do the job, or just write a shell loop that calls the script repeatedly and have that be run on startup. The script will automatically kill possibly-leftover instances of Melodyne using the provided `taskkill.exe` binary. If you don't trust a random binary in some random GitHub repo (which is good!), then check if you already have it in your Windows installation somewhere (it's a [standard Windows tool][taskkill.exe] now), or grab a copy from somewhere else on the Internet.

Also, you may want to tweak the `slowfactor` variable in the `sleep` function to adjust how long the script wait between steps. All the `sleep` calls have their sleep time multiplied by this value. The current value is pretty slow to be on the safe side, so if your VM is consistently faster than the time the sleeps allows for, decrease the `slowfactor`.

Why is this script so dirty? So full of brittle assumptions? Why doesn't it take arguments? Why is it so crappy-looking? Mostly because it was written quickly and meant to be run in a single VM that should never change and continuously get reset, under circumstances which would allow it to work. It's been working fairly well at that for a while. If you feel like making the script more robust, more reliable, or less eye-bleedy, feel free to send a pull request.

[GLaDOS voice generator]: http://glados.biringa.com/
[win32all]: https://sourceforge.net/projects/pywin32/
[SendKeys]: https://pypi.python.org/pypi/SendKeys/0.3
[PIL]: http://www.pythonware.com/products/pil/
[psyco]: http://psyco.sourceforge.net/
[taskkill.exe]: https://www.microsoft.com/resources/documentation/windows/xp/all/proddocs/en-us/taskkill.mspx
