# FileMorph/converters/image_converter.py
from pathlib import Path

from PIL import Image

from converters.base import BaseConverter


class ImageConverter(BaseConverter):
    @property
    def supported_input_formats(self) -> list[str]:
        return ["jpg", "jpeg", "png", "webp", "bmp", "tiff"]

    @property
    def supported_output_formats(self) -> list[str]:
        return ["jpg", "png", "webp", "bmp", "tiff"]

    def convert(self, src: Path, dst: Path, options: dict) -> None:

        with Image.open(src) as img:
            img = self._apply_transformations(img, dst, options)
            save_kwargs = self._build_save_kwargs(dst, options)
            img.save(dst, **save_kwargs)

    def _apply_transformations(self, img: Image.Image, dst: Path, options: dict) -> Image.Image:
        width = int(options.get("width", 0) or 0)
        height = int(options.get("height", 0) or 0)
        quality = int(options.get("quality", 90) or 90)
        rotate = int(options.get("rotate", 0) or 0)
        grayscale = bool(options.get("grayscale", False))

        if grayscale:
            img = img.convert("L")

        if rotate in (90, 180, 270):
            img = img.rotate(-rotate, expand=True)

        if width > 0 or height > 0:
            current_width, current_height = img.size

            new_width = width if width > 0 else current_width
            new_height = height if height > 0 else current_height

            img = img.resize((new_width, new_height))

        if dst.suffix.lower() in [".jpg", ".jpeg"] and img.mode in ("RGBA", "LA", "P"):
            background = Image.new("RGB", img.size, (255, 255, 255))
            alpha_source = img.convert("RGBA")
            background.paste(alpha_source, mask=alpha_source.split()[3])
            img = background
        elif dst.suffix.lower() in [".jpg", ".jpeg"] and img.mode not in ("RGB", "L"):
            img = img.convert("RGB")

        _ = quality

        return img

    def _build_save_kwargs(self, dst: Path, options: dict) -> dict:
        quality = int(options.get("quality", 90) or 90)
        ext = dst.suffix.lower()

        save_kwargs = {}

        if ext in [".jpg", ".jpeg", ".webp"]:
            save_kwargs["quality"] = quality

        return save_kwargs