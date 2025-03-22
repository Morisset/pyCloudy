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
    
ATOMIC_MASS = {}
ATOMIC_MASS['H'] = 1.008
ATOMIC_MASS['He'] = 4.003

ATOMIC_MASS['Li'] = 6.96
ATOMIC_MASS['Be'] = 9.012 
ATOMIC_MASS['B'] = 10.814
ATOMIC_MASS['C'] = 12.01
ATOMIC_MASS['N'] = 14.007
ATOMIC_MASS['O'] = 16
ATOMIC_MASS['F'] = 18.998
ATOMIC_MASS['Ne'] = 20.18

ATOMIC_MASS['Na'] = 22.99
ATOMIC_MASS['Mg'] = 24.305
ATOMIC_MASS['Al'] = 26.98
ATOMIC_MASS['Si'] = 28.085
ATOMIC_MASS['P'] = 30.974
ATOMIC_MASS['S'] = 32.068
ATOMIC_MASS['Cl'] = 35.45
ATOMIC_MASS['Ar'] = 39.948
 
ATOMIC_MASS['K'] = 39.098
ATOMIC_MASS['Ca'] = 40.078
ATOMIC_MASS['Sc'] = 44.96
ATOMIC_MASS['Ti'] = 47.87
ATOMIC_MASS['V'] = 50.94
ATOMIC_MASS['Cr'] = 51.996
ATOMIC_MASS['Mn'] = 54.938
ATOMIC_MASS['Fe'] = 55.845
ATOMIC_MASS['Co'] = 58.933
ATOMIC_MASS['Ni'] = 58.693
ATOMIC_MASS['Cu'] = 63.546
ATOMIC_MASS['Zn'] = 65.38


Z = {'H': 1,
'He': 2,
'Li': 3,
'Be': 4,
'B': 5,
'C': 6,
'N': 7,
'O': 8,
'F': 9,
'Ne': 10,
'Na': 11,
'Mg': 12,
'Al': 13,
'Si': 14,
'P': 15,
'S': 16,
'Cl': 17,
'Ar': 18,
'K': 19,
'Ca': 20,
'Sc': 21,
'Ti': 22,
'V': 23,
'Cr': 24,
'Mn': 25,
'Fe': 26,
'Co': 27,
'Ni': 28,
'Cu': 29,
'Zn': 30}

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

def get_metallicity(abund_dic):
    Z = 0.
    for elem in abund_dic:
        Z += 10**abund_dic[elem] * ATOMIC_MASS[elem]
    return Z

abund_C17_default = {'H': 0.0,
                    'He': -1.0,
                    'Li': -8.769,
                    'Be': -10.58,
                    'B': -9.21,
                    'C': -3.61,
                    'N': -4.07,
                    'O': -3.31,
                    'F': -7.52,
                    'Ne': -4.00,
                    'Na': -5.67,
                    'Mg': -4.46,
                    'Al': -5.53,
                    'Si': -4.46,
                    'P': -6.50,
                    'S': -4.74,
                    'Cl': -6.72,
                    'Ar': -5.6,
                    'K': -6.88,
                    'Ca': -5.64,
                    'Sc': -8.83,
                    'Ti': -6.98,
                    'V': -8.00,
                    'Cr': -6.33,
                    'Mn': -6.54,
                    'Fe': -4.55,
                    'Co': -7.08,
                    'Ni': -5.75,
                    'Cu': -7.79,
                    'Zn': -7.40}

abund_C17_GASS = {'H': 0.0,
                    'He': -1.07,
                    'Li': -10.95,
                    'Be': -10.62,
                    'B': -9.3,
                    'C': -3.57,
                    'N': -4.17,
                    'O': -3.31,
                    'F': -7.44,
                    'Ne': -4.07,
                    'Na': -5.76,
                    'Mg': -4.4,
                    'Al': -5.55,
                    'Si': -4.49,
                    'P': -6.59,
                    'S': -4.88,
                    'Cl': -6.5,
                    'Ar': -5.6,
                    'K': -6.97,
                    'Ca': -5.66,
                    'Sc': -8.85,
                    'Ti': -7.05,
                    'V': -8.07,
                    'Cr': -6.36,
                    'Mn': -6.57,
                    'Fe': -4.5,
                    'Co': -7.01,
                    'Ni': -5.78,
                    'Cu': -7.81,
                    'Zn': -7.44}

abund_Grevesse_1998 = {'Al': 6.47 -12,
                    'Ar': 6.40 -12,
                    'B': 2.55 -12,
                    'Be': 1.40 -12,
                    'C': 8.52 - 12,
                    'Ca': 6.36 -12,
                    'Cl': 5.50 -12,
                    'Co': 4.92 -12,
                    'Cr': 5.67 -12,
                    'Cu': 4.21 -12,
                    'F': 4.56 -12,
                    'Fe': 7.50 -12,
                    'He': 10.93 - 12,
                    'K': 5.12 -12,
                    'Li': 1.10 -12,
                    'Mg': 7.58 -12,
                    'Mn': 5.39 -12,
                    'N': 7.92 -12,
                    'Na': 6.33 -12,
                    'Ne': 8.08 -12,
                    'Ni': 6.25 -12,
                    'O': 8.83 -12,
                    'P': 5.45 -12,
                    'S': 7.33 -12,
                    'Sc': 3.17 -12,
                    'Si': 7.55 -12,
                    'Ti': 5.02 -12,
                    'V': 4.00 -12,
                    'Zn': 4.60 - 12}

abunds_Bressan_2012 = {'Al': 6.47 -12,
                    'Ar': 6.40 -12,
                    'B': 2.55 -12,
                    'Be': 1.40 -12,
                    'C': 8.50 - 12,
                    'Ca': 6.36 -12,
                    'Cl': 5.50 -12,
                    'Co': 4.92 -12,
                    'Cr': 5.67 -12,
                    'Cu': 4.21 -12,
                    'F': 4.56 -12,
                    'Fe': 7.52 -12,
                    'He': 10.93 - 12,
                    'K': 5.11 -12,
                    'Li': 1.03 - 12,
                    'Mg': 7.58 -12,
                    'Mn': 5.39 -12,
                    'N': 7.86 -12,
                    'Na': 6.33 -12,
                    'Ne': 8.02 -12,
                    'Ni': 6.25 -12,
                    'O': 8.76 -12,
                    'P': 5.46 -12,
                    'S': 7.16 -12,
                    'Sc': 3.17 -12,
                    'Si': 7.55 -12,
                    'Ti': 5.02 -12,
                    'V': 4.00 -12,
                    'Zn': 4.60 - 12}

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

abund_Nicholls_GC_2017 = {'H': 0.0,
'He': -1.01,
'Li': -8.722,
'Be': -10.68,
'B': -9.193,
'C': -3.577,
'N': -4.2099,
'O': -3.24,
'F': -7.56,
'Ne': -3.91,
'Na': -5.79,
'Mg': -4.44,
'Al': -5.57,
'Si': -4.5,
'P': -6.59,
'S': -4.88,
'Cl': -6.75,
'Ar': -5.6,
'K': -6.96,
'Ca': -5.68,
'Sc': -8.84,
'Ti': -7.07,
'V': -8.11,
'Cr': -6.38,
'Mn': -6.58,
'Fe': -4.48,
'Co': -7.07,
'Ni': -5.8,
'Cu': -7.82,
'Zn': -7.44}

scalingP_Nicholls_2017 = {'He': 0.,
'Li':  0.,
'Be':  0.,
'B':   0.,
'C':  -0.437,
'N':  -0.764,
'O':   0.,
'F':   0.,
'Ne':  0.,
'Na': -0.3,
'Mg': -0.1,
'Al': -0.1,
'Si': -0.1,
'P':  -0.5,
'S':  -0.1,
'Cl':  0.,
'Ar':  0.,
'K':  -0.1,
'Ca': -0.15,
'Sc': -0.25,
'Ti': -0.15,
'V':  -0.5,
'Cr': -0.5,
'Mn': -0.5,
'Fe': -0.5,
'Co': -0.5,
'Ni': -0.5,
'Cu': -0.5,
'Zn': -0.3}

def get_abund_nicholls(logOH):
    """
    From Nicholls et al. 2017, MNRAS, 466, 4403
    Checked at https://mappings.anu.edu.au/abund/ 
    """
    
    ab = {} 
#    diff = {} 
    scaling = logOH - abund_Nicholls_GC_2017['O']
    for elem in abund_Nicholls_GC_2017:
        if elem == 'H':
            ab[elem] = 0.
#            diff[elem] = 0.
        elif elem == 'He':
            ab[elem] = -1.0783 + np.log10(1 + 0.17031 * 10**(scaling))
#            diff[elem] = ab[elem] - abund_Nicholls_GC_2017[elem]
        elif elem in ('Li', 'Be', 'B'):
            ab[elem] =  abund_Nicholls_GC_2017[elem]
#            diff[elem] = 0.
        elif elem == 'N':
            delta = np.log10(10**-0.764 + 10**(scaling-0.082))
            ab[elem] =  abund_Nicholls_GC_2017[elem] + scaling + delta
#            diff[elem] = scaling + delta
        else:
            if scaling < -0.5:
                delta = scalingP_Nicholls_2017[elem]
            elif scaling > 0.25:
                delta = -0.5 * scalingP_Nicholls_2017[elem]
            else:
                delta = - 2 * scaling * scalingP_Nicholls_2017[elem] 
            ab[elem] =  abund_Nicholls_GC_2017[elem] + scaling + delta
#            diff[elem] = scaling + delta
    return ab
                

abund_Nicholls_GC_2017_0020 = get_abund_nicholls(-4.939)
abund_Nicholls_GC_2017_0080 = get_abund_nicholls(-4.3369)
abund_Nicholls_GC_2017_0200 = get_abund_nicholls(-3.939)
abund_Nicholls_GC_2017_0400 = get_abund_nicholls(-3.6379)
abund_Nicholls_GC_2017_0700 = get_abund_nicholls(-3.3949)
abund_Nicholls_GC_2017_1000 = get_abund_nicholls(-3.24)
abund_Nicholls_GC_2017_1300 = get_abund_nicholls(-3.1261)
abund_Nicholls_GC_2017_1700 = get_abund_nicholls(-3.0096)
abund_Nicholls_GC_2017_2100 = get_abund_nicholls(-2.9178)
abund_Nicholls_GC_2017_2500 = get_abund_nicholls(-2.8421)
abund_Nicholls_GC_2017_3000 = get_abund_nicholls(-2.7629)
abund_Nicholls_GC_2017_3500 = get_abund_nicholls(-2.6959)


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

depletion_cloudy_17 = {'He': 1,
                       'Li': 0.16,
                       'Be': 0.6,
                       'B': 0.13,
                       'C': 0.5,
                       'N': 1,
                       'O': 0.7,
                       'F': 0.3,
                       'Ne': 1,
                       'Na': 0.25,
                       'Mg': 0.2,
                       'Al': 0.02,
                       'Si': 0.1,
                       'P': 0.25,
                       'S': 1, 
                       'Cl': 0.5,
                       'Ar': 1,
                       'K':  0.3,
                       'Ca': 0.003,
                       'Sc': 0.005,
                       'Ti': 0.008,
                       'V': 0.006,
                       'Cr': 0.006,
                       'Mn': 0.05,
                       'Fe': 0.01,
                       'Co': 0.01,
                       'Ni': 0.04,
                       'Cu': 0.1,
                       'Zn': 0.25}

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

depletion_jenkins_2014_Fe_1_5 = {'He':  10**0.00,
'Li': 10**-0.22,
'Be': 10**-0.40,
'B':  10**-0.58,
'C':  10**-0.16,
'N':  10**-0.04,
'O':  10**-0.11,
'F':  10**-0.09,
'Ne': 10**0.00,
'Na': 10**-0.42,
'Mg': 10**-0.70,
'Al': 10**-0.70,
'Si': 10**-0.71,
'P':  10**-0.11,
'S':  10**0.00,
'Cl': 10**-0.09,
'Ar': 10**0.00,
'K':  10**-0.62,
'Ca': 10**-1.95,
'Sc': 10**-0.69,
'Ti': 10**-1.95,
'V':  10**-2.17,
'Cr': 10**-1.45,
'Mn': 10**-1.27,
'Fe': 10**-1.50,
'Co': 10**-1.64,
'Ni': 10**-1.57,
'Cu': 10**-0.90,
'Zn': 10**-0.20}

depletions_jenkins_2014 = {'C': (8.46, -0.101, -0.193, 0.803), 
                           'N':  (7.90, -0.000, -0.109, 0.550), 
                           'O':  (8.76, -0.225, -0.145, 0.598), 
                           'Mg': (7.62, -0.997, -0.800, 0.531), 
                           'Si': (7.61, -1.136, -0.570, 0.305), 
                           'P':  (5.54, -0.945, -0.166, 0.488), 
                           'Cl': (5.33, -1.242, -0.314, 0.609), 
                           'Ti': (5.00, -2.048, -1.957, 0.430), 
                           'Cr': (5.72, -1.447, -1.508, 0.470), 
                           'Mn': (5.58, -0.857, -1.354, 0.520), 
                           'Fe': (7.54, -1.285, -1.513, 0.437), 
                           'Ni': (6.29, -1.490, -1.829, 0.599), 
                           'Cu': (4.34, -0.710, -1.102, 0.711), 
                           'Zn': (4.70, -0.610, -0.279, 0.555), 
                           'Ge': (3.70, -0.615, -0.725, 0.690), 
                           'Kr': (3.36, -0.166, -0.332, 0.684) }
