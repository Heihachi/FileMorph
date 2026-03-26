# FileMorph/converters/video_converter.py
from pathlib import Path

import ffmpeg

from converters.base import BaseConverter


class VideoConverter(BaseConverter):
    @property
    def supported_input_formats(self) -> list[str]:
        return ["mp4", "avi", "mkv", "mov", "webm"]

    @property
    def supported_output_formats(self) -> list[str]:
        return ["mp4", "avi", "mkv", "mov", "webm", "gif"]

    def convert(self, src: Path, dst: Path, options: dict) -> None:
        fps = options.get("video_fps", "")
        resolution = options.get("video_resolution", "")
        codec = options.get("video_codec", "")

        stream = ffmpeg.input(str(src))

        output_kwargs = {}

        if fps:
            output_kwargs["r"] = fps

        if resolution:
            output_kwargs["s"] = resolution

        if codec:
            output_kwargs["vcodec"] = codec

        stream = ffmpeg.output(stream, str(dst), **output_kwargs)

        try:
            ffmpeg.run(stream, overwrite_output=True, quiet=True)
        except ffmpeg.Error as e:
            error_text = e.stderr.decode(errors="replace").strip() if e.stderr else str(e).strip()
            if not error_text:
                error_text = "Неизвестная ошибка ffmpeg."
            raise RuntimeError(f"Ошибка ffmpeg при конвертации видео:\n{error_text}") from e