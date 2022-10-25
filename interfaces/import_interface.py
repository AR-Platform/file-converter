"""Interface for all file-converter import scripts."""
from abc import ABC, abstractmethod


class ImportInterface(ABC):
    """Importer class interface."""

    @abstractmethod
    def supported_formats(self) -> list:
        """The supported file extensions as a list of strings."""
        pass

    @abstractmethod
    def analyze(self, file_path: str) -> None:
        """Analyzes the file with the given file path and outputs information and options if available.

        :param file_path: The path to the desired file.
        """
        pass

    @abstractmethod
    def extract(self, file_path: str, options: str) -> dict:
        """Extracts the data from the file taking into account the options string.

        :param file_path: The path to the desired file.
        :param options: A string containing the user selected options
        """
        pass
