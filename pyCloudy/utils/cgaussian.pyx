from __future__ import division
import numpy as np
cimport numpy as np

cpdef np.ndarray gaussian(np.ndarray[double, ndim = 3] x, np.ndarray[double, ndim = 3] zeta_0):
    """
    Return the value of a gaussian function.
    param:
        x
        One of the following parameter must be given:
        zeta_0, sigma or FWHM
    """
    cdef np.ndarray[double, ndim = 3] res 
    res = np.exp(-((x/zeta_0)**2)) /zeta_0 / np.sqrt(np.pi)
    return res
