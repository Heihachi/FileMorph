# FileMorph/utils/app_paths.py
import os
import sys
from pathlib import Path


APP_NAME = "FileMorph"


def get_base_path() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent.parent


def get_user_data_dir() -> Path:
    local_appdata = os.getenv("LOCALAPPDATA")
    if local_appdata:
        path = Path(local_appdata) / APP_NAME
    else:
        path = Path.home() / f".{APP_NAME.lower()}"

    path.mkdir(parents=True, exist_ok=True)
    return path


def get_asset_path(*parts: str) -> Path:
    return get_base_path().joinpath(*parts)