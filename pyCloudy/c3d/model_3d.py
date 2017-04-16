import numpy as np
from numpy import sin, cos, arctan2, arcsin
import pyCloudy as pc
from pyCloudy.utils import misc
from pyCloudy.utils.physics import atomic_mass
if pc.config.INSTALLED['Triangulation']:
    try:
        from matplotlib.tri.triangulation import Triangulation
    except:
        from matplotlib.delaunay import Triangulation
if pc.config.INSTALLED['scipy']:
    from scipy.interpolate import interp1d
if pc.config.INSTALLED['plt']:
    import matplotlib.pyplot as plt
#from pyCloudy.utils import cgaussian #TEST WITH Cython

## @include copyright.txt
class CubCoord(object):
    """
    Object to generate and manage cube of coordinates
    """
    def __init__(self, dims, center=True, coeffs=1., shift=0., unit='deg', angles=None):
        """
        params:
            - dims [int 1- or 3-elements array-list] dimension of the cube. May be different. One may be 1.
            - center [boolean] if True, the coordinate-center is in the center of the cube, otherwise it's in the corner.
            - coeffs [int 1- or 3-elements array-list] multiplicative coefficients to apply to cartesian coordinates.
            - shift [int 1- or 3-elements array-list] shift applied to the cartesian coordinates, before rotation
            - unit ['deg' or 'rad'] unit for the theta and phi angles. Default is deg.
            - angles [3-elements array-list] (degrees) rotation angles
        """
        self.log_ = pc.log_
        self.calling = 'CubCoord'
        self._unit_coeff = 1. if unit == 'rad' else 180. / np.pi
        if np.asarray(dims).size == 1:
            self.dim_x = self.dim_y = self.dim_z = dims
        else:
            self.dim_x, self.dim_y, self.dim_z = dims
        self.N = self.dim_x * self.dim_y * self.dim_z
        self.log_.message('building a cube of {0.dim_x}x{0.dim_y}x{0.dim_z}'.format(self), calling = self.calling)
        
        if np.asarray(coeffs).size == 1:
            self.coeff_x = self.coeff_y = self.coeff_z = coeffs
        else:
            self.coeff_x, self.coeff_y, self.coeff_z = coeffs

        if np.asarray(shift).size == 1:
            self.shift_x = self.shift_y = self.shift_z = shift
        else:
            self.shift_x, self.shift_y, self.shift_z = shift
            
        start = -1. if center else 0.
        if self.dim_x > 1:
            self.x_vec = np.linspace(start, 1, self.dim_x) * self.coeff_x + self.shift_x
        else:
            self.x_vec = np.zeros(1) + self.shift_x
        if self.dim_y > 1:
            self.y_vec = np.linspace(start, 1, self.dim_y) * self.coeff_y + self.shift_y
        else:
            self.y_vec = np.zeros(1) + self.shift_y
        if self.dim_z > 1:
            self.z_vec = np.linspace(start, 1, self.dim_z) * self.coeff_z + self.shift_z
        else:
            self.z_vec = np.zeros(1) + self.shift_z

        x3, y3, z3 = np.ix_(self.x_vec, self.y_vec, self.z_vec)    

        x1 = np.ones((self.dim_x, 1, 1))
        y1 = np.ones((1, self.dim_y, 1))
        z1 = np.ones((1, 1, self.dim_z))
        
        self._x0 = x3 * y1 * z1
        self._y0 = x1 * y3 * z1
        self._z0 = x1 * y1 * z3
        
        if angles is None:
            self.angles = [0., 0., 0.]
        else:
            self.angles = angles
        self.vel_defined = False
     
    def _update_rot_matrix(self):
        """
        Adjust the rotation matrix after angles been changed.
        """
        a_x = self.angles[0] * np.pi / 180.
        a_y = self.angles[1] * np.pi / 180. 
        a_z = self.angles[2] * np.pi / 180.
        cx = cos(a_x)
        cy = cos(a_y)
        cz = cos(a_z)
        sx = sin(a_x)
        sy = sin(a_y)
        sz = sin(a_z)
        self._rot_matrix = np.asarray([
                               [cy * cz, -cx * sz + sx * sy * cz, sx * sz + cx * sy * cz],
                               [cy * sz, cx * cz + sx * sy * sz, -sx * cz + cx * sy * sz],
                               [-sy, sx * cy, cx * cy]])
        self.log_.message('Rotation matrix by {0[0]}, {0[1]}, {0[2]} degrees.'.format(self.angles)
                          , calling = self.calling)
    
    def _reset_coords(self):
        self.__x = None
        self.__y = None
        self.__z = None
        self.__r = None
        self.__theta = None
        self.__phi = None

    def _get_angles(self):
        return self.__angles
    def _set_angles(self, value):
        if np.size(value) != 3:
            self.log_.error('angles must contain 3 values.', calling = self.calling)
        else:
            self.__angles = np.asarray(value, dtype=float)
            self._update_rot_matrix()
            self._reset_coords()

    ## angles are in degrees. Changing value of angles updates the rotation matrix.
    angles = property(_get_angles, _set_angles, None, "Angles must be a 3-elements list or array. Unit: Degrees")    

    ## x is the cube of y 1rst cartesian coordinates
    @property
    def x(self):
        if self.__x is None:
            self.__x = np.squeeze(self._x0 * self._rot_matrix[0, 0] + 
                                  self._y0 * self._rot_matrix[0, 1] + 
                                  self._z0 * self._rot_matrix[0, 2])
        return self.__x

    ## y is the cube of y 2nd cartesian coordinates
    @property
    def y(self):
        if self.__y is None:
            self.__y = np.squeeze(self._x0 * self._rot_matrix[1, 0] + 
                                  self._y0 * self._rot_matrix[1, 1] + 
                                  self._z0 * self._rot_matrix[1, 2])
        return self.__y

    ## z is the cube of y 3rd cartesian coordinates
    @property
    def z(self):
        if self.__z is None:
            self.__z = np.squeeze(self._x0 * self._rot_matrix[2, 0] + 
                                  self._y0 * self._rot_matrix[2, 1] + 
                                  self._z0 * self._rot_matrix[2, 2])
        return self.__z

    ## r = \f$ \sqrt{x^2+y^2+z^2}\f$
    @property
    def r(self):
        if self.__r is None:
            self.__r = np.squeeze((self.x ** 2 + self.y ** 2 + self.z ** 2) ** 0.5)
        return self.__r

    ## theta \f$ \Theta = arcsin(z/r)\f$
    @property
    def theta(self):
        if self.__theta is None:
            self.__theta = np.zeros_like(self.r)
            oldsettings = np.seterr(all='ignore')
            self.__theta = np.squeeze(arcsin(self.z / self.r)) * self._unit_coeff
            misc.revert_seterr(oldsettings)
            self.__theta[self.r == 0.] = 0.
        return self.__theta
    
    ## phi \f$ \Phi = arctan(y/x)+\pi\f$
    @property
    def phi(self):
        if self.__phi is None:
            self.__phi = (np.squeeze(arctan2(self.y, self.x)) + np.pi) * self._unit_coeff
        return self.__phi
    
    ## delta_x = (x[-1,0,0]-x[0,0,0])/(dim_x -1)
    @property
    def delta_x(self):
        if self.dim_x > 1:
            self.__delta_x = (self._x0[-1, 0, 0] - self._x0[0, 0, 0]) / (self.dim_x - 1)
        else:
            self.__delta_x = 1.
        return self.__delta_x

    ## delta_y = (x[-1,0,0]-x[0,0,0])/(dim_x -1)
    @property
    def delta_y(self):
        if self.dim_y > 1:
            self.__delta_y = (self._y0[0, -1, 0] - self._y0[0, 0, 0]) / (self.dim_y - 1)
        else:
            self.__delta_y = 1.
        return self.__delta_y

    ## delta_x = (x[-1,0,0]-x[0,0,0])/(dim_x -1)
    @property
    def delta_z(self):
        if self.dim_z > 1:
            self.__delta_z = (self._z0[0, 0, -1] - self._z0[0, 0, 0]) / (self.dim_z - 1)
        else:
            self.__delta_z = 1.
        return self.__delta_z
    
    ## cell_size = delta_x * delta_y * delta_z
    @property
    def cell_size(self):
        self.__cell_size = self.delta_x * self.delta_y * self.delta_z
        return self.__cell_size
        
    def _poly(self, params):
        tmp = 0.
        max_r = np.max(self.r)
        for i, param in enumerate(params):
            tmp += param * (self.r/max_r)**i
        oldsettings = np.seterr(all='ignore')
        tmp = tmp / self.r
        misc.revert_seterr(oldsettings)
        tt = (self.r == 0.)
        tmp[tt] = 0
        vel_x = tmp * self.x 
        vel_y = tmp * self.y 
        vel_z = tmp * self.z 
        return vel_x, vel_y, vel_z
    
    def set_velocity(self, velocity_law = 'poly', params = [1., 1., 0.], user_function = None):
        """
        Set a velocity field.
        param:
            - velocity_law [str] one of ['poly','user'].
            - params [list] parameters passed to the velocity function
            - user_function [function] if velocity_law is 'user', this function is used. Must return vel_x, vel_y, vel_z
        """
        vel_dict = {}
        vel_dict['poly'] = self._poly
        vel_dict['user'] = user_function

        if velocity_law is 'user' and user_function is None:
            self.log_.error('Undefined velocity function', calling = self.calling)
            self.vel_defined = False
            return None

        if velocity_law not in vel_dict:
            self.log_.error('Undefined velocity law', calling = self.calling)
            self.vel_defined = False
            return None

        self.vel_x, self.vel_y, self.vel_z = vel_dict[velocity_law](params)
        self.vel = np.sqrt(self.vel_x**2 + self.vel_y**2 + self.vel_z**2)
        self.vel_defined = True
            
## @include copyright.txt
def _get_interp_bi(x_in, gr_x, method=None):
    """
    For each value of x_in, returns _indexes of the closets values (smaller and higher) in the gr_x table. 
    and the corresponding coefficients.
    """
    
    calling = 'interp_2D'
    methods = ['1-dist', 'inter_theta','sphere']
    
    if method is None:
        method = methods[0]
    if method not in methods:
        pc.log_.error('{0} is not a valid method'.format(method), calling = calling)
        return None

    n_points = np.size(x_in)
    n_gr = np.size(gr_x)
    indexes = np.zeros((n_points, 2), dtype=int) - 1
    coeffs = np.zeros((n_points, 2))
    gr_sort = np.argsort(gr_x)
    
    if method == 'inter_theta':
        for i in np.arange(n_gr - 1):
            x1 = gr_x[gr_sort[i]]
            x2 = gr_x[gr_sort[i + 1]]
            tt = (x_in >= x1) & (x_in <= x2)
            ttr = tt.ravel()
            indexes[ttr, 0] = gr_sort[i]
            indexes[ttr, 1] = gr_sort[i]
            coeffs[ttr, 0] = 1.
            coeffs[ttr, 1] = 0.
        return indexes, coeffs
        
    if method == 'sphere':
        indexes[:] = 0.
        coeffs[:, 0] = 1
        coeffs[:, 1] = 0
        return indexes, coeffs
    
    if method == 'cos':
        """Does not work!"""
        def get_coeff(x1, x2, x):
            (cos(x2 / 180. * np.pi) - cos(x / 180. * np.pi)) / (cos(x2 / 180. * np.pi) - cos(x1 / 180. * np.pi))

    if method == '1-dist':
        def get_coeff(x1, x2, x):
            return (x2 - x) / (x2 - x1)
    
    # one have to think to a method for N sectors models, so that no interpolation is done, only affecting one
    # single model to each spaxel.
    if method == '1-dist' or method == 'cos':   
        for i in np.arange(n_gr - 1):
            x1 = gr_x[gr_sort[i]]
            x2 = gr_x[gr_sort[i + 1]]
            tt = (x_in >= x1) & (x_in <= x2)
            ttr = tt.ravel()
            indexes[ttr, 0] = gr_sort[i]
            indexes[ttr, 1] = gr_sort[i + 1]
            coeffs[ttr, 0] = get_coeff(x1, x2, x_in[tt])
            coeffs[ttr, 1] = 1. - coeffs[ttr, 0]
        return indexes, coeffs


## @include copyright.txt
def _get_interp_tri(x_in, y_in, gr_x, gr_y, method=None):
    """
    For each value (x_in, y_in) returns _indexes of the closets 3 values (Delaunay) in the (gr_x, gr_y) table, 
    and the corresponding coefficients.
    @method: tri_surf', 'plan_interp'
    """
    methods = ['tri_surf', 'plan_interp']

    calling = 'interp_3D'
    pc.log_.message('Entering interp 3D', calling = calling)
    if not pc.config.INSTALLED['Triangulation']:
        pc.log_.error('Triangulation package not available from matplotlib.', calling = calling)
        return None
    if method is None:
        method = methods[0]
    if method not in methods:
        pc.log_.error('{0} is not a valid method'.format(method), calling = calling)
        return None
    
    n_points = np.size(x_in)
    indexes = np.zeros((n_points, 3), dtype=int) - 1
    coeffs = np.zeros((n_points, 3))
    if method == 'tri_surf':
        def get_coeff(x, y, P1, P2, P3):
            v1x = P1[0]-x
            v1y = P1[1]-y
            v2x = P2[0]-x
            v2y = P2[1]-y
            v3x = P3[0]-x
            v3y = P3[1]-y
            d1 = abs(v2x*v3y-v2y*v3x)
            d2 = abs(v1x*v3y-v1y*v3x)
            d3 = abs(v1x*v2y-v1y*v2x)
            dsum = d1 + d2 + d3
            return np.squeeze(np.transpose([d1 / dsum, d2 / dsum, d3 / dsum]))
    elif method == 'plan_interp':
        def get_coeff(x, y, P1, P2, P3):
            XY = np.asarray((x, y))
            d1 = misc.dist_point_line(XY, P2, P3) / dpl1
            d2 = misc.dist_point_line(XY, P1, P3) / dpl2
            d3 = misc.dist_point_line(XY, P1, P2) / dpl3
            dsum = d1 + d2 + d3
            return np.squeeze(np.transpose([d1 / dsum, d2 / dsum, d3 / dsum]))

    tri = Triangulation(gr_x, gr_y)
    pc.log_.message('Triangulation done', calling = calling)
    n_triangles = tri.triangle_nodes.shape[0]
    for i, triangle in enumerate(tri.triangle_nodes):
        T1 = np.asarray((gr_x[triangle[0]], gr_y[triangle[0]]))
        T2 = np.asarray((gr_x[triangle[1]], gr_y[triangle[1]]))
        T3 = np.asarray((gr_x[triangle[2]], gr_y[triangle[2]]))
        points_inside = misc.points_inside_triangle(x_in, y_in, T1, T2, T3)
        pc.log_.message('{0} points inside triangle {1} over {2}'.format(points_inside.sum(), i, n_triangles),
                        calling = calling)
        if method == 'plan_interp':
            dpl1 = misc.dist_point_line(T1, T2, T3)
            dpl2 = misc.dist_point_line(T2, T3, T1)
            dpl3 = misc.dist_point_line(T3, T1, T2)
        if points_inside.sum() != 0:
            indexes[points_inside] = triangle
            coeffs[points_inside] = get_coeff(x_in[points_inside], y_in[points_inside], T1, T2, T3)
    return indexes, coeffs

## @include copyright.txt
def _interpol(tab_x, tab_v, x, fill_value = 0., method = 'numpy'):
    if method == 'numpy':
        res = np.interp(x, tab_x, tab_v, left = fill_value, right = fill_value)
    elif method == 'scipy': 
        if pc.config.INSTALLED['scipy']:
            res = np.ones_like(x) * fill_value
            tt = (x >= np.min(tab_x)) & (np.max(tab_x) >= x)
            f = interp1d(tab_x, tab_v)
            res[tt] = f(x[tt])
        else:
            pc.log_.error('Scipy not available, use "numpy" method', calling = 'C3D')    
    return res

## @include copyright.txt
class C3D(object):

    def __init__(self, list_of_models, dims=51, center=True, angles=None, n_dim=2,
                 file_coeffs=None, interp_method = None, plan_sym = False, r_max = None, r_interp_method = 'numpy'):
        """
        Object to create and manage pseudo-3D models.
        param:
            - list_of_models [list of pyCloudy.CloudyModel] list of models, as obtained e.g. by pyCloudy.load_models
            - dims [int 1- or 3-elements array-list] dimension of the cube. May be different. One may be 1.
            - center [boolean] if True, the coordinate-center is in the center of the cube, otherwise it's in the corner.
            - angles [3-elements array-list] (degrees) rotation angles
            - n_dim [int]
            - file_coeffs [str] file_ to store the coeffs (not used yet)
            - interp_method [str] method used for the interpolation of theta and phi
            - plan_sym [Boolean] If True, the theta angles are only from 0 to 90, negative values are obtained by
                mirror symmetry on the equatorial plane
            - r_max [float] (cm) Geometrical size of the cube 
            - r_interp_method [str] method used for the radial interpolation (numpy or scipy)
        """
        self.log_ = pc.log_
        self.calling = 'C3D'
        self.log_.message('Entering C3D', calling = self.calling)
        self.interp_method = interp_method
        self.r_interp_method = r_interp_method
        self.n_dim = n_dim
        self.dims = dims
        self.center = center
        self.plan_sym = plan_sym
        self.r_max = r_max
        ## @todo test validity of models in list of models
        self.m = list_of_models
        self.file_coeffs = file_coeffs
        if self.n_dim == 2:
            self.theta_tab = np.asarray([m1.theta for m1 in self.m])
            self.phi_tab = 0.
        elif self.n_dim == 3:
            self.theta_tab = np.asarray([m1.theta for m1 in self.m])
            self.phi_tab = np.asarray([m1.phi for m1 in self.m])
        else:
            self.m = [self.m]
            self.theta_tab = 0.
            self.phi_tab = 0.
        try:
            self.emis_labels = self.m[0].emis_labels
        except:
            self.emis_labels = None
        self.angles = angles
        self.config_profile()
        self.x_unit = 'arcsec'

    def _init_cub_coord(self):
        if self.r_max is None:
            r_out_tab = np.asarray([m1.r_out_cut for m1 in self.m])
            self.r_max = max(r_out_tab)
        self.cub_coord = CubCoord(self.dims, coeffs=self.r_max, center=self.center, angles=self.angles)
        self.log_.message('CubCoord done.', calling = self.calling)
            
    def _init_coeffs(self):
        ## @todo Need to see how to use this for just create a N-components model, without 3D structure.
        if self.plan_sym:
            cub_theta = np.abs(self.cub_coord.theta)
        else:
            cub_theta = self.cub_coord.theta
        if self.n_dim == 1:
            n_points = self.cub_coord.N
            self._indexes = np.zeros((n_points, 2), dtype=int)
            self._coeffs = np.ones((n_points, 2)) * 0.5
        elif self.n_dim == 2:
            # for any points in cub_coord, we search for the 2 closest models, 
            # defined by the closest lower and higher theta values. The _coeffs are used latter for the interpolation
            self._indexes, self._coeffs = _get_interp_bi(cub_theta, self.theta_tab, method=self.interp_method)
            self.log_.message('interp_bi done.', calling = self.calling)
        elif self.n_dim == 3:
            self._indexes, self._coeffs = _get_interp_tri(cub_theta, self.cub_coord.phi,
                                                        self.theta_tab, self.phi_tab, method=self.interp_method)
            self.log_.message('interp_tri done.', calling = self.calling)
            
    def save_coeffs(self, file_coeffs):
        pc.save(file_coeffs, coeffs=self._coeffs, indexes=self._indexes)
        self.log_.message('{0} saved'.format(file_coeffs), calling = self.calling)
        
    def _load_coeffs(self, file_coeffs):
        dd = pc.restore(file_coeffs)
        self._coeffs = dd['_coeffs']
        self._indexes = dd['_indexes']
        self.log_.message('{0} load'.format(file_coeffs), calling = self.calling)
        
    def _reset_vars(self):
        self.__nH = None
        self.__nHff = None
        self.__ne = None
        self.__nenH = None
        self.__nenHff = None
        self.__te = None
        self.__ff = None
        self.__log_U = None 
        self._emis = {}
        self._profiles = {}
        self._ionic = {}
        self.log_.message('All 3D values reset', calling = self.calling)
        
    def _init_integ_mesh(self):       
        ##
        # @todo the full 3D (with phi) is still not implemented

        n_points = self.cub_coord.N
        r_vect = self.cub_coord.r.ravel()
        self.relative_depth = np.zeros(n_points)
        self._tt2 = {}
        self._c1 = {}
        self._c2 = {}
        self._i1_i2 = []
        self._depth1 = {}
        self._depth2 = {}
        
        for i_1 in np.unique(self._indexes[:, 0]):
            tt1 = (self._indexes[:, 0] == i_1)
            for i_2 in np.unique(self._indexes[tt1, 1]):
                self._i1_i2.append((i_1, i_2))
                tt2 = (self._indexes[:, 1] == i_2) & (self._indexes[:, 0] == i_1)
                self._tt2[(i_1, i_2)] = tt2
                c1 = self._coeffs[tt2, 0]
                c2 = self._coeffs[tt2, 1]
                self._c1[(i_1, i_2)] = c1
                self._c2[(i_1, i_2)] = c2
                
                thickness_1 = self.m[i_1].thickness
                thickness_2 = self.m[i_2].thickness
                # computes the interpolated thickness for the current points 
                thickness_interp = thickness_1 * c1 + thickness_2 * c2
                # computes the interpolated inner radius for the current points
                r_in_interp = self.m[i_1].r_in * c1 + self.m[i_2].r_in * c2
                # relative position (between 0 and 1) of the current points in the depth of the nebula
                relative_depth = (r_vect[tt2] - r_in_interp) / thickness_interp
                # looking for points outside the nebula (R< R_in and R> R_in+depth)
                tt_bad = (relative_depth < 0) | (1 < relative_depth)
                # computes the position of the current points on the m[i_1] and m[i_2] nebulae
                depth_1 = thickness_1 * relative_depth
                depth_2 = thickness_2 * relative_depth
                # prepare the points outside the nebula to be removed from the interpolation
                depth_1[tt_bad] = -1. # depth[i_1][]
                depth_2[tt_bad] = -1.
                self._depth1[i_1] = depth_1
                self._depth2[i_2] = depth_2
                self.relative_depth[tt2] = relative_depth
        self.relative_depth = self.relative_depth.reshape(self.cub_coord.r.shape)
        self.log_.message('Interpolation mesh done', calling = self.calling)

    def _get_3d(self, var):
        ##
        # @todo the full 3D (with phi) is still not implemented
        res = np.zeros(self.cub_coord.N)        
        for i_1, i_2 in self._i1_i2:
            tt2 = self._tt2[(i_1, i_2)]
            V_1 = eval('_interpol(self.m[i_1].depth,self.m[i_1].{0},self._depth1[i_1], method = self.r_interp_method)'.format(var))
            V_2 = eval('_interpol(self.m[i_2].depth,self.m[i_2].{0},self._depth2[i_2], method = self.r_interp_method)'.format(var))
            res[tt2] = V_1 * self._c1[(i_1, i_2)] + V_2 * self._c2[(i_1, i_2)] 
        res = res.reshape(self.cub_coord.r.shape)
        self.log_.message('{0} interpolated using {1}-method'.format(var, self.r_interp_method), calling = self.calling)
        return res

    def _get_angles(self):
        return self.__angles
    
    def _set_angles(self, value):
        self.__angles = value
        self._init_cub_coord()
        if self.file_coeffs is not None:
            self._load_coeffs(self.file_coeffs)
            self.file_coeffs = None
        else:
            self._init_coeffs()
        self._init_integ_mesh()                
        self._reset_vars()
        
    angles = property(_get_angles, _set_angles, None, None)
        
    @property
    def nH(self):
        if self.__nH is None:
            self.__nH = self._get_3d('nH')
        return self.__nH
        
    @property
    def ne(self):
        if self.__ne is None:
            self.__ne = self._get_3d('ne')
        return self.__ne
    
    @property
    def te(self):
        if self.__te is None:
            self.__te = self._get_3d('te')
        return self.__te
    
    @property
    def ff(self):
        if self.__ff is None:
            self.__ff = self._get_3d('ff')
        return self.__ff
    
    @property
    def log_U(self):
        if self.__log_U is None:
            self.__log_U = self._get_3d('log_U')
        return self.__log_U

    @property
    def log_U_mean(self):
        """ log of mean value of U on the volume """
        if self.log_U is not None:
            return np.log10(self.vol_mean(10**self.log_U, 1.))
        else:
            return None      
    
    def get_emis(self, ref):
        """
        Interpolate the emissivity of the referred line on the 3D cube
        param:
            ref [int or str] line reference
        return:
            3D cube of emissivities (erg/s/cm3)
        """
        i_ref = self.m[0]._i_emis(ref)       
        if i_ref is None:
            self.log_.warn('%s is not a valid reference' % str(ref), calling = self.calling)
            return None
        elif i_ref not in self._emis: #test if this emis already computed.
            self._emis[i_ref] = self._get_3d("get_emis({0})".format(i_ref))
        self.emis_labels = self.m[0].emis_labels[self.get_emis_list()]
        return self._emis[i_ref]
    
    def get_emis_list(self, available = False):
        """
        Return the list of labels for the line emissivities
        """
        if available:
            return self.m[0].emis_labels
        else:
            return list(self._emis.keys())
    
    def del_emis(self, ref):
        """
        Delete the emissivity cube associated to the reference
        """
        i_ref = self.m[0]._i_emis(ref)
        if i_ref in self._emis:
            del self._emis[i_ref]
            
    def get_emis_vol(self, ref, at_earth=False):
        """
        Compute the intensity of a line.
        Parameters:
            - ref [int or str]: line reference
            - at_earth:    if True (not default): the result is divided by 4.pi.D2
        return:
            integral of the emissivity of the referred line on the volume of cube (erg/s)
        """
        if at_earth:
            coeff = 4. * np.pi * (self.m[0].distance * pc.CST.KPC) ** 2
        else:
            coeff = 1.
        return self.vol_integ(self.get_emis(ref)) / coeff
    
    ## Hp_mass = \f$ \int m_H.n_{H^+}.dV\f$ [solar mass]
    @property        
    def Hp_mass(self):
        """Return the H+ mass of the nebula in solar mass"""
        return self.vol_integ(self.nH * self.get_ionic('H',1)) * pc.CST.HMASS / pc.CST.SUN_MASS
        
    ## H0_mass = \f$ \int m_H.n_{H^0}.dV\f$ [solar mass]
    @property        
    def H0_mass(self):
        """Return the H0 mass of the nebula in solar mass"""
        return self.vol_integ(self.nH * self.get_ionic('H',0)) * pc.CST.HMASS / pc.CST.SUN_MASS
        
    ## H_mass = \f$ \int m_H.n_{H}.dV\f$ [solar mass]
    @property        
    def H_mass(self):
        """Return the H mass of the nebula in solar mass"""
        return self.vol_integ(self.nH) * pc.CST.HMASS / pc.CST.SUN_MASS
    
    def get_ionic(self, elem, ion):
        """
        Return the 3D cube of ionic fraction corresponding to elem, ion
        """
        if self.m[0].is_valid_ion(elem, ion):
            if (elem, ion) not in self._ionic: #test if this (elem, ion) already computed.
                self._ionic[elem, ion] = self._get_3d("get_ionic('{0}', {1})".format(elem, ion))
            return self._ionic[elem, ion]
        else:
            self.log_.warn('{0} {1} is not a valid ion'.format(elem, ion), calling = self.calling)
            return None
        
    def get_ionic_list(self):
        """
        Return the labels of the computed ionic fraction cubes 
        """
        return list(self._ionic.keys())
    
    def del_ionic(self, elem, ion):
        """
        Delete a ionic fraction cube
        """
        if (elem, ion) in self._ionic:
            del self._ionic[(elem, ion)]
            
    def print_all_emis_vol(self, norm=None):
        """
        Print the intensities of all the lines
        Parameter:
            - norm [str or int]: line ref to nromalize the intnesities
        """
        if norm is None:
            coeff = 1.
        else:
            coeff = self.get_emis_vol(norm)
        for line in self.m[0].emis_labels: print(line,self.get_emis_vol(line)/coeff)
    
    def vol_integ(self, a):
        """
        Volume integrator
        """
        return (a * self.ff * self.cub_coord.cell_size).sum()
    
    def vol_mean(self, a, b):
        """
        Volume weighted integrator.
        Return Integ(a*b) / Integ(b)
        Parameters:
            - a: to be integrated
            - b: the weigth
        """
        return (self.vol_integ(a * b) / self.vol_integ(b))
    
    def get_T0_emis(self, ref):
        """
        Return Integ(Te.Emiss(ref)) / Integ(Emiss(ref))
        """
        return self.vol_mean(self.te, self.get_emis(ref))
    
    def get_t2_emis(self, ref):
        """
        Return Integ((Te-T0)**2.Emiss(ref)) / Integ(Emiss(ref)) / T0**2
        """
        
        T0 = self.get_T0_emis(ref)
        return self.vol_mean((self.te - T0)**2, self.get_emis(ref)) / T0**2
    
    def get_T0_ion_vol(self, elem, ion):
        """
        Return Integ(Te.nH.Xi/X) / Integ(nH.Xi/X)
        """
        nion = self.nH * self.get_ionic(elem, ion)
        return self.vol_mean(self.te,  nion)

    def get_t2_ion_vol(self, elem, ion):
        """
        Return Integ((Te-T0)**2.nH.Xi/X) / Integ(nH.Xi/X) / T0**2
        """        
        nion = self.nH * self.get_ionic(elem, ion)
        T0 = self.get_T0_ion_vol(elem, ion)
        return self.vol_mean((self.te - T0)**2, nion) / T0**2

    def get_T0_ion_vol_ne(self, elem, ion):
        """
        Return Integ(Te.ne.nH.Xi/X) / Integ(ne.nH.Xi/X)
        """        
        nenion = self.ne * self.nH * self.get_ionic(elem, ion)
        return self.vol_mean(self.te, nenion)

    def get_t2_ion_vol_ne(self, elem, ion):
        """
        Return Integ((Te-T0)**2.ne.nH.Xi/X) / Integ(ne.nH.Xi/X) / T0**2
        """
        nenion = self.ne * self.nH * self.get_ionic(elem, ion)
        T0 = self.get_T0_ion_vol_ne(elem, ion)
        return self.vol_mean((self.te - T0)**2, nenion) / T0**2
    
    def get_ab_ion_vol(self, elem=None, ion=None):
        """
        Return Integ(Xi/X.nH / Integ(nH)
        """
        ab_ion = self.get_ionic(elem, ion)
        return self.vol_mean(ab_ion, self.nH)

    def get_ab_ion_vol_ne(self, elem=None, ion=None):
        """
        Return Integ(Xi/X.ne.nH / Integ(ne.nH)
        """
        ab_ion = self.get_ionic(elem, ion)
        return self.vol_mean(ab_ion, self.ne * self.nH)
    
    def get_vel_ionic(self, elem, ion):
        """
        return the velocity weigthed by the ionic fraction
        param:
            elem [str] element 
            ion [int] ionic stage
            
        """
        if not self.cub_coord.vel_defined:
            self.log_.warn('Velocity not defined', calling = self.calling)
            return None
        else:
            return (self.cub_coord.vel * self.get_ionic(elem, ion)).sum() / self.get_ionic(elem, ion).sum()

    def get_vel_emis(self, ref):
        """
        return the velocity weigthed by the line emissivity
        param:
            ref [int or str] a line reference
        """
        if not self.cub_coord.vel_defined:
            self.log_.warn('Velocity not defined', calling = self.calling)
            return None
        else:
            return (self.cub_coord.vel * self.get_emis(ref)).sum() / self.get_emis(ref).sum()
    
    def _get_v_turb(self):
        """
        This return the turbulent velocity (km/s) added quadratically to the thermal velocity.
        """
        return self.__v_turb
    
    def _set_v_turb(self, value):
        self.__v_turb = value
        self.del_profile()
        
    v_turb = property(_get_v_turb, _set_v_turb, None, 'Turbulent velocity (km/s)')
    
    def _get_size_spectrum(self):
        return self.__size_spectrum

    def _set_size_spectrum(self, value):
        self.__size_spectrum = value
        self.vel_tab = np.linspace(-1*self.vel_max, self.vel_max, self.size_spectrum)
        self.del_profile()

    size_spectrum = property(_get_size_spectrum, _set_size_spectrum, None, "size of the array to compute line profile (pixels)")

    def _get_vel_max(self):
        return self.__vel_max

    def _set_vel_max(self, value):
        self.__vel_max = value
        self.vel_tab = np.linspace(-1*self.vel_max, self.vel_max, self.size_spectrum)
        self.del_profile()

    vel_max = property(_get_vel_max, _set_vel_max, None, "Line profiles computed between -vel_max and +vel_max")

    def _set_pf(self, value):
        if value == 'misc_gaussian':
            self.__profile_function = misc.gaussian
 #       elif value == 'cython_gaussian':
 #           self.__profile_function = cgaussian.gaussian
        elif value == 'gaussian':
            sqpi = np.sqrt(np.pi)
            self.__profile_function = lambda x, zeta_0: np.exp(-((x/zeta_0)**2)) / zeta_0 / sqpi
        else:
            self.__profile_function = value
        self.del_profile()
        
    def _get_pf(self):
        return self.__profile_function
     
    profile_function = property(_get_pf, _set_pf, None, 'Profile function for the line profile f(x, zeta_0)')

    def set_velocity(self, *args, **kwargs):
        """
        Call cub_coord.set_velocity with the same parameters and reset profiles.
        """
        self.cub_coord.set_velocity(*args, **kwargs)
        self.del_profile()
    
    def config_profile(self, size_spectrum = 21, vel_max = 20., v_turb = 5., profile_function = 'gaussian'):
        """
        param:
            - size_spectrum [int] size of the array to compute emission line profiles
            - vel_max [float] (km/s) the line profiles are computed on the [-vel_max, vel_max] array
            - v_turb [float] (km/s) turbulent velocity
            - profile_function ['gaussian' or a function] shape of the profile. If not 'gaussian', a user defined
                function must be provide, taking x and zeta_0 as arguments.
        """
        self.__size_spectrum = size_spectrum # doing this because vel_max still undefined
        self.vel_max = vel_max
        self.v_turb = v_turb
        self.profile_function = profile_function
        
    def get_profile(self, ref, axis = 'x'):
        """
        return: 
            the emission line profiles as a 3D spectral data of shape (size_spectrum, dim1, dim2), 
            where dim1 and dim2 are the dimensions in the directions not being the axis. 
        param:
            ref [int or str] line reference
            axis [one of 'x', 'y', 'z', 0, 1, 2] projection axis for the line profile
        """
        l_ref = self.m[0]._l_emis(ref)       
        if l_ref is None:
            self.log_.warn('{0} is not a valid reference'.format(ref), calling = self.calling)
            return None
        if axis not in ('x', 'y', 'z', 0, 1, 2):
            self.log_.warn('{0} is not a valid axis'.format(axis), calling = self.calling)
            return None            
        if (l_ref, axis) not in self._profiles: #test if this profile already computed.
            self._profiles[(l_ref, axis)] = self._calc_profile(ref, axis=axis)
        return self._profiles[(l_ref, axis)]
    
    def get_profile_list(self):
        """
        Return the labels of the computed line profiles
        """
        return list(self._profiles.keys())
    
    def del_profile(self, ref = None, axis = 'x'):
        """
        Delete a line profile cube.
        """
        if ref is None:
            self._profiles = {}
        else:
            l_ref = self.m[0]._l_emis(ref)       
            if (l_ref, axis) in self._profiles:
                del self._profiles[(l_ref, axis)]
                
    def plot_profiles(self, Nx = 10, Ny = 10, ref = None, axis = 'x', normalized = True, i_fig = None, 
                      transp = True, color = 'yellow', pos_x0 = 0., pos_y0 = 0., pos_dx = 1.0, pos_dy = 1.0):
        """
        Still experimental. Some problem with the size and shape of the axes.
        """
        if not pc.config.INSTALLED['plt']:
            pc.log_.error('matplotlib.pyplot not installed')
            return None
        
        profs = self.get_profile(ref, axis)

        size_x = profs.shape[1]
        size_y = profs.shape[2]
        if (Nx > size_x) or (Ny > size_y):
            pc.log_.warn('Nx and Ny must be smaller or equal to the size of the image ({0}x{1})'.format(size_x, size_y))
            return None
        sx = size_x / Nx
        sy = size_y / Ny
        dx = (size_x - (sx * Nx)) / 2
        dy = (size_y - (sy * Ny)) / 2
        fig = plt.figure(i_fig)
        for ix in np.arange(Nx):
            for iy in np.arange(Ny):
                prof = profs[:, dx + ix * sx:dx + (ix + 1) * sx, dy + iy * sy : dy + (iy + 1) * sy].sum(axis=1).sum(axis=1)
                if normalized:
                    prof /= np.max(prof)
                else:
                    prof /= np.max(profs) * sx * sy
                if prof.sum() > 0.:
                    ax_pos = (pos_x0 + (dx + ix * sx ) * pos_dx / size_x, pos_y0 + (dy + iy * sy ) * pos_dy / size_y, 
                              sx * pos_dx / size_x, sy * pos_dy / size_y)
                    ax = fig.add_axes(ax_pos)
                    plt.plot(prof, c = color)
                    plt.ylim((0., 1.05))
                    ax.xaxis.set_ticks_position("none")
                    ax.yaxis.set_ticks_position("none")
                    ax.xaxis.set_ticklabels([])
                    ax.yaxis.set_ticklabels([])
                    if transp:
                        ax.axesPatch.set_alpha(0.0)
    
    def _calc_profile(self, ref, axis):
        """
        Mihalas,1969,p250,p339 corrected from 3D to 1D (sqrt(3):
        zeta_0 = sqrt(2)*sigma to have gaus=exp(-(v/zeta)^2)
        sigma_therm_lambda = lambda_0 * sqrt(kT/mc2)
        then zeta_0_velo(km/s) = sqrt(2*k*1d4/M_H) * sqrt(M_H/m*T4) *1d-5
        where sqrt(2.*!phy.k*1d4/!phy.M_H)/1d5 = 12.85 km/s 
        leading to FWHM = 21.4 km/s for H atom at 1d4 K
        """
        l_ref = self.m[0]._l_emis(ref)       
        elem = misc.get_elem_ion(l_ref)[0].capitalize()
        emis = self.get_emis(l_ref)
        coeff1 =  np.sqrt(2 * pc.CST.BOLTZMANN * 1e4 / pc.CST.HMASS) / 1e5   
        zeta_0 = np.sqrt(self.v_turb**2 + coeff1**2. * self.te / 1e4 / atomic_mass(elem))
        if not self.cub_coord.vel_defined:
            self.log_.warn('Velocity not defined', calling = self.calling)
            return None
        if axis == 'x' or axis == 0:
            sum_axis = 0
            vel = self.cub_coord.vel_x
            res = np.zeros((self.size_spectrum,self.cub_coord.dim_y,self.cub_coord.dim_z))
        elif axis == 'y' or axis == 1:
            sum_axis = 1
            vel = self.cub_coord.vel_y
            res = np.zeros((self.size_spectrum,self.cub_coord.dim_x,self.cub_coord.dim_z))
        elif axis == 'z' or axis == 2:
            sum_axis = 2
            vel = self.cub_coord.vel_z
            res = np.zeros((self.size_spectrum,self.cub_coord.dim_x,self.cub_coord.dim_y))
        for i in np.arange(self.size_spectrum):
            delta_v = vel + self.vel_tab[i]
            try:
                res[i] = (emis * self.profile_function(x = delta_v, zeta_0 = zeta_0)).sum(axis=sum_axis)
            except:
                self.log_.error('Error using the profile function', calling = self.calling)
        self.log_.message('line {0} : profile computed on axis {1}'.format(l_ref, axis), calling = self.calling)
        return res

    def get_RGB(self, list_emis = [0, 1, 2], axes = 1):
        """
        Return a 3-colored imaged.
        
        Parameters:
            - list_emis: list of indices of the line to be used. Default = [0, 1, 2], associated to R, G, B.
                Elements of the list are integers or line references.
            - axes:    on which the projection is done.
            
        Usage:
            plt.imshow(m3d.get_RGB(['N__2__6548A', 'O__3__5007A', 'H__1__4861A']))
        """
        if pc.config.INSTALLED['Image']:
            self.im_R = self.get_emis(list_emis[0]).sum(axes)
            self.im_G = self.get_emis(list_emis[1]).sum(axes)
            self.im_B = self.get_emis(list_emis[2]).sum(axes)
            return misc.convert2RGB(self.im_R, self.im_G, self.im_B)
        else:
            self.log_.error('Image not installed, RBG image not available', calling = self.calling)
    