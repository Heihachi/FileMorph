# FileMorph/utils/ffmpeg_checker.py
import shutil
import subprocess
from pathlib import Path

from utils.app_paths import get_base_path


def find_ffmpeg() -> str | None:
    base = get_base_path()
    local_path = base / "ffmpeg" / "bin" / "ffmpeg.exe"

    if local_path.exists():
        return str(local_path)

    path = shutil.which("ffmpeg")
    if path:
        return path

    try:
        result = subprocess.run(
            ["where", "ffmpeg"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            lines = result.stdout.strip().splitlines()
            if lines:
                return lines[0]
    except Exception:
        pass

    return None


def is_ffmpeg_available() -> bool:
    return find_ffmpeg() is not None


def get_ffmpeg_version() -> str | None:
    path = find_ffmpeg()
    if not path:
        return None

    try:
        result = subprocess.run(
            [path, "-version"],
            capture_output=True,
            text=True
        )

        if result.stdout:
            return result.stdout.splitlines()[0]

    except Exception:
        pass

    return None


def get_ffmpeg_full_info() -> str | None:
    path = find_ffmpeg()
    if not path:
        return None

    try:
        result = subprocess.run(
            [path, "-version"],
            capture_output=True,
            text=True
        )
        return result.stdout
    except Exception:
        return None