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

abund_Nicholls_GC_2017_1000 = abund_Nicholls_GC_2017

abund_Nicholls_GC_2017_0020 = {'H': 0.0,
'He': -1.0768,
'Li': -8.722,
'Be': -10.68,
'B': -9.193,
'C': -5.713,
'N': -6.6331,
'O': -4.939,
'F': -9.259,
'Ne': -5.609,
'Na': -7.789,
'Mg': -6.239,
'Al': -7.369,
'Si': -6.299,
'P': -8.789,
'S': -6.679,
'Cl': -8.449,
'Ar': -7.299,
'K': -8.759,
'Ca': -7.529,
'Sc': -10.789,
'Ti': -8.919,
'V': -10.309,
'Cr': -8.579,
'Mn': -8.779,
'Fe': -6.679,
'Co': -9.269,
'Ni': -7.999,
'Cu': -10.019,
'Zn': -9.439}

abund_Nicholls_GC_2017_0080 = {'H': 0.0,
'He': -1.0724,
'Li': -8.722,
'Be': -10.68,
'B': -9.193,
'C': -5.1109,
'N': -5.9296,
'O': -4.3369,
'F': -8.6569,
'Ne': -5.0069,
'Na': -7.1869,
'Mg': -5.6369,
'Al': -6.7669,
'Si': -5.6969,
'P': -8.1869,
'S': -6.0769,
'Cl': -7.8469,
'Ar': -6.6969,
'K': -8.1569,
'Ca': -6.9269,
'Sc': -10.187,
'Ti': -8.3169,
'V': -9.7069,
'Cr': -7.9769,
'Mn': -8.1769,
'Fe': -6.0769,
'Co': -8.6669,
'Ni': -7.3969,
'Cu': -9.4169,
'Zn': -8.8369}

abund_Nicholls_GC_2017_0200 = {'H': 0.0,
'He': -1.0638,
'Li': -8.722,
'Be': -10.68,
'B': -9.193,
'C': -4.713,
'N': -5.3803,
'O': -3.939,
'F': -8.259,
'Ne': -4.609,
'Na': -6.789,
'Mg': -5.239,
'Al': -6.369,
'Si': -5.299,
'P': -7.789,
'S': -5.679,
'Cl': -7.449,
'Ar': -6.299,
'K': -7.759,
'Ca': -6.529,
'Sc': -9.789,
'Ti': -7.919,
'V': -9.309,
'Cr': -7.579,
'Mn': -7.779,
'Fe': -5.679,
'Co': -8.269,
'Ni': -6.999,
'Cu': -9.019,
'Zn': -8.439}

abund_Nicholls_GC_2017_0400 = { 'H': 0.0,
'He': -1.0497,
'Li': -8.722,
'Be': -10.68,
'B': -9.193,
'C': -4.3227,
'N': -4.9061,
'O': -3.6379,
'F': -7.9579,
'Ne': -4.3079,
'Na': -6.4267,
'Mg': -4.9175,
'Al': -6.0475,
'Si': -4.9775,
'P': -7.3859,
'S': -5.3575,
'Cl': -7.1479,
'Ar': -5.9979,
'K': -7.4375,
'Ca': -6.1973,
'Sc': -9.4369,
'Ti': -7.5873,
'V': -8.9059,
'Cr': -7.1759,
'Mn': -7.3759,
'Fe': -5.2759,
'Co': -7.8659,
'Ni': -6.5959,
'Cu': -8.6159,
'Zn': -8.0767}

abund_Nicholls_GC_2017_0700 = {'H': 0.0,
'He': -1.0294,
'Li': -8.722,
'Be': -10.68,
'B': -9.193,
'C': -3.8673,
'N': -4.4888,
'O': -3.3949,
'F': -7.7149,
'Ne': -4.0649,
'Na': -6.0378,
'Mg': -4.6259,
'Al': -5.7559,
'Si': -4.6859,
'P': -6.8998,
'S': -5.0659,
'Cl': -6.9049,
'Ar': -5.7549,
'K': -7.1459,
'Ca': -5.8814,
'Sc': -9.0724,
'Ti': -7.2714,
'V': -8.4198,
'Cr': -6.6898,
'Mn': -6.8898,
'Fe': -4.7898,
'Co': -7.3798,
'Ni': -6.1098,
'Cu': -8.1298,
'Zn': -7.6878}
abund_Nicholls_GC_2017_1300 = {'H': 0.0,
'He': -0.9914,
'Li': -8.722,
'Be': -10.68,
'B': -9.193,
'C': -3.3635,
'N': -3.9997,
'O': -3.1261,
'F': -7.4461,
'Ne': -3.7961,
'Na': -5.6077,
'Mg': -4.3033,
'Al': -5.4333,
'Si': -4.3633,
'P': -6.3621,
'S': -4.7433,
'Cl': -6.6361,
'Ar': -5.4861,
'K': -6.8233,
'Ca': -5.5319,
'Sc': -8.6691,
'Ti': -6.9219,
'V': -7.8821,
'Cr': -6.1521,
'Mn': -6.3521,
'Fe': -4.2521,
'Co': -6.8421,
'Ni': -5.5721,
'Cu': -7.5921,
'Zn': -7.2577}

abund_Nicholls_GC_2017_1700 = {'H': 0.0,
'He': -0.9679,
'Li': -8.722,
'Be': -10.68,
'B': -9.193,
'C': -3.1451,
'N': -3.781,
'O': -3.0096,
'F': -7.3296,
'Ne': -3.6796,
'Na': -5.4213,
'Mg': -4.1635,
'Al': -5.2935,
'Si': -4.2235,
'P': -6.1291,
'S': -4.6035,
'Cl': -6.5196,
'Ar': -5.3696,
'K': -6.6835,
'Ca': -5.3804,
'Sc': -8.4943,
'Ti': -6.7704,
'V': -7.6491,
'Cr': -5.9191,
'Mn': -6.1191,
'Fe': -4.0191,
'Co': -6.6091,
'Ni': -5.3391,
'Cu': -7.3591,
'Zn': -7.0713}

abund_Nicholls_GC_2017_2100 = {'H': 0.0,
'He': -0.9455,
'Li': -8.722,
'Be': -10.68,
'B': -9.193,
'C': -3.0363,
'N': -3.6066,
'O': -2.9178,
'F': -7.2378,
'Ne': -3.5878,
'Na': -5.3178,
'Mg': -4.0678,
'Al': -5.1978,
'Si': -4.1278,
'P': -6.0178,
'S': -4.5078,
'Cl': -6.4278,
'Ar': -5.2778,
'K': -6.5878,
'Ca': -5.2828,
'Sc': -8.3928,
'Ti': -6.6728,
'V': -7.5378,
'Cr': -5.8078,
'Mn': -6.0078,
'Fe': -3.9078,
'Co': -6.4978,
'Ni': -5.2278,
'Cu': -7.2478,
'Zn': -6.9678}

abund_Nicholls_GC_2017_2500 = {'H': 0.0,
'He': -0.9243,
'Li': -8.722,
'Be': -10.68,
'B': -9.193,
'C': -2.9606,
'N': -3.4614,
'O': -2.8421,
'F': -7.1621,
'Ne': -3.5121,
'Na': -5.2421,
'Mg': -3.9921,
'Al': -5.1221,
'Si': -4.0521,
'P': -5.9421,
'S': -4.4321,
'Cl': -6.3521,
'Ar': -5.2021,
'K': -6.5121,
'Ca': -5.2071,
'Sc': -8.3171,
'Ti': -6.5971,
'V': -7.4621,
'Cr': -5.7321,
'Mn': -5.9321,
'Fe': -3.8321,
'Co': -6.4221,
'Ni': -5.1521,
'Cu': -7.1721,
'Zn': -6.8921}

abund_Nicholls_GC_2017_3000 = {'H': 0.0,
'He': -0.8991,
'Li': -8.722,
'Be': -10.68,
'B': -9.193,
'C': -2.8814,
'N': -3.3086,
'O': -2.7629,
'F': -7.0829,
'Ne': -3.4329,
'Na': -5.1629,
'Mg': -3.9129,
'Al': -5.0429,
'Si': -3.9729,
'P': -5.8629,
'S': -4.3529,
'Cl': -6.2729,
'Ar': -5.1229,
'K': -6.4329,
'Ca': -5.1279,
'Sc': -8.2379,
'Ti': -6.5179,
'V': -7.3829,
'Cr': -5.6529,
'Mn': -5.8529,
'Fe': -3.7529,
'Co': -6.3429,
'Ni': -5.0729,
'Cu': -7.0929,
'Zn': -6.8129}

abund_Nicholls_GC_2017_3500 = {'H': 0.0,
'He': -0.8752,
'Li': -8.722,
'Be': -10.68,
'B': -9.193,
'C': -2.8144,
'N': -3.1788,
'O': -2.6959,
'F': -7.0159,
'Ne': -3.3659,
'Na': -5.0959,
'Mg': -3.8459,
'Al': -4.9759,
'Si': -3.9059,
'P': -5.7959,
'S': -4.2859,
'Cl': -6.2059,
'Ar': -5.0559,
'K': -6.3659,
'Ca': -5.0609,
'Sc': -8.1709,
'Ti': -6.4509,
'V': -7.3159,
'Cr': -5.5859,
'Mn': -5.7859,
'Fe': -3.6859,
'Co': -6.2759,
'Ni': -5.0059,
'Cu': -7.0259,
'Zn': -6.7459}

# def get_abund_nicholls(logOH):
#     """
#     logOH : log10 (O/H).
#     Solar value = -3.24 
#     """
#     ab = abund_Nicholls_GC_2017.copy()
#     scaling = logOH - ab['O']
#     
#     for elem in ab:
#         if elem == 'O':
#             ab['O'] = logOH
#         elif elem == 'C':
#             ab['C'] = ab['O'] + np.log10(10**-0.8 + 10**(ab['O'] + 2.72))
#         elif elem == 'N':
#             ab['N'] = ab['O'] + np.log10(10**-1.732 + 10**(ab['O'] + 2.19))
#         elif elem in ('F', 'Ne', 'Cl', 'Ar'):
#             ab[elem] += scaling
#         elif elem == 'He':
#             ab['He'] = -1.0783 + np.log10(1. + 0.17031*10**scaling)
#         elif elem == 'Fe':
#             ab['Fe'] += scaling
#         elif elem in ('P', 'V', 'Cr', 'Mn', 'Co', 'Ni', 'Cu', 'Zn'):
#             ab[elem] += ab['Fe'] - abund_Nicholls_GC_2017['Fe']
#         else: 
#             ab[elem] += scaling
#     return ab
            
            
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

