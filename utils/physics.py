import numpy as np

class CST(object):
    BOLTZMANN = 1.3806488e-16 # erg/K - NIST 2010
    K = BOLTZMANN
    CLIGHT = 2.99792458e10 # cm/s - NIST 2010
    HPLANCK = 6.62606957e-27 # erg s - NIST 2010
    EMASS = 9.10938291e-28 # g - NIST 2010
    PMASS = 1.67262158e-24 # g
    HMASS = 1.660538921e-24 # g
    ECHARGE = 1.602176565e-19 # Electron charge in Coulomb - NIST 2010
    PI = 3.141592653589793238462643
    BOLTZMANN_ANGK = BOLTZMANN / HPLANCK / CLIGHT / 1.e8 # Boltzmann constant in (Ang * Kelvin) ** -1
    RYD = 109737.31568539 # Rydberg constant in cm^-1 - NIST 2010 
    RYD_EV = HPLANCK * CLIGHT * RYD * 1.e-7 / ECHARGE # infinite mass Rydberg in eV
    RYD_ANG = 1.e8 / RYD # infinite mass Rydberg in A
    PC = 3.0856780e18 # Parsec
    KPC = 3.0856780e21 # kiloParsec
    ALPHA_B = 2.6e-13
    SUN_MASS = 1.9891e33 #g
    SUN_RADIUS = 6.955e10 # cm
    SIGMA = 2 * np.pi**5 * K**4 / (15 * HPLANCK**3 * CLIGHT**2) # erg s-1 cm-2 K-4
    ##
    # @var BOLTZMANN
    # Boltzmann constant (erg/K) - NIST 2010
    # @var CLIGHT
    # Light velocity in vacuum (cm/s) - NIST 2010
    # @var HPLANCK
    # Planck constant (erg.s) NIST 2010
    # @var EMASS
    # Electron mass (g) NIST 2010
    # @var PMASS
    # Proton mass (g)
    # @var HMASS 
    # Hydrogen atom mass (g)
    # @var ECHARGE
    # Electron charge (C) NIST 2010
    # @var BOLTZMANN_ANGK
    # Boltzmann constant ((angstrom.K)^-1))
    # @var RYD
    # Rydberg constant (cm^-1)
    # @var RYD_EV
    # Infinite mass Rydberg (eV)
    # @var RYD_ANG
    # Infinite mass Rydberg (Angstrom)
    # @var PC
    # Parsec (cm)
    # @var KPC
    # Kiloparsec (cm)
    
ATOMIC_MASS = {}
ATOMIC_MASS['H'] = 1
ATOMIC_MASS['He'] = 4
ATOMIC_MASS['C'] = 12
ATOMIC_MASS['N'] = 14
ATOMIC_MASS['O'] = 16
ATOMIC_MASS['Ne'] = 20
ATOMIC_MASS['Ar'] = 40
ATOMIC_MASS['S'] = 32
ATOMIC_MASS['Si'] = 28
ATOMIC_MASS['Fe'] = 55.8

def flux_convert(x, y, x_unit, y_unit_in, y_unit_out):
    pass

def planck(T, x = None, x_min = None, x_max = None, n_steps = 1000, x_log = True, 
           x_unit = 'Angstrom', y_unit = 'erg/s/cm2/A'):
    if x_unit not in ('Angstrom', 'mu', 'cm', 'Hz', 'eV', 'Rydberg'):
        return None, None
    if y_unit not in ('erg/s/cm2/A', 'erg/s/cm2/cm', 'erg/s/cm2/Hz', 'erg/s/cm2/eV', 'Jy', 'mJy'):
        return None, None
    x_min_def = {'Angstrom': 1e1, 'mu': 1e-3, 'cm': 1e-7, 'Hz': 3e11, 'eV': 1e-3, 'Rydberg': 1e-4}
    x_max_def = {'Angstrom': 1e7, 'mu': 1e3, 'cm': 1e-1, 'Hz': 3e17, 'eV': 1e3, 'Rydberg': 1e2}
    if x is None:
        if x_min is None:
            x_min = x_min_def[x_unit]
        if x_max is None:
            x_max = x_max_def[x_unit]
        if x_log:    
            x = 10.**np.linspace(np.log10(x_min), np.log10(x_max), n_steps)
        else:
            x = np.linspace(x_min, x_max, n_steps)
    if x_unit in ('Angstrom', 'mu', 'cm'):
        if x_unit == 'mu':
            lam = x / 1e4
        elif x_unit == 'cm':
            lam = x / 1e8
        elif x_unit == 'Angstrom':
            lam = x
        I_lam = (4. * np.pi * 2. * CST.HPLANCK * (CST.CLIGHT*1e8)**2 / lam**5 / 
                 (np.exp(CST.HPLANCK * (CST.CLIGHT*1e8) / (lam * CST.K * T )) - 1.)) # erg/s/cm2/A
        if y_unit == 'erg/s/cm2/A':
            return x, I_lam
        elif y_unit == 'erg/s/cm2/cm':
            return x, I_lam * 1e8
        else:
            return None, None
    if x_unit in ('Hz', 'eV', 'Rydberg'):
        if x_unit == 'Hz':
            nu = x
        elif x_unit == 'eV':
            nu = x * CST.RYD * CST.CLIGHT / CST.RYD_EV
        elif x_unit == 'Rydberg':
            nu = x * CST.RYD * CST.CLIGHT
        I_nu = (4. * np.pi * 2. * CST.HPLANCK / (CST.CLIGHT)**2 * nu**3 / 
                 (np.exp(CST.HPLANCK * nu / (CST.K * T )) - 1.)) # erg/s/cm2/Hz
        if y_unit == 'erg/s/cm2/Hz':
            return x, I_nu
        elif y_unit == 'erg/s/cm2/eV':
            return x, I_nu * (CST.HPLANCK / CST.ECHARGE * 1e-7)
        elif y_unit == 'Jy':
            return x, I_nu * 1e-23
        elif y_unit == 'mJy':
            return x, I_nu * 1e-23 * 1e6
        else:
            return None, None

def atomic_mass(elem):
    if elem in ATOMIC_MASS:
        return ATOMIC_MASS[elem]
    else:
        return None
    
    
