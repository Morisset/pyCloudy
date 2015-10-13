import numpy as np
from scipy.interpolate import interp1d
import pyCloudy as pc

## @include copyright.txt
## @test The Sphere module is for test purpose, use C3D instead
class Sphere(object):

    def __init__(self, c1, n_pixels=100, verbose=None, emis_labels=None, list_elem=None, do_2D=False,
                 interp_phy=True, center=True):
        """
        Compute a 3D model from one 1D model (then the 3D model will be a sphere !)
        @ _c1: a CloudyModel object.
        @ n_pixels : size of the cube.
        @ emis_labels : If set, give the list of line labels in CloudyModel that will be interpolate on the cube.
                  If set to [], no lines are computed
        @ list_elem : if set, give the list of elements for which the ionic fracions will be interpolate on the cube.
                  If set to [], no ionic fractions are computed
        @ interp_phy : If set to False, no interpolation of physical parameters (ne, nH, te) is done.
        @ do_2D : is set to True, remove the z-dimension so only a 2D plane is computed.
        @verbose :level of verbosity as defined by my_logging()

        Usage:
        m3 = Sphere(m1,n_pixels=100,
              emis_labels=['H__1__4861A','S_II__6731A','S_II__6716A','O__3__5007A','TOTL__4363A'],
              list_elem=['H','N','O'])
        plt.imshow(m3.emis[1].sum(axis=1)/m3.emis[2].sum(axis=1))
        plt.imshow(m3.ionic['O'][2][0,:,:])
        plt.plot(m3.r_3D.ravel(),m3.te.ravel(),'r.')

        m3 = Sphere(m1,n_pixels=400,do_2D=True)
        plt.imshow(m3.ionic['O'][2])
        plt.plot m3.x,m3.emis[3].sum(axis=1)

        """
        self.log_ = pc.log_
        self.calling = 'Sphere'
        if verbose is not None:
            self.log_.level = verbose
        self._c1 = c1
        self.center = center
        self._init_cub(n_pixels, do_2D)
        self.log_.message('Init with {} pixels'.format(n_pixels), calling = self.calling)
        if do_2D:
            self.log_.message('2D', calling = self.calling)
        else:
            self.log_.message('3D', calling = self.calling)
        
        if interp_phy:
            self._interp_phy()

        if emis_labels is None:
            self.emis_labels = np.asarray(self._c1.emis_labels)
        else:
            self.emis_labels = np.asarray(emis_labels)
        self.n_emis = np.size(self.emis_labels)
        if self.n_emis != 0:
            self._interp_emis()
            
        self.emis_ind = {}
        for i, em in enumerate(self.emis_labels):
            self.emis_ind[em] = i
            
        if list_elem is None:
            self.list_elem = self._c1.list_elem
        else:
            self.list_elem = list_elem
        self.n_elements = np.size(self.list_elem)
        if self.n_elements != 0:
            self._interp_ionic()

    def inter3D(self, var_1D):
        f = interp1d(self._c1.radius, var_1D, bounds_error=False, fill_value=0.)
        res = f(self.r_3D)
        return res
    
    def _init_cub(self, n_pixels, do_2D):
        self.n_pixels_x = n_pixels
        self.n_pixels_y = n_pixels
        if do_2D:
            self.n_pixels_z = 1
        else:
            self.n_pixels_z = n_pixels
        
        a = pc.CubCoord([self.n_pixels_x, self.n_pixels_y, self.n_pixels_z], coeffs=self._c1.r_out, center=self.center)
        self.x = a.x_vec
        self.r_3D = a.r

    def _interp_emis(self):

        self.emis = np.squeeze(np.zeros((self.n_emis, self.n_pixels_x, self.n_pixels_y, self.n_pixels_z)))
        if self.n_emis == 1:
            self.emis = np.expand_dims(self.emis_full, axis=0)
        for i, line in enumerate(self.emis_labels):
            self.log_.message('Interpolating ' + line, calling = self.calling)
            if line in self._c1.emis_labels:
                self.emis[i] = self.inter3D(self._c1.get_emis(line))
            else:
                self.log_.error(line + ' not found in emis', calling = self.calling)

    def _interp_phy(self):
        
        self.log_.message('Interpolating te', calling = self.calling)
        self.te = self.inter3D(self._c1.te)
        self.log_.message('Interpolating ne', calling = self.calling)
        self.ne = self.inter3D(self._c1.ne)
        self.log_.message('Interpolating nH', calling = self.calling)
        self.nH = self.inter3D(self._c1.nH)
        
    def _interp_ionic(self):

        self.ionic = {}
        for elem in self.list_elem:
            if elem in self._c1.ionic_names.keys():
                n_elements = 0
                for ion in np.arange(self._c1.n_ions[elem]):
                    if ion.sum() > 0.0:
                        n_elements = n_elements + 1
                ionic = np.squeeze(np.zeros((n_elements, self.n_pixels_x, self.n_pixels_y, self.n_pixels_z)))
                for i in range(n_elements):
                    self.log_.message('Interpolating ionic {} {}'.format(elem, i), calling = self.calling)
                    ionic[i] = self.inter3D(self._c1.get_ionic(elem, i))
                self.ionic[elem] = ionic
            else:
                self.log_.warn(elem + ' not found in element list.', calling = self.calling)
                
