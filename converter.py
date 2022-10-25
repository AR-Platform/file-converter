"""Analyzes or converts the desired file."""
import os
import sys
import normalize
# noinspection PyUnresolvedReferences
from importer import *
# noinspection PyUnresolvedReferences
from exporter import *

import_scripts = []
export_scripts = []

desired_output_format = "ares"


def main():
    """Creates the import and export classes and executes the desired action on the given file."""
    create_io_classes()
    decode_arguments(sys.argv)


# noinspection PyUnresolvedReferences
def create_io_classes():
    """Fetches all available import and export modules and creates the required instances."""
    global import_scripts, export_scripts
    for m in sys.modules:
        if "importer." in m:
            import_scripts.append(sys.modules[m].Import())
        if "exporter." in m:
            export_scripts.append(sys.modules[m].Export())


def decode_arguments(args):
    """Decodes the given argument list and calls the respective function.

    :param args: The console arguments as a list.
    """
    validate_arg_amount(args)
    arg_one = int(sys.argv[1])
    if arg_one == 0:
        print_supported_formats()
        exit()
    elif arg_one == 1:
        analyze_file(args[2], args[3])
    elif arg_one == 2:
        extract_file(args[2], args[3], args[4], args[5])
    else:
        print("Invalid parameter")
        exit()


def validate_arg_amount(args: list):
    """Validates the amount of arguments.

    :param args: The argument list.
    """
    args_length = len(args)
    if args_length >= 2:
        arg_one = int(args[1])
        if arg_one == 0 and args_length == 2:
            return
        elif arg_one == 1 and args_length == 4:
            return
        elif arg_one == 2 and args_length >= 5:
            return
    print("Invalid parameter amount")
    exit()


def print_supported_formats():
    """Outputs all supported file formats to console."""
    for element in import_scripts:
        for file_format in element.supported_formats():
            print(file_format)


def analyze_file(file_path, file_format):
    """Analyzes the desired file with the given file format.

    :param file_path: The path to the file.
    :param file_format: The file format of the file.
    """
    get_correct_io_class(file_format).analyze(file_path)


def extract_file(file_path, file_format, file_output, options):
    """Extracts the desired information from the file with the given file format.

    :param file_path: The path to the file.
    :param file_format: The file format of the file.
    :param file_output: The location of the output file.
    :param options: The options string.
    """
    data = get_correct_io_class(file_format).extract(file_path, options)
    normalize.normalize_data(data)
    get_correct_io_class(desired_output_format, False).export(data, file_output)
    print("Export successful")


def validate_file(file_path):
    """Checks if the given file exists.

    :param file_path: The file to validate.
    """
    if not os.path.isfile(file_path):
        print("File does not exist")
        exit()


def get_file_format(file_path):
    """Fetches the file extension from the given file path.

    :param file_path: The file path.
    :return: The file extension.
    """
    return os.path.splitext(file_path)[1][1:].lower()


def get_correct_io_class(file_format, importer: bool = True):
    """Fetches the correct import / export class for the given file format.

    :param file_format: The desired file format.
    :param importer: Importer desired, default true.
    :return: The import / export class if available.
    """
    for element in import_scripts if importer else export_scripts:
        if file_format in element.supported_formats():
            return element
    print("File format not supported")
    exit()


if __name__ == "__main__":
    main()
