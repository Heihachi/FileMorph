# FileMorph/converters/audio_converter.py
from pathlib import Path

import ffmpeg

from converters.base import BaseConverter


class AudioConverter(BaseConverter):
    @property
    def supported_input_formats(self) -> list[str]:
        return ["mp3", "wav", "flac", "ogg", "aac", "m4a"]

    @property
    def supported_output_formats(self) -> list[str]:
        return ["mp3", "wav", "flac", "ogg", "aac", "m4a"]

    def convert(self, src: Path, dst: Path, options: dict) -> None:
        bitrate = options.get("audio_bitrate", "192k")
        sample_rate = options.get("audio_sample_rate", "44100")

        stream = ffmpeg.input(str(src))
        stream = ffmpeg.output(
            stream,
            str(dst),
            audio_bitrate=bitrate,
            ar=sample_rate
        )

        try:
            ffmpeg.run(stream, overwrite_output=True, quiet=True)
        except ffmpeg.Error as e:
            error_text = e.stderr.decode(errors="replace").strip() if e.stderr else str(e).strip()
            if not error_text:
                error_text = "Неизвестная ошибка ffmpeg."
            raise RuntimeError(f"Ошибка ffmpeg при конвертации аудио:\n{error_text}") from e