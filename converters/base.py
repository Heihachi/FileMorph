# FileMorph/converters/base.py
from abc import ABC, abstractmethod
from pathlib import Path


class BaseConverter(ABC):

    @abstractmethod
    def convert(self, src: Path, dst: Path, options: dict) -> None:

        raise NotImplementedError

    @property
    @abstractmethod
    def supported_input_formats(self) -> list[str]:

        raise NotImplementedError

    @property
    @abstractmethod
    def supported_output_formats(self) -> list[str]:

        raise NotImplementedError