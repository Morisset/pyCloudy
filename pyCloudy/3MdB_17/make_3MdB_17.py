#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec  2 18:16:56 2019

@author: morisset
"""

import pyCloudy as pc
import numpy as np
from pyCloudy.db import use3MdB
import pandas as pd
import pymysql
import os
import matplotlib.pyplot as plt
#%%
OVN_dic = {'host' : 'nefeles',
       'user_name' : 'OVN_admin',
       'user_passwd' : 'getenv',
       'base_name' : '3MdB_17',
       'tmp_name' : 'OVN_tmp',
       'pending_table' : '`pending_17`',
       'master_table' : '`tab_17`',
       'teion_table' : '`teion_17`',
       'abion_table' : '`abion_17`',
       'temis_table' : '`temis_17`',
       'lines_table' : '`lines_17`',
       'procIDs_table' : '`procIDs`',
       'seds_table': '`seds_17`' 
       }

"""
TODO for any distribution od c17.01:
    increase NPUNLM in save_line.cpp from 200 to 400
    add 4 radio continuum definitions
    add Pequignot for 4363 recombination (prt_lines.cpp)
"""

dir_ = './models/'
#%%
def get_emis_tab():
    transfo_unit = {'M': 'm', 'A': 'A', 'C':'m'}
    
    from pyCloudy.db.initSQL import lines_list
    emis_tab = []
    for line in lines_list:
        label = line[0]
        ide = line[1]
        if label[-2:] != 'PN':
            lambda_ = line[2]
            if lambda_ > 1000:
                lambda_str = '{0:5.2f}'.format(lambda_)
            elif lambda_ > 100:
                lambda_str = '{0:5.3f}'.format(lambda_)
            elif lambda_ > 10:
                lambda_str = '{0:5.4f}'.format(lambda_)
            else:
                lambda_str = '{0:5.5f}'.format(lambda_)
            unit = transfo_unit[label[11]]
            emis_tab.append('{0} {1}{2}'.format(ide, lambda_str, unit))
    return emis_tab
#%%
def test_labels(model_name, run_it = True):
    full_model_name = '{0}{1}'.format(dir_, model_name)
    dens = 4. #log cm-3
    Teff = 200000. #K
    qH = 47. #s-1
    r_min = 5e16 #cm
    dist = 1.26 #kpc
    options = ('no molecules',
                'COSMIC RAY BACKGROUND'
                )
    abund = {'He' : -0.92, 'C' : 6.85 - 12, 'N' : -4.0, 'O' : -3.40, 'Ne' : -4.00, 
             'S' : -5.35, 'Ar' : -5.80, 'Fe' : -7.4, 'Cl' : -7.00}

    c_input = pc.CloudyInput(full_model_name)
    c_input.set_BB(Teff = Teff, lumi_unit = 'q(H)', lumi_value = qH)
    c_input.set_cste_density(dens)
    # Defining the inner radius. A second parameter would be the outer radius (matter-bounded nebula).
    c_input.set_radius(r_in=np.log10(r_min))
    c_input.set_abund(ab_dict = abund, nograins = True)
    c_input.set_other(options)
    c_input.set_iterate() # (0) for no iteration, () for one iteration, (N) for N iterations.
    c_input.set_sphere() # () or (True) : sphere, or (False): open geometry.
    c_input.set_emis_tab(get_emis_tab()) # better use read_emis_file(file) for long list of lines, where file is an external file.
    c_input.set_distance(dist=dist, unit='kpc', linear=True) # unit can be 'kpc', 'Mpc', 'parsecs', 'cm'. If linear=False, the distance is in log.
    
    # Writing the Cloudy inputs. to_file for writing to a file (named by full_model_name). verbose to print on the screen.
    c_input.print_input(to_file = True, verbose = False)
    if run_it:
        c_input.run_cloudy()
        
def run_test_labels(model_name='model_1'):
    test_labels(model_name)
    M = pc.CloudyModel('{0}{1}'.format(dir_, model_name), read_cont=True)
    M.print_lines(norm='CA_B_486133A')
#%%
def set_grid():
    MdB = pc.MdB(OVN_dic)
    models_dir = 'TEST1/'
    name = 'test_2'
    options = ('no molecules',
               'no level2 lines',
               'no fine opacities',
               'COSMIC RAY BACKGROUND',
               )

    wP = use3MdB.writePending(MdB, OVN_dic)
    
    wP.set_ref(name)
    wP.set_user('Test')
    wP.set_C_version('17.01')
    wP.set_iterate(1)
    wP.set_file(name)
    wP.set_dir(models_dir)
    wP.set_cloudy_others(options)
    wP.set_N_Hb_cut(4)
    wP.set_geometry('Sphere')
    wP.set_stop(('temperature 20', 'pfrac 0.02', 'zone 10'))
    # Starting the main loop on the 4 parameters.
    for age in 1e6 * (1+np.arange(200)/100):
        wP.set_priority(5)
        wP.set_radius(r_in = 18)
        wP.set_cste_density(dens = 2)
        ab_O = -3.5
        abund = {'He' :   -1,
                 'C'  :   -4,
                 'N'  :   ab_O -1,
                 'O'  :   ab_O,
                 'Ne' :   ab_O - 0.73, 
                 'Mg' :   ab_O - 2.02,
                 'Si' :   ab_O - 2.02,
                 'S'  :   ab_O - 1.66,
                 'Cl' :   ab_O - 3.54,
                 'Ar' :   ab_O - 2.32,
                 'Fe' :   ab_O - 1.83}
        wP.set_abund(ab_dict = abund)
        wP.set_dust('ism 1')         
        wP.set_distance(1.0)
        wP.set_star('table stars', atm_file='sp_cha.mod', 
                    atm1=age, atm2=-2.4, 
                    lumi_unit= 'q(H)', lumi_value = 50)
        wP.insert_model()
#%%
def run_multi_3MdB():
    pc.log_.level=2
    pc.MdB.MdBlog_.level = -1
    M = use3MdB.manage3MdB(OVN_dic,
                       models_dir='/DATA/',
                       Nprocs=8, clean=True)
    M.start()
#%%
def test_BPT():
    co = pymysql.connect(host=os.environ['MdB_HOST'], 
                         db=os.environ['MdB_DB_17'], 
                         user=os.environ['MdB_USER'], 
                         passwd=os.environ['MdB_PASSWD'])
    res = pd.read_sql("""SELECT log10(N__2_658345A/H__1_656281A) AS n2, 
                      log10(O__3_500684A/H__1_486133A) AS o3, 
                      OXYGEN AS O FROM tab_17 WHERE ref = 'test_1' AND HBfrac > 0.9""", con=co)
    co.close()
    f, ax = plt.subplots()
    ax.scatter(res['n2'], res['o3'], c=res['O'], edgecolor='')   