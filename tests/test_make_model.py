import pytest
import pyCloudy as pc


options = ('no molecules',
            'no level2 lines',
            'no fine opacities',
            'atom h-like levels small',
            'atom he-like levels small',
            'COSMIC RAY BACKGROUND',
            'element limit off -8',
            )
emis_tab = ['H  1  4861.33A',
            'H  1  6562.81A',
            'N  2  6583.45A',
            'O  2  3726.03A',
            'O  2  3728.81A',
            'O  3  5006.84A',
            'S  2  6716.44A',
            'S  2  6730.82A',
            'Cl 3  5517.71A',
            'Cl 3  5537.87A']
def test_make_17():
    pc.config.cloudy_exe = '/usr/local/Cloudy/c17.03/source/cloudy.exe'

    c_input = pc.CloudyInput('models/M17')
    c_input.set_BB(Teff = 40000, lumi_unit = 'q(H)', lumi_value = 47)
    c_input.set_cste_density(2.)
    c_input.set_radius(r_in=17.3)
    c_input.set_abund(predef='ism')
    c_input.set_other(options)
    c_input.set_iterate() # (0) for no iteration, () for one iteration, (N) for N iterations.
    c_input.set_sphere() # () or (True) : sphere, or (False): open geometry.
    c_input.set_emis_tab(emis_tab) # better use read_emis_file(file) for long list of lines, where file is an external file.
    c_input.set_distance(dist=1.0, unit='kpc', linear=True) # unit can be 'kpc', 'Mpc', 'parsecs', 'cm'. If linear=False, the distance is in log.

    c_input.print_input(to_file = True, verbose = False)
    c_input.run_cloudy()

def test_make_23():
    pc.config.cloudy_exe = '/usr/local/Cloudy/c23.01/source/cloudy.exe'

    c_input = pc.CloudyInput('models/M23')
    c_input.set_BB(Teff = 40000, lumi_unit = 'q(H)', lumi_value = 47)
    c_input.set_cste_density(2.)
    c_input.set_radius(r_in=17.3)
    c_input.set_abund(predef='ism')
    c_input.set_other(options)
    c_input.set_iterate() # (0) for no iteration, () for one iteration, (N) for N iterations.
    c_input.set_sphere() # () or (True) : sphere, or (False): open geometry.
    c_input.set_emis_tab(emis_tab) # better use read_emis_file(file) for long list of lines, where file is an external file.
    c_input.set_distance(dist=1.0, unit='kpc', linear=True) # unit can be 'kpc', 'Mpc', 'parsecs', 'cm'. If linear=False, the distance is in log.

    c_input.print_input(to_file = True, verbose = False)
    c_input.run_cloudy()

