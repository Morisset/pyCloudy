"""
PyCloudy is a Python library to deal with input and output files of Cloudy (Gary Ferland) photoionization code. 
Is also allows to generate 3D nebula models from various runs of the 1D Cloudy code.

Visit the web page https://sites.google.com/site/pycloudy/
Chris.Morisset@Gmail.com
"""

__all__ = ['c1d', 'c3d', 'utils', 'db']

from .version import __version__

import sys
__pyversion__ = sys.version_info[0]

from .utils.Config import _Config
config = _Config()
log_ = _Config.log_
log_.message('Starting pyCloudy.', calling = 'PyCloudy init')

log_.level=0
config.db_connector = 'PyMySQL'
log_.level=2

from .c1d.cloudy_model import CloudyModel, load_models, CloudyInput, print_make_file, run_cloudy
from .c3d.model_3d import CubCoord, C3D
from .utils.misc import sextract, save, restore
from .utils.physics import CST
from .utils.red_corr import RedCorr
from .utils import astro
from .db.MdB import MdB

log_.message('pyCloudy ready.', calling = 'PyCloudy init')
