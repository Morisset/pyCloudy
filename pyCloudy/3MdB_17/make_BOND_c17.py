'''
Created on 9 mai 2014

@author: christophemorisset
'''
import numpy as np
import pyCloudy as pc
from pyCloudy.db import use3MdB

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

MdB = pc.MdB(OVN_dic)

models_dir = 'BOND/'
                  
name = 'BOND'  

alpha_B = 2.6e-13

options = ('no molecules',
           'no level2 lines',
           'no fine opacities',
           'COSMIC RAY BACKGROUND',
           )

NH = 1e2
ff = 1.0

tab_lU_mean = np.asarray([-1., -1.5, -2, -2.5, -3, -3.5, -4.0])
tab_O = np.linspace(6.6, 9.4, 15) - 12
tab_NO = np.asarray([-2, -1.5, -1, -0.5, 0.])
tab_NO = np.asarray([-1.75, -1.25, -0.75, -0.25])
tab_age = np.asarray([1., 2, 3, 4, 5, 6]) * 1e6
tab_fr = [.03, 3.00]

pc.log_.level = 2

def get_He(logO):
    
    Y = 0.2514 + 29.81 * 10**logO
    Z = (8.64 * (logO + 12) - 47.44) * 10**logO
    He = np.log10(Y / (4 * (1. - Z - Y)))
    return He

def test_inputs(all_tabs):
    i = 1
    for lU_mean, ab_O, NO, age, fr in all_tabs:
        xt = 8.10
        x = 12 + ab_O
        a = 2.21 # log(G/D) solar
        if x > xt:
            y = a + 1.00 * (8.69 - x)
        else:
            y = 0.96 + 3.10 * (8.69 - x)
        solar_GoD = 10**a 
        this_GoD = 10**y # y is log(G/D)
        this_relative_GoD =  this_GoD / solar_GoD#  we want the correction to apply to solar Dust abundance
        this_relative_DoG = 1.0 / this_relative_GoD
        print('{} {} {} {} {} {} {} '.format(i, lU_mean, ab_O, NO, age, fr, this_relative_DoG))
        i += 1
        
def make_inputs(all_tabs):
    
    wP = use3MdB.writePending(MdB, OVN_dic)
    wP.set_ref(name)
    wP.set_user('Natalia')
    wP.set_C_version('17.01')
    wP.set_iterate(1)
    wP.set_file(name)
    wP.set_dir(models_dir)
    wP.set_cloudy_others(options)
    wP.set_N_Hb_cut(9)
    wP.set_geometry('Sphere')
    wP.set_stop(('temperature 20', 'pfrac 0.02'))
    c = pc.CST.CLIGHT
    # Starting the main loop on the 4 parameters.
    for lU_mean, ab_O, NO, age, fr in all_tabs:
        U_mean = 10**lU_mean
        w = (1 + fr**3.)**(1./3) - fr
        Q0 = 4. * np.pi * c**3 * U_mean**3 / (3. * NH * ff**2 * alpha_B**2 * w**3)
        R_str = (3. * Q0 / (4 * np.pi * NH**2 * alpha_B * ff))**(1./3)
        R_in = fr * R_str
        if fr < 1.0:
            wP.set_priority(5)
        else:
            wP.set_priority(15)
        wP.set_radius(r_in = np.log10(R_in))
        wP.set_cste_density(dens = np.log10(NH))
        ###GS  for Ne/O, S/O, Cl/O, Ar/O, Fe/O we take the average ot the ratios 
        ###GS in the DR7-025-clean + DR10 samples from the O3O2 paper (Stasinska et al 2014)
        ###GS we do not take into account the observed variation of Fe/O
        ###GS for Si/O and Mg/O we take the CEL Orion values from Simon-Diaz & Stasinska 2011
        
        abund = {'N'  :   ab_O + NO,
                 'O'  :   ab_O,
                 'Ne' :   ab_O - 0.73, 
                 'Mg' :   ab_O - 2.02,
                 'Si' :   ab_O - 2.02,
                 'S'  :   ab_O - 1.66,
                 'Cl' :   ab_O - 3.54,
                 'Ar' :   ab_O - 2.32,
                 'Fe' :   ab_O - 1.83}
        ab_O_12 = 12 + ab_O
        if ab_O_12 > 8.1:
            abund['Si'] -= 1 
            abund['Mg'] -= 1 
            abund['Fe'] -= 1.5 
        abund['He'] = get_He(abund['O'])
        ###GS C is inspired by CEL vales of C and N in Orion (SDS11) and fig 11 from Esteban et al 2014
        abund['C'] = 8.40 - 7.92 + abund['N']
        wP.set_abund(ab_dict = abund)
        
        ###Remy-Ruyer et al 2014, broken power-law XCO,z case (as recommended by them)
        xt = 8.10
        x = 12 + ab_O
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
        wP.set_dust('ism {0}'.format(Draine_fact * this_relative_DoG)) 
                
        wP.set_comments(('lU_mean = {0}'.format(lU_mean),
                        'fr = {0}'.format(fr),
                        'age = {0}'.format(age),
                        'ab_O = {0}'.format(ab_O),
                        'NO = {0}'.format(NO)))
        
        metallicity = min(max(-1.87 + (ab_O - -3.3), -3.99), -1.31)
        wP.set_star('table stars', atm_file='sp_cha.mod', atm1=age, atm2=metallicity, 
                        lumi_unit= 'q(H)', lumi_value = np.log10(Q0))
        wP.insert_model()
            

all_tabs =  [(lU_mean, ab_O, NO, age, fr) 
             for lU_mean in tab_lU_mean 
             for ab_O in tab_O 
             for NO in tab_NO 
             for age in tab_age
             for fr in tab_fr]

#all_tabs = [(-2, -4.4, -1, 3000000., 0.03), (-2, -4.4, -1, 3000000., 3.0)]
"""
In [2]: tab_lU_mean                                                                                                                            
Out[2]: array([-1. , -1.5, -2. , -2.5, -3. , -3.5, -4. ])

In [3]: tab_O                                                                                                                                  
Out[3]: 
array([-5.4, -5.2, -5. , -4.8, -4.6, -4.4, -4.2, -4. , -3.8, -3.6, -3.4,
       -3.2, -3. , -2.8, -2.6])

In [4]: tab_NO                                                                                                                                 
Out[4]: array([-2. , -1.5, -1. , -0.5,  0. ])

In [5]: tab_age                                                                                                                                
Out[5]: array([1000000., 2000000., 3000000., 4000000., 5000000., 6000000.])

"""

make_inputs(all_tabs)

Version = 3

