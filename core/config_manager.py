import json
from pathlib import Path
import platform
import sys
import os
APP_NAME = "YTDX"
ROOT = Path(os.getenv("LOCALAPPDATA", ".")) / APP_NAME


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    root_path = getattr(sys, '_MEIPASS', os.getcwd())

    return os.path.join(root_path, relative_path)


RESOURCE_BASE = Path(resource_path("."))


SYSTEM = platform.system()
CONFIG_PATH = ROOT / "config.json"
BIN_PATH = RESOURCE_BASE / "bin"
DEFAULT_CONFIG = {
    'last_folder': str(Path.home()),
    'dark_mode': False,
    'format_preset': 'Best (video+audio)'
}
FFMPEG_PATH = Path(BIN_PATH) / ('ffmpeg.exe' if SYSTEM == 'Windows' else 'ffmpeg')
FFPROBE_PATH = Path(BIN_PATH) / ('ffprobe.exe' if SYSTEM == 'Windows' else 'ffprobe')


os.environ["PATH"] += os.pathsep + str(BIN_PATH)
os.environ["FFMPEG"] = str(FFMPEG_PATH)
os.environ["FFPROBE"] = str(FFPROBE_PATH)


def load_config():
    try:
        os.makedirs(ROOT, exist_ok=True)
        if Path(CONFIG_PATH).exists():
            with open(CONFIG_PATH, 'r') as f:
                data = json.load(f)
                return {**DEFAULT_CONFIG, **data}
    except Exception:
        pass
    return DEFAULT_CONFIG.copy()


def save_config(cfg):
    try:
        with open(CONFIG_PATH, 'w') as f:
            json.dump(cfg, f)
    except Exception:
        pass
