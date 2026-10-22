"""
Brave Cast: a tiny local server that opens YouTube links in Brave.

Run:   python app.py
Open:  http://127.0.0.1:8765   (or your GitHub Pages copy of docs/index.html)

Brave Shields blocks YouTube ads by default, so the video plays ad-free.
"""

import os
import shutil
import subprocess
from pathlib import Path
from urllib.parse import urlparse

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

HOST = "127.0.0.1"
PORT = 8765
PAGE = Path(__file__).parent / "docs" / "index.html"

# Pages allowed to call this server. Add your GitHub Pages origin here,
# e.g. "https://yourname.github.io".
ALLOWED_ORIGINS = [
    f"http://{HOST}:{PORT}",
    f"http://localhost:{PORT}",
    *filter(None, os.environ.get("BRAVE_CAST_ORIGINS", "").split(",")),
]

YOUTUBE_HOSTS = {"youtube.com", "www.youtube.com", "m.youtube.com",
                 "music.youtube.com", "youtu.be"}


def find_brave() -> str:
    """Locate brave.exe (Windows), brave-browser (Linux) or Brave.app (macOS)."""
    candidates = [
        os.environ.get("BRAVE_PATH"),
        os.path.expandvars(r"%ProgramFiles%\BraveSoftware\Brave-Browser\Application\brave.exe"),
        os.path.expandvars(r"%ProgramFiles(x86)%\BraveSoftware\Brave-Browser\Application\brave.exe"),
        os.path.expandvars(r"%LocalAppData%\BraveSoftware\Brave-Browser\Application\brave.exe"),
        "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
        shutil.which("brave-browser"),
        shutil.which("brave"),
    ]
    for path in candidates:
        if path and Path(path).is_file():
            return path
    raise RuntimeError("Brave not found. Set the BRAVE_PATH environment variable.")


def validate_youtube_url(url: str) -> str:
    parsed = urlparse(url.strip())
    if parsed.scheme not in ("http", "https") or parsed.hostname not in YOUTUBE_HOSTS:
        raise HTTPException(400, "Only YouTube links are allowed.")
    return parsed._replace(scheme="https").geturl()


app = FastAPI(title="Brave Cast")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.middleware("http")
async def private_network_access(request: Request, call_next):
    # Lets an https:// page (GitHub Pages) talk to this localhost server
    # in Chromium-based browsers.
    response = await call_next(request)
    if request.headers.get("access-control-request-private-network"):
        response.headers["Access-Control-Allow-Private-Network"] = "true"
    return response


class PlayRequest(BaseModel):
    url: str
    app_window: bool = True   # clean window without tabs/address bar
    fullscreen: bool = False


@app.get("/")
def index():
    return FileResponse(PAGE)


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/play")
def play(req: PlayRequest):
    url = validate_youtube_url(req.url)
    try:
        brave = find_brave()
    except RuntimeError as e:
        raise HTTPException(500, str(e))

    # Not headless on purpose: a headless browser has no window, so you
    # would hear/see nothing. This opens a normal Brave window with Shields on.
    args = [brave, f"--app={url}" if req.app_window else "--new-window"]
    if not req.app_window:
        args.append(url)
    if req.fullscreen:
        args.append("--start-fullscreen")

    subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return {"status": "playing", "url": url}


if __name__ == "__main__":
    print(f"Brave Cast running at http://{HOST}:{PORT}")
    uvicorn.run(app, host=HOST, port=PORT)
