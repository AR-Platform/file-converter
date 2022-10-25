""" Fetches all import modules inside the package. """
from os.path import basename, dirname, isfile, join
from glob import glob

modules = glob(join(dirname(__file__), "*_import.py"))
__all__ = [basename(m)[:-3] for m in modules if isfile(m)]
