# FileMorph/utils/file_utils.py
import os
import subprocess
import sys
from pathlib import Path


def ensure_directory(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def build_output_path(src: Path, output_dir: Path | None, target_ext: str) -> Path:
    if output_dir is None:
        output_dir = src.parent

    ensure_directory(output_dir)

    clean_ext = target_ext.lower().lstrip(".")
    return output_dir / f"{src.stem}.{clean_ext}"


def open_path(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Path not found: {path}")

    if sys.platform.startswith("win"):
        os.startfile(str(path))
        return

    if sys.platform == "darwin":
        subprocess.run(["open", str(path)], check=True)
        return

    subprocess.run(["xdg-open", str(path)], check=True)


def unique_output_path(path: Path) -> Path:

    if not path.exists():
        return path

    counter = 1
    while True:
        candidate = path.with_name(f"{path.stem} ({counter}){path.suffix}")
        if not candidate.exists():
            return candidate
        counter += 1