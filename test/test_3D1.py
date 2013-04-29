import numpy as np
import matplotlib.pyplot as plt
import pyCloudy as pc

pc.config.cloudy_exe = '/usr/local/Cloudy/c13.00_rc1/source/cloudy.exe'

#dir_ = '/Users/christophemorisset/Using_pyCloudy/Models'
dir_ = '.'

"""
Run a 3D model of a bipolar nebula. Compute the line profiles and some images and statistics. 
"""
def set_models(dir_, model_name):
    emis_tab = ['H  1  4861',
                'H  1  6563',
                'He 1  5876',
                'N  2  6584',
                'O  1  6300',
                'O II  3726',
                'O II  3729',
                'O  3  5007',
                'TOTL  4363',
                ]   
    a = 2.
    b = 1.0
    thetas = np.linspace(0., 90., 6)
    thetas_rad = np.pi / 180. * thetas
    fact_elli = a * b / np.sqrt((b * np.sin(thetas_rad))**2 + (a * np.cos(thetas_rad))**2)
    rs_in = 16.5 + np.log10(fact_elli)
    densities = 4 - np.log10(fact_elli) * 2
    
    model = pc.CloudyInput()
    model.set_BB(80000., 'q(H)', 47.3)
    model.set_grains()
    model.set_emis_tab(emis_tab)
    
    for theta, r_in, density in zip(thetas, rs_in, densities):
        model.model_name = '{0}/{1}_{2:.0f}'.format(dir_, model_name,theta)
        model.set_cste_density(density)
        model.set_radius(r_in)
        model.set_theta_phi(theta)
        model.print_input(to_file = True, verbose = False)

def def_profiles(m3d):
    def velo_polynome(params):
        coeffs = params[0]
        cub_coord = params[1]
        tmp = 0.
        for i, coeff in enumerate(coeffs):
            tmp = tmp + coeff * cub_coord.r**i
        tmp = tmp / cub_coord.r
        tt = (cub_coord.r == 0.)
        tmp[tt] = 0
        vel_x = tmp * cub_coord.x / np.max(cub_coord.x)
        vel_y = tmp * cub_coord.y / np.max(cub_coord.y)
        vel_z = tmp * cub_coord.z / np.max(cub_coord.z)
        return vel_x, vel_y, vel_z
    
    m3d.set_velocity(velocity_law='user', params = [[20.,60.], m3d.cub_coord], user_function = velo_polynome)
    m3d.config_profile(size_spectrum = 41, vel_max = 25, profile_function = 'gaussian', v_turb = 0.01)
#    m3d.config_profile(size_spectrum = 41, vel_max = 25, profile_function = Hb_prof, v_turb = 0.01)
    
def plot_profiles(m3d, x_pos, y_pos):
    plt.figure(1) 
    plt.plot(m3d.vel_tab,m3d.get_profile('H__1__4861A', axis='x')[:,x_pos,y_pos] * 5, label = r'H$\beta$')
    plt.plot(m3d.vel_tab,m3d.get_profile('N__2__6584A', axis='x')[:,x_pos,y_pos] * 5, label = r'[NII]$\lambda$6584')
    plt.plot(m3d.vel_tab,m3d.get_profile('O__3__5007A', axis='x')[:,x_pos,y_pos], label = r'[OIII]$\lambda$5007')
    plt.legend()
    
def other_plots(m3d, proj_axis):
    plt.figure(2)
    plt.subplot(331)
    plt.imshow(m3d.get_emis('H__1__4861A').sum(axis = proj_axis)*m3d.cub_coord.cell_size)
    plt.title('Hb')
    plt.colorbar()
    
    plt.subplot(332)
    plt.imshow(m3d.get_emis('N__2__6584A').sum(axis = proj_axis)*m3d.cub_coord.cell_size)
    plt.title('[NII]')
    plt.colorbar()
    
    plt.subplot(333)
    plt.imshow(m3d.get_emis('O__3__5007A').sum(axis = proj_axis)*m3d.cub_coord.cell_size)
    plt.title('[OIII]')
    plt.colorbar()
    
    plt.subplot(334)
    plt.imshow(m3d.get_emis('N__2__6584A').sum(axis = proj_axis)/m3d.get_emis('H__1__4861A').sum(axis = proj_axis))
    plt.title('[NII]/Hb')
    plt.colorbar()
    
    plt.subplot(335)
    plt.imshow(m3d.get_emis('O__3__5007A').sum(axis = proj_axis)/m3d.get_emis('H__1__4861A').sum(axis = proj_axis))
    plt.title('[OIII]/Hb')
    plt.colorbar()
    
    plt.subplot(336)
    plt.imshow(m3d.get_ionic('O',1)[n_cut,:,:])
    plt.title('O+ cut')
    plt.colorbar()
    
    plt.subplot(337)
    plt.scatter(m3d.get_ionic('O',1).ravel(),m3d.get_ionic('N',1).ravel()/m3d.get_ionic('O',1).ravel(),
                c=np.abs(m3d.cub_coord.theta.ravel()), edgecolors = 'none')
    plt.title('Colored by |Theta|')
    plt.xlabel('O+ / O')
    plt.ylabel('N+/O+ / N/O')
    plt.colorbar()
    
    plt.subplot(338)
    plt.scatter(m3d.get_ionic('O',1).ravel(),m3d.get_ionic('N',1).ravel()/m3d.get_ionic('O',1).ravel(),
                c=m3d.relative_depth.ravel(),vmin = 0, vmax = 1, edgecolors = 'none')
    plt.title('Colored by position in the nebula')
    plt.xlabel('O+ / O')
    plt.ylabel('N+/O+ / N/O')
    plt.colorbar()
    
    plt.subplot(339)
    C1 = (m3d.get_ionic('N',1)/m3d.get_ionic('O',1)*m3d.get_ionic('N',2))
    C2 = (m3d.get_ionic('N',2))
    tt = (m3d.get_ionic('O',1) == 0)
    C1[tt] = 0
    C2[tt] = 0
    V = C1.sum(axis = proj_axis) / C2.sum(axis = proj_axis)
    plt.imshow(V)
    plt.colorbar()
    plt.title('N+/O+ / N/O weighted by NII')
    plt.contour(V,levels=[1,1])

def plot_RGB(m3d):
    plt.figure(3)
    plt.imshow(m3d.get_RGB(('H__1__4861A', 'N__2__6584A', 'O__3__5007A'), axes = 1))

model_name = "M3D_1"
pc.log_.calling = 'Model3D : ' + model_name
pc.log_.level = 3

dim = 101
n_cut = (dim-1) /2
proj_axis = 0

set_models(dir_, model_name)
pc.run_cloudy(dir_ = dir_, n_proc = 6, model_name = model_name, use_make = True)

liste_of_models = pc.load_models('{0}/{1}'.format(dir_, model_name), list_elem=['H', 'He', 'C', 'N', 'O', 'Ar', 'Ne'],  
                                           read_cont = False, read_grains = False)

m3d = pc.C3D(liste_of_models, dims = [dim, dim, dim], angles = [45,45,0], plan_sym = True)

def_profiles(m3d)

im = m3d.get_RGB(list_emis = [0, 3, 7])
plt.imshow(im, origin = 'lower')
m3d.plot_profiles(ref = 3, i_fig = 1, Nx=20, Ny=20)


plot_profiles(m3d, 55, 55)
other_plots(m3d, proj_axis)
plot_RGB(m3d)

plt.show()

pc.log_.message('Finished')
