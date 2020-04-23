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
pc.log_.level=2
pc.MdB.MdBlog_.level = -1
M = use3MdB.manage3MdB(OVN_dic,
                       models_dir='/DATA/',
                       Nprocs=7, clean=True)
M.start()

