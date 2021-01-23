# set version dunder variable
from importlib import metadata

__version__ = metadata.version('jupyfmt')


from .main import main
