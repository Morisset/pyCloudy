import os
import glob
import time
import threading
import numpy as np
import datetime
import pyCloudy as pc
from random import randint
from pyCloudy.utils.init import SYM2ELEM, LIST_ALL_ELEM
from pyCloudy.utils.misc import cloudy2pyneb
import pyneb as pn

status_dic = {'Pending model selected':2,
              'Read_pending':3,
              'Cloudy Input filled':4,
              'Cloudy Input printed':5,
              'Cloudy start':6,
              'Cloudy run':7,
              'Cloudy failed':-2,
              'Read_pending2':11,
              'Read model':12,
              'Model read':13,
              'Model not read':-3,
              'Model inserted':14,
              'Abion inserted':15,
              'Teion inserted':16,
              'Temis inserted':17,
              'Master table updated':50,
              }

save_list_elems = [e[0] for e in pc.config.SAVE_LIST_ELEMS]
for elem in list(SYM2ELEM.values()):
    if elem not in save_list_elems:
        syms = [key for key,value in list(SYM2ELEM.items()) if value==elem ]
        if syms != []:
            pc.config.SAVE_LIST_ELEMS.append([elem, '.ele_{0}'.format(syms[0])])
    
def select_from_priorities(Ps):
        Pmax = np.max(Ps)
        Proba = np.cumsum(4**(Pmax-Ps))
        rand = np.random.ranf() * Proba[-1]
        return np.where(rand < Proba)[0][0]
        
class writePending(object):
    
    def __init__(self, MdB=None, OVN_dic = None):
        
        self.log_ = pc.log_
        if MdB is None:
            MdB = pc.MdB(OVN_dic = OVN_dic)
        else:
            OVN_dic = MdB.OVN_dic
            
        if not isinstance(MdB, pc.MdB):
            self.log_.error('The second argument must be a MdB object')
            
        self.MdB = MdB
        self.OVN_dic = OVN_dic
        self.table = OVN_dic['pending_table']
        if self.MdB.connected:
            self.fields = self.MdB.get_fields(from_ = self.table)            
        self._dic = {}
        self.set_status(0)
        self.calling = 'writePending'
    
    def init_all(self):
        self.set_ref()
        self.set_user()
        self.set_radius()
        for i in range(2):
            self.set_star(i_star = i)
        self.set_cste_density()
        self.set_abund()
        self.set_status(0)
        self.set_file('')
        for i in range(2):
            self.set_dust(i_dust = i)
        for i in range(5):
            self.set_stop(i_stop = i)
        self.set_distance()
        self.set_priority()
        self.set_geometry()
        self.set_iterate(1)
        for i in range(8):
            self.set_cloudy_others(i_other = i)
        for i in range(8):
            self.set_comments(i_com = i)
        self.set_N_Mass_cut()
        self.set_GuessMassFrac()
    
    def insert_in_dic(self, key, value):
        
        if value is None:
            if key in self._dic:
                del self._dic[key]
        else:
            self._dic[key] = value

    def set_ref(self, ref=None):
        """
        param:
            ref [string]
        """
        self.insert_in_dic('ref', ref)
        
    def set_dir(self, dir_='.'):
        
        self.insert_in_dic('dir', dir_)
        
    def set_user(self, user=None):
        """
        param:
            user [string]
        """
        self.insert_in_dic('user', user)

    def set_radius(self, r_in=None):
        """
        param:
            r_in [float] (log cm)
        """
        self.insert_in_dic('radius', r_in)

    def set_star(self, SED_shape=None, atm1=None, atm2=None, atm3=None,
                 lumi_unit=None, lumi_value=None, i_star = 0, atm_file=None):
            
        if type(SED_shape) == type(()) or type(SED_shape) == type([]):
            fil = None if atm_file is None else atm_file[0]
            at1 = None if atm1 is None else atm1[0]
            at2 = None if atm2 is None else atm2[0]
            at3 = None if atm3 is None else atm3[0]
            self.set_star(self, SED_shape = SED_shape[0], lumi_unit=lumi_unit[0], 
                          atm_file=fil1, atm1=at1, atm2=at2, atm3=at3,
                          lumi_value=lumi_value[0], i_star = 0)
            
            fil = None if atm_file is None else atm_file[1]
            at1 = None if atm1 is None else atm1[1]
            at2 = None if atm2 is None else atm2[1]
            at3 = None if atm3 is None else atm3[1]
            self.set_star(self, SED_shape = SED_shape[1], lumi_unit=lumi_unit[1], 
                          atm_file=fil1, atm1=at1, atm2=at2, atm3=at3,
                          lumi_value=lumi_value[1], i_star = 1)
        else:
            if i_star == 0:
                i_star_str = ''
            else:
                i_star_str = '2'
            self.insert_in_dic('atm_cmd{0}'.format(i_star_str), SED_shape)
            self.insert_in_dic('atm_file{0}'.format(i_star_str), atm_file)
            self.insert_in_dic('lumi_unit{0}'.format(i_star_str), lumi_unit)
            self.insert_in_dic('lumi{0}'.format(i_star_str), lumi_value)
            self.insert_in_dic('atm1{0}'.format(i_star_str), atm1)
            self.insert_in_dic('atm2{0}'.format(i_star_str), atm2)
            self.insert_in_dic('atm3{0}'.format(i_star_str), atm3)
    
    def set_cste_density(self, dens = None, ff = None):
        self.insert_in_dic('dens', dens)
        self.insert_in_dic('ff', ff)

    def set_ff(self, ff=None):
        self.insert_in_dic('ff', ff)

    def set_dlaw(self, dlaw_params=None, i_param=0):
        """
        Define the user-define density law.
        Parameters:
            - dlaw_params may be of type: 1.4, (1, 2, 4.5) or [1,2,3]
            - i_param: indice of the parameter to set (from 0 to 8). 
                Unused if dlaw_params is a list or a tuple
        """
        if i_param < 0 or i_param > 8:
            self.log_.error('i_param must be between 0 and 8', calling=self.calling)
            return
        if type(dlaw_params) == type(()) or type(dlaw_params)==type([]):
            for i_param, param in enumerate(dlaw_params):
                self.set_dlaw(param, i_param)
        else:
            dlaw_str = 'dlaw{0}'.format(i_param+1)
            self.insert_in_dic(dlaw_str, dlaw_params)


    def set_abund(self, predef = None, elem = None, value = None, nograins = True, 
                  ab_dict = None):
        """
        Define the elemental abundance(s)
        
        Usage:
            set_abund(ab_dict = {'He' : -0.92, 'C' : -4.65}
            
        Parameters:
            ab_dict:    dictionary of abundances. Keys are element symbols, values are abundances in log 
        """
        if ab_dict is not None:
            for elem in ab_dict:
                self.set_abund(elem = elem, value = ab_dict[elem])
        elif predef is not None:
            pass
        elif elem is not None:
            if elem in SYM2ELEM:
                elem_long = SYM2ELEM[elem].upper()
                self.insert_in_dic(elem_long, value)
            else:
                self.log_.error('Unkown element: {0}'.format(elem))
                return None
        else:
            for elem in SYM2ELEM:
                elem_long = SYM2ELEM[elem].upper()
                self.insert_in_dic(elem_long, None)
                
    def set_dust(self, dust_type=None, dust_value=None, i_dust=0):
        
        if i_dust > 2:
            self.log_.error('i_dust must be <= 2', calling=self.calling)
            return
        if type(dust_type) == type(()) or type(dust_type)==type([]):
            if dust_value is None:
                self.log_.error('If dust_type is a list, dust_value must be a list', calling=self.calling)
                return
            for i_dust, dtype in enumerate(dust_type):
                self.set_dust(dtype, dust_value[i_dust], i_dust)
        else:
            type_str = 'dust_type{0}'.format(i_dust+1)
            value_str = 'dust_value{0}'.format(i_dust+1)
            self.insert_in_dic(type_str, dust_type)
            self.insert_in_dic(value_str, dust_value)
        
    def set_iterate(self, n_iter=None):
        
        self.insert_in_dic('iterate', n_iter)
        
    def set_stop(self, stopping_crit=None, i_stop=0):
        
        if i_stop > 5:
            self.log_.error('i_stop must be <= 5', calling=self.calling)
            return
        if type(stopping_crit) == type(()) or type(stopping_crit)==type([]):
            for i_stop, crit in enumerate(stopping_crit):
                self.set_stop(crit, i_stop)
        else:
            stop_str = 'stop{0}'.format(i_stop+1)
            self.insert_in_dic(stop_str, stopping_crit)

    def set_distance(self, distance=None):
        """
        distance in kpc
        """
        self.insert_in_dic('distance', distance)
        
    def set_file(self, name=None):
        self.insert_in_dic('file', name)
        
    def set_status(self, status=0):
        self.insert_in_dic('status', status)

    def set_priority(self, priority=10):
        if (priority < 0) or (priority > 20):
            self.log_.error('priority must be between 0 and 20', calling=self.calling)
            return
        self.insert_in_dic('priority', priority)

    def set_geometry(self, geometry=None):
        if geometry not in (None, 'Sphere'):
            self.log_.error('geometry must be None or "Sphere"', calling=self.calling)
            return
        self.insert_in_dic('geom', geometry)
        
    def set_cloudy_others(self, others=None, i_other=0):
        if (i_other < 0) or (i_other > 8):
            self.log_.error('cloudy other parameter indice must be between 0 and 8', calling=self.calling)
            return
        if type(others) == type(()) or type(others)==type([]):
            for i_other, other in enumerate(others):
                self.set_cloudy_others(other, i_other)
        else:
            other_str = 'cloudy{0}'.format(i_other+1)
            self.insert_in_dic(other_str, others)

    def set_N_Mass_cut(self, N = None):
        self.insert_in_dic('N_Mass_cut', N)
        
    def set_N_Hb_cut(self, N = None):
        self.insert_in_dic('N_Hb_cut', N)
        
    def set_GuessMassFrac(self, massFrac=None):
        self.insert_in_dic('GuessMassFrac', massFrac)

    def set_comments(self, comments=None, i_com=0):
        if (i_com < 0) or (i_com > 8):
            self.log_.error('comments indice must be between 0 and 8', calling=self.calling)
            return
        if type(comments) == type(()) or type(comments)==type([]):
            for i_com, comment in enumerate(comments):
                self.set_comments(comment, i_com)
        else:
            com_str = 'com{0}'.format(i_com+1)
            self.insert_in_dic(com_str, comments)
            
    def set_C_version(self, version=None):
        if version in pc.config.cloudy_dict:
            self.insert_in_dic('C_version', version)

    def insert_model(self, verbose_only=False, status=None):
        
        if not self.MdB.connected:
            self.log_.error('Not connected to the database')
            return None
        
        if status is not None:
            self.set_status(status)
        fields_str = '`date_submitted`, '
        values_str = 'now(), '
        for key in self._dic:
            if self._dic[key] is not None:
                if key in self.fields:
                    fields_str += '`{0}`, '.format(key)
                    if type(self._dic[key]) == type(''):
                        values_str += "'{0}', ".format(self._dic[key])
                    else:
                        values_str += "{0}, ".format(self._dic[key])
                else:
                    self.log_.warn('Unknown field {0} in table {1}'.format(key, self.table))
        fields_str = fields_str[:-2]
        values_str = values_str[:-2]
        command = 'INSERT INTO {0} ({1}) VALUES ({2});'.format(self.table, fields_str, values_str)
        if verbose_only:
            print(command)
        else:
            self.MdB.exec_dB(command, commit=True)
            res, N = self.MdB.select_dB(select_='last_insert_id()', from_=self.table, format_ = 'dict2', commit=True)
            self.last_N = res['last_insert_id()'][0]
            command = 'UPDATE {0} SET FILE="{1}_{2}" WHERE N={2};'.format(self.table, self._dic['file'], 
                                                                          self.last_N)
            self.MdB.exec_dB(command, commit=True)
            self.log_.message('Model sent to {0} with N={1}'.format(self.table, self.last_N),
                              calling=self.calling)
        
def clean_SED(MdB, seds_table, ref, obj_name):
    command = 'DELETE FROM {} WHERE ref = "{}" AND sed_name LIKE "{}_%"'.format(seds_table, ref, obj_name)
    MdB.exec_dB(command)
    
def insert_SED(MdB, seds_table, ref, sed_name, atm_cmd, atm_file, atm1=None, atm2=None, atm3=None, 
                   lumi_unit='', lumi_value=None):
    
    fields_str = 'ref, sed_name, atm_cmd, atm_file, '
    values_str = "'{}', '{}', '{}', '{}', ".format(ref, sed_name, atm_cmd, atm_file)
    if atm1 is not None:
        fields_str += 'atm1, '
        values_str += '{}, '.format(atm1)
    if atm2 is not None:
        fields_str += 'atm2, '
        values_str += '{}, '.format(atm2)
    if atm3 is not None:
        fields_str += 'atm3, '
        values_str += '{}, '.format(atm3)
    fields_str += 'lumi_unit, lumi'
    values_str += "'{}', {}".format(lumi_unit, lumi_value)
    command = 'INSERT INTO {0} ({1}) VALUES ({2});'.format(seds_table, fields_str, values_str)
    MdB.exec_dB(command)
        
        
class writeTab(object):
    
    def __init__(self, MdB=None, OVN_dic=None, models_dir = './', do_update_status=True):
        
        self.log_ = pc.log_
        if MdB is None:
            MdB = pc.MdB(OVN_dic=OVN_dic)
        else:
            OVN_dic = MdB.OVN_dic
        if not isinstance(MdB, pc.MdB):
            self.log_.error('The first argument must be a MdB object')    
        self.MdB = MdB
        if not self.MdB.connected:
            self.MdB.connect_dB()
        self.OVN_dic = OVN_dic
        self.table = OVN_dic['master_table']
        self.pending_table = OVN_dic['pending_table']
        self.models_dir = models_dir
        self.fields = self.MdB.get_fields(from_ = self.table)
        self.pending_fields = self.MdB.get_fields(from_ = self.pending_table)
        self._dic = {}
        self.selectedN = None
        self.do_update_status = do_update_status
         
    def insert_in_dic(self, key, value):
        
        if value is not None and np.isreal(value):
            if not np.isfinite(value):
                value = None
                
        if value is None:
            if key in self._dic:
                del self._dic[key]
        else:
            if key in self.fields:
                self._dic[key] = value
            else:
                self.log_.error('Not a valid field {0}'.format(key))
    
    def update_status(self, status):
        
        if not self.do_update_status:
            return
        if status in status_dic and self.selectedN is not None:
            command = 'UPDATE {0} SET `status`={1} WHERE N = {2}'.format(self.pending_table, 
                                                                         status_dic[status], self.selectedN)   
            self.MdB.exec_dB(command, commit=True)
        else:
            self.log_.error('Unknown status "{0}"'.format(status))

    def read_pending(self, N_pending):
        
        #N_pending = int(pc.sextract(self.CloudyModel.comments,'M3db pending number','*')[0])
        self.selectedN = N_pending
        if not self.MdB.connected:
            self.log_.error('Not connected')
            return None
        
        res, Nres = self.MdB.select_dB(select_='*', from_=self.pending_table, 
                                       where_='N = {0}'.format(N_pending), commit=True)
        self.update_status('Read_pending2')
        self.pending = res[0]

    def read_model(self, name=None):
        if name is None:
            name = self.pending['file']
        self.update_status('Read model')
        try:
            self.CloudyModel = pc.CloudyModel('{0}/{1}/{2}'.format(self.models_dir, self.pending['dir'], name), 
                                              read_cont=True, list_elem = LIST_ALL_ELEM)
            if not self.CloudyModel.aborted:
                self.update_status('Model read')
                status = True
            else:
                self.update_status('Model not read')
                status = False
        except:
            self.update_status('Model not read')
            status = False
            self.log_.warn('Model {0} not read in {1}/{2}/{3}'.format(name, self.models_dir, self.pending['dir'], name))
        self.insert_in_dic('file', name)
        return status
        
    def pending2dic(self):
        
        self.insert_in_dic('N_pending', self.pending['N'])
        
        for field in self.pending_fields:
            if field in self.fields and field[0:4] != 'date' and field != 'N':
                self.insert_in_dic(field, self.pending[field])
        
    def model2dic(self):
        
        self.insert_in_dic('N_zones', self.CloudyModel.n_zones)
        self.insert_in_dic('rout', np.log10(self.CloudyModel.r_out_cut))
        self.insert_in_dic('thickness', self.CloudyModel.thickness)
        self.insert_in_dic('logQ', np.log10(self.CloudyModel.Q0))
        self.insert_in_dic('logQ0', np.log10(self.CloudyModel.Q[0]))
        self.insert_in_dic('logQ1', np.log10(self.CloudyModel.Q[1]))
        self.insert_in_dic('logQ2', np.log10(self.CloudyModel.Q[2]))
        self.insert_in_dic('logQ3', np.log10(self.CloudyModel.Q[3]))
        self.insert_in_dic('logPhi', np.log10(self.CloudyModel.Phi0))
        self.insert_in_dic('logPhi0', np.log10(self.CloudyModel.Phi[0]))
        self.insert_in_dic('logPhi1', np.log10(self.CloudyModel.Phi[1]))
        self.insert_in_dic('logPhi2', np.log10(self.CloudyModel.Phi[2]))
        self.insert_in_dic('logPhi3', np.log10(self.CloudyModel.Phi[3]))
        self.insert_in_dic('Cloudy_version', self.CloudyModel.cloudy_version)
        if self.CloudyModel.n_zones > 1:
            self.insert_in_dic('DepthFrac', self.CloudyModel.depth[-1] / self.CloudyModel.depth_full[-1])
            self.insert_in_dic('MassFrac', self.CloudyModel.H_mass / self.CloudyModel.H_mass_full[-1])
            self.insert_in_dic('HbFrac', self.CloudyModel.Hbeta / self.CloudyModel.Hbeta_full[-1])
            if 'Cloudy ends' in self.CloudyModel.out:
                self.insert_in_dic('CloudyEnds', self.CloudyModel.out['Cloudy ends'])
            if '###First' in self.CloudyModel.out:
                self.insert_in_dic('FirstZone', self.CloudyModel.out['###First'])
            if '###Last' in self.CloudyModel.out:
                self.insert_in_dic('LastZone', self.CloudyModel.out['###Last'])
            if 'stop' in self.CloudyModel.out:
                self.insert_in_dic('CalculStop', self.CloudyModel.out['stop'])
            self.insert_in_dic('logU_in', self.CloudyModel.log_U[0])
            self.insert_in_dic('logU_out', self.CloudyModel.log_U[-1])
            self.insert_in_dic('logU_mean', self.CloudyModel.log_U_mean_ne)
            self.insert_in_dic('t2_H1', self.CloudyModel.get_t2_ion_vol_ne('H',1))
            self.insert_in_dic('t2_O1', self.CloudyModel.get_t2_ion_vol_ne('O',1))
            self.insert_in_dic('t2_O2', self.CloudyModel.get_t2_ion_vol_ne('O',2))
            self.insert_in_dic('t2_O3', self.CloudyModel.get_t2_ion_vol_ne('O',3))
            self.insert_in_dic('ne_H1', self.CloudyModel.get_ne_ion_vol_ne('H',1))
            self.insert_in_dic('ne_O1', self.CloudyModel.get_ne_ion_vol_ne('O',1))
            self.insert_in_dic('ne_O2', self.CloudyModel.get_ne_ion_vol_ne('O',2))
            self.insert_in_dic('ne_O3', self.CloudyModel.get_ne_ion_vol_ne('O',3))
            self.insert_in_dic('H_mass', self.CloudyModel.H_mass)
            self.insert_in_dic('H1_mass', self.CloudyModel.Hp_mass)
            self.insert_in_dic('nH_mean', self.CloudyModel.nH_mean)
            self.insert_in_dic('nH_in', self.CloudyModel.nH[0])
            self.insert_in_dic('nH_out', self.CloudyModel.nH[-1])
            self.insert_in_dic('Hb_SB', self.CloudyModel.get_Hb_SB())
            self.insert_in_dic('Hb_EW', self.CloudyModel.get_Hb_EW())
            self.insert_in_dic('Ha_EW', self.CloudyModel.get_Ha_EW())
                 
    def lines2dic(self):
        
        if self.CloudyModel.n_zones > 1:
            for clabel in self.CloudyModel.emis_labels:
                self.insert_in_dic(clabel, self.CloudyModel.get_emis_vol(clabel))
                self.insert_in_dic(clabel+'_rad', self.CloudyModel.get_emis_rad(clabel))
                  
    def insert_model(self, add2dic=None):
        if not self.MdB.connected:
            self.log_.error('Not connected')
            return None

        self.pending2dic()
        self.model2dic()
        self.lines2dic()
        if add2dic is not None:
            for key in add2dic:
                self.insert_in_dic(key, add2dic[key])
        
        fields_str = '`datetime`, '
        values_str = 'now(), '
        
        for key in self._dic:
            if self._dic[key] is not None:
                if key in self.fields:
                    fields_str += '`{0}`, '.format(key)
                    if type(self._dic[key]) == type(''):
                        values_str += "'{0}', ".format(self._dic[key])
                    else:
                        values_str += "{0}, ".format(self._dic[key])
                else:
                    self.log_.warn('Unknown field {0} in table {1}'.format(key, self.table))
        fields_str = fields_str[:-2]
        values_str = values_str[:-2]
        command = 'INSERT INTO {0} ({1}) VALUES ({2});'.format(self.table, fields_str, values_str)
        self.MdB.exec_dB(command)
        res, N = self.MdB.select_dB(select_='last_insert_id()', from_=self.table)
        self.last_N = res[0]['last_insert_id()']
        self.log_.message('Model sent to {0} with N={1}'.format(self.table, self.last_N))
        self.update_status('Model inserted') #14
        # ToDo : Loosing a lot of time in the following, check why
        if self.CloudyModel.n_zones > 1:
            ab_fields_str = '`N`, `ref`, '
            t_fields_str = '`N`, `ref`, '
            values_ab_str = "{0}, '{1}', ".format(self.last_N, self._dic['ref'])
            values_te_str = "{0}, '{1}', ".format(self.last_N, self._dic['ref'])        
            abion_fields = self.MdB.get_fields(from_ = self.OVN_dic['abion_table'])
            for abion_field in abion_fields:
                if (abion_field != 'N') and (abion_field != 'ref'):
                    ab,elem_long, integ, ion = abion_field.split('_')
                    ion = int(ion)
                    elem = None
                    for sym, elem_long_dic in SYM2ELEM.items():
                        if elem_long_dic.upper() == elem_long:
                            elem = sym
                    if elem is not None:
                        if self.CloudyModel.is_valid_ion(elem, ion):
                            ab_fields_str += '`{0}`, '.format(abion_field)
                            t_fields_str += '`T_{0}`, '.format(abion_field[2::])
                            if integ == 'vol':
                                values_ab_str += '{0}, '.format(self.CloudyModel.get_ab_ion_vol_ne(elem, ion))
                                t_ion = self.CloudyModel.get_T0_ion_vol_ne(elem, ion)
                                if np.isfinite(t_ion):
                                    values_te_str += '{0}, '.format(t_ion)
                                else:
                                    values_te_str += '-40, '
                            elif integ == 'rad':
                                values_ab_str += '{0}, '.format(self.CloudyModel.get_ab_ion_rad_ne(elem, ion))
                                t_ion = self.CloudyModel.get_T0_ion_rad_ne(elem, ion)
                                if np.isfinite(t_ion):
                                    values_te_str += '{0}, '.format(t_ion)     
                                else:
                                    values_te_str += '-40, '
            ab_fields_str = ab_fields_str[:-2]
            t_fields_str = t_fields_str[:-2]
            values_ab_str = values_ab_str[:-2]
            command = 'INSERT INTO {0} ({1}) VALUES ({2});'.format(self.OVN_dic['abion_table'], ab_fields_str, values_ab_str)
            self.MdB.exec_dB(command)
            self.update_status('Abion inserted') #15
            values_te_str = values_te_str[:-2]
            command = 'INSERT INTO {0} ({1}) VALUES ({2});'.format(self.OVN_dic['teion_table'], t_fields_str, values_te_str)
            self.MdB.exec_dB(command)
            self.update_status('Teion inserted') #16
         
         
        if self.CloudyModel.n_zones > 1:
            fields_str = '`N`, `ref`,'
            values_tem_str = "{0}, '{1}',".format(self.last_N,  self._dic['ref'])
            for clabel in self.CloudyModel.emis_labels:
                try:
                    fields_str += '`T_{0}`, '.format(clabel)
                    values_tem_str += '{0}, '.format(self.CloudyModel.get_T0_emis(clabel))
                except:
                    pass
            fields_str = fields_str[:-2]
            values_tem_str = values_tem_str[:-2]
            command = 'INSERT INTO {0} ({1}) VALUES ({2});'.format(self.OVN_dic['temis_table'], fields_str, values_tem_str)
            self.MdB.exec_dB(command)
        self.update_status('Temis inserted') #17
                        
        self.update_status('Master table updated')
            
    def clean_files(self):
        fname = '{0}/{1}/{2}.*'.format(self.models_dir, self.pending['dir'], self.pending['file'])
        for f in glob.glob(fname):
            os.remove(f)
        

class runCloudy(object):
    
    def __init__(self, MdB = None, OVN_dic=None, proc_name = None, models_dir = './', 
                 do_update_status=True, register=True):
        
        self.log_ = pc.log_
        self.calling = 'runCloudy'
        if MdB is None:
            MdB = pc.MdB(OVN_dic=OVN_dic)
        else:
            OVN_dic = MdB.OVN_dic
        self.OVN_dic = OVN_dic
        if not isinstance(MdB, pc.MdB):
            self.log_.error('The second argument must be a MdB object')    
        self.MdB = MdB
        if not self.MdB.connected:
            self.MdB.connect_dB()
        self.table = self.OVN_dic['master_table']
        self.pending_table = self.OVN_dic['pending_table']
        self.proc_name = proc_name
        self.models_dir = models_dir
        self.do_update_status = do_update_status        
        self.lines, N_lines = MdB.select_dB(select_='id, lambda, label, name', from_=self.OVN_dic['lines_table'], 
                                           where_='used = 1', limit_=None, format_='numpy')
       
        if register:
            self.get_ID()
        self.init_CloudyInput()
    
    def get_emis_table(self):
        emis_tab = []
        for line in self.lines:
            ide = line['id']
            lambda_ = line['lambda']
            unit = line['label'][-1]
            if lambda_ > 1000:
                lambda_str = '{0:5.0f}'.format(lambda_)
            elif lambda_ > 100:
                lambda_str = '{0:5.1f}'.format(lambda_)
            elif lambda_ > 10:
                lambda_str = '{0:5.2f}'.format(lambda_)
            else:
                lambda_str = '{0:5.3f}'.format(lambda_)
            emis_tab.append('{0} {1}{2}'.format(ide, lambda_str, unit))
        return emis_tab
    
    def init_CloudyInput(self):
        self.CloudyInput = pc.CloudyInput()
        self.CloudyInput.save_list = [['radius', '.rad'], 
                                      ['physical conditions', '.phy'],
                                      ['continuum', '.cont']]
        self.CloudyInput._save_list_grains = []
        self.emis_tab = self.get_emis_table()
        
    def get_ID(self):
        table=self.OVN_dic['procIDs_table']
        if not self.MdB.connected:
            self.log_.error('Not connected')
            return None
        
        host = os.getenv('HOST')
        user = os.getenv('USER')
        command = 'INSERT INTO {0} (`proc_name`, `datetime`, `user`, `host`) VALUES ("{1:s}", now(), "{2:s}", "{3:s}");'.format(table, self.proc_name, user, host)
        self.MdB.exec_dB(command)
        res, N = self.MdB.select_dB(select_='last_insert_id()', from_=table)
        self.procID = res[0]['last_insert_id()']
        
    def select_pending(self):

        if not self.MdB.connected:
            self.log_.error('Not connected')
            self.selectedN = None
            return
        
        if self.procID is None:
            self.log_.error('Not connected')
            
        try:
            res, N = self.MdB.select_dB(select_ = 'distinct(priority)', from_ = self.pending_table, 
                                       where_ = 'status = 0', limit_=None, commit=True)
        except:
            self.log_.error('Error looking for status=0 models in {0} - 1'.format(self.pending_table), 
                          calling='runCloudy.select_pending')
            self.selectedN = None
            return
        if N == 1:
            try:
                res, N = self.MdB.select_dB(select_ = 'N', from_ = self.pending_table, 
                                       where_ = 'status = 0', 
                                       limit_=1, commit=True)
                self.selectedN = res[0]['N']
            except:
                self.log_.error('Error looking for status=0 models in {0} - 2'.format(self.pending_table), 
                              calling='runCloudy.select_pending')
                self.selectedN = None
                return
        else:
            try:
                res, N = self.MdB.select_dB(select_ = 'N, priority', from_ = self.pending_table, 
                                           where_ = 'status = 0', limit_=None, format_='numpy', commit=True)
            except:
                self.log_.error('Error looking for status=0 models in {0} - 3'.format(self.pending_table), 
                              calling='runCloudy.select_pending')
                self.selectedN = None
                return
            if N == 0:
                self.selectedN = None
                return
            else:
                self.selectedN = res['N'][select_from_priorities(res['priority'])]
        
        command = 'UPDATE {0} SET `procID`={1}, `status`=1,`date_running`=now() WHERE N = {2} AND status=0'.format(self.pending_table, 
                                                                             self.procID, self.selectedN)   
        self.MdB.exec_dB(command, commit=True)

        currentID, N = self.MdB.select_dB(select_='procID', from_=self.pending_table, 
                                          where_='N = {0}'.format(self.selectedN), 
                                          format_='numpy')
        if currentID['procID'][0] != self.procID:
            self.log_.warn('currentID != self.procID : {0} != {1}'.format(currentID['procID'][0], self.procID))
            self.selectedN = None
        
    def update_status(self, status):
        
        command = 'UPDATE {0} SET `status`={1} WHERE N = {2}'.format(self.pending_table, 
                                                                    status_dic[status], self.selectedN)   
        if not self.do_update_status:
            self.log_.message(command, calling=self.calling)
            return
        if status in status_dic:
            self.MdB.exec_dB(command, commit=True)
        else:
            self.log_.error('Unknown status "{0}"'.format(status))
    
    def read_pending(self, N_pending=None):

        if not self.MdB.connected:
            self.log_.error('Not connected to the database')
            self.pending = None
            return None
        
        if N_pending is None:
            N_pending = self.selectedN
        else:
            self.selectedN = N_pending
        res, Nres = self.MdB.select_dB(select_='*', from_=self.pending_table, 
                                       where_='N = {0}'.format(N_pending), commit=True)
        
        self.update_status('Read_pending')
        if Nres == 0:
            self.pending = None
        else:
            self.pending = res[0]
    
    def read_tab(self, N=None):

        if not self.MdB.connected:
            self.log_.error('Not connected to the database')
            self.tab_dic = None
            return None
        
        if N is None:
            N = self.selectedN
        else:
            self.selectedN = N
        res, Nres = self.MdB.select_dB(select_='*', from_=self.table, 
                                       where_='N = {0}'.format(N), commit=True)
        
        if Nres == 0:
            self.tab_dic = None
        else:
            self.tab_dic = res[0]
    
    def fill_CloudyInput(self, N_pending=None, noinput=False, dir=None, parameters=None, read_tab=False):
        """
        Method that print out a Cloudy input file
        keywords:
            - N_pending : value of the N from the pending table where to find the parameters of the model.
                if set to None (default), the value of runCloudy.selectedN is used
            - noinput (False): is set to True, no input file is written
            - dir: if not set to None (default), set the directory where to write the file
            - parameters: if not set to None (default), is a dictionnary of parameters to substitute the 
                ones from the pending table
            - read_tab: By default the parameters are read from the pending table. 
                If read_tab, parameters are read from tab.
        """
        if N_pending is None:
            N_pending = self.selectedN
        if read_tab:
            self.read_tab(N_pending)
            P = self.tab_dic
        else:
            self.read_pending(N_pending)
            P = self.pending
        if dir is not None:
            P['dir'] = dir
        if type(parameters) is dict:
            for k in parameters:
                P[k] = parameters[k]
        if P is not None:
            self.CloudyInput.model_name = '{0}/{1}/{2}'.format(self.models_dir, P['dir'], P['file'])
            self.CloudyInput.cloudy_version = P['C_version']
            self.CloudyInput.set_distance(P['distance'])
            if P['dens'] != 0:
                self.CloudyInput.set_cste_density(P['dens'], P['ff'])
            if P['dlaw1'] is not None:
                dlaws = [P['dlaw1']]
                for i_dlaw in range(8):
                    if P['dlaw{0}'.format(i_dlaw+2)] is not None:
                        dlaws.append(P['dlaw{0}'.format(i_dlaw+2)])
                self.CloudyInput.set_dlaw(dlaws)
            if P['radius'] != 0:
                self.CloudyInput.set_radius(P['radius'])
            for elem in SYM2ELEM:
                if SYM2ELEM[elem].upper() in P:
                    value = P[SYM2ELEM[elem].upper()]
                    if value > -35:
                        self.CloudyInput.set_abund(elem = elem, value = value)
            SED_params = None
            self.CloudyInput.set_star()
            if P['atm_cmd'] == 'sed_db':
                seds_table = self.OVN_dic['seds_table']
                where_ = 'ref = "{0}" and sed_name = "{1}"'.format(P['ref'], P['atm_file'])
                SEDs, N = self.MdB.select_dB(select_ = '*', from_ = seds_table, where_ = where_, 
                  limit_ = None, format_ = 'dict')
                if N == 0:
                    print(('No SED!!! where_ = {}'.format(where_)))
                for SED in SEDs:
                    self.CloudyInput.set_star(SED = '{} "{}"'.format(SED['atm_cmd'], SED['atm_file']), 
                                              SED_params = (SED['atm1'], SED['atm2']), 
                                              lumi_unit=SED['lumi_unit'], lumi_value=SED['lumi'])
                
            else:
                if P['atm_file'] == '':
                    SED = '{0}'.format(P['atm_cmd'])
                else:
                    SED = '{0} "{1}"'.format(P['atm_cmd'],P['atm_file'])
                if P['atm1'] is not None:
                    SED_params = ' {0}'.format(P['atm1'])
                if P['atm2'] is not None:
                    SED_params += ' {0}'.format(P['atm2'])
                if P['atm3'] is not None:
                    SED_params += ' {0}'.format(P['atm3'])
                
                self.CloudyInput.set_star(SED = SED, SED_params = SED_params, 
                                          lumi_unit = P['lumi_unit'], lumi_value = P['lumi'])
                if P['atm_cmd2'] is not '':
                    SED_params = None
                    SED = '{0} "{1}"'.format(P['atm_cmd2'],P['atm_file2'])
                    if P['atm12'] is not None:
                        SED_params = ' {0}'.format(P['atm12'])
                    if P['atm22'] is not None:
                        SED_params += ' {0}'.format(P['atm22'])
                    if P['atm32'] is not None:
                        SED_params += ' {0}'.format(P['atm32'])
                    
                    self.CloudyInput.set_star(SED = SED, SED_params = SED_params, 
                                              lumi_unit = P['lumi_unit2'], lumi_value = P['lumi2'])
                    
            if P['geom'] == 'Sphere':
                self.CloudyInput.set_sphere()
            else:
                self.CloudyInput.set_sphere(False)
            self.CloudyInput.set_iterate(P['iterate'])
            for i_dust in range(3):
                if P['dust_type{0}'.format(i_dust+1)] != '':
                    self.CloudyInput.set_grains('{0} {1}'.format(P['dust_type{0}'.format(i_dust+1)], 
                                                                 P['dust_value{0}'.format(i_dust+1)]))
            for i_stop in range(6):
                if P['stop{0}'.format(i_stop+1)] != '':
                    self.CloudyInput.set_stop(P['stop{0}'.format(i_stop+1)])
            for i_others in range(9):
                if P['cloudy{0}'.format(i_others+1)] != '':
                    self.CloudyInput.set_other(P['cloudy{0}'.format(i_others+1)])
            self.CloudyInput.set_comment('3MdB pending number {0}'.format(N_pending))
            for i in np.arange(9)+1:
                com_str = 'com{}'.format(i)
                if P[com_str] != '':
                    self.CloudyInput.set_comment('3MdB {0} {1}'.format(com_str, P[com_str]))
            self.CloudyInput.set_emis_tab(self.emis_tab)
            self.update_status('Cloudy Input filled')
            
            if not noinput:
                self.CloudyInput.print_input()
            self.update_status('Cloudy Input printed')

def printInput(N, MdB= None, OVN_dic=None, dir='./', parameters=None, read_tab=False):
    """
    Procedure that print out the input file corresponding the entry N in the pending (or master) table of OVN_dic
    It does not write nothing in the database.
    Take care that some comments may have been added a posteriori to the master table and may break Cloudy.
    """
    if MdB is None:
        MdB = pc.MdB(OVN_dic=OVN_dic)
    else:
        OVN_dic = MdB.OVN_dic
    MdB = pc.MdB(OVN_dic)
    rc = runCloudy(MdB = MdB, do_update_status=False, register=False, models_dir='./')
    rc.fill_CloudyInput(N, dir=dir, parameters=parameters, read_tab=read_tab)
    MdB.close_dB()

class runCloudyByThread(threading.Thread):

    def __init__(self, OVN_dic, models_dir, norun=False, noinput=False):
        
        self.log_ = pc.log_
        threading.Thread.__init__(self)
        self._stop = threading.Event()
        self.models_dir = models_dir
        self.norun = norun
        self.noinput = noinput
        self.MdB = None
        self.sleep_time = 10.
        self.setDaemon(True)
        self.OVN_dic = OVN_dic
        self.calling = 'runCloudyByThread'
    
    def run(self):
        
        self.MdB = pc.MdB(self.OVN_dic)
        tname = threading.currentThread().getName()
        rC = runCloudy(self.MdB, OVN_dic = self.OVN_dic, models_dir = self.models_dir, proc_name=tname)
        
        while not self.stopped():
            rC.init_CloudyInput()
            rC.select_pending()
            self.selectedN = rC.selectedN 
            if self.selectedN is not None:
                rC.update_status('Pending model selected')
                rC.fill_CloudyInput(noinput = self.noinput)
                rC.update_status('Cloudy start')
                try:
                    if not self.norun:
                        rC.CloudyInput.run_cloudy(precom="\\nice -10")
                        rC.update_status('Cloudy run')
                    read_it = True
                except:
                    self.log_.warn('Cloudy model {0} failed'.format(self.selectedN))
                    rC.update_status('Cloudy failed')
                    read_it = False
                if read_it:
                    wT = writeTab(self.MdB, OVN_dic = self.OVN_dic, models_dir = self.models_dir)
                    wT.read_pending(self.selectedN)
                    insert_it = wT.read_model()
                else:
                    insert_it = False
                if insert_it:
                    if rC.pending['GuessMassFrac'] < 1.0:
                        wT.CloudyModel.H_mass_cut = rC.pending['GuessMassFrac'] * wT.CloudyModel.H_mass_full[-1]
                        wT.insert_model()
                        master_N = [wT.last_N]
                    else:
                        wT.insert_model()
                        master_N = [wT.last_N]
                        Ncuts = rC.pending['N_Mass_cut']
                        for mass_cut in np.linspace(0, 1, Ncuts + 2)[1:-1]:
                            if wT.CloudyModel.n_zones > 1:
                                wT.CloudyModel.H_mass_cut = mass_cut * wT.CloudyModel.H_mass_full[-1]
                                wT.insert_model()
                                master_N.append(wT.last_N)
                        Ncuts = rC.pending['N_Hb_cut']
                        for Hbeta_cut in np.linspace(0, 1, Ncuts + 2)[1:-1]:
                            if wT.CloudyModel.n_zones > 1:
                                wT.CloudyModel.Hbeta_cut = Hbeta_cut * wT.CloudyModel.Hbeta_full[-1]
                                wT.insert_model()
                                master_N.append(wT.last_N)
                    wT.clean_files()
                    self.log_.message('model {0} finished, inserted into {1}.'.format(self.selectedN, master_N), 
                                 calling=self.calling)
            else:
                time.sleep(self.sleep_time)
            
        self.MdB.close_dB()

    def stop(self):
        self._stop.set()
    
    def stopped(self):
        return self._stop.isSet()
    
    def clear(self):
        self._stop.clear()
    
class Genetic(object):
    
    def __init__(self, MdB = None, OVN_dic=None, N=None):

        self.log_ = pc.log_
        
        if MdB is None:
            self.OVN_dic = OVN_dic
            MdB = pc.MdB(OVN_dic=self.OVN_dic)
        else:
            self.OVN_dic = MdB.OVN_dic            
        if not isinstance(MdB, pc.MdB):
            self.log_.error('The second argument must be a MdB object')    
        self.MdB = MdB
        if not self.MdB.connected:
            self.MdB.connect_dB()
        self.def_variable_list()
        self.N = N
        
    def readModel(self, N=None):

        if not self.MdB.connected:
            self.log_.error('Not connected to the database')
            return None
        
        if N is not None:
            self.N = N
        if self.N is None:
            self.model = None
            return
        
        models, n = self.MdB.select_dB(select_='*', from_=self.OVN_dic['master_table'], 
                                       where_='N={0}'.format(self.N), limit_=1, format_='dict')
        if n == 0:
            self.model = None
        else:
            self.model = models[0]
            
    def initPending(self):
        
        self.wP = writePending(self.MdB, self.OVN_dic)
        
        P_dic = ['ALUMINIUM', 'ARGON', 'BERYLLIUM', 'BORON', 'CALCIUM', 'CARBON', 'CHLORINE', 'CHROMIUM', 'COBALT', 'COPPER',
                 'FLUORINE', 'HELIUM', 'HYDROGEN', 'IRON', 'LITHIUM', 'MAGNESIUM', 'MANGANESE', 'NEON', 'NICKEL', 'NITROGEN',
                 'OXYGEN', 'PHOSPHORUS', 'POTASSIUM', 'SCANDIUM', 'SILICON', 'SODIUM', 'SULPHUR', 'TITANIUM', 'VANADIUM', 'ZINC',
                 'atm1', 'atm12', 'atm2', 'atm22', 'atm3', 'atm32', 'atm_cmd', 'atm_cmd2', 'atm_file', 'atm_file2',
                 'cloudy1', 'cloudy2', 'cloudy3', 'cloudy4', 'cloudy5', 'cloudy6', 'cloudy7', 'cloudy8', 'cloudy9',
                 'com1', 'com2', 'com3', 'com4', 'com5', 'com6', 'com7', 'com8', 'com9',
                 'dens', 'dlaw1', 'dlaw2', 'dlaw3', 'dlaw4', 'dlaw5', 'dlaw6', 'dlaw7', 'dlaw8', 'dlaw9',
                 'dust_type1', 'dust_type2', 'dust_type3', 'dust_value1', 'dust_value2', 'dust_value3',
                 'ff', 'geom', 'iterate', 'lumi', 'lumi2', 'lumi_unit', 'lumi_unit2', 'priority', 'radius', 'ref',
                 'stop1', 'stop2', 'stop3', 'stop4', 'stop5', 'stop6',
                 'distance', 'user', 'dir', 'C_version']
        for key in P_dic:
            if key in self.model:
                self.wP.insert_in_dic(key, self.model[key])
        
        self.wP.set_N_Mass_cut(0)
        self.wP.set_GuessMassFrac(self.model['MassFrac'])

        
    def setGeneration(self, generation):
        self.wP.insert_in_dic('precursor', self.N)
        self.wP.insert_in_dic('generation', generation)
    
    def shake(self, key, sigma, addit=True, lowlim=None, highlim=None):

        if np.isinf(sigma) or np.isnan(sigma):
            sigma = 0.
        self.randomcoeff = np.random.standard_normal()
        if type(key) is str:
            key = (key,)
        for k in key:
            if k in self.wP._dic:
                if addit:
                    new_value = self.wP._dic[k] + sigma * self.randomcoeff
                else:
                    new_value = self.wP._dic[k] * (1 + sigma * self.randomcoeff)
                if lowlim is not None:
                    if new_value < lowlim:
                        new_value = lowlim
                if highlim is not None:
                    if new_value > highlim:
                        new_value = highlim
                self.wP.insert_in_dic(k, new_value)
            
    def shift(self, key, delta, addit=True, lowlim=None, highlim=None, sigma=0):
        
        if np.isinf(delta) or np.isnan(delta):
            delta = 0.
        if key in self.wP._dic:
            if addit:
                new_value = self.wP._dic[key] + delta 
            else:
                new_value = self.wP._dic[key] * (1 + delta)
            if lowlim is not None:
                if new_value < lowlim:
                    new_value = lowlim
            if highlim is not None:
                if new_value > highlim:
                    new_value = highlim
            self.wP.insert_in_dic(key, new_value)
        if sigma != 0.:
            self.shake(key=key, sigma=sigma, addit=addit, lowlim=lowlim, highlim=highlim)
            
    def def_variable_list(self, exclude=(), include=()):
        """
        This define the tuple of variables that are used to build the chromosome
        """
        self.var_chroms_list = ['ARGON', 'CARBON', 'HELIUM', 'IRON', 'NEON', 'NITROGEN',
                               'OXYGEN', 'SULPHUR', 
                               'atm1', 'atm12', 'atm2', 'atm22', 'atm3', 'atm32', 
                               'dens', 
                               'dust_value1', 'dust_value2', 'dust_value3',
                               'ff', 'lumi', 'lumi2', 'radius']
        for e in exclude:
            if e in self.var_chroms_list:
                self.var_chroms_list.remove(e)
        for i in include:
            if i not in self.var_chroms_list:
                self.var_chroms_list.append(i)
        
                    
    def crossover(self, M1, M2):
        C1 = M1.copy()
        C2 = M2.copy()
        
        N_var = len(self.var_chroms_list)
        i_change = randint(0,N_var-1)
        for i in range(i_change):
            C1[self.var_chroms_list[i]] = M2[self.var_chroms_list[i]]
            C2[self.var_chroms_list[i]] = M1[self.var_chroms_list[i]]
            
        v1 = '{}'.format(M1[self.var_chroms_list[i_change]])
        v2 = '{}'.format(M2[self.var_chroms_list[i_change]])
        if len(v1) == len(v2):
            j_change = randint(0,len(v1)-1)
            v1_n = v2[0:j_change]
            v2_n = v1[0:j_change]
            try:
                C1[i_change] = eval(v1_n)
                C2[i_change] = eval(v2_n)
            except:
                pass
        return C1, C2

    def mutation(self, M):
        N_var = len(self.var_chroms_list)
        i_change = randint(0,N_var-1)
        M[self.var_chroms_list[i_change]] = M[self.var_chroms_list[i_change]]
        return M
            
class ObsfromMdB(object):
    
    
    def __init__(self, MdB = None, OVN_dic=None, N=None):

        self.log_ = pc.log_
        self.OVN_dic = OVN_dic
        if MdB is None:
            MdB = pc.MdB(OVN_dic=self.OVN_dic)
        if not isinstance(MdB, pc.MdB):
            self.log_.error('The second argument must be a MdB object')    
        self.MdB = MdB
        if not self.MdB.connected:
            self.MdB.connect_dB()
        
        self.N = N
        self.init_obs()
        
    def init_obs(self):
        self.obs = pn.Observation()

    def readModel(self, select_='*', from_=None, N=None, where_=None, order_ = None, limit_ = None):
        
        if not self.MdB.connected:
            self.log_.error('Not connected to the database')
            return None
        if from_ is None:
            from_ = self.OVN_dic['master_table']
        if N is not None:
            self.N = N
        if self.N is None and where_ is None:
            self.models = None
            return
        if where_ is None:
            where_ = 'N={0}'.format(self.N)
            
        models, n = self.MdB.select_dB(select_=select_, from_=from_, where_=where_, order_=order_,
                                       limit_=limit_, format_='dict2')
        if n == 0:
            self.models = None
        else:
            self.models = models
        
        cl2py = cloudy2pyneb()
        n_lines = -1
        for line in cl2py:
            if line in self.models:
                pyneb_label = '{0[0]}_{0[1]}'.format(cl2py[line])
                EL = pn.EmissionLine(label=pyneb_label, obsIntens=self.models[line], corrected = True)
                if n_lines == -1:
                    n_lines = EL.corrIntens.size
                    self.obs.addLine(EL)
                else:
                    if EL.corrIntens.size == n_lines:
                        self.obs.addLine(EL)

class manage3MdB(object):
    
    def __init__(self, OVN_dic, models_dir='/DATA/MdB', Nprocs=pn.config.Nprocs):
        self.OVN_dic = OVN_dic
        self.models_dir = models_dir
        self.Nprocs = Nprocs
                
    def start(self, norun=False, noinput=False):
        self.all_threads = []
        for i in range(self.Nprocs):
            self.all_threads.append(runCloudyByThread(self.OVN_dic, self.models_dir, norun=norun, noinput=noinput))
        for t in self.all_threads:
            t.start()
    
    def stop(self):
        for t in self.all_threads: 
            t.stop()
            
def print_all_refs(MdB = None, OVN_dic=None):
    """
    Print all the references from the master table, with the number of entries for each.
    """
    if MdB is None:
        MdB = pc.MdB(OVN_dic=OVN_dic)
    else:
        OVN_dic = MdB.OVN_dic
    if not isinstance(MdB, pc.MdB):
        self.log_.error('The first argument must be a MdB object')    
    res, N_ref = MdB.select_dB(select_ = 'distinct(ref), count(*)', from_ = OVN_dic['master_table'], 
                               group_ = 'ref', limit_ = None)
    for row in res:
        print(('The ref "{0:15}" counts {1:8d} entries.'.format(row['ref'], row['count(*)'])))
    print(('Number of distinct references = {0}'.format(N_ref)))
    
def print_all_lines(MdB = None, OVN_dic=None, limit_=None):
    """
    Print all the emission lines.
    A limit can be given
    """
    if MdB is None:
        MdB = pc.MdB(OVN_dic=OVN_dic)
    else:
        OVN_dic = MdB.OVN_dic
    if not isinstance(MdB, pc.MdB):
        self.log_.error('The first argument must be a MdB object')    
    lines, N_lines = MdB.select_dB(select_ = '*', from_ = OVN_dic['lines_table'], limit_ = limit_)
    for line in lines:
        print(('Nl = {0[Nl]:3} id = {0[id]:4} label = {0[label]:5} wavelength = {0[lambda]:6} full name = {0[name]}'.format(line)))

def print_status_stats(MdB = None, OVN_dic=None, ref_=None):
    """
    Print the number of pending models for each status.
    A reference can be given. 
    """
    if MdB is None:
        MdB = pc.MdB(OVN_dic=OVN_dic)
    else:
        OVN_dic = MdB.OVN_dic
    if not isinstance(MdB, pc.MdB):
        self.log_.error('The first argument must be a MdB object')
    if ref_ is not None:
        where_ = 'ref = "{0}"'.format(ref_)
    else:
        where_ = None
    res, N_res = MdB.select_dB(select_='status, count(*) as ct',from_=OVN_dic['pending_table'],
                               where_=where_, group_='status', limit_=None, commit=True)
    for status in res: 
        print(('{0:7} models with status = {1:4}.'.format(status['ct'], status['status'])))

def print_mean_running_time(MdB = None, OVN_dic=None, ref_=None):
    """
    Print the mean time to run photoionization models.
    A reference can be given
    """
    if MdB is None:
        MdB = pc.MdB(OVN_dic=OVN_dic)
    else:
        OVN_dic = MdB.OVN_dic
    if not isinstance(MdB, pc.MdB):
        self.log_.error('The first argument must be a MdB object')
    if ref_ is not None:
        where_ = 'ref = "{0}"'.format(ref_)
    else:
        where_ = None
    res, N_res = MdB.select_dB(select_='avg(substring_index(CloudyEnds,"ExecTime(s)", -1)) as MRT, '\
                               'min(substring_index(CloudyEnds,"ExecTime(s)", -1)) as MN, '\
                               'max(substring_index(CloudyEnds,"ExecTime(s)", -1)) as MX',
                              from_=OVN_dic['master_table'], where_=where_, limit_=None)
    print(('Mean running time = {0[MRT]}, min = {0[MN]}, max = {0[MX]}'.format(res[0])))
    
def print_elapsed_time(MdB = None, OVN_dic=None, ref_=None):
    """
    Print the time elapsed between the first and the last model run.
    A reference can be given
    """
    if MdB is None:
        MdB = pc.MdB(OVN_dic=OVN_dic)
    else:
        OVN_dic = MdB.OVN_dic
    if not isinstance(MdB, pc.MdB):
        self.log_.error('The first argument must be a MdB object')
    if ref_ is not None:
        where_ = 'ref = "{0}"'.format(ref_)
    else:
        where_ = None
    res, N_res = MdB.select_dB(select_='time_to_sec(timediff(max(datetime),min(datetime))) as ET',
                               from_=OVN_dic['master_table'], where_=where_, limit_=None)
    print(('Models running during = {0}'.format(datetime.timedelta(seconds=res[0]['ET']))))
    
def print_ETA(MdB= None, OVN_dic=None, ref_=None):
    if MdB is None:
        MdB = pc.MdB(OVN_dic=OVN_dic)
    else:
        OVN_dic = MdB.OVN_dic
    if not isinstance(MdB, pc.MdB):
        self.log_.error('The first argument must be a MdB object')
    if ref_ is not None:
        where_ = 'ref = "{0}"'.format(ref_)
    else:
        where_ = ''
    res, N_res = MdB.select_dB(select_='count(*)',from_=OVN_dic['pending_table'],
                               where_=where_ + ' AND status=0', limit_=None, commit=True)
    N_pending = res[0]['count(*)']
    res, N_res = MdB.select_dB(select_='count(*)',from_=OVN_dic['pending_table'],
                               where_=where_ + 'AND status=50', limit_=None, commit=True)
    N_run = res[0]['count(*)']
    res, N_res = MdB.select_dB(select_='time_to_sec(timediff(max(datetime),min(datetime))) as ET',
                               from_=OVN_dic['master_table'], where_=where_, limit_=None)
    ET = res[0]['ET']
    
    eta = datetime.datetime.today() + datetime.timedelta(seconds=ET/float(N_run)*N_pending)
    print('ETA : ' + str(eta))

def print_efficiency(MdB= None, OVN_dic=None, ref_=None):
    if MdB is None:
        MdB = pc.MdB(OVN_dic=OVN_dic)
    else:
        OVN_dic = MdB.OVN_dic
    if not isinstance(MdB, pc.MdB):
        self.log_.error('The first argument must be a MdB object')
    if ref_ is not None:
        where_ = 'ref = "{0}"'.format(ref_)
    else:
        where_ = ''
    res, N_res = MdB.select_dB(select_='count(*)',from_=OVN_dic['pending_table'],
                               where_=where_ + 'AND status=50', limit_=None, commit=True)
    N_run = res[0]['count(*)']
    res, N_res = MdB.select_dB(select_='time_to_sec(timediff(max(datetime),min(datetime))) as ET',
                               from_=OVN_dic['master_table'], where_=where_, limit_=None)
    ET = res[0]['ET']
    res, N_res = MdB.select_dB(select_='avg(cast(substring_index(CloudyEnds,"ExecTime(s)", -1) as decimal)) as MRT, '\
                               'min(cast(substring_index(CloudyEnds,"ExecTime(s)", -1) as decimal)) as MN, '\
                               'max(cast(substring_index(CloudyEnds,"ExecTime(s)", -1) as decimal)) as MX',
                              from_=OVN_dic['master_table'], where_=where_, limit_=None)
    MRT = res[0]['MRT']
    
    print(('Mean efficiency = {}'.format(np.float(N_run)*MRT/ET)))
    
def print_infos(MdB= None, OVN_dic=None, ref_=None, where_=None, Nprocs=32):
    if MdB is None:
        MdB = pc.MdB(OVN_dic=OVN_dic)
    else:
        OVN_dic = MdB.OVN_dic
    if not isinstance(MdB, pc.MdB):
        self.log_.error('The first argument must be a MdB object')
    if ref_ is not None:
        this_where_ = 'ref = "{0}"'.format(ref_)
    else:
        this_where_ = ''
    if where_ is not None:
        this_where_ += ' AND {}'.format(where_)
    res, N_res = MdB.select_dB(select_='count(*)',from_=OVN_dic['pending_table'],
                               where_=this_where_ + ' AND status=0', limit_=None, commit=True)
    N_pending = res[0]['count(*)']
    res, N_res = MdB.select_dB(select_='count(*)',from_=OVN_dic['pending_table'],
                               where_=this_where_ + ' AND status=50', limit_=None, commit=True)
    N_run = res[0]['count(*)']
    if N_run == 0 and N_pending == 0:
        print('No entry')
        return
    res_et, N_res = MdB.select_dB(select_='time_to_sec(timediff(max(datetime),min(datetime))) as ET',
                               from_=OVN_dic['master_table'], where_=this_where_, limit_=None)
    ET = res_et[0]['ET']
    
    eta = datetime.datetime.today() + datetime.timedelta(seconds=ET/float(N_run)*N_pending)
    res, N_res = MdB.select_dB(select_='avg(cast(substring_index(CloudyEnds,"ExecTime(s)", -1) as decimal)) as MRT, '\
                               'min(cast(substring_index(CloudyEnds,"ExecTime(s)", -1) as decimal)) as MN, '\
                               'max(cast(substring_index(CloudyEnds,"ExecTime(s)", -1) as decimal)) as MX',
                              from_=OVN_dic['master_table'], where_=this_where_, limit_=None)
    MRT = float(res[0]['MRT'])
    MN = float(res[0]['MN'])
    MX = float(res[0]['MX'])
    Mean_eff = np.float(N_run)*MRT/ET
    eta2 = datetime.datetime.today() + datetime.timedelta(seconds=MRT*N_pending/float(Nprocs))
    print(('{} pending, {} run'.format(N_pending, N_run)))
    print(('Mean running time = {0:.0f}s, min = {1:.0f}s, max = {2:.0f}s'.format(MRT, MN, MX)))
    print(('Models running during {0}'.format(datetime.timedelta(seconds=ET))))
    print(('ETA1 : {0}, ETA2 : {1}'.format(eta, eta2)))
    print(('Mean efficiency = {0:.1f}'.format(Mean_eff)))
    
def remove_lines(OVN_dic, line_labels):
    """
    Usage:
        remove_lines(OVN_dic, ('FE_6__5177A', 'FE_7__4894A', 'FE_7__5277A'))
        remove_lines(OVN_dic, ('H__1__4102A', 'H__1__3970A', 'H__1__3835A', 'H__1_2625M', 'H__1_7458M', 'HE_1__4471A', 'CA_B__4471A'))
    """
    MdB = pc.MdB(OVN_dic=OVN_dic)
    for label in line_labels:
        command = 'update {0} set used = 0 where label = "{1}"'.format(OVN_dic['lines_table'], label)
        MdB.exec_dB(command)
    MdB.close_dB()
        
    
def remove_models(MdB= None, OVN_dic=None, where_=None):
    """
    Usage:
        remove_models(OVN_dic=OVN_dic, where_='ref = "CALIFA_6" AND com1 = "name = NGC4630"')
        remove_models(MdB=MdB, where_='ref = "CALIFA_6" AND com1 = "name = NGC4630"')
    """
    if MdB is None:
        MdB = pc.MdB(OVN_dic=OVN_dic)
    else:
        OVN_dic = MdB.OVN_dic
    command = 'delete temis from temis join tab on temis.N=tab.N where {}'.format(where_)
    MdB.exec_dB(command)
    command = 'delete teion from teion join tab on teion.N=tab.N where {}'.format(where_)
    MdB.exec_dB(command)
    command = 'delete abion from abion join tab on abion.N=tab.N where {}'.format(where_)
    MdB.exec_dB(command)
    command = 'delete from tab where {}'.format(where_)
    MdB.exec_dB(command)
    
    MdB.close_dB()
    
    
    