import numpy as np

def conv_arc(dist_proj=None, dist=None, ang_size=None):

    """
    resul = conv_arc(2 of dist_proj,dist,ang_size)
    dist_proj en cm, dist en kpc, ang_size en arcsec
    """
    # need to be changed to return the missing one when 2 are given
    if ang_size is None:
        return 3600. * 180. / np.pi * np.arctan(dist_proj / (dist * 3.086e21))
    if dist_proj is None:
        return (dist * 3.086e21) * np.tan(ang_size * np.pi / 180. / 3600.)
