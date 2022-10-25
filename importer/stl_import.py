"""Imports or analyzes the given STL file."""
import struct
import os

from interfaces.import_interface import ImportInterface
import numpy as np


# ======================================================================================================================
#    _____ _______ _        _____ __  __ _____   ____  _____ _______
#   / ____|__   __| |      |_   _|  \/  |  __ \ / __ \|  __ \__   __|
#  | (___    | |  | |        | | | \  / | |__) | |  | | |__) | | |
#   \___ \   | |  | |        | | | |\/| |  ___/| |  | |  _  /  | |
#   ____) |  | |  | |____   _| |_| |  | | |    | |__| | | \ \  | |
#  |_____/   |_|  |______| |_____|_|  |_|_|     \____/|_|  \_\ |_|
#
# ======================================================================================================================


class Import(ImportInterface):
    """Import class that contains the STL file import."""

    def supported_formats(self) -> list:
        """Returns the supported formats.

        :return: The supported formats.
        """
        return ["stl"]

    def analyze(self, file_path):
        """Analyzes the file with the given file path and outputs mesh information and options.

        :param file_path: The path to the desired file.
        """
        print("#File is binary: " + str(self.is_binary(file_path)))
        print("#Vertices amount: " + str(self.get_amount_of_vertices(file_path)))
        print("Enable smooth shading:bool")

    def extract(self, file_path, options):
        """Extracts the data from the file.

        :param file_path: The path to the desired file.
        :param options: Options string reflecting the user decisions for the import process.
        """
        vertex_amount = self.get_amount_of_vertices(file_path)
        data = {"polygon": 3, "frames": 1, "vertices": []}
        if self.is_binary(file_path):
            self.extract_binary(data, file_path)
        else:
            self.extract_ascii(data, file_path)

        self.create_connectivity(data, vertex_amount)
        if options == "1":
            self.deduplicate(data)
        return data

    def get_amount_of_vertices(self, file_path):
        """Fetches the amount of vertices in the file.

        :param file_path: The path to the file.
        :return: The amount of vertices.
        """
        if self.is_binary(file_path):
            with open(file_path, "rb") as file:
                file.seek(80)
                amount_bin = file.read(4)
                return struct.unpack("i", amount_bin)[0] * 3
        else:
            with open(file_path, "r") as file:
                return file.read().count("vertex")

    @staticmethod
    def extract_binary(data, file_path):
        """Extracts the geometry information from the file in binary format.

        :param data: The dictionary which will hold the data.
        :param file_path: The path to the file.
        """
        vertices = []
        with open(file_path, "rb") as file:
            file.seek(80)  # Header
            amount = struct.unpack("i", file.read(4))[0]
            for i in range(amount):
                file.seek(12, os.SEEK_CUR)
                for j in range(3):
                    vertices.extend(struct.unpack("f" * 3, file.read(12))[:3])
                file.seek(2, os.SEEK_CUR)
        data["vertices"] = vertices

    @staticmethod
    def extract_ascii(data, file_path):
        """Extracts the geometry information from the file in ascii format.

        :param data: The dictionary which will hold the data.
        :param file_path: The path to the file.
        """
        with open(file_path, "r") as file:
            lines = file.readlines()[1:]
            for line in lines:
                if "vertex" in line:
                    line_split = line.split()
                    line_split = line_split[-3:]
                    list_of_vertex = [float(element) for element in line_split]
                    data["vertices"].extend(list_of_vertex)

    @staticmethod
    def is_binary(file_path):
        """Checks if the file at the given filepath is a binary STL file or in ascii format.

        :param file_path: The path to the file.
        :return: True if the file is binary, else False.
        """
        file_size = os.path.getsize(file_path)
        # Minimum size for binary stl files
        if file_size < 84:
            return False
        with open(file_path, "rb") as file:
            file.seek(80)
            amount = struct.unpack("i", file.read(4))[0]
            return 84 + (amount * 50) == file_size

    @staticmethod
    def create_connectivity(data, vertex_amount):
        """Creates the connectivity data for the given data dictionary.

        :param data: The data dictionary for connectivity data.
        :param vertex_amount: The amount of vertices.
        """
        data["connectivity"] = list(range(vertex_amount))

    @staticmethod
    def deduplicate(data):
        """De-duplicates the given data dictionary.

        :param data: The data dictionary to de-duplicate.
        """
        vertices = np.reshape(data["vertices"], (-1, 3))
        vertex_amount = len(vertices)
        vertex_filter = np.ones(vertex_amount, dtype=bool)
        connectivity = np.array(data["connectivity"])
        for i in range(vertex_amount):
            if not vertex_filter[i]:
                continue
            indices = np.where((vertices == vertices[i]).all(axis=1))[0][1:]
            for index in indices:
                vertex_filter[index] = False
                connectivity[index] = i

        duplicate_amount = 0
        for i in range(vertex_amount):
            if not vertex_filter[i]:
                connectivity[connectivity > i - duplicate_amount] -= 1
                duplicate_amount += 1
        data["vertices"] = vertices[vertex_filter].flatten().tolist()
        data["connectivity"] = connectivity.tolist()
