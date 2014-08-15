from logging import my_logging
import os
import numpy as np

class _Config(object):
    """
    This is where to put stuf that all the modules may need to know or use. A kind of COMMON.
    """
    log_ = my_logging()
    
    def __init__(self):

        if 'CLOUDY_EXE' in os.environ:
            self.cloudy_exe = os.environ['CLOUDY_EXE']
        else:
            self.cloudy_exe = 'cloudy.exe'
        
        self.cloudy_dict = {'10.00': '/usr/local/Cloudy/c10.00/cloudy.exe',
                       '13.03': '/usr/local/Cloudy/c13.03/cloudy.exe'}
            
        self.INSTALLED ={}
        try:
            from matplotlib import delaunay
            self.INSTALLED['delaunay'] = True
        except:
            self.INSTALLED['delaunay'] = False
            _Config.log_.warn('pyCloudy works better with matplotlib', calling = 'pyCloudy config')
        try:
            import matplotlib.pyplot as plt
            self.INSTALLED['plt'] = True
        except:
            self.INSTALLED['plt'] = False
        try:
            import pyneb as pn
            self.INSTALLED['PyNeb'] = True
        except:
            self.INSTALLED['PyNeb'] = False
            _Config.log_.warn('pyCloudy works better with PyNeb', calling = 'pyCloudy config')
        try:
            from scipy.integrate import cumtrapz
            from scipy.interpolate import interp1d
            self.INSTALLED['scipy'] = True
        except:
            self.INSTALLED['scipy'] = False
            _Config.log_.warn('pyCloudy works better with scipy', calling = 'pyCloudy config')
        try:
            import Image
            self.INSTALLED['Image'] = True
        except:
            self.INSTALLED['Image'] = False
            _Config.log_.warn('pyCloudy works better with Image (PIL)', calling = 'pyCloudy config')
        try:
            import MySQLdb
            self.INSTALLED['MySQL'] = True
        except:
            self.INSTALLED['MySQL'] = False
        try:
            import pandas
            self.INSTALLED['pandas'] = True
        except:
            self.INSTALLED['pandas'] = False
            
        try:
            test_str = ['#one\t two\t three', '1\t 2\t 3']
            test_res = np.genfromtxt(test_str, names=True, comments= ';', delimiter = '\t')
            if test_res.dtype.fields is None:
                self.INSTALLED['np.genfromtxt new'] = False
            else:
                self.INSTALLED['np.genfromtxt new'] = True
        except:
            self.INSTALLED['np.genfromtxt new'] = False
        if not self.INSTALLED['np.genfromtxt new']:
            _Config.log_.warn('pyCloudy works better with numpy >= 1.6.0', calling = 'pyCloudy config')

        try:
            import multiprocessing as mp
            self.INSTALLED['mp'] = True
            self.Nprocs = mp.cpu_count()
        except:
            self.INSTALLED['mp'] = False
            self.log_.message('multiprocessing not available', calling=self.calling)
            self.Nprocs = 1
        
        self.SAVE_LIST = [['radius', '.rad'],
                          ['continuum', '.cont'],
                          ['physical conditions', '.phy'],
                          ['overview', '.ovr'],
                          ['heating', '.heat'],
                          ['cooling', '.cool'],
                          ['optical depth', '.opd']
                          ]
        
        self.SAVE_LIST_GRAINS = [['grain temperature', '.gtemp'],
                                 ['grain abundances', '.gabund'],
                                 ['grain D/G ratio', '.gdgrat']]
        
        self.SAVE_LIST_ELEMS = [['hydrogen','.ele_H'],
                                ['helium','.ele_He'],
                                ['carbon','.ele_C'],
                                ['nitrogen','.ele_N'],
                                ['oxygen','.ele_O'],
                                ['argon','.ele_Ar'],
                                ['neon','.ele_Ne'],
                                ['sulphur','.ele_S'],
                                ['chlorin','.ele_Cl'],
                                ['iron','.ele_Fe'],
                                ['silicon','.ele_Si']]

    
    def _get_cloudy_exe(self):
        return self.__cloudy_exe
    
    def _set_cloudy_exe(self, value):
        self.__cloudy_exe = value
        _Config.log_.message('cloudy_exe set to {0}'.format(self.__cloudy_exe), calling = '_Config')

    cloudy_exe = property(_get_cloudy_exe, _set_cloudy_exe, None, None)
    