import numpy as np

class CST(object):
    BOLTZMANN = 1.3806488e-16 # erg/K - NIST 2010
    K = BOLTZMANN
    CLIGHT = 2.99792458e10 # cm/s - NIST 2010
    HPLANCK = 6.62606957e-27 # erg s - NIST 2010
    EMASS = 9.10938291e-28 # g - NIST 2010
    PMASS = 1.67262158e-24 # g
    HMASS = 1.660538921e-24 * 1.00794 # g
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

abund_Asplund_2009 = {'Al': 6.45 -12,
            'Ar': 6.40 -12,
            'B': 2.70 -12,
            'Be': 1.38 -12,
            'C': 8.43 - 12,
            'Ca': 6.34 -12,
            'Cl': 5.50 -12,
            'Co': 4.99 -12,
            'Cr': 5.64 -12,
            'Cu': 4.19 -12,
            'F': 4.56 -12,
            'Fe': 7.50 -12,
            'He': 10.93 - 12,
            'K': 5.03 -12,
            'Li': 1.05 -12,
            'Mg': 7.60 -12,
            'Mn': 5.43 -12,
            'N': 7.83 -12,
            'Na': 6.24 -12,
            'Ne': 7.93 -12,
            'Ni': 6.22 -12,
            'O': 8.69 -12,
            'P': 5.41 -12,
            'S': 7.12 -12,
            'Sc': 3.15 -12,
            'Si': 7.51 -12,
            'Ti': 4.95 -12,
            'V': 3.93 -12,
            'Zn': 4.56 - 12}

abund_Lodder_2003 = {'Al': 6.54 -12,
            'Ar': 6.62 -12,
            'B': 2.85 -12,
            'Be': 1.48 -12,
            'C': 8.46 - 12,
            'Ca': 6.41 -12,
            'Cl': 5.33 -12,
            'Co': 4.98 -12,
            'Cr': 5.72 -12,
            'Cu': 4.34 -12,
            'F': 4.53 -12,
            'Fe': 7.54 -12,
            'He': 10.984 - 12,
            'K': 5.18 -12,
            'Li': 3.35 -12,
            'Mg': 7.62 -12,
            'Mn': 5.58 -12,
            'N': 7.90 -12,
            'Na': 6.37 -12,
            'Ne': 7.95 -12,
            'Ni': 6.29 -12,
            'O': 8.76 -12,
            'P': 5.54 -12,
            'S': 7.26 -12,
            'Sc': 3.15 -12,
            'Si': 7.61 -12,
            'Ti': 5.00 -12,
            'V': 4.07 -12,
            'Zn': 4.70 - 12}

depletion_cloudy_13 = {}
depletion_cloudy_13['He']= 1.00 #noble gas
depletion_cloudy_13['Li']=  0.16 #White, 1986
depletion_cloudy_13['Be']=  0.6 # York et al., 1982
depletion_cloudy_13['B']=  0.13 #Federman et al., 1993
depletion_cloudy_13['C']=  0.4
depletion_cloudy_13['N']=  1.
depletion_cloudy_13['O']=  0.6
depletion_cloudy_13['F']=  0.3 # Snow and York, 1981
depletion_cloudy_13['Ne']= 1.0 # noble gas
depletion_cloudy_13['Na']= 0.2
depletion_cloudy_13['Mg']= 0.2
depletion_cloudy_13['Al']= 0.01
depletion_cloudy_13['Si']= 0.03
depletion_cloudy_13['P']= 0.25 #Cardelli et al., 1991
depletion_cloudy_13['S']=  1.0
depletion_cloudy_13['Cl']= 0.4
depletion_cloudy_13['Ar']=  1.0 # noble gas
depletion_cloudy_13['K']=  0.3 # Chaffee and White, 1982
depletion_cloudy_13['Ca']=  1e-4
depletion_cloudy_13['Sc']=  5e-3 #Snow and Dodgen, 1980
depletion_cloudy_13['Ti']=  8e-3 #Crinklaw et al., 1994
depletion_cloudy_13['V']=  6e-3 #Cardelli, 1994
depletion_cloudy_13['Cr']= 6e-3 #Cardelli et al., 1991
depletion_cloudy_13['Mn']=  5e-2 #Cardelli et al., 1991
depletion_cloudy_13['Fe']=  1e-2
depletion_cloudy_13['Co']=  1e-2
depletion_cloudy_13['Ni']=  1e-2
depletion_cloudy_13['Cu']=  0.1 # Cardelli et al., 1991
depletion_cloudy_13['Zn']=  0.25 #Cardelli et al., 1991

depletion_dopita_2013 = {} # 10** : dopita_ et al 2013, ApJSS 208
depletion_dopita_2013['C']=  10**-0.3
depletion_dopita_2013['N']=  10**-0.05
depletion_dopita_2013['O']=  10**-0.07
depletion_dopita_2013['Na']= 10**-1
depletion_dopita_2013['Mg']= 10**-1.08
depletion_dopita_2013['Al']= 10**-1.39
depletion_dopita_2013['Si']= 10**-0.81
depletion_dopita_2013['Cl']= 10**-1.0
depletion_dopita_2013['Ca']=  10**-2.52
depletion_dopita_2013['Fe']=  10**-1.31
depletion_dopita_2013['Ni']=  10**-2

depletion_jenkins_2009 = {}
depletion_jenkins_2009['C']=  10**-0.112
depletion_jenkins_2009['N']=  10**-0.109
depletion_jenkins_2009['O']=  10**-0.010
depletion_jenkins_2009['Mg']= 10**-0.270
depletion_jenkins_2009['Si']= 10**-0.223
depletion_jenkins_2009['P']= 10**0.296
depletion_jenkins_2009['Cl']= 10**0.442
depletion_jenkins_2009['Ti']=  10**-1.077
depletion_jenkins_2009['Cr']= 10**-0.827
depletion_jenkins_2009['Mn']=  10**-0.909
depletion_jenkins_2009['Fe']=  10**-0.951
depletion_jenkins_2009['Cu']=  10**-0.597
depletion_jenkins_2009['Zn']=  10**0.059

depletion_jenkins_2009l = {}
depletion_jenkins_2009l['C']=  10**-0.213
depletion_jenkins_2009l['N']=  10**-0.109
depletion_jenkins_2009l['O']=  10**-0.236
depletion_jenkins_2009l['Mg']= 10**-1.267
depletion_jenkins_2009l['Si']= 10**-1.359
depletion_jenkins_2009l['P']= 10**-0.649
depletion_jenkins_2009l['Cl']= 10**-0.800
depletion_jenkins_2009l['Ti']=  10**-3.125
depletion_jenkins_2009l['Cr']= 10**-2.274
depletion_jenkins_2009l['Mn']=  10**-1.765
depletion_jenkins_2009l['Fe']=  10**-2.236
depletion_jenkins_2009l['Cu']=  10**-1.307
depletion_jenkins_2009l['Zn']=  10**-0.551

