#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 30 16:05:34 2020

@author: christophemorisset
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Aug 15 14:37:14 2012

@author: morisset
"""

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

pc.config.SAVE_LIST_ELEMS.append(['nickel', '.ele_Ni'])

commons = ['no molecules', 'no level2 lines', 'no fine opacities']
tab_L = np.log10(np.asarray([2e2, 1e3, 3e3, 5.6e3, 1e4, 1.78e4]))
tab_dens = np.log10(np.asarray([3e1,1e2,3e2,1e3,3e3,1e4,3e4,1e5,3e5]))
tab_R = np.log10(np.asarray([3e15, 1e16, 3e16, 1e17, 3e17, 1e18, 3e18]))

tabs_T = {'BB' : np.asarray([25, 30, 35, 40, 50, 60, 70, 75, 80, 90, 100, 110, 120, 125, 130, 140, 
                             150, 160, 170, 180, 190, 200, 210, 220, 230, 240, 250, 260, 270, 280, 290, 300])*1e3,
          'TR' : np.asarray([50, 60, 70, 75, 80, 90, 100, 110, 120, 125, 130, 140, 150, 160, 170, 180])*1e3,
          'TL' : np.asarray([27.5, 30, 35, 40, 45, 50, 55])*1e3,
          'WM' : np.asarray([30, 35, 40, 45, 50])*1e3,
          }
dic_SEDs = {'TR': "rauch_h-ni_3d.mod",
            'TL': "ostar2002_3d.mod",
            'WM': "wmbasic.mod"
            }
dic_O = {-3.66:'L', -3.36:'S', -3.06:'H', -2.76:'VH'}

Q02Lum = {'BB' : {25000.0 : 43.23, 35000.0 : 43.63, 50000.0 : 43.83, 75000.0 : 43.89, 100000.0 : 43.86, 
                  125000.0 : 43.81, 150000.0 : 43.76, 180000.0 : 43.7, 210000.0 : 43.65, 240000.0 : 43.6,
                  270000.0 : 43.55, 300000.0 : 43.51, 30000.0 : 43.47, 40000.0 : 43.72, 60000.0 : 43.87, 
                  70000.0 : 43.89, 80000.0 : 43.88,
                  90000.0 : 43.87, 110000.0 : 43.84, 120000.0 : 43.82, 130000.0 : 43.80, 140000.0 : 43.78,
                  160000.0 : 43.74, 170000.0 : 43.72, 190000.0 : 43.68, 200000.0 : 43.66, 220000.0 : 43.63,
                  230000.0 : 43.61, 250000.0 : 43.58, 260000.0 : 43.57, 280000.0 : 43.54, 290000.0 : 43.53},
          'TR' : {50000.0 : 43.78, 60000.0 : 43.84, 70000.0 : 43.86, 75000.0 : 43.86, 80000.0 : 43.86, 90000.0 : 43.86,
                  100000.0 : 43.85, 110000.0 : 43.84,120000.0 : 43.82,125000.0 : 43.81, 130000.0 : 43.79, 140000.0 : 43.76,
                  150000.0 : 43.73, 160000.0 : 43.70, 170000.0 : 43.67, 180000.0 : 43.66},
          'TL' : {27500.0 : 42.46, 30000.0 : 42.93, 35000.0 : 43.49, 40000.0 : 43.70, 45000.0 : 43.80,
                  50000.0 : 43.85, 55000.0 : 43.88},
          'WM' : {30000.0 : 42.35, 35000.0 : 43.33, 40000.0 : 43.61, 45000.0 : 43.75,50000.0 : 43.82}
          }

def get_Q02Lum(SED, logg):
    """
    Usage: get_Q02Lum('TL', 4)
    """
    if SED not in tabs_T:
        print('{0} is not in {1}'.format(SED, tabs_T.keys()))
        return None
    Q02l = {}
    lumi = 3
    for Teff in tabs_T[SED]:
        In = pc.CloudyInput('./M1')
        In.set_cste_density(2)
        In.set_radius(19)
        if SED[0:2] != 'BB':
            In.set_star('table star "{0}"'.format(dic_SEDs[SED]), (Teff, logg, 0), 'luminosity total solar', lumi)
        else:
            In.set_BB(Teff, 'luminosity total solar', lumi)
        In.set_stop('zone 2')
        In.print_input()
        In.run_cloudy()
        Out = pc.CloudyModel('./M1', read_emis = False)
        print('{0} : {1:.2f},'.format(Teff, np.log10(Out.Q0)-lumi))
        Q02l[Teff] = np.log10(Out.Q0)-lumi
    

def S_thickness(Q0, dens, r_in):
    """
    Stromgren thickness.
    Q0 in log
    dens in cm-3
    r_in in cm
    """
    alphaB = 1.6e-13
    return (3 * 10**Q0 / (4. * np.pi * alphaB * dens**2) + r_in**3)**(1./3.) - r_in
    
        
def make_inputs_MdB(SED = 'BB', dens_law = 'C', dust=True, ab_O = -2.76):
    
    name = '{0}_{1}'.format(SED, dens_law)
    all_tabs =  [(T, R, dens, L) 
                 for T in tabs_T[SED] 
                 for R in tab_R 
                 for dens in tab_dens 
                 for L in tab_L]    
    ab_NO  = -0.39
    
    MdB = pc.MdB(OVN_dic)
    pc.log_.level = 3
    wP = use3MdB.writePending(MdB, OVN_dic)
    wP.set_ref("PNe_2020")
    wP.set_user('Gloria')
    wP.set_C_version('17.01')
    wP.set_iterate(1)
    wP.set_file(name)
    wP.set_priority(10)
    wP.set_cloudy_others(('no molecules',
                'no level2 lines',
                'no fine opacities',
                'COSMIC RAY BACKGROUND'))
    wP.set_N_Mass_cut(4)
    wP.set_dir('PNe_2020/')

    for T, R, dens, L in all_tabs:
        Q0 = L + Q02Lum[SED][T]
        wP.set_comments(dic_O[ab_O], i_com=3)
        wP.set_radius(R)
        if dens_law == 'C':
            wP.set_cste_density(dens)
        elif dens_law == 'G1':
            thickness = S_thickness(Q0, 10.**dens, 10.**R)
            wP.set_dlaw((3, 0., 10.**dens, 0.0, np.log10(thickness)+0.05, 0., 17., 17.))
        elif dens_law == 'G2':
            thickness = S_thickness(Q0, 10.**dens, 10.**R)
            wP.set_dlaw((310, 10.**dens / 0.37/5., 10.**dens / 0.37, np.log10(thickness)+0.05, np.log10(thickness)+0.05, 0., 17., 17.))
        else:
            pc.log_.error('unknown dens_law {0}'.format(dens_law))
        wP.set_comments(dens_law, i_com=1)
        if dust:
            wP.set_dust('ism', 1.)
            wP.set_comments('D', i_com=4)
        else:
            wP.set_dust()
            wP.set_comments('N', i_com=4)
        if SED == 'BB':
            wP.set_star('Blackbody', atm1=T, lumi_unit = 'luminosity total solar',
                         lumi_value = L)
            wP.set_comments('BB', i_com=0)
        elif SED == 'BB2':
            wP.set_star('Blackbody', atm1=T, lumi_unit = 'luminosity total solar',
                         lumi_value = L)
            wP.set_comments('BB', i_com=0)
        elif SED == 'TR':
            wP.set_star('table star \"{0}\"'.format(dic_SEDs[SED]), atm1=T, atm2=6, atm3=0, 
                        lumi_unit= 'luminosity total solar', lumi_value = L)
            wP.set_comments('TR', i_com=0)
        elif SED == 'TL':
            wP.set_star('table star \"{0}\"'.format(dic_SEDs[SED]), atm1=T, atm2=4, atm3=0, 
                        lumi_unit= 'luminosity total solar', lumi_value = L)
            wP.set_comments('TL', i_com=0)
        elif SED == 'WM':
            wP.set_star('table star \"{0}\"'.format(dic_SEDs[SED]), atm1=T, atm2=4, atm3=0, 
                        lumi_unit= 'luminosity total solar', lumi_value = L)
            wP.set_comments('WM', i_com=0)
        else:
            pc.log_.error('unknown SED {0}'.format(SED))
        
        ab_dict = {'He' : -1.00, 'Li': -8.69, 'Be':-10.67, 'B' : -9.21, 
                                'C': ab_O + 0.25, 'N' : ab_O + ab_NO, 'O' : ab_O, 
                                'F': -6.5, 'Ne' :ab_O - 0.60, 'Na': -5.7, 'Mg' : -5.8, 'Al': -6.57, 'Si' : -5.0, 'P': -6.7,
                                'S': ab_O - 1.64, 'Cl': ab_O - 3.41, 'Ar': ab_O - 2.21, 'K': -6.9, 'Ca': -7.9,
                                'Sc': -8.83, 'Ti': -6.98, 'V' : -8.0, 'Cr': -6.33, 'Mn': -6.54, 'Fe': -6.30,
                                'Co': -7.08, 'Ni': -5.75, 'Cu': -7.79, 'Zn': -7.4}
        
        wP.set_abund(ab_dict = ab_dict)

        wP.set_stop(('eden {0}'.format(dens - 3), 'temperature off', 'pfrac 0.02'))
        wP.insert_model()

def make_grids():

    for dust in ((True, False)):
        for ab_O in ((-3.66, -3.36, -3.06, -2.76)):
            make_inputs_MdB(SED = 'BB', dens_law = 'C', dust=dust, ab_O=ab_O)
            make_inputs_MdB(SED = 'TR', dens_law = 'C', dust=dust, ab_O=ab_O)

def post_processing(OVN_dic=OVN_dic):
    
    MdB = pc.MdB(OVN_dic)
    
    ref = 'PNe_2020'
    MdB.exec_dB("update tab_17 set com6 = '' where ref like '{0}' ".format(ref))
    MdB.exec_dB("update tab_17 set com3 = 'R' where  ref like '{0}' and MassFrac >= 0.95".format(ref))
    MdB.exec_dB("update tab_17 set com3 = 'M80' where  ref like '{0}' and MassFrac < 0.95 and MassFrac >= 0.7".format(ref))
    MdB.exec_dB("update tab_17 set com3 = 'M60' where  ref like '{0}' and MassFrac < 0.7 and MassFrac >= 0.5".format(ref))
    MdB.exec_dB("update tab_17 set com3 = 'M40' where  ref like '{0}' and MassFrac < 0.5 and MassFrac >= 0.3".format(ref))
    MdB.exec_dB("update tab_17 set com3 = 'M20' where  ref like '{0}' and MassFrac < 0.3".format(ref))
    
    MdB.exec_dB("update tab_17 set cloudy5 = '1' where  ref like '{0}' and lumi < 4.2 and (lumi > 3.4 or atm1 > 100000) and lumi > 1.5e-5*atm1-0.25".format(ref))
    MdB.exec_dB("update tab_17 set cloudy6 = '1' where  ref like '{0}' and H_mass < 1.0".format(ref))
    MdB.exec_dB("update tab_17 join abion_17 on tab_17.N = abion_17.N set tab_17.cloudy7 = abion_17.A_HYDROGEN_vol_1  where tab_17.ref like '{0}'".format(ref))
    MdB.exec_dB("update tab_17 set cloudy8 = '1' where  ref like '{0}' and nH_mean * pow(10,rout*3) > 2e53 and nH_mean * pow(10, rout*3) < 3e56".format(ref))
    MdB.exec_dB("update tab_17 set cloudy9 = '1' where  ref like '{0}' and H__1_486133A/pow(4*3.1415967*pow(10,rout)*206265., 2) < 1e-11 and H__1_486133A/pow(4*3.1415967*pow(10,rout)*206265., 2) > 1e-15".format(ref))

    MdB.exec_dB("update tab_17 set com6 = '1' where ref like '{0}' and cloudy5 = '1' and cloudy6 = '1' and cloudy8 = '1' and cloudy9 = '1' and MassFrac > 0.2".format(ref))
    MdB.exec_dB("update tab_17 set com6 = '0' where ref like '{0}' and com6 != '1'".format(ref))



__version__ = 4
