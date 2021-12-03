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

OVN_dic = {'host' : 'taranis',#  'nefeles',
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

models_dir = 'HII_21/'
                  
name = 'HII_21'  

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
        Z, Z_dep, ksi_d_ori = get_metallicity(ab_dic, depl_dic, log_depl, ksi_d=None)
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
    return M_metals / M_all, M_metals_dep / M_all_dep, 1 - M_metals_dep/M_metals
        
def print_ab_dics(ab_dics, norm=12):
    
    Zs = [get_metallicity(ab_dic)[0] for ab_dic in ab_dics]
    print('  ', ' '.join(['{:9.5f}'.format(Z) for Z in Zs]))
    for elem in sorted(ab_dics[0], key=lambda elem: Z_pc[elem]):
        if elem != 'H':
            print('{:2s}'.format(elem), ' '.join(['{:9.5f}'.format(norm+ab_dic[elem]) for ab_dic in ab_dics]))

def get_Gutkin(log_OH=-3.16526):
    ref_log_OH =-3.16526
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

#%% Define tables
options = ('COSMIC RAY BACKGROUND',)

params_dic = {'logU': (-4, -1, 0.5),
              'log_OH': (6.5-12, 9.5-12, 0.5),
              'log_NO': (-2, 0, 0.5),
              'log_CO': (-1, 0.5, 0.5),
              'age': (1, 6, 0.),
              'log_fr': (-1.5, 1.5, 0),
              'log_nH': (1, 4, 0.5),
              'log_dep': (-0.2, -0.05, 0.05),
              'ksi_d': (0.15, 0.55, 0.)
              }

abund_width = 0.02


#%% define small functions

def get_params(N):

    values = {k: plateau_ailes(N, params_dic[k]) for k in params_dic.keys()}
    return pd.DataFrame(values)


#%% define main function        
def make_inputs(N, insert=False, abund_type='Nicholls', verbose=False, 
                abund_width=abund_width, use_ksi_d=True):
    
    if insert:
        MdB = pc.MdB(OVN_dic)
        wP = use3MdB.writePending(MdB, OVN_dic)
        wP.set_ref(name)
        wP.set_user('Stephane')
        wP.set_C_version('17.02')
        wP.set_iterate(1)
        wP.set_file(name)
        wP.set_dir(models_dir)
        wP.set_cloudy_others(options)
        wP.set_N_Hb_cut(9)
        wP.set_geometry('Sphere')
        wP.set_stop(('temperature 20', 'pfrac 0.02'))
    
    c = pc.CST.CLIGHT
    alpha_B = 2.6e-13
    params = get_params(N)
    params['U'] = 10**params['logU']
    params['NH'] = 10**params['log_nH']
    params['fr'] = 10**params['log_fr']
    ff = 1.0
    if abund_type == 'Nicholls':
        depletion = depletion_dopita_2013
    elif abund_type == 'Gutkin':
        depletion = depletion_cloudy_17
    else:
        raise 
    
    w = (1 + params['fr']**3.)**(1./3) - params['fr']
    Q0 = 4. * np.pi * c**3 * params['U']**3 / (3. * params['NH'] * ff**2 * alpha_B**2 * w**3)
    R_str = (3. * Q0 / (4 * np.pi * params['NH']**2 * alpha_B * ff))**(1./3)
    params['R_in'] = params['fr'] * R_str
    
    ab_dic_list = {}
    
    for i in range(N):
        p = params.iloc[i]
        log_OH = p['log_OH']
        log_dep = 0.#p['log_dep']
        if abund_type == 'Nicholls':
            abund = get_abund_nicholls(log_OH)
        elif abund_type == 'Gutkin':
            abund = get_Gutkin(log_OH)
        
        abund['N'] = p['log_NO'] + log_OH
        abund['C'] = p['log_CO'] + log_OH
        CH_tot = abund['C']
        if use_ksi_d:
            ksi_d = p['ksi_d']
        else:
            ksi_d = None #p['ksi_d']
        Z, Z_dep, ksi_d = get_metallicity(abund, depletion, log_dep, ksi_d=ksi_d)
        abund = deplete(abund, depletion, log_dep, ksi_d=ksi_d)
        CH_dep = abund['C']
        
        for elem in abund:
            if elem != 'H':
                abund[elem] += np.random.normal(0, abund_width)
        
        ###Remy-Ruyer et al 2014, broken power-law XCO,z case (as recommended by them)
        xt = 8.10
        x = 12 + abund['O']
        a = 2.21 # log(G/D) solar
        if x > xt:
            y = a + 1.00 * (8.69 - x)
        else:
            y = 0.96 + 3.10 * (8.69 - x)
        Draine_fact = 2./3. # Draine 2011, 
        solar_GoD = 10**a 
        this_GoD = 10**y # y is log(G/D)
        this_relative_GoD =  this_GoD / solar_GoD#  we want the correction to apply to solar Dust abundance
        this_relative_DoG = 1.0 / this_relative_GoD
        dtg = Draine_fact * this_relative_DoG
        
        dtg = ksi_d / 0.4

        metallicity = min(max(-1.87 + (np.log10(Z)), -3.99), -1.31)
        
        if insert:
            wP.set_priority(5)
            wP.set_radius(r_in = np.log10(p['R_in']))
            wP.set_cste_density(dens = p['log_NH'])
            wP.set_abund(ab_dict = abund)
            wP.set_dust('ism {0}'.format(ksi_d/0.4)) 
                    
            wP.set_comments(('lU_mean = {}'.format(p['logU']),
                            'fr = {}'.format(p['fr']),
                            'age = {}'.format(p['age']),
                            'Z = {}'.format(Z),
                            'NO = {}'.format(p['log_NO']),
                            'CO = {}'.format(p['log_CO']),
                            'abund_width = {}'.format(abund_width),
                            'abund_type = {}'.format(abund_type),
                            'ksi_d = {}'.format(p['ksi_d'])))
            
            wP.set_star('table stars', atm_file='sp_cha.mod', atm1=p['age'], atm2=metallicity, 
                            lumi_unit= 'q(H)', lumi_value = np.log10(Q0))
            wP.insert_model()
        if verbose:
            print('logU {:5.2f}, O/H {:5.2f} Z {:5.2f} age {:5.2f} fr {:5.2f} dtg {:5.2f}'.format(p['logU'], abund['O'], 
                                                                                                  np.log10(Z), p['age'], 
                                                                                                  p['fr'], dtg))
        if i == 0:
            ab_dic_list['log_Z'] = [np.log10(Z)]
            ab_dic_list['DTG'] = [dtg]
            for elem in abund:
                ab_dic_list[elem] = [abund[elem]]
        else:
            ab_dic_list['log_Z'].append(np.log10(Z))
            ab_dic_list['DTG'].append(dtg)
            for elem in abund:
                ab_dic_list[elem].append(abund[elem])
        
    for elem in ab_dic_list:
        params[elem] = ab_dic_list[elem]
    return params

#%%

def plot_params(p, bins=100):
    
    f, axes = plt.subplots(4, 3, figsize=(10,10))
    alpha = .01
    ax = axes[0,0]
    ax.hist(p['logU'], bins=bins)
    ax.set_xlabel('logU')

    ax = axes[0,1]
    ax.hist(p['log_fr'], bins=bins)
    ax.set_xlabel('log_fr')

    ax = axes[0,2]
    ax.hist(p['age'], bins=bins)
    ax.set_xlabel('age')
    
    ax = axes[1,0]
    ax.hist(p['log_Z'], bins=bins)
    ax.set_xlabel('log_Z')

    ax = axes[1,1]
    ax.hist(p['O'], bins=bins)
    ax.set_xlabel('log O/H')
    
    ax = axes[1,2]
    ax.hist((p['DTG']), bins=bins)
    ax.set_xlabel('DTG')
    
    ax = axes[2,0]
    ax.scatter(p['O'], p['Ne'] - p['O'], alpha=alpha, c=p['ksi_d'])
    ax.set_xlabel('log O/H')
    ax.set_ylabel('log Ne/O')
    
    ax = axes[2,1]
    ax.scatter(p['O'], p['S'] - p['O'], alpha=alpha, c=p['ksi_d'])
    ax.set_xlabel('log O/H')
    ax.set_ylabel('log S/O')
    
    ax = axes[2,2]
    ax.scatter(p['O'], p['Fe'] - p['O'], alpha=alpha, c=p['ksi_d'])
    ax.set_xlabel('log O/H')
    ax.set_ylabel('log Fe/O')
    
    ax = axes[3,0]
    ax.hist(p['ksi_d'], bins=bins)
    ax.set_xlabel('ksi_d')
    
    ax = axes[3,1]
    ax.hist(p['Fe'], bins=bins)
    ax.set_xlabel('log Fe/H')
    
    ax = axes[3,2]
    ax.scatter(p['Fe'] - p['O'], p['ksi_d'], alpha=alpha, c=p['O'])
    ax.set_xlabel('log O/H')
    ax.set_xlabel('log Fe/O')
    

    f.tight_layout()
#%% run the make_inputs and get params

#paramsN = make_inputs(N=10000, abund_type='Nicholls', use_ksi_d=False)
#paramsG = make_inputs(N=10000, abund_type='Gutkin', use_ksi_d=False)
#paramsNk = make_inputs(N=10000, abund_type='Nicholls')
paramsGk = make_inputs(N=10000, abund_type='Gutkin')

#%% plot params
#plot_params(paramsN)
#plot_params(paramsG)
#plot_params(paramsNk)
plot_params(paramsGk)

Version = 1

