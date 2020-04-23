#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 13 11:16:32 2020

@author: christophemorisset
"""


import numpy as np
import pyCloudy as pc
from pyCloudy.db import use3MdB
from pyCloudy.utils.physics import abund_Asplund_2009 as selected_abunds

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

tab_lU_mean = np.asarray([-1.5, -1.75, -2, -2.25, -2.5, -2.75, -3, -3.25, -3.5, -3.75, -4.0])
tab_NH = np.array([10.])
tab_fr = np.array([0.03, 3.00])
tab_dNO = np.array([-1.5,-1.25,-1.0, -0.75, -0.5, -0.25, 0.0, 0.25, 0.5]) # relative to N/O = 7.83-8.69 = -0.86

uniq_ages = np.array([1.00000000e-03,   3.00000000e-03,   4.00000000e-03,
                       5.60000000e-03,   8.90000000e-03,   1.00000000e-02,
                       1.26000000e-02,   1.41000000e-02,   1.78000000e-02,
                       1.99000000e-02,   2.51000000e-02,   3.16000000e-02,
                       3.98000000e-02,   5.62000000e-02,   6.30000000e-02,
                       6.31000000e-02,   7.08000000e-02,   1.00000000e-01,
                       1.12200000e-01,   1.25900000e-01,   1.58500000e-01,
                       1.99500000e-01,   2.81800000e-01,   3.54800000e-01,
                       5.01200000e-01,   7.07900000e-01,   8.91300000e-01,
                       1.12200000e+00,   1.25890000e+00,   1.41250000e+00,
                       1.99530000e+00,   2.51190000e+00,   3.54810000e+00,
                       4.46680000e+00,   6.30960000e+00,   7.94330000e+00,
                       1.00000000e+01,   1.25893000e+01,   1.41254000e+01])

uniq_mets = np.array([ 0.0037,  0.0076,  0.019 ,  0.0315])

alpha_B = 2.6e-13

def count_CALIFA():
    all_tabs =  [(lU_mean, met, dNO, age, fr, NH) 
                 for lU_mean in tab_lU_mean 
                 for met in uniq_mets 
                 for dNO in tab_dNO 
                 for age in uniq_ages 
                 for fr in tab_fr
                 for NH in tab_NH]
    i = 0
    for lU_mean, met, dNO, age, fr, NH in all_tabs:
        i += 1
    print(i)

def make_CALIFA_dB():
    """
    Create the pending entries to run individual grids of models corresponding to the CALIFA ages and metallicities.
    """
    
    
    ff = 1.0
    c = pc.CST.CLIGHT
    MdB = pc.MdB(OVN_dic)
    wP = use3MdB.writePending(MdB, OVN_dic)
    wP.set_ref("CALIFA")
    wP.set_user("Christophe")
    wP.set_file('CALIFA')
    wP.set_dir('CALIFA')
    wP.set_priority(4)
    wP.set_cloudy_others(('no molecules',
                'no level2 lines',
                'no fine opacities',
                'COSMIC RAY BACKGROUND'))
    wP.set_iterate(1)
    wP.set_N_Hb_cut(4)
    wP.set_C_version('17.01')
    wP.set_geometry('Sphere')
    wP.set_stop(('temperature 200', 'pfrac 0.05'))
    all_tabs =  [(lU_mean, met, dNO, age, fr, NH) 
                 for lU_mean in tab_lU_mean 
                 for met in uniq_mets 
                 for dNO in tab_dNO 
                 for age in uniq_ages 
                 for fr in tab_fr
                 for NH in tab_NH]
    for lU_mean, met, dNO, age, fr, NH in all_tabs:
        U_mean = 10**lU_mean
        w = (1 + fr**3.)**(1./3) - fr
        Q0 = 4. * np.pi * c**3 * U_mean**3 / (3. * NH * ff**2 * alpha_B**2 * w**3)
        R_str = (3. * Q0 / (4 * np.pi * NH**2 * alpha_B * ff))**(1./3)
        R_in = fr * R_str
        wP.set_radius(r_in = np.log10(R_in))
        wP.set_cste_density(dens = np.log10(NH))
        coeff_met = met / 0.019 
        abunds = selected_abunds.copy()
        for elem in abunds:
            if elem != 'He':
                abunds[elem] += np.log10(coeff_met)
        abunds['N'] += dNO
        wP.set_abund(ab_dict = abunds)        
        xt = 7.96
        x = 12 + abunds['O']
        if x > xt:
            y = 2.21 + 1.00 * (8.69 - x)
        else:
            y = 0.68 + 3.08 * (8.69 - x)
        Draine_fact = 2./3. # Draine 2001, 
        wP.set_dust('ism {0}'.format(Draine_fact * 10**(2.21-y)))
        wP.set_comments(('lU_mean = {0}'.format(lU_mean),
                        'fr = {0}'.format(fr),
                        'age = {0}'.format(age),
                        'met = {0}'.format(met),
                        'NO = {0}'.format(dNO),
                        'NH = {0}'.format(NH)))
        wP.set_star('table stars \"sp_cha.mod\" ', age*1e9, np.log10(met), 
                    lumi_unit= 'q(H)', lumi_value = np.log10(Q0))
        wP.insert_model()
    MdB.close_dB()
