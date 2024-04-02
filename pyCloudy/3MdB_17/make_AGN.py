#!/usr/bin/env python
# coding: utf-8

import numpy as np
import copy
import pyCloudy as pc
from pyCloudy.db import use3MdB
from pyCloudy.utils.physics import abunds_Bressan_2012, get_abund_nicholls, ATOMIC_MASS
from pyCloudy.utils.physics import depletion_dopita_2013, depletion_cloudy_17

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

name = 'AGN_1'  

models_dir = 'AGN_1/'
                  
options = ('COSMIC RAY BACKGROUND',)


def get_metallicity(ab_dic, depl_dic=None, log_depl = 0.0, ksi_d=None):
    """
    Return the total metallicity, the metallicity in gaseous phase, the ksi_d, and Y from:
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
 
def get_abunds(log_OH_tot=-3.16526, log_CO=-0.3565, log_NO=-1.155, ksi_d=0, 
               abund_type = 'Gutkin'):
    
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
    
    
    Z, Z_dep, ksi_d2, Y = get_metallicity(abund, depletion, log_depl=0, ksi_d=ksi_d)
    abund2 = deplete(abund, depletion, log_depl=0, ksi_d=ksi_d)
    
    if abund_type == 'Gutkin':
        Y_Gut = 0.2485 + 1.7756 * Z
        abund2['He'] = np.log10(Y_Gut / (4 * (1. - Z - Y_Gut)))
        Z_, Z_dep, ksi_d3, Y = get_metallicity(abund2)
    
    
    return Z, Z_dep, ksi_d2, abund, abund2


tab_lU_mean = np.asarray([-1, -1.5, -2, -2.5, -3, -3.5, -4.0])
tab_log_OH_tot = np.linspace(-5, -2, 15)
tab_lognH = np.asarray((2,3,4,5,5.5, 6, 6.5, 7)) 
tab_ksiD = np.asarray((0.1, 0.3, 0.5))
tab_alpha = np.asarray((-1.2, -1.4, -1.7, -2.0))

all_tabs =  [(lU_mean, log_OH_tot, lognH, ksiD, alpha) 
             for lU_mean in tab_lU_mean 
             for log_OH_tot in tab_log_OH_tot 
             for lognH in tab_lognH
             for ksiD in tab_ksiD
             for alpha in tab_alpha
             ]

def make_inputs(all_tabs, insert=False, verbose=False):
    
    ff = 1.0
    Z_sol = 0.01525

    
    if insert:
        MdB = pc.MdB(OVN_dic)
        wP = use3MdB.writePending(MdB, OVN_dic)
    
        wP.set_ref(name)
        wP.set_user('Chris')
        wP.set_C_version('17.03')
        wP.set_iterate(1)
        wP.set_file(name)
        wP.set_dir(models_dir)
        wP.set_cloudy_others(options)
        wP.set_N_Hb_cut(5)
        wP.set_stop(('temperature 20', 'pfrac 0.02'))
    c = pc.CST.CLIGHT

    # Starting the main loop on the 5 parameters.
    for lU_mean, log_OH_tot, lognH, ksiD, alpha in all_tabs:
        
        Z, Z_dep, ksi_d2, abund_ism, abund = get_abunds(log_OH_tot=log_OH_tot, 
                                                        ksi_d=ksiD, 
                                                        abund_type='Nicholls')
        
        dtg = ksi_d2 / 0.36 * Z / Z_sol 
        

        if insert:
            wP.set_cste_density(dens = lognH)
            wP.set_abund(ab_dict = abund)
            wP.set_dust('ism linear {0}'.format(dtg)) 
                    
            wP.set_comments(('lU_mean = {0}'.format(lU_mean),
                            'OH_tot = {0}'.format(log_OH_tot),
                            'Z = {0}'.format(Z),
                            'ksiD = {0}'.format(ksiD),
                            'alpha = {0}'.format(alpha)
                            ))
            wP.set_star('table power law slope', atm_file='', atm1=alpha, 
                            lumi_unit= 'Ionization parameter log', lumi_value = lU_mean)
            wP.insert_model()

print(len(all_tabs))
#make_inputs(all_tabs, insert=True)

