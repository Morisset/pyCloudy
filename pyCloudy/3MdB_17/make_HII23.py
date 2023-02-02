'''
Created on 13 / 10 / 2021

@author: christophemorisset
'''
#%% imports

import numpy as np
import pyCloudy as pc
import copy
from pyCloudy.db import use3MdB
from pyCloudy.utils.physics import abunds_Bressan_2012, get_abund_nicholls, ATOMIC_MASS, Z as Z_pc
from pyCloudy.utils.physics import depletion_dopita_2013, depletion_cloudy_17
import pandas as pd
import matplotlib.pyplot as plt
#%%

OVN_dic = {'host' : 'nefeles',
           'user_name' : 'OVN_admin',
           'user_passwd' : 'getenv',
           'base_name' : '3MdB_17',
           'pending_table' : '`pending_17`',
           'master_table' : '`tab_17`',
           'teion_table' : '`teion_17`',
           'abion_table' : '`abion_17`',
           'temis_table' : '`temis_17`',
           'lines_table' : '`lines_17`',
           'procIDs_table' : '`procIDs`'
           }

models_dir = 'HII_23/'
                  
name = 'HII_23'  

#%% plateau

def plateau_ailes(N, p):
    x1, x2, s = p
    fwhm = s 
    unif = x1 - fwhm + (x2 - x1 + 2 * fwhm) * np.random.rand(N)
    gaus = np.random.normal(0, s/2., N)
    res = unif + gaus
    return res

def deplete(ab_dic, depl_dic=None, log_depl = 0.0, ksi_d=None):
    
    if ksi_d is not None:
        Z, Z_dep, ksi_d_ori, Y = get_metallicity(ab_dic, depl_dic, log_depl, ksi_d=None)
        #print(ksi_d_ori)
    new_dic = {}
    for elem in ab_dic:
        new_dic[elem] = ab_dic[elem]
        if elem not in ('H' 'He'):
            if depl_dic is not None:
                if elem in depl_dic:
                    if ksi_d is not None:
                        if ksi_d <= ksi_d_ori: # lim ksi_d = 0 -> fdepl = 0; ksi_d = kdi_d_ori -> fdepl = (1-depl_dic)
                            fdepl = ksi_d/ksi_d_ori * (1-depl_dic[elem])
                        else: # lim ksi_d = 1 -> fdepl = 1; ksi_d = kdi_d_ori -> fdepl = (1-depl_dic)
                            fdepl = 1 - depl_dic[elem] * (1-ksi_d) / (1-ksi_d_ori)
                        new_dic[elem] +=  np.log10((1 - fdepl))
                    else:
                        new_dic[elem] += np.log10(depl_dic[elem])
            new_dic[elem] += log_depl 
    return new_dic

def get_metallicity(ab_dic, depl_dic=None, log_depl = 0.0, ksi_d=None):
    """
    Return the total metallicity, the metallicity in gaseous phase, the ksi_d from:
        ab_dic: dictionnary of abundances in log X/H
        depl_dic: dictionnary of depletion as factors
        log_depl: [dex] a factor applied to the depletion to adjust the Ksi_d value
    """
    
    
    M_metals = 0
    M_metals_dep = 0
    M_all = ATOMIC_MASS['H']
    M_all_dep = ATOMIC_MASS['H'] 
    M_Helio = 0
    dep_dic = deplete(ab_dic, depl_dic=depl_dic, log_depl = log_depl, ksi_d=ksi_d)
    for elem in dep_dic:
        if elem != 'H':
            to_add = 10**ab_dic[elem] * ATOMIC_MASS[elem]
            to_add_dep = 10**dep_dic[elem] * ATOMIC_MASS[elem]
            M_all += to_add
            M_all_dep += to_add_dep
            if elem != 'He':
                M_metals += to_add
                M_metals_dep += to_add_dep
            else:
                M_Helio += to_add
    return M_metals / M_all, M_metals_dep / M_all_dep, 1 - M_metals_dep/M_metals, M_Helio/M_all
        
def print_ab_dics(ab_dics, norm=12):
    
    Zs = [get_metallicity(ab_dic)[0] for ab_dic in ab_dics]
    print('  ', ' '.join(['{:9.5f}'.format(Z) for Z in Zs]))
    for elem in sorted(ab_dics[0], key=lambda elem: Z_pc[elem]):
        if elem != 'H':
            print('{:2s}'.format(elem), ' '.join(['{:6.2f}'.format(norm+ab_dic[elem]) for ab_dic in ab_dics]))

def get_Gutkin(log_OH=-3.16526):
    ref_log_OH = -3.16526
    abunds_G16_2 = copy.deepcopy(abunds_Bressan_2012)
    abunds_G16_2['N'] -= 0.15
    abunds_G16_2['O'] += 0.10
    abunds_G16_2['He'] = -1.00946
    
    abunds_G16_2 = deplete(abunds_G16_2, log_depl=-0.02526) # for Z=0.01524, log_depl=-0.0413 for He = -1.07, log_depl=-0.02526 for He = -1.00946
    shift = log_OH - ref_log_OH
    for elem in abunds_G16_2:
        if elem not in ('H', 'He'):
            abunds_G16_2[elem] += shift
    return abunds_G16_2

#%% get_abunds

def get_abunds(log_OH_tot=-3.16526, log_CO=-0.3565, log_NO=-1.155, ksi_d=0, 
               abund_type = 'Gutkin', abund_width=0.):
    
    if abund_type == 'Nicholls':
        abund = get_abund_nicholls(log_OH_tot)
        depletion = depletion_cloudy_17
        for elem in depletion_dopita_2013:
            depletion[elem] = depletion_dopita_2013[elem]
    elif abund_type == 'Gutkin':
        abund = get_Gutkin(log_OH_tot)
        depletion = depletion_cloudy_17
    else:
        raise
        
    abund['N'] = log_NO + abund['O']
    abund['C'] = log_CO + abund['O']
    
    for elem in abund:
        if elem not in ('H', 'He'):
            abund[elem] += np.random.normal(0, abund_width)
    
    Z, Z_dep, ksi_d2, Y = get_metallicity(abund, depletion, log_depl=0, ksi_d=ksi_d)
    abund2 = deplete(abund, depletion, log_depl=0, ksi_d=ksi_d)
    
    if abund_type == 'Gutkin':
        Y_Gut = 0.2485 + 1.7756 * Z
        abund2['He'] = np.log10(Y_Gut / (4 * (1. - Z - Y_Gut)))
        Z_, Z_dep, ksi_d3, Y = get_metallicity(abund2)
    
    
    return Z, Z_dep, ksi_d2, abund, abund2

def get_SO(log_OH_tot,ksi_d):
    Z, Z_dep, ksi_d2, abund, abund2 = get_abunds(log_OH_tot, log_CO=-0.4, log_NO=-1.5, ksi_d=ksi_d, abund_type = 'Nicholls')
    return abund2['S'] - abund2['O']

#%% Define tables
options = ('COSMIC RAY BACKGROUND',)

params_dic = {'logU': (-4, -1, 0.5),
              'log_OH': (5.5-12, 9.-12, 0.5),
              'log_NO': (-2, 0, 0.5),
              'log_CO': (-1, 0.5, 0.5),
              'age': (1, 7, 0.),
              'log_fr': (-1.5, 1.5, 0),
              'log_nH': (1, 4, 0.5),
              'ksi_d': (0.15, 0.55, 0.)
              }

abund_width = 0.10


#%% define small functions

def get_params(N):

    values = {k: plateau_ailes(N, params_dic[k]) for k in params_dic.keys()}
    return pd.DataFrame(values)


def get_params_test(N):
    values = {'logU': np.ones(N) * -3,
              'log_OH': np.linspace(5.5-12, 9.-12, N),
              'log_NO': np.ones(N) * -4.08 + 3.17,
              'log_CO':  np.ones(N) * -3.446 + 3.17,
              'age': np.ones(N) * 1,
              'log_fr': np.ones(N) * 0,
              'log_nH':  np.ones(N) * 1,
              'ksi_d': np.ones(N) * 0.36
              }
    return pd.DataFrame(values)


#%% define main function        
def make_inputs(N, insert=False, abund_type='Nicholls', verbose=False, atm_type='BPASS_B',
                abund_width=abund_width, use_ksi_d=True, test_only=False, random_seed=None):

    if test_only:
        insert = False
        abund_width = 0.
    if insert:
        MdB = pc.MdB(OVN_dic)
        wP = use3MdB.writePending(MdB, OVN_dic)
        wP.set_ref(name)
        wP.set_user('Stephane')
        wP.set_C_version('17.03')
        wP.set_iterate(1)
        wP.set_file(name)
        wP.set_dir(models_dir)
        wP.set_cloudy_others(options)
        wP.set_N_Hb_cut(9)
        wP.set_geometry('Sphere')
        wP.set_stop(('temperature 20', 'pfrac 0.02'))
    
    c = pc.CST.CLIGHT
    alpha_B = 2.6e-13
    np.random.seed(random_seed)
    if test_only:
        params = get_params_test(N)
    else:
        params = get_params(N)
    params['U'] = 10**params['logU']
    params['NH'] = 10**params['log_nH']
    params['fr'] = 10**params['log_fr']
    ff = 1.0
    if abund_type == 'Nicholls':
        Z_sol = 0.01425
    elif abund_type == 'Gutkin':
        Z_sol = 0.01525
    else:
        raise 
    
    w = (1 + params['fr']**3.)**(1./3) - params['fr']
    Q0 = 4. * np.pi * c**3 * params['U']**3 / (3. * params['NH'] * ff**2 * alpha_B**2 * w**3)
    R_str = (3. * Q0 / (4 * np.pi * params['NH']**2 * alpha_B * ff))**(1./3)
    params['R_in'] = params['fr'] * R_str
    params['Q0'] = Q0
    
    ab_dic_list = {}
    
    for i in range(N):
        p = params.iloc[i]
        """
        log_OH = p['log_OH']
        log_dep = p['log_dep']
        if abund_type == 'Nicholls':
            depletion = depletion_cloudy_17
            for elem in depletion_dopita_2013:
                depletion[elem] = depletion_dopita_2013[elem]
            abund = get_abund_nicholls(log_OH)
        elif abund_type == 'Gutkin':
            depletion = depletion_cloudy_17
            abund = get_Gutkin(log_OH)
        
        abund['N'] = p['log_NO'] + log_OH
        abund['C'] = p['log_CO'] + log_OH
        if use_ksi_d:
            ksi_d = p['ksi_d']
        else:
            ksi_d = None #p['ksi_d']
        Z, Z_dep, ksi_d2, Y = get_metallicity(abund, depletion, log_depl=0, ksi_d=ksi_d)
        abund = deplete(abund, depletion, log_depl=0, ksi_d=ksi_d)
        
        if abund_type == 'Gutkin':
            Y_Gut = 0.2485 + 1.7756 * Z
            abund['He'] = np.log10(Y_Gut / (4 * (1. - Z - Y_Gut)))
        
        """        
        Z, Z_dep, ksi_d2, abund_ism, abund = get_abunds(log_OH_tot=p['log_OH'], 
                                                        log_CO=p['log_CO'], 
                                                        log_NO=p['log_NO'], 
                                                        ksi_d=p['ksi_d'], 
                                                        abund_type=abund_type,
                                                        abund_width=abund_width)
        
                
        dtg = ksi_d2 / 0.36 * Z / Z_sol # log10(0.01524) = -1.817015

        if atm_type == 'BPASS_B':
            metallicity = min(max(np.log10(Z), -4.99), -1.41)
            atm_file = 'BPASSv2.2.1_bin-imf_chab300.mod'
        elif atm_type == 'BPASS_S': 
            metallicity = min(max(np.log10(Z), -4.99), -1.41)
            atm_file = 'BPASS_2.2.1_chab100_burst_single.mod'
           
        elif atm_type == 'Popstar':
            metallicity = min(max(np.log10(Z), -2.39), -1.31)
            atm_file = 'spneb_cha_0.15_100_HR.mod'
        if insert:
            wP.set_priority(5)
            wP.set_radius(r_in = np.log10(p['R_in']))
            wP.set_cste_density(dens = p['log_nH'])
            wP.set_abund(ab_dict = abund)
            wP.set_dust('ism linear {0}'.format(dtg)) 
                    
            wP.set_comments(('logU = {}'.format(p['logU']),
                            'fr = {}'.format(p['fr']),
                            'age = {}'.format(p['age']),
                            'log Z = {}'.format(np.log10(Z)),
                            'log Z_gas = {}'.format(np.log10(Z_dep)),
                            'logOH = {}'.format(p['log_OH']),
                            'abund_width = {}'.format(abund_width),
                            'abund_type = {}'.format(abund_type),
                            'ksi_d = {}'.format(p['ksi_d'])))
            
            wP.set_star('table stars', atm_file=atm_file, atm1=p['age']*1e6, atm2=metallicity, 
                            lumi_unit= 'q(H)', lumi_value = np.log10(p['Q0']))
            wP.insert_model()
        if verbose:
            #print('logU {:5.2f}, O/H {:5.2f} Z {:5.2f} age {:5.2f} fr {:5.2f} dtg {:5.2f}'.format(p['logU'], abund['O'], 
            #                                                                                      np.log10(Z), p['age'], 
            #                                                                                      p['fr'], dtg))
            print(f'O/H in {p["log_OH"]:5.2f} O/H {abund["O"]:5.2f} log10(Z) {np.log10(Z):5.2f} ksi_d {ksi_d2:5.2f} dtg {dtg:5.2f}')


        if i == 0:
            ab_dic_list['log_Z'] = [np.log10(Z)]
            ab_dic_list['log_Z_gas'] = [np.log10(Z_dep)]
            ab_dic_list['DTG'] = [dtg]
            ab_dic_list['log_DTG'] = [np.log10(dtg)]
            ab_dic_list['ksi_d2'] = [ksi_d2]
            for elem in abund:
                ab_dic_list[elem] = [abund[elem]]
        else:
            ab_dic_list['log_Z'].append(np.log10(Z))
            ab_dic_list['log_Z_gas'].append(np.log10(Z_dep))
            ab_dic_list['DTG'].append(dtg)
            ab_dic_list['ksi_d2'].append(ksi_d2)
            ab_dic_list['log_DTG'].append(np.log10(dtg))
            for elem in abund:
                ab_dic_list[elem].append(abund[elem])
        
    for elem in ab_dic_list:
        params[elem] = ab_dic_list[elem]
    return params

#%% tests       

#dN = make_inputs(10000, test_only=False, abund_type='Nicholls', random_seed=42, abund_width=0.2)

#dG = make_inputs(10000, test_only=False, abund_type='Gutkin', random_seed=42, abund_width=0.2)

def plot_compare(dG, dN, var):
    plt.scatter(dG.log_OH, dG[var], label='Gutkin')
    plt.scatter(dN.log_OH, dN[var], alpha=0.05, label='Nicholls')
    plt.legend()
    plt.title(var)

Version = 1.23

