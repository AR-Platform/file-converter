"""Interface for all file-converter export scripts."""
from abc import ABC, abstractmethod


class ExportInterface(ABC):
    """Exporter class interface."""

    @abstractmethod
    def supported_formats(self) -> list:
        """The supported file extensions as a list of strings."""
        pass

    @abstractmethod
    def export(self, data: list, path: str) -> None:
        """Exports the given data to the desired path.

        :param data: The data dictionary.
        :param path: The path to the export directory.
        """
        pass
