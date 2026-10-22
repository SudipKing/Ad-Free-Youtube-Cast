# Ad-Free YouTube Cast

Paste a YouTube link, click **Play**, and it opens in a Brave window on your PC.
Brave Shields blocks YouTube ads by default, so playback is ad-free.

## Run

Requires Python 3.10+ (a standard build, not the free-threaded `3.13t`) and [Brave](https://brave.com).

```bash
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:8765.

If Brave is installed somewhere unusual, set `BRAVE_PATH` to the full path of the Brave executable.

## Use from GitHub Pages

GitHub Pages only serves static files, so it hosts the page (`docs/index.html`) while `app.py` keeps running on your PC.

1. In the repo settings, set Pages to deploy from the `main` branch, `/docs` folder.
2. Allow your Pages site to call the local server, then start it:
   ```bash
   set BRAVE_CAST_ORIGINS=https://sudipking.github.io
   python app.py
   ```
3. Open `https://sudipking.github.io/Ad-Free-Youtube-Cast/`. If the browser asks for local network access, allow it.

The page only reaches the server on the same machine; it is not casting to another device.

## Options

- **Clean window**: opens the video as an app window with no tabs or address bar.
- **Fullscreen**: starts the window fullscreen.

Only YouTube links (`youtube.com`, `youtu.be`, `music.youtube.com`) are accepted.
