import pyCloudy as pc
import numpy as np
import glob
import os
import subprocess
import random
import time
from ..utils.init import LIST_ELEM, LIST_ALL_ELEM, SYM2ELEM
from ..utils.misc import sextract, cloudy2pyneb, convert_c13_c17, convert_c17_c13
from ..utils.physics import ATOMIC_MASS
if pc.config.INSTALLED['PyNeb']:
    import pyneb
if pc.config.INSTALLED['scipy']:
    from scipy.integrate import cumtrapz
if pc.config.INSTALLED['plt']:
    import matplotlib.pyplot as plt
    
##
# @bug There is a problem for plan parallel models (yes Will, you are right!) (when depth << radius) 
# it can be that all the values in radius are the same, which gives pb to m_cut etc
# Need to identify this situation and to deal with it without "try", but safetly.

## @include copyright.txt
class CloudyModel(object):

    """
    Read the outputs of Cloudy into variables of the object. Also perform some computations
    like T0, t2 for all the ions and lines.
    Provides methods to access some outputs (e.g. continuum in various units)

    The Cloudy model must have been run with the following punch or save in the input file:

    set punch prefix "MODEL" (can be changed)
    punch last radius ".rad"
    punch last continuum ".cont"
    punch last physical conditions ".phy"
    punch last overview ".ovr"
    punch last grain temperature ".gtemp_full"
    punch last element hydrogen ".ele_H"
    punch last element helium ".ele_He"
    punch last element carbon ".ele_C"
    punch last element nitrogen ".ele_N"
    punch last element oxygen ".ele_O"
    punch last element argon ".ele_Ar"
    punch last element neon ".ele_Ne"
    punch last element sulphur ".ele_S"
    punch last element chlorin ".ele_Cl"
    punch last element iron ".ele_Fe"
    punch last element silicon ".ele_Si"
    punch last linelist ".lin" "liste_of_lines.dat"
    punch last lines emissivity ".emis"
    ... liste of lines  ... No need to be the same as liste_of_lines.dat
    end of lines
    in case of version >= 10:
    save last grain abundances ".gabund_full"'
    save last grain D/G ratio ".gdgrat_full"'

    usage:  m1 = CloudyModel('MODEL')
    plot(m1.radius,m1.get_emis('Fe_3__5271A'))
    plot m1.depth,m1.te
    
    y = 'e("TOTL__4363A")/e("O__3__5007A")'
    e = lambda line: m1.get_emis(line)
    plot m1.te,eval(y)

    self.n_zones : number of zones Cloudy used.
    self.depth : depth in cm, ndarray(n_zones)
    self.radius : radius in cm, ndarray(n_zones)
    self.r_in and r_out : minimum and maximum of self.radius
    self.ne and nH : electron and H-densities in cm-3, ndarray(n_zones)
    self.te : electron temperature in K, ndarray(n_zones)
    self.nenH and tenenH : some products of the previous.
    self.T0 and self.t2: mean T and t2 for H+

    self.n_lines : number of emission lines in the .lin file
    self.line_labels : lines names, ndarray(n_lines,dtype='S20')
    self.get_line : line intensities
    
    some lines can appear more than one time in the list of lines, they then have a _N at the end of the label.
    the following deal with this:
    self.slines : array of uniq values for lines (single lines)
    self.n_slines : number of 
    self.rlines : array of reduced labels : for duplicate lines, removing the trailing _N 
    
    dev comments:
    
    GPL Chris.Morisset@Gmail.com
    """

    ## Cloudy model object
    def __init__(self, model_name, verbose=None, 
                 read_all_ext = True, read_rad=True, read_phy=True, read_emis = True, read_grains = False, 
                 read_cont = True, read_heatcool = False, read_lin = False, read_opd = False, 
                 list_elem = LIST_ELEM, distance = None, line_is_log = False, 
                 emis_is_log = True, 
                 ionic_str_key = 'ele_'):
        """
        param:
            - model_name [str] The name of the model to be read.
            - verbose [int] level of verbosity as defined by pyCloudy.my_logging.
            - read_all_ext [boolean] if True, all the extensions are read, if False no extension (empty object).
            - read_emis [boolean] if True, emissivities .emis file_ is read and interpreted.
            - read_grains [boolean] if True, grains .gtemp, .gdgrat and .gabund files are read and interpreted.
            - read_cont [boolean] if True, continuum .cont file_ is read and interpreted.
            - list_elem [list of str] list of elements X for which ionic abundance .ele_X file_ is read.
            - distance [float] distance to the nebula in kpc
            - line_is_log [boolean] if True, intensities in .lin file_ are in log, if False are in linear
            - emis_is_log [boolean] if True, intensities in .emis file_ are in log, if False are in linear
        """

        self.log_ = pc.log_
        if verbose is not None:
            self.log_.level = verbose
        self.model_name = model_name
        self.info = '<Cloudy model from {0}>'.format(self.model_name) 
        self.calling = 'CloudyModel {0.model_name}'.format(self)
        self.log_.message('Creating CloudyModel for {0.model_name}'.format(self), calling = self.calling)
        self.model_name_s = model_name.split('/')[-1]
        self.line_is_log = line_is_log
        self.distance = distance
        self.empty_model = True
        self._read_stout(emis_is_log=emis_is_log)
        if self.out_exists and not self.aborted and read_all_ext:
            self._init_all2zero()
            if read_rad:
                self._init_rad()
            if read_phy:
                self._init_phy()
            for elem in list_elem:
                self._init_ionic(elem, str_key = ionic_str_key)
            self.liste_elem = list(self.ionic_names.keys())
            if read_opd:
                self._init_opd()
            if read_lin:
                self._init_lin()
            if read_emis:
                self._init_emis()
            if read_cont:
                self._init_cont()
            if read_grains:
                self._init_grains()
            if read_heatcool:
                self._init_heatcool()
    ##            
    # @var distance
    # distance to the object (kpc)
    # @var model_name
    # name of the model [str]
    # @var log_
    # logging tool [my_logging object]
    
    def _init_all2zero(self):
        self._res = {}
        self.n_ions = {}
        self.ionic_full = {}
        self.ionic_names = {}
        self.n_zones_full = None
        self.zones_full = None
        self.depth_full = None
        self.radius_full = None
        self.dv_full = None
        self.dr_full = None
        self.r_in = None
        self.r_out = None
        self.thickness_full = None
        self.ne_full = None
        self.nH_full = None
        self.te_full = None
        self.nenH_full = None
        self.tenenH_full = None
        self.n_lines = 0
        self.lines = None
        self.intens = None
        self.slines = None
        self.rlines = None
        self.heat_full = None
        self.cool_full = None
        self.emis_full = None
        self.opd_energy = None
        self.opd_total = None
        self.opd_absorp = None
        self.opd_scat = None
        self.n_gtemp = 0
        self.gtemp_full = None
        self.gsize = None
        self.gtemp_labels = None            
        self.n_gabund = 0
        self.gabund_full = None
        self.gasize = None
        self.gabund_labels = None
        self.n_gdgrat = 0
        self.gdgrat_full = None
        self.gdsize = None
        self.gdgrat_labels = None        
        self.plan_par = None
        self.Hbeta_full = None
    
    def _init_rad(self):
        key = 'rad'
        self._res[key] = self.read_outputs(key)
        if self._res[key] is not None:
            self.empty_model = False
            self.n_zones_full = self._res[key].size
            self.zones_full = np.arange(self.n_zones_full)
            self.log_.message('Number of zones: {0:d}'.format(self.n_zones_full), calling = self.calling)
            self.depth_full = self._res[key]['depth']
            if self.n_zones_full > 1:
                self.thickness_full = self.depth_full[-1]
            else: 
                self.thickness_full = self.depth_full
            self.radius_full = self._res[key]['radius'] 
            self.dr_full = self._res[key]['dr']
            self.dv_full = 4. * np.pi * self.radius_full ** 2 * self.dr_full
            if self.n_zones_full > 1:
                self.r_in = self.radius_full[0] - self.dr_full[0]/2
                self.r_out = self.radius_full[-1] + self.dr_full[0]/2
            else:
                self.r_in = self.radius_full - self.dr_full/2
                self.r_out = self.radius_full + self.dr_full/2   
            self.r_in_cut = self.r_in
            self.r_out_cut = self.r_out
            if self.Phi0 == 0.:
                self.Phi = self.Q / (4 * np.pi * self.r_in**2)
                self.Phi0 = self.Phi.sum()

            

    ## 
    # @var r_in 
    # Initial radius [float] (cm)
    # @var r_out 
    # Final radius [float] (cm)
    # @var n_zones_full
    # total number of zones, r_range unused [int] 
    # @var zones_full
    # arrays of zones, r_range unused [int array]
    # @var depth_full
    # array of depths, r_range unused [float array] (cm)
    # @var radius_full
    # array of radius, r_range unused [float array] (cm)
    # @var dv_full
    # array of volume element of each zone, r_range unused [float array] (\f$cm^3\f$)
    # @var dr_full
    # array of thickness element of each zone, r_range unused [float array] (cm)
    # @var thickness_full
    # total thickness of the nebula, r_range not used [float] (cm)
            
    def _init_phy(self):
        key = 'phy'
        self._res[key] = self.read_outputs(key)
        if self._res[key] is not None:
            self.ne_full = self._res[key]['ne']
            self.nH_full = self._res[key]['nH']
            self.nenH_full = self.ne_full * self.nH_full
            self.te_full = self._res[key]['Te']
            self.tenenH_full = self.te_full * self.nenH_full
            self.ff_full = self._res[key]['fillfac']
            self.nenHff2_full = self.ne_full * self.nH_full * self.ff_full**2
            self.nHff_full = self.nH_full * self.ff_full
            self.H_mass_full = (self.nH_full * self.dv_full * self.ff_full).cumsum() * pc.CST.HMASS / pc.CST.SUN_MASS
            self.__H_mass_cut = self.H_mass_full[-1]
    ##
    # @var ne_full
    # array of electron density, r_range unused [float] (cm^-3)
    # @var nH_full
    # array of Hydrogen density, r_range unused [float] (cm^-3)
    # @var nenH_full
    # array of ne.nH, r_range unused [float] (cm^-6)
    # @var te_full
    # array of electron temperature, r_range unused [float] (K)
    # @var tenenH_full
    # array of te.ne.nH, r_range unused [float] (K.cm^-6)
    # @var ff_full
    # array of filling factor, r_range unused [float]
             
    def _init_lin(self):
        key = 'lin'
        self._res[key] = self.read_outputs(key, case_sensitive='upper')
        if self._res[key] is not None:
            if self.line_is_log:
                trans_line = lambda x: pow(10., x)
            else:
                trans_line = lambda x: x
            lines = self._res[key]
            self.line_labels = np.asarray(lines.dtype.names[1::])
            self.n_lines = np.size(self.line_labels)
            self.log_.message('Number of lines: {0.n_lines:d}'.format(self), calling = self.calling)
            self.lines = np.zeros(self.n_lines)
            for i, label in enumerate(self.line_labels):
                self.lines[i] = trans_line(lines[label])
            self.slines = np.asarray([label for label in self.line_labels if label[-2] != '_'])
            self.rlines = np.asarray([(label[:-2], label) [label[-2] != '_'] for label in self.line_labels])

    def _init_emis(self):
        key = 'emis'
        self._res[key] = self.read_outputs(key, case_sensitive='upper') #may need skip_header=1
        if self._res[key] is not None:
            if self.emis_is_log:
                trans_emis = lambda x: pow(10., x)
            else:
                trans_emis = lambda x: x
            emis = self._res[key]            
            self.emis_labels = np.asarray(emis.dtype.names[1::])
            
            if self.cloudy_version_major > 13:
                # We are with c17+ and will create emis_labels_13
                self.emis_labels_17 = self.emis_labels
                self.emis_labels_13 = []
                for label in self.emis_labels:
                    try:
                        self.emis_labels_13.append(convert_c17_c13(label))
                    except:
                        self.emis_labels_13.append('')
                self.emis_labels_13 = np.array(self.emis_labels_13, dtype=str)
            else:
                # We are with c13 and will create emis_labels_17
                self.emis_labels_13 = self.emis_labels
                self.emis_labels_17 = []
                for label in self.emis_labels:
                    try:
                        self.emis_labels_17.append(convert_c13_c17(label))
                    except:
                        self.emis_labels_17.append('')            
                self.emis_labels_17 = np.array(self.emis_labels_17, dtype=str)
            self.n_emis = np.size(self.emis_labels)
            self.log_.message('Number of emissivities: {0.n_emis:d}'.format(self), calling = self.calling)
            self.emis_full = np.zeros((self.n_emis, np.size(emis)))
            for i, label in enumerate(self.emis_labels):
                self.emis_full[i] = trans_emis(emis[label])
            if 'H__1__4861A' in self.emis_labels:
                self.Hbeta_full = (self.get_emis('H__1__4861A') * self.dvff).cumsum()
                self.__Hbeta_cut = self.Hbeta_full[-1]

    def _init_ionic(self, elem, str_key = 'ele_'):
        key = str_key + elem
        self._res[key] = self.read_outputs(key)
        if self._res[key] is not None:
            ionic_names = self._res[key].dtype.names[1:]
            n_ions = np.size(ionic_names)
            ionic = np.zeros((n_ions, self.n_zones))
            try:
                for i, ion in enumerate(ionic_names):
                    ionic[i, :] = self._res[key][ion]
                self.ionic_names[elem] = ionic_names
                self.n_ions[elem] = n_ions
                self.ionic_full[elem] = ionic
                self.log_.message('filling ' + elem + ' with ' + str(n_ions) + ' columns', calling = self.calling)
            except:
                self.log_.message('File {0} not read'.format(key))
        self.n_elements = np.size(list(self.n_ions.keys()))

    def _init_heatcool(self):
        key = 'heat'
        self._res[key] = self.read_outputs(key, names = 'depth, temp, heat, cool', 
                                           usecols = (0, 1, 2, 3), comments = '#')
        if self._res[key] is not None:
            self.heat_full = self._res[key]['heat']
            self.cool_full = self._res[key]['cool']
           
    def _init_cont(self):
        key = 'cont'
        self._res[key] = self.read_outputs(key, usecols=(0, 1, 2, 3, 4, 5))

    def _init_opd(self):
        key = 'opd'
        self._res[key] = self.read_outputs(key)
        if self._res[key] is not None:
            if 'energy' in self._res[key].dtype.names:
                self.opd_energy = self._res[key]['energy']
            elif 'energyRyd' in self._res[key].dtype.names:
                self.opd_energy = self._res[key]['energyRyd']
            else:
                self.opd_energy = None
                self.log_.warn('No energy found in opd file', calling = self.calling)
            self.opd_total = self._res[key]['total']
            self.opd_absorp = self._res[key]['absorp']
            self.opd_scat = self._res[key]['scat']
            
    def _init_grains(self):
        key = 'gtemp'
        if int(self.cloudy_version_major) == 7:
            sk_header = 0
        else:
            sk_header = 1
        self._res[key] = self.read_outputs(key, skip_header=sk_header)
        if self._res[key] is not None:
            self.gtemp_labels = list(self._res[key].dtype.names[1:])
            gtemp = self._res[key]
            self.n_gtemp = np.size(self.gtemp_labels)
            self.gtemp_full = np.zeros((self.n_gtemp, np.size(gtemp) - 1))
            self.gsize = np.zeros((self.n_gtemp))
            for i, label in enumerate(self.gtemp_labels):
                self.gtemp_full[i] = gtemp[label][1::]
                self.gsize[i] = gtemp[label][0]
        key = 'gabund'
        self._res[key] = self.read_outputs(key, skip_header=1, usecols=np.arange(self.n_gtemp + 1))
        if self._res[key] is not None:
            self.gabund_labels = self._res[key].dtype.names[1:]
            gabund = self._res[key]
            self.n_gabund = np.size(self.gabund_labels)
            self.gabund_full = np.zeros((self.n_gabund, np.size(gabund) - 1))
            self.gasize = np.zeros((self.n_gabund))
            for i, label in enumerate(self.gabund_labels):
                self.gabund_full[i] = gabund[label][1::]
                self.gasize[i] = gabund[label][0]
        key = 'gdgrat'
        self._res[key] = self.read_outputs(key, skip_header=1, usecols=np.arange(self.n_gtemp + 1))
        if self._res[key] is not None:
            self.gdgrat_labels = self._res[key].dtype.names[1:]
            gdgrat = self._res[key]
            self.n_gdgrat = np.size(self.gdgrat_labels)
            self.gdgrat_full = np.zeros((self.n_gdgrat, np.size(gdgrat) - 1))
            self.gdsize = np.zeros((self.n_gdgrat))
            for i, label in enumerate(self.gdgrat_labels):
                self.gdgrat_full[i] = gdgrat[label][1::]
                self.gdsize[i] = gdgrat[label][0]
        
    def _read_stout(self, emis_is_log):
        self.out = {}
        file_name = self.model_name + '.out'
        self.C3D_comments = []
        self.comments = []
        self.warnings = []
        self.cautions = []
        try:
            file_ = open(file_name, 'r')
            self.out_exists = True
        except:
            self.log_.warn(file_name + ' NOT read.', calling = self.calling)
            self.out_exists = False
            self.info = '<!!! Model {0} without output file>'.format(self.model_name)
            return None
        self.date_model = time.ctime(os.path.getctime(file_name))
        self.Teff = None
        self.out['Cloudy ends'] = ''
        self.out['stop'] = ''
        self.cloudy_version = ''
        for line in file_:
            if 'Cloudy' in line and 'testing' not in line and 'Please' not in line and self.cloudy_version == '':
                self.cloudy_version = line.strip()
                self.cloudy_version_major = pc.sextract(self.cloudy_version,'Cloudy ','.')
                try:
                    self.cloudy_version_major = int(self.cloudy_version_major)
                except:
                    pass
                try:
                    if int(self.cloudy_version_major) >= 17:
                        self.emis_is_log = False
                    else:
                        self.emis_is_log = emis_is_log
                except:
                    self.emis_is_log = emis_is_log        
            elif line[0:8] == ' ####  1':
                self.out['###First'] = line
            elif line[0:4] == ' ###':
                self.out['###Last'] = line
            elif 'Calculation stopped' in line:
                self.out['stop'] = line
            elif 'Cloudy ends' in line:
                self.out['Cloudy ends'] = line
            elif 'Gas Phase Chemical Composition' in line:
                for i in range(4):
                    self.out['Chem' + str(i + 1)] = next(file_)
            elif 'Grain Chemical Composition' in line:
                self.out['GrainChem'] = next(file_)
            elif 'Dust to gas ratio' in line:
                self.out['D/G'] = line
            elif 'iterate' in line:
                self.out['iterate'] = line
            elif 'Hi-Con' in line:
                for i in range(7):
                    self.out['SED' + str(i + 1)] = next(file_)
            elif 'table star' in line:
                self.out['table star'] = line
            elif 'Blackbody' in line:
                self.out['Blackbody'] = line
                try:
                    self.Teff = np.float(pc.sextract(self.out['Blackbody'], 'Blackbody ', '*'))
                except:
                    try:
                        self.Teff = np.float(pc.sextract(self.out['Blackbody'], 'Blackbody ', '\n'))
                    except:
                        self.Teff = None
            elif 'hden' in line:
                self.out['hden'] = line
            elif 'dlaw' in line:
                self.out['dlaw'] = line
            elif 'TOTL  4861A' in line:
                self.out['Hbeta'] = line
            elif 'H  1      4861.36A' in line:
                self.out['Hbeta'] = line
            elif 'luminosity' in line:
                self.out['luminosity'] = line
            elif 'turbulence' in line:
                self.out['turbulence'] = line
            elif 'fudge' in line:
                self.out['fudge'] = line
            elif 'distance' in line:
                self.out['distance'] = line
                dist_str = sextract(line, '=', 'kpc')
                dist_set = False
                if 'linear' in line:
                    correc = lambda x: x
                else:
                    correc = lambda x: 10.**x
                if dist_str != '':
                    self.distance = correc(np.float(dist_str))
                    dist_set = True
                dist_str = sextract(line, '=', 'parsecs')
                if dist_str != '':
                    self.distance = correc(np.float(dist_str)) / 1e3
                    dist_set = True
                dist_str = sextract(line, '=', 'cm')
                if dist_str != '':
                    self.distance = correc(np.float(dist_str)) / pc.CST.KPC
                    dist_set = True
                if not dist_set:
                    self.log_.warn('Unable to determine distance', calling = self.calling)
            elif 'C3D' in line:
                self.C3D_comments.append(line)
            elif 'C **' in line:
                self.comments.append(line)
            elif line[0:3] == ' C-':
                self.cautions.append(line)
            elif line[0:3] == '  !' or line[0:3] == ' W-':
                self.warnings.append(line)
        file_.close()
        try:
            self.theta = float(pc.sextract(self.C3D_comments, 'theta = ', ' ')[0])
        except:
            self.theta = None
        try:
            self.phi = float(pc.sextract(self.C3D_comments, 'phi = ', ' ')[0])
        except:
            self.phi = None
        self.Q = np.zeros(4)
        self.Phi = np.zeros(4)
        try:
            self.Q[0] = float(pc.sextract(self.out['SED2'], 'Q(1.0-1.8):', 'Q(1.8-4.0):'))
            self.Q[1] = float(pc.sextract(self.out['SED2'], 'Q(1.8-4.0):', 'Q(4.0-20):'))
            self.Q[2] = float(pc.sextract(self.out['SED2'], 'Q(4.0-20):', 'Q(20--):'))
            self.Q[3] = float(pc.sextract(self.out['SED2'], 'Q(20--):', 'Ion pht'))
            self.Q = pow(10., self.Q)
            self.plan_par = False
        except:
            pass
        self.Q0 = self.Q.sum()
        try:
            self.Phi[0] = float(pc.sextract(self.out['SED2'], 'phi(1.0-1.8):', 'phi(1.8-4.0):'))
            self.Phi[1] = float(pc.sextract(self.out['SED2'], 'phi(1.8-4.0):', 'phi(4.0-20):'))
            self.Phi[2] = float(pc.sextract(self.out['SED2'], 'phi(4.0-20):', 'phi(20--):'))
            self.Phi[3] = float(pc.sextract(self.out['SED2'], 'phi(20--):', 'Ion pht'))
            self.Phi = pow(10., self.Phi)
            self.plan_par = True
        except:
            pass
        self.Phi0 = self.Phi.sum()
        
        self.abund = {}
        try:
            Chem = self.out['Chem1'][0:-1]
            chem_is_ok = True
            if self.out['Chem2'] != ' \n':
                Chem += self.out['Chem2'][0:-1]
                if self.out['Chem3'] != ' \n':
                    Chem += self.out['Chem3'][0:-1]
                    if self.out['Chem4'] != ' \n':
                        Chem += self.out['Chem4'][0:-1]
            self.gas_mass_per_H = 0.
            for ab_str in LIST_ALL_ELEM:
                if len(ab_str) == 1:
                    sub1 = ab_str + ' : '
                else:
                    sub1 = ab_str + ': '
                try:             
                    self.abund[ab_str] = float(pc.sextract(Chem, sub1, 7))
                except:
                    self.log_.message(ab_str + ' abundance not defined', calling = self.calling)
                if (ab_str in ATOMIC_MASS) and (ab_str in self.abund):
                    self.gas_mass_per_H += 10**self.abund[ab_str] * ATOMIC_MASS[ab_str]
        except:
            chem_is_ok = False
        if ("ABORT" in self.out['Cloudy ends']) or ("aborted" in self.out['stop']) or (not chem_is_ok):
            self.aborted = True
            self.log_.warn('Model aborted', calling = self.calling)
            self.info = '<!!! Model {0} aborted>'.format(self.model_name)
        else:
            self.aborted = False
        return True
    
    def read_outputs(self, extension, delimiter='\t', comments=';', names=True, **kwargs):
        file_ = self.model_name + '.' + extension
        if os.path.exists(file_):
            try:
                res = np.genfromtxt(file_, delimiter=delimiter, comments=comments, names=names, **kwargs) # some arguments can be sent here
                self.log_.message(file_ + ' read', calling=self.calling)
            except ValueError:
                if self.cloudy_version_major == '08':
                    self.log_.error(file_ + ' NOT read. You may need to remove \t depth in line 132 and to move "strcat( chHeader, "\t" )" from line 139 to 135 in source/punch_line.cpp', 
                                    calling = self.calling)
                else:
                    self.log_.error(file_ + ' NOT read.', calling=self.calling)
                res = None
            except IndexError:
                self.log_.warn(file_ + ' empty.', calling=self.calling)
                res = None
            except: 
                self.log_.error(file_ + ' NOT read.', calling=self.calling)
                res = None
        else:
                self.log_.warn(file_ + ' does not exist.', calling=self.calling)
                res = None
        return res

    def _get_over_range(self, var):
        
        if self.n_zones > 1:
            return var[self.r_range]
        else:
            if type(var) is np.ndarray:
                return var.ravel()[0]
            else:
                return var
    
    ## array of zones [int array]
    @property
    def zones(self):
        if self.empty_model:
            return None
        else:
            return self.zones_full[self.r_range]
    
    ## number of zones [int]
    @property
    def n_zones(self):
        if self.empty_model:
            return 0
        else:
            return self.zones.size

    ## depth [float array] (cm)
    @property
    def depth(self):
        """ array of depth (on r_range)"""
        return self._get_over_range(self.depth_full)

    ## thickness [float array] (cm)
    @property
    def thickness(self):
        """ array of thickness (on r_range)"""
        
        if self.n_zones > 1:
            return self.depth[-1]-self.depth[0]
        else:
            return 0.0

    ## radius [float array] (cm)
    @property
    def radius(self):
        """ array of radius (on r_range)"""
        return self._get_over_range(self.radius_full)

    ## size of each zone [float array] (cm)
    @property
    def dr(self):
        """ array of dr (on r_range)"""
        return self._get_over_range(self.dr_full)

    ## size of each zone taking into account filling factor [float array] (cm)
    @property
    def drff(self):
        """ array of dr (on r_range)"""
        return self._get_over_range(self.dr_full * self.ff_full)

    ## volume of each zone [float array] (cm^3)
    @property
    def dv(self):
        """ array of volume element (on r_range)"""
        return self._get_over_range(self.dv_full)

    ## volume of each zone taking into account filling factor [float array] (cm^3)
    @property
    def dvff(self):
        """ array of volume element (on r_range)"""
        return self._get_over_range(self.dv_full * self.ff_full)

    ## electron density [float array] (cm^-3)
    @property
    def ne(self):
        """ array of electron density (on r_range)"""
        return self._get_over_range(self.ne_full)

    ## Hydrogen density [float array] (cm^-3)
    @property
    def nH(self):
        """ array of Hydrogen density (on r_range)"""
        return self._get_over_range(self.nH_full)

    ## ne.nH [float array] (cm^-6)
    @property
    def nenH(self):
        """ array of ne.nH (on r_range)"""
        return self._get_over_range(self.nenH_full)

    ## Electron temperature [float array] (K)
    @property
    def te(self):
        """ array of electron temperature (on r_range)"""
        return self._get_over_range(self.te_full)

    ## te.ne.nH [float array] (K.cm^-6)
    @property
    def tenenH(self):
        """ array of Te.ne.nH (on r_range)"""
        return self._get_over_range(self.tenenH_full)

    ## filling factor [float array]
    @property
    def ff(self):
        """ array of filling factor (on r_range)"""
        return self._get_over_range(self.ff_full)

    ## cooling [float array]
    @property
    def cool(self):
        """ array of colling (on r_range)"""
        return self._get_over_range(self.cool_full)

    ## heating [float array]
    @property
    def heat(self):
        """ array of heating (on r_range)"""
        return self._get_over_range(self.heat_full)
    
    def _quiet_div(self, a, b):
        if a is None or b is None:
            to_return = None
        else:
            np.seterr(all="ignore")
            to_return = a / b
            np.seterr(all=None)
        return to_return

    ##rad_integ(a) = \f$\int a.ff.dr\f$ 
    def rad_integ(self, a):
        """ integral of a on the radius"""
        if a is None or self.dr is None:
            return None
        else:
            #return np.trapz(a, self.radius)
            return (a * self.drff).sum()
    
    ##vol_integ(a) = \f$\int a.ff.dV\f$
    def vol_integ(self, a):
        """ integral of a on the volume"""
        if a is None or self.dv is None:
            return None
        else:
            return (a * self.dvff).sum()
            #return 4.0*np.pi*np.trapz((a*self.radius**2*ff)[self.r_range], self.radius[self.r_range])

    ##vol_mean(a, b) = \f$\frac{\int a.b.ff.dV}{\int b.ff.dV}\f$
    def vol_mean(self, a, b = 1.):
        """ Return the mean value of a weighted by b on the volume"""
        return self._quiet_div(self.vol_integ(a * b), self.vol_integ(b))
    
    ##rad_mean(a, b) = \f$\frac{\int a.b.dr}{\int b.dr}\f$    
    def rad_mean(self, a, b = 1.):
        """ Return the mean value of a weighted by b on the radius"""
        return self._quiet_div(self.rad_integ(a * b), self.rad_integ(b))    

    ## log(U) in each zone [float array], with U(r) = \f$ Phi_0 * (r_0/r)^2/ (n_H.c)\f$
    @property
    def log_U(self):
        """ U = Phi0 * (r_in/rarius) / (nH c)"""
        try:
            log_U = np.log10(self.Phi0 * (self.r_in/self.radius)**2 / (self.nH * pc.CST.CLIGHT))
        except:
            self.log_.warn('No U computed', calling = self.calling)
            log_U = None
        return log_U
        
    ## log_U_mean = \f$\frac{\int U.dV}{\int dV}\f$ [float]
    @property
    def log_U_mean(self):
        """ log of mean value of U on the volume """
        if self.log_U is not None:
            return np.log10(self.vol_mean(10**self.log_U))
        else:
            return None      

    ## log_U_mean_ne = \f$\frac{\int U.ne.nH.dV}{\int ne.nH.dV}\f$ [float]
    @property
    def log_U_mean_ne(self):
        """ log of mean value of U on the volume weighted by ne.nH"""
        if self.log_U is not None:
            return np.log10(self.vol_mean(10**self.log_U, self.nenH))
        else:
            return None      
    
    def get_ionic(self, elem, ion):
        """ 
        param
            elem [str] element
            ion [str or int] ionic state of ion
        return: 
            ionic fraction of (elem, ion). 
        """
        if self.is_valid_ion(elem, ion):
            return self.ionic_full[elem][ion][self.r_range]
        else:
            return None
        
    @property
    def gtemp(self):
        if self.gtemp_full is not None:
            return self.gtemp_full[:,self.r_range]
        else:
            return None
        
    @property
    def gabund(self):
        if self.gabund_full is not None:
            return self.gabund_full[:,self.r_range]
        else:
            return None
        
    @property
    def gdgrat(self):
        if self.gdgrat_full is not None:
            return self.gdgrat_full[:,self.r_range]
        else:
            return None
    
    @property
    def gmass(self):
        if self.gabund_full is not None:
            res = []
            for ig in range(self.gdsize.size):
                res.append(self.vol_integ(self.gabund[ig]) / pc.CST.SUN_MASS)
            if self.gdsize.size == 1:
                return res[0]
            else:
                return np.array(res)
        else:
            return None
        
    
    ## get_T0_ion_vol(X, i) = \f$ \frac{\int T_e.n_H.ff.X^i/X.dV}{\int n_H.ff.X^i/X.dV}\f$
    def get_T0_ion_vol(self, elem=None, ion=None):
        """
        param:
            elem [str] element
            ion [str or int] ionic state of ion
        return:    
            Electron temperature integrated on the volume weighted by ionic abundance
        """
        if self.is_valid_ion(elem, ion):
            nion = self.nH * self.get_ionic(elem, ion)
            return self.vol_mean(self.te, nion)
        else:
            err = "Ion {0} {1:d} not available".format(elem, ion)
            self.log_.warn(err, calling = self.calling)
            return None
        
    ## get_T0_ion_rad(X, i) = \f$ \frac{\int T_e.n_H.ff.X^i/X.dr}{\int n_H.ff.X^i/X.dr}\f$
    def get_T0_ion_rad(self, elem=None, ion=None):
        """
        param:
            elem [str] element
            ion [str or int] ionic state of ion
        return:    
            Electron temperature integrated on the radius weighted by ionic abundance
        """
        if self.is_valid_ion(elem, ion):
            nion = self.nH * self.get_ionic(elem, ion)
            return self.rad_mean(self.te, nion)
        else:
            err = "Ion {0} {1:d} not available".format(elem, ion)
            self.log_.warn(err, calling = self.calling)
            return None
        
    ## get_ab_ion_vol(X, i) = \f$ \frac{\int X^i/X.n_H.ff.dr}{\int n_H.ff.dr}\f$
    def get_ab_ion_vol(self, elem=None, ion=None):
        """
        param:
            elem [str] element
            ion [str or int] ionic state of ion
        return:    
            Ionic fraction integrated on the volume weighted by hydrogen density
        """
        if self.is_valid_ion(elem, ion):
            ab_ion = self.get_ionic(elem, ion)
            return self.vol_mean(ab_ion, self.nH)
        else:
            err = "Ion {0} {1:d} not available".format(elem, ion)
            self.log_.warn(err, calling = self.calling)
            return None
        
    ## get_ab_ion_rad(X, i) = \f$\frac{\int X^i/X.n_H.ff.dr}{\int n_H.ff.dr}\f$
    def get_ab_ion_rad(self, elem=None, ion=None):
        """
        param:
            elem [str] element
            ion [str or int] ionic state of ion
        return:    
            Ionic fraction integrated on the radius weighted by nH
        """
        if self.is_valid_ion(elem, ion):
            ab_ion = self.get_ionic(elem, ion)
            return self.rad_mean(ab_ion, self.nH)
        else:
            err = "Ion {0} {1:d} not available".format(elem, ion)
            self.log_.warn(err, calling = self.calling)
            return None
        
    ## get_ne_ion_vol_ne(X, i) = \f$\frac{\int ne.ne.nH.ff.Xi/X.dV}{\int ne.nH.ff.Xi/X.dV}\f$
    def get_ne_ion_vol_ne(self, elem=None, ion=None):
        """
        param:
            elem [str] element
            ion [str or int] ionic state of ion
        return:    
            electron density integrated on the volume weighted by ne.nH.Xi/X
        """
        if self.is_valid_ion(elem, ion):
            nenion = self.nenH * self.get_ionic(elem, ion)
            return self.vol_mean(self.ne, nenion)
        else:
            err = "Ion {0} {1:d} not available".format(elem, ion)
            self.log_.warn(err, calling = self.calling)
            return None
        
    ## get_T0_ion_vol_ne(X, i) = \f$\frac{\int Te.ne.nH.ff.Xi/X.dV}{\int ne.nH.ff.X^i/X.dV}\f$
    def get_T0_ion_vol_ne(self, elem=None, ion=None):
        """
        param:
            elem [str] element
            ion [str or int] ionic state of ion
        return:    
            electron temperature integrated on the volume weighted by ne.nH.Xi/X
        """
        if self.is_valid_ion(elem, ion):
            nenion = self.nenH * self.get_ionic(elem, ion)
            return self.vol_mean(self.te, nenion)
        else:
            err = "Ion {0} {1:d} not available".format(elem, ion)
            self.log_.warn(err, calling = self.calling)
            return None
        
    ## get_T0_ion_rad_ne(X, i) = \f$\frac{\int Te.ne.nH.ff.Xi/X.dr}{\int ne.nH.ff.Xi/X.dr}\f$
    def get_T0_ion_rad_ne(self, elem=None, ion=None):
        """
        param:
            elem [str] element
            ion [str or int] ionic state of ion
        return:    
            electron temperature integrated on the radius weighted by ne.nH.Xi/X
        """
        if self.is_valid_ion(elem, ion):
            nenion = self.nenH * self.get_ionic(elem, ion)
            return self.rad_mean(self.te, nenion)
        else:
            err = "Ion {0} {1:d} not available".format(elem, ion)
            self.log_.warn(err, calling = self.calling)
            return None
        
    ## get_ne_ion_rad_ne(X, i) = \f$\frac{\int ne.ne.nH.ff.Xi/X.dr}{\int ne.nH.ff.Xi/X.dr}\f$
    def get_ne_ion_rad_ne(self, elem=None, ion=None):
        """
        param:
            elem [str] element
            ion [str or int] ionic state of ion
        return:    
            electron density integrated on the radius weighted by ne.nH.Xi/X
        """
        if self.is_valid_ion(elem, ion):
            nenion = self.nenH * self.get_ionic(elem, ion)
            return self.rad_mean(self.ne, nenion)
        else:
            err = "Ion {0} {1:d} not available".format(elem, ion)
            self.log_.warn(err, calling = self.calling)
            return None
        
    ## get_ab_ion_vol_ne(X, i) = \f$\frac{\int Xi/X.n_e.n_H.ff.dV}{\int ne.nH.ff.dV}\f$
    def get_ab_ion_vol_ne(self, elem=None, ion=None):
        """
        param:
            elem [str] element
            ion [str or int] ionic state of ion
        return:    
            ionic fraction integrated on the volume weighted by ne.nH
        """
        if self.is_valid_ion(elem, ion):
            ab_ion = self.get_ionic(elem, ion)
            return self.vol_mean(ab_ion, self.nenH)
        else:
            err = "Ion {0} {1:d} not available".format(elem, ion)
            self.log_.warn(err, calling = self.calling)
            return None
        
    ## get_ab_ion_rad_ne(X, i) = \f$\frac{\int Xi/X.n_e.n_H.ff.dr}{\int ne.nH.ff.dr}\f$
    def get_ab_ion_rad_ne(self, elem=None, ion=None):
        """
        param:
            elem [str] element
            ion [str or int] ionic state of ion
        return:    
            ionic fraction integrated on the radius weighted by ne.nH
        """
        if self.is_valid_ion(elem, ion):
            ab_ion = self.get_ionic(elem, ion)
            return self.rad_mean(ab_ion, self.nenH)
        else:
            err = "Ion {0} {1:d} not available".format(elem, ion)
            self.log_.warn(err, calling = self.calling)
            return None
        
    ## get_t2_ion_vol_ne(X, i) = \f$\frac{\int (T_e-T_{X^i})^2.n_e.n_H.ff.X^i/X.dV}{T_{X^i}^2.\int ne.nH.ff.X^i/X.dV}\f$
    def get_t2_ion_vol_ne(self, elem=None, ion=None):
        """
        param:
            elem [str] element
            ion [str or int] ionic state of ion
        return:    
            t2 integrated on the volume weighted by ne.nH.X^i/X
        """
        if self.is_valid_ion(elem, ion):
            nenion = self.nenH * self.get_ionic(elem, ion)
            t_ion_vol_ne = self.get_T0_ion_vol_ne(elem, ion)
            return self.vol_mean((self.te - t_ion_vol_ne) ** 2., nenion) / t_ion_vol_ne ** 2.
        else:
            err = "Ion {0} {1:d} not available".format(elem, ion)
            self.log_.warn(err, calling = self.calling)
            return None
        
    ## get_t2_ion_vol_ne(X, i) = \f$\frac{\int (T_e-T_{X^i})^2.n_e.n_H.ff.X^i/X.dr}{T_{X^i}^2.\int ne.nH.ff.X^i/X.dr}\f$
    def get_t2_ion_rad_ne(self, elem=None, ion=None):
        """
        param:
            elem [str] element
            ion [str or int] ionic state of ion
        return:    
            t2 integrated on the radius weighted by ne.nH.X^i/X
        """
        if self.is_valid_ion(elem, ion):
            nenion = self.nenH * self.get_ionic(elem, ion)
            t_ion_rad_ne = self.get_T0_ion_rad_ne(elem, ion)
            return self.rad_mean((self.te - t_ion_rad_ne) ** 2., nenion) / t_ion_rad_ne ** 2.
        else:
            err = "Ion {0} {1:d} not available".format(elem, ion)
            self.log_.warn(err, calling = self.calling)
            return None
    
    def _i_line(self, ref):
        if type(ref) is str or type(ref) is np.str_:
            if ref in self.line_labels_13:                
                to_return = np.argwhere(self.emis_labels_13 == ref)[0][0]
            elif ref in self.line_labels_17:                
                to_return = np.argwhere(self.emis_labels_17 == ref)[0][0]
            else:
                self.log_.warn(ref + ' is not a correct line reference - 1', calling = self.calling)
                to_return = None
        elif type(ref) is int or type(ref) is np.int32:
            if (ref >= 0) & (ref < self.n_lines):
                to_return = ref
            else:
                self.log_.warn(str(ref) + ' is not a correct line reference - 2', calling = self.calling)
                to_return = None
        else:
            self.log_.warn(str(type(ref)) + ' is not a correct line type - 3', calling = self.calling)
            to_return = None
        return to_return
    
    def _i_emis(self, ref):
        """
        param:
            ref [int or str] line reference
        return:
            the indice of the line in the emis liste
        """
        if type(ref) is str or type(ref) is np.str_:
            if ref in self.emis_labels_13:                
                to_return = np.argwhere(self.emis_labels_13 == ref)[0][0]
            elif ref in self.emis_labels_17:
                to_return = np.argwhere(self.emis_labels_17 == ref)[0][0]
            else:
                self.log_.warn(ref + ' is not a correct line reference - 1', calling = self.calling)
                to_return = None
        elif type(ref) is int or type(ref) is np.int32:
            if (ref >= 0) & (ref < self.n_emis):
                to_return = ref
            else:
                self.log_.warn(str(ref) + ' is not a correct line reference - 2', calling = self.calling)
                to_return = None
        else:
            self.log_.warn(str(type(ref)) + ' is not a correct line type - 3', calling = self.calling)
            to_return = None
        return to_return

    def _l_emis(self, ref):
        """
        param:
            ref [int or str] line reference
        return:
            the label of the line
        """
        if type(ref) is str or type(ref) is np.str_:
            if ref in self.emis_labels_13:                
                to_return = ref
            elif ref in self.emis_labels_17:                
                to_return = ref
            else:
                self.log_.warn(ref + ' is not a correct line reference - 1', calling = self.calling)
                to_return = None
        elif type(ref) is int or type(ref) is np.int32:
            if (ref >= 0) & (ref < self.n_emis):
                to_return = self.emis_labels[ref]
            else:
                self.log_.warn(str(ref) + ' is not a correct line reference - 2', calling = self.calling)
                to_return = None
        else:
            self.log_.warn(str(type(ref)) + ' is not a correct line type - 3', calling = self.calling)
            to_return = None
        return to_return
        

    def get_line(self, ref):
        """
        Return line intensity.
        ref can be a label or a number (starting at 0 with the first line)
        """
        if self._i_line(ref) is not None:
            return self.lines[self._i_line(ref)]
        else:
            return None
                        
    ## return the emissivities(radius)  of the given line [array float] (erg/cm^3/s)
    def get_emis(self, ref):
        """
        Return emissivity.
        param:
            ref can be a label or a number (starting at 0 with the first line)
        """
        if self._i_emis(ref) is not None:
            return self.emis_full[self._i_emis(ref)][self.r_range]
        else:
            return None
            
    ## get_emis_vol(ref, [at_earth]) = \f$ \int \epsilon(ref).dV [/ 4.\pi.(distance)^2]\f$
    def get_emis_vol(self, ref, at_earth=False):
        """
        Return integration of the emissivity on the volume (should be the line intensity if r_out_cut>=r_out)
        param:
            ref can be a label or a number (starting at 0 with the first line)
        """
        if at_earth:
            coeff = 4. * np.pi * (self.distance * pc.CST.KPC) ** 2
        else:
            coeff = 1.
        return self.vol_integ(self.get_emis(ref)) / coeff

    ## get_emis_rad(ref) = \f$ \int \epsilon(ref).dr\f$
    def get_emis_rad(self, ref):
        """
        Return integration of the emissivity on the radius
        param:
            ref can be a label or a number (starting at 0 with the first line)
        """
        return self.rad_integ(self.get_emis(ref))

    ## get_T0_emis(ref) = \f$\frac{\int T_e.\epsilon(ref).dV}{\int \epsilon(ref).dV}\f$
    def get_T0_emis(self, ref):        
        """ 
        integral of the electron temperature on the volume, weighted by emissivity of a given line
        param:
            ref [int or str] line reference
        return:
            [float]
        """
        return self.vol_mean(self.te, self.get_emis(ref))
    
    ## get_T0_emis_rad(ref) = \f$\frac{\int T_e.\epsilon(ref).dr}{\int \epsilon(ref).dr}\f$
    def get_T0_emis_rad(self, ref):        
        """ 
        integral of the electron temperature on the radius, weighted by emissivity of a given line
        param:
            ref [int or str] line reference
        return:
            [float]
        """
        return self.rad_mean(self.te, self.get_emis(ref))
    
    ## get_ne_emis(ref) = \f$\frac{\int n_e.\epsilon(ref).dV}{\int \epsilon(ref).dV}\f$
    def get_ne_emis(self, ref):        
        """ 
        integral of the electron density on the volume, weighted by emissivity of a given line
        param:
            ref [int or str] line reference
        return:
            [float]
        """
        return self.vol_mean(self.ne, self.get_emis(ref))
    
    #nH_mean = \f$\frac{\int n_H.dV}{\int dV}\f$
    @property
    def nH_mean(self):
        """ 
        mean of the Hydrogen density over the volume
        return:
            [float]
        """
        return self.vol_mean(self.nH, 1.)
    
    ## get_t2_emis(ref) = \f$\frac{\int (T_e-T(ref))^2.\epsilon(ref).dV}{T(ref)^2\int \epsilon(ref).dV}\f$
    def get_t2_emis(self, ref):      
        """
        t2(emissivity) integrated on the volume, weigthed by the emissivity
        param:
            ref [int or str] line reference
        return:
            [float]
        """  
        return self.vol_mean((self.te - self.get_T0_emis(ref)) ** 2., self.get_emis(ref)) / self.get_T0_emis(ref) ** 2

    ## Return the wavelength/energy/frequency array
    def get_cont_x(self, unit='Ryd'):
        """
        param:
            unit : one of ['Ryd','eV','Ang','mu','cm-1','Hz']
        return:
            continuum X: wavelength, energys, wv number, or frequency
        """
        if 'Cont_nu' in self._res['cont'].dtype.names:
            hnu = self._res['cont']['Cont_nu']
        elif 'Cont__nu' in self._res['cont'].dtype.names:
            hnu = self._res['cont']['Cont__nu']
        else:
            self.log_.warn('Hnu NOT defined in the continuum', calling = self.calling)
            return None
        if unit == 'Ryd':
            to_return = hnu
        elif unit == 'eV':
            to_return = hnu * pc.CST.RYD_EV
        elif unit == 'Ang':
            to_return = pc.CST.RYD_ANG / hnu
        elif unit == 'mu':
            to_return = pc.CST.RYD_ANG / hnu / 1e4
        elif unit == 'cm-1':
            to_return = hnu * pc.CST.RYD
        elif unit == 'Hz':
            to_return = hnu * pc.CST.RYD * pc.CST.CLIGHT
        elif unit == 'GHz':
            to_return = hnu * pc.CST.RYD * pc.CST.CLIGHT / 1e9
        else:
            self.log_.warn("Unit must be one of: ['Ryd','eV','Ang','mu','cm-1','Hz']", calling = self.calling)
            to_return = None
        return to_return

    ## Return the continuum flux (stellar or nebular, depending on cont parameter
    def get_cont_y(self, cont='incid', unit='es', dist_norm='at_earth'):
        """
        param:
            cont : one of ['incid','trans','diffout','ntrans','reflec']
            unit : one of ['esc', 'ec3','es','esA','esAc','esHzc','Jy','Q', 'Wcmu', 'phs', 'phsmu']
            dist_norm : one of ['at_earth', 'r_out', a float for a distance in cm]
        return:
            continuum flux or intensity
        """

        """ First define which of the 5 continua will be return """
        if cont == 'incid':
            cont1 = self._res['cont']['incident'].copy()
        elif cont == 'trans':
            cont1 = self._res['cont']['trans'].copy()
        elif cont == 'diffout':
            cont1 = self._res['cont']['DiffOut'].copy()
        elif cont == 'ntrans':
            cont1 = self._res['cont']['net_trans'].copy()
        elif cont == 'reflec':
            cont1 = self._res['cont']['reflec'].copy()
        else:
            self.log_.warn("cont must be one of: ['incid','trans','diffout','ntrans','reflec']", calling = self.calling)
            cont1 = None
        
        inner_surface = 4. * np.pi * self.r_in ** 2.
        if int(self.cloudy_version_major) >= 17:
            cont1 /= inner_surface
        """ Define the continuum depending on the unit """
        if unit not in ('es', 'esA', 'esHz', 'Q', 'phs', 'phsmu'):
            if self.distance is not None:
                if dist_norm == 'at_earth':
                    dist_fact = (self.r_in / (self.distance * pc.CST.KPC)) ** 2.
                elif dist_norm == 'r_out':
                    dist_fact = (self.r_in / self.r_out_cut) ** 2.
                else:
                    try:
                        dist_fact = (self.r_in / dist_norm) ** 2.
                    except:
                        self.log_.error('{0} is not a valid dist parameter.'.format(dist_norm), calling = 'CloudyModel.get_cont_y')                        
            else:
                self.log_.error('No distance set to compute cont_y', calling = self.calling)
     
        if unit == 'es':
            """ erg.s-1 """            
            to_return = cont1 * inner_surface
        elif unit == 'esA':
            """erg.s-1.A-1"""
            to_return = cont1 / self.get_cont_x(unit='Ang') * inner_surface
        elif unit == 'esHz':
            """erg.s-1.Hz-1"""
            to_return = cont1 / self.get_cont_x(unit='Hz') * inner_surface
        elif unit == 'esc':
            """ erg.s-1.cm-2 """
            to_return = cont1 * dist_fact
        elif unit == 'ec3':
            """ erg.cm-3 """
            to_return = cont1 * dist_fact / pc.CST.CLIGHT
        elif unit == 'ec3A':
            """ erg.cm-3.A-1 """
            to_return = cont1 / self.get_cont_x(unit='Ang') * dist_fact / pc.CST.CLIGHT
        elif unit == 'esAc':
            """ erg.s-1.cm-2.A-1 """
            to_return = cont1 / self.get_cont_x(unit='Ang') * dist_fact
        elif unit == 'esHzc':
            """ erg.s-1.cm-2.Hz-1 """
            to_return = cont1 / self.get_cont_x(unit='Hz') * dist_fact
        elif unit == 'WmHz':
            """Watt.m-2.Hz-1"""
            to_return = 1e-3 * cont1 / self.get_cont_x(unit='Hz') * dist_fact
        elif unit == 'Wcmu':
            """Watt.cm-2.microns-1"""
            to_return = 1e-7 * cont1 / self.get_cont_x(unit='mu') * dist_fact
        elif unit == 'WmA':
            """Watt.m-2.Angstrom-1"""
            to_return = 1e-3 * cont1 / self.get_cont_x(unit='Ang') * dist_fact
        elif unit == 'Jy':
            to_return = 1e23 * cont1 / self.get_cont_x(unit='Hz') * dist_fact
        elif unit == 'Q':
            """ Number of photons emitted per second above the energy hnu"""
            if pc.config.INSTALLED['scipy']:
                x = self.get_cont_x(unit='Ryd')
                y = cont1 / (x ** 2 * pc.CST.ECHARGE * 1e7 * pc.CST.RYD_EV) * inner_surface
                int_cum = np.zeros_like(y)
                int_cum[0:-1] = -1. * cumtrapz(y[::-1], x[::-1])[::-1]
                to_return = int_cum
            else:
                self.log_.warn('Scipy not found to integrate Q', calling = self.calling)
                to_return = None
        elif unit == 'phs':
            to_return = cont1 / (self.get_cont_x(unit='Ryd') * pc.CST.ECHARGE * 1e7 * pc.CST.RYD_EV) * inner_surface
        elif unit == 'phsmu':
            to_return = cont1 / (self.get_cont_x(unit='mu') * self.get_cont_x(unit='Ryd') * 
                                 pc.CST.ECHARGE * 1e7 * pc.CST.RYD_EV) * inner_surface
        else:
            self.log_.warn("unit must be one of: ['esc', 'ec3','es','esA','esAc','esHzc','WmHz','Wcmu','Jy','Q']",
                            calling = self.calling)
            to_return = None        
        return to_return

    ## get_G0 = integral(f_lambda . dlambda) Between lam_min and lam_max (Ang), normalized by norm, in unit of W.m-2 or erg.cm-3
    def get_G0(self, lam_min = 913, lam_max = 1e8, dist_norm = 'r_out', norm = 1.6e-6, unit = 'Wm'):
        """
        Normalisation from Habing 1968: 1.6e-6 erg.cm-2.s-1
        """
        lam = self.get_cont_x(unit = 'Ang')
        lam_range = (lam > lam_min) & (lam < lam_max)
        if unit == 'Wm':  
            G0 = abs(np.trapz(y = self.get_cont_y('ntrans', 'WmA', dist_norm = dist_norm)[lam_range], x = lam[lam_range]))/norm
        elif unit == 'ec3':
            G0 = abs(np.trapz(y = self.get_cont_y('ntrans', 'ec3A', dist_norm = dist_norm)[lam_range], x = lam[lam_range]))/norm
        return G0

    def _get_r_out_cut(self):    
        return self.__r_out_cut
    
    def _set_r_out_cut(self, value):
        if self.n_zones_full > 1:
            if value >= self.r_in:
                self.__r_out_cut = value         
            else:
                self.log_.warn('r_out_cut ({0:e}) cannot be lower than r_min ({1:e})'.format(value, self.r_in), calling = self.calling)
                self.__r_out_cut = self.radius_full[1]
        else:
            if value != self.r_out:
                self.__r_out_cut = self.r_out     
                self.log_.warn('r_out_cut ({0:e}) cannot be != than r_out ({1:e})'.format(value, self.r_in), calling = self.calling)
            else:
                self.__r_out_cut = value   
            
    _r_out_cut_doc = 'User defined outer radius of the nebula. For example: r_out_cut = m.radius[m.zones[m.ionic["H"][1] < 0.2][0]]'
    ## User defined outer radius of the nebula [float] (cm). 
    # For example: r_out_cut = m.radius[m.zones[m.ionic['H'][1] < 0.2][0]].
    # It is used to define r_range and thus all the radial properties of the nebula
    r_out_cut = property(_get_r_out_cut, _set_r_out_cut, None, _r_out_cut_doc)

    def _get_r_in_cut(self):    
        return self.__r_in_cut
    
    def _set_r_in_cut(self, value):
        if self.n_zones_full > 1:
            if value >= self.r_in:
                self.__r_in_cut = value
            else:
                self.log_.warn('r_in_cut ({0:e}) cannot be lower than r_min ({1:e})'.format(value, self.r_in), calling = self.calling)
                self.__r_in_cut = self.r_in[0]
        else:
            if value != self.r_in:  
                self.log_.warn('r_in_cut ({0:e}) cannot be != than r_min ({1:e})'.format(value, self.r_in), calling = self.calling)
                self.__r_in_cut = self.r_in
            else:
                self.__r_in_cut = value
    ## User defined inner radius of the nebula [float] (cm)
    r_in_cut = property(_get_r_in_cut, _set_r_in_cut, None, 'User defined inner radius of the nebula.')

    ## Boolean array defining the range used for the radial parameters (such as ne, ionic, integrals, etc)
    # Defined by r_in_cut and r_out_cut
    @property
    def r_range(self):
        """ boolean array. True for r_in_cut < radius < r_out_cut, False elsewhere.
        Used in most of the parameter calls such as te, get_emis, get_ionic, etc"""
        if self.n_zones_full > 1:
            self.__r_range = (self.radius_full <= self.r_out_cut) & (self.radius_full >= self.r_in_cut)
            return self.__r_range
        elif self.n_zones_full == 1:
            return 0

    def _get_H_mass_cut(self):
        return self.__H_mass_cut
    
    def _set_H_mass_cut(self, value):
        if value > self.H_mass_full[1]:
            self.r_out_cut = self.radius_full[self.H_mass_full <= value][-1]
            self.__H_mass_cut = self.H_mass
        else:
            self.log_.warn('H_mass_cut must be greater than minimal value', calling = self.calling)
            
    H_mass_cut = property(_get_H_mass_cut, _set_H_mass_cut, None, None)

    def _get_Hbeta_cut(self):
        return self.__Hbeta_cut
    
    def _set_Hbeta_cut(self, value):
        if value > self.Hbeta_full[1]:
            self.r_out_cut = self.radius_full[self.Hbeta_full <= value][-1]
            self.__Hbeta_cut = self.Hbeta
        else:
            self.log_.warn('Hbeta_cut must be greater than minimal value', calling = self.calling)

    Hbeta_cut = property(_get_Hbeta_cut, _set_Hbeta_cut, None, None)

    ## Hp_mass = \f$ \int m_H.n_{H^+}.ff.dV\f$ [solar mass]
    @property        
    def Hp_mass(self):
        """Return the H+ mass of the nebula in solar mass"""
        try:
            return self.vol_integ(self.nH * self.get_ionic('H',1)) * pc.CST.HMASS / pc.CST.SUN_MASS
        except:
            self.log_.warn('H+ mass_tot not available', calling = self.calling)
            return None

    ## H0_mass = \f$ \int m_H.n_{H^0}.ff.dV\f$ [solar mass]        
    @property        
    def H0_mass(self):
        """Return the H0 mass of the nebula in solar mass"""
        try:
            return self.vol_integ(self.nH * self.get_ionic('H',0)) * pc.CST.HMASS / pc.CST.SUN_MASS
        except:
            self.log_.warn('H0 mass_tot not available', calling = self.calling)
            return None
        
    ## H0_mass = \f$ \int m_H.n_H.ff.dV\f$ [solar mass]                
    @property        
    def H_mass(self):
        """Return the H mass of the nebula in solar mass"""
        try:
            return self.vol_integ(self.nH) * pc.CST.HMASS / pc.CST.SUN_MASS
        except:
            self.log_.warn('H mass_tot not available', calling = self.calling)
            return None
        
    ## Hbeta = \f$ \int Hbeta.n_H.ff.dV\f$ [solar mass]                
    @property        
    def Hbeta(self):
        """Return the intensity of Hbeta"""
        try:
            return self.get_emis_vol('H__1__4861A')
        except:
            self.log_.warn('H beta not available', calling = self.calling)
            return None
        
    
    ## Mean Temperature \f$T0=\frac{\int T_e.n_e.n_H.ff.dV}{\int n_e.n_H.ff.dV}\f$
    @property        
    def T0(self):
        try:
            return self.vol_mean(self.te, self.nenH)
        except:
            self.log_.warn('T0 not available', calling = self.calling)
            return None
        
    ## t2 a la Peimbert \f$t^2=\frac{\int (T_e-T0)^2.n_e.n_H.ff.dV}{T0^2 \int n_e.n_H.ff.dV}\f$
    @property        
    def t2(self):
        try:
            return self.vol_mean((self.te - self.T0) ** 2, self.nenH) / self.T0 ** 2
        except:
            self.log_.warn('t2 not available', calling = self.calling)
            return None

    ## Hb_SB = I\f$_\beta / (Rout^2 * pi * 206265.^2)\f$
    def get_Hb_SB(self):
        """
        Hbeta surface brightness:
        Returns Ibeta / (Rout**2 * pi * 206265.**2)
        """
        if 'H__1__4861A' in self.emis_labels:
            return self.get_emis_vol('H__1__4861A') / (self.r_out_cut**2 * np.pi * 206265.**2)
        elif 'H__1_486136A' in self.emis_labels:
            return self.get_emis_vol('H__1_486136A') / (self.r_out_cut**2 * np.pi * 206265.**2)
        else:
            self.log_.warn('Hbeta emissivity not in emis file', calling = self.calling + '.get_Hb_SB')
    
    def get_EW(self, label, lam0, lam_inf, lam_sup):
        """
        Equivalent Width:
        Returns -lam0 * I(label) / continuum(lam0)
        where continuum(lam0) is estimated by looking for the minimum of the net transmited continuum between
        lam_inf and lam0 on one side, and lam0 and lam_sup on the other side, and meaning them.
        In case of steep continuum or absorbtion lines, the mean continuum is underestimated.
        """
        if type(label) in (type(()), type([])):
            res = 0
            for lab in label:
                res += self.get_EW(lab, lam0, lam_inf, lam_sup)
                return res
        if label in self.emis_labels:
            mask_low = (self.get_cont_x('Ang') < lam0) & (self.get_cont_x('Ang') > lam_inf)
            I_low = np.min(self.get_cont_y('ntrans', 'esA')[mask_low])
            mask_high = (self.get_cont_x('Ang') > lam0) & (self.get_cont_x('Ang') < lam_sup)
            I_high = np.min(self.get_cont_y('ntrans', 'esA')[mask_high])
            return -self.get_emis_vol(label) / np.mean((I_low, I_high))
        else:
            self.log_.warn('{} line not in emis file'.format(label), calling = self.calling + '.get_EW')
        return None

    def get_EW2(self, label, lam0, lam_inf, lam_sup, plot=False):
        """
        Equivalent Width:
        Returns -lam0 * I(label) / continuum(lam0)
        where continuum(lam0) is estimated by fitting the continuum between [lam_inf, lam0*0.99] and [lam0*1.01, lam_sup]
        and applying the fit to lam0.
        Of course, if strong emission/absorbtion lines are included in this domain, the results is not correct
        """
        if type(label) in (type(()), type([])):
            res = 0
            for lab in label:
                res += self.get_EW2(lab, lam0, lam_inf, lam_sup)
                return res
        if label in self.emis_labels:
            mask_low = (self.get_cont_x('Ang') < lam0*0.99) & (self.get_cont_x('Ang') > lam_inf)
            mask_high = (self.get_cont_x('Ang') > lam0*1.01) & (self.get_cont_x('Ang') < lam_sup)
            mask = mask_low | mask_high
            fit = np.polyfit(self.get_cont_x('Ang')[mask], self.get_cont_y('ntrans', 'esA')[mask], deg=1)
            if plot:
                f, ax = plt.subplots()
                ax.plot(self.get_cont_x('Ang'), self.get_cont_y('ntrans', 'esA'))
                ax.plot(self.get_cont_x('Ang'), np.polyval(fit, self.get_cont_x('Ang')))
                ax.set_xlim((lam_inf, lam_sup))
            return -self.get_emis_vol(label) / np.polyval(fit, lam0)
        else:
            self.log_.warn('{} line not in emis file'.format(label), calling = self.calling + '.get_EW')
            return None

    ## Hb_EW = -\f$\lambda_\beta$ x I$_\beta^{line}$ / $\lambda.F_\beta^{cont}\f$
    def get_Hb_EW(self):
        """
        Hbeta Equivalent Width:
        Returns -4861 * I(H__1__4861A) / continuum(4860)
        where continuum(4860) is estimated by looking for the minimum of the net transmited continuum between
        4560 and 4860 on one side, and 4860 and 5160 on the other side, and meaning them.
        """
        if 'H__1__4861A' in self.emis_labels:
            return self.get_EW('H__1__4861A', 4861, 4560, 5160)
        elif 'H__1_486136A' in self.emis_labels:
            return self.get_EW('H__1_486136A', 4861, 4560, 5160)

    ## Ha_EW = -\f$\lambda_\alpha$ x I$_\alpha^{line}$ / $\lambda.F_\alpha^{cont}\f$
    def get_Ha_EW(self):
        """
        Halpha Equivalent Width:
        Returns -6563 * I(H__1__6563A) / continuum(6563)
        where continuum(6563) is estimated by looking for the minimum of the net transmited continuum between
        6260 and 6560 on one side, and 6560 and 6860 on the other side, and meaning them.
        """
        if 'H__1__6563A'in self.emis_labels:
            return self.get_EW('H__1__6563A', 6563., 6260, 6860)
        elif 'H__1_656285A'in self.emis_labels:
            return self.get_EW('H__1_656285A', 6563., 6260, 6860)
            
    ## is_valid_ion(elem, ion) return True if elem, ion is available in get_ionic.
    def is_valid_ion(self, elem, ion):        
        """
        param:
            elem [str] element
            ion [str or int] ionic state of ion
        return:    
            [boolean] True if elem,ion has value for get_ionic(elem, ion)
        """
        to_return = False
        if elem in list(self.ionic_names.keys()):
            if (ion >= 0) & (ion < self.n_ions[elem]):
                to_return = True
        return to_return  
   
    def emis_from_pyneb(self, emis_labels = None, atoms = None):
        """
        change the emissivities using PyNeb.
        emis_labels: list of line to be changed. If unset, all the lines will be changed. You may generate emis_labels
            this way (here to select only S lines): S_labels = [emis for emis in CloudyModel.emis_labels if emis[0:2] == 'S_']
        atoms: dictionary of pyneb.Atom objects to be used. If unset, all the atoms will be build 
            using pyneb. This allows the user to mix atomic dataset by creating atoms outside CloudyModel. Keys
            of the dictionnary pointing to None instaed of an Atom will not change the corresponding emissivities.
        """
        if not pc.config.INSTALLED['PyNeb']:
            self.log_.error('PyNeb not availabel', calling = self.calling + 'emis_from_pyneb')
            return
        if emis_labels is None:
            emis_labels = self.emis_labels
        if atoms is None:
            atoms = {}
        dic = cloudy2pyneb()
        for line in emis_labels:
            if line in dic:
                ion = dic[line][0]
                elem = ion[0:-1]
                spec = int(ion[-1])
                wave = dic[line][1]
                if ion not in atoms and elem not in ('H', 'He'):
                    try:
                        atoms[ion] = pyneb.Atom(elem, spec)
                    except:
                        pass
                if ion in atoms:
                    if self.is_valid_ion(elem, spec - 1) and atoms[ion] is not None:
                        emis = atoms[ion].getEmissivity(self.te_full, self.ne_full, wave = wave, product = False) * \
                            self.ionic_full[elem][spec - 1] * self.ne_full * self.nH_full * 10**self.abund[elem]
                        self.emis_full[self._i_emis(line)] = emis
                        pc.log_.message('emissivity for {0} changed from PyNeb'.format(line), calling = self.calling)
                    else:
                        pc.log_.warn('ion {0} not in Cloudy outputs'.format(ion), calling = self.calling)
                else:
                    pc.log_.warn('ion {0} not in PyNeb'.format(ion), calling = self.calling)
            else:
                pc.log_.warn('line {0} not in Cloudy2PyNeb'.format(line), calling = self.calling)
    
    def add_emis_from_pyneb(self, new_label, pyneb_atom, label=None, wave=None):
        
        """
        Add a new line emissivity using PyNeb.
        new_label: name of the new emission line
        pyneb_atom: a Atom or RecAtom PyNeb object
        label or wave: identifier of the transition in the PyNeb object
        example:
            M.add_emis_from_pyneb('O__2R_4639', O2, label='4638.86')

        """
        
        new_emis_full = np.zeros((len(self.emis_labels)+1, self.n_zones_full))
        new_emis_full[:-1, :] = self.emis_full
        if type(pyneb_atom) is pyneb.RecAtom:
            spec = pyneb_atom.spec
        else:
            spec = pyneb_atom.spec - 1
        
        if wave is not None:
            new_emis_full[-1, :] = pyneb_atom.getEmissivity(self.te_full, self.ne_full, wave = wave, product = False) * \
                                   self.ionic_full[pyneb_atom.elem][spec] * self.ne_full * \
                                   self.nH_full * 10**self.abund[pyneb_atom.elem]
        else:
            new_emis_full[-1, :] = pyneb_atom.getEmissivity(self.te_full, self.ne_full, label = label, product = False) * \
                                   self.ionic_full[pyneb_atom.elem][spec] * self.ne_full * \
                                   self.nH_full * 10**self.abund[pyneb_atom.elem]
        new_emis_labels = np.zeros(len(self.emis_labels)+1, dtype=self.emis_labels.dtype)
        new_emis_labels[:-1] = self.emis_labels
        new_emis_labels[-1] = new_label
        
        self.emis_full = new_emis_full
        self.emis_labels = new_emis_labels
        if self.cloudy_version_major > 16:
            self.emis_labels_17 = new_emis_labels
        else:
            self.emis_labels_13 = new_emis_labels
    
    def plot_spectrum(self, xunit='eV', cont='ntrans', yunit='es', ax=None, 
                      xlog=True, ylog=True, **kargv):
        """
        plot the spectrum of the model.
        parameters:
            - xunit ['eV']
            - cont ['ntrans']
            - yunit ['es']
            - ax
            - xlog [True]
            - ylog [True]
            - **kargv passed to the plot.
        """
        if not pc.config.INSTALLED['plt']:
            pc.log_.error('Matplotlib not available', calling = self.calling)
        if ax is None:
            return_ax = True
            fig, ax = plt.subplots()
        else:
            return_ax = False
        if xlog and ylog:
            ax.loglog(self.get_cont_x(unit=xunit), self.get_cont_y(cont=cont, unit=yunit), **kargv)
        elif xlog:
            ax.semilogx(self.get_cont_x(unit=xunit), self.get_cont_y(cont=cont, unit=yunit), **kargv)
        elif ylog:
            ax.semilogy(self.get_cont_x(unit=xunit), self.get_cont_y(cont=cont, unit=yunit), **kargv)
        else:
            ax.plot(self.get_cont_x(unit=xunit), self.get_cont_y(cont=cont, unit=yunit), **kargv)
        ax.set_xlabel(xunit)
        ax.set_ylabel(yunit)
        if return_ax:
            return ax
                        
    def print_lines(self, ref = None, norm = None, at_earth = False, use_emis = True):
        """
        Print line intensities
        param:
            at_earth [boolean] if True, divide the intensity by 4.pi.distance^2
            ref [int or str] reference of a line (if None, all lines are printed)
            norm [int or str] reference of a line to normalize the intensities
            use_emis [boolean] use integral of emissivity (default) or line intensities
        """      
        if ref != None:
            if norm is not None:
                e_norm = self.get_emis_vol(norm, at_earth = at_earth)
            else:
                e_norm = 1.
            print('{0} {1:e}'.format(ref, self.get_emis_vol(ref, at_earth = at_earth)/e_norm)) 
        else:
            if use_emis:
                for em in self.emis_labels:
                    self.print_lines(em, norm=norm, at_earth = at_earth, use_emis = use_emis)
            else:
                for label, intensity in zip(self.line_labels, self.lines):
                    print('{0} {1:e}'.format(label, intensity))
                
    def print_stats(self):
        print(' Name of the model: {0}'.format(self.model_name))
        try:
            print((' R_in (cut) = {0.r_in:.3e} ({0.r_in_cut:.3e}), R_out (cut) = {0.r_out:.3e} ({0.r_out_cut:.3e})'.
                  format(self)))
        except:
            pass
        try:
            print(' H+ mass = {0.Hp_mass:.2e}, H mass = {0.H_mass:.2e}'.format(self))
        except:
            pass
        try:
            print(' T0 = {0.T0:.0f}, t2 = {0.t2:.1e}, <nH> = {1:.2}'.format(self, self.get_nH()))
        except:
            pass
        
        try:
            print(' <H+/H> = {0:.2f}, <He++/He> = {1:.2f}, <He+/He> = {2:.2f}'.format(self.get_ab_ion_vol_ne('H',1), 
                                                                         self.get_ab_ion_vol_ne('He',2), 
                                                                         self.get_ab_ion_vol_ne('He',1)))
        except:
            pass
        try:
            print(' <O+++/O> = {0:.2f}, <O++/O> = {1:.2f}, <O+/O> = {2:.2f}'.format(self.get_ab_ion_vol_ne('O',3), 
                                                                     self.get_ab_ion_vol_ne('O',2), 
                                                                     self.get_ab_ion_vol_ne('O',1)))
        except:
            pass
        try:
            print(' <N+++/O> = {0:.2f}, <N++/O> = {1:.2f}, <N+/O> = {2:.2f}'.format(self.get_ab_ion_vol_ne('N',3), 
                                                                     self.get_ab_ion_vol_ne('N',2), 
                                                                     self.get_ab_ion_vol_ne('N',1)))
        except:
            pass
        try:
            print(' T(O+++) = {0:.0f}, T(O++) = {1:.0f}, T(O+) = {2:.0f}'.format(self.get_T0_ion_vol_ne('O',3), 
                                                                     self.get_T0_ion_vol_ne('O',2), 
                                                                     self.get_T0_ion_vol_ne('O',1)))
        except:
            pass
        try:
            print(' <ne> = {0:.0f},  <nH> = {1:.0f}, T0 = {2.T0:.0f}, t2={2.t2:.4f}'.format(self.vol_mean(self.ne), 
                                                                                            self.vol_mean(self.nH), self))
        except:
            pass
        try:
            print(' <log U> = {0.log_U_mean:.2f}'.format(self))
        except:
            pass
        
    def __repr__(self):
        return "{0.info}".format(self)
    
    def __str__(self):
        return "{0.info}".format(self)
    
## @include copyright.txt
def load_models(model_name = None, mod_list = None, n_sample = None, verbose = False, **kwargs):
    """
    Return a list of CloudyModel correspondig to a generic name
    
    Parameters:
        - model_name:    generic name. The method is looking for any "model_name*.out" file.
        - mod_list:    in case model_name=None, this is the list of model names (something.out or something)
        - n_sample:    randomly select n_sample from the model list
        - verbose:    print out the name of the models read
        - **kwargs:    arguments passed to CloudyModel
    """
    
    if model_name is not None:
        mod_list = glob.glob(model_name + '*.out') 
    if mod_list is None or mod_list == []:
        pc.log_.error('No model found', calling = 'load models')
        return None
    if n_sample is not None:
        if n_sample > len(mod_list):
            pc.log_.error('less models {0:d} than n_sample {1:d}'.format(len(mod_list), n_sample), 
                          calling = 'load models')
            return None
        mod_list = random.sample(mod_list, n_sample)
    m = []
    for outfile in mod_list:
        if outfile[-4::] == '.out':
            model_name = outfile[0:-4]
        else:
            model_name = outfile
        cm = CloudyModel(model_name, **kwargs)
        if not cm.aborted:
            m.append(cm)
        if verbose:
            print('{0} model read'.format(outfile[0:-4]))
    pc.log_.message('{0} models read'.format(np.size(mod_list)), calling = 'load_models')
    return m 

## @include copyright.txt

class CloudyInput(object):
    """
    Object used to create and write input file for Cloudy code.
    """
    ## CloudyInput object
    def __init__(self, model_name = None):
        """
        - model_name : name of the model. Used to name the input file and all the output files.
        The other parameters of the model are set using the methods
        """
        self.log_ = pc.log_
        self.calling = 'CloudyInput'
        self.model_name = model_name
        self.init_all()
    
    def init_all(self):
        self.set_save_str()
        self.set_other()
        self.set_emis_tab()
        self.set_star()
        self.set_radius()
        self.set_cste_density()
        self.set_abund()
        self.set_grains()
        self.set_stop()
        self.set_line_file()
        self.set_distance()
        self.set_heat_cooling()
        self.set_fudge()
        self.set_C3D_comment()
        self.set_comment()
        self.import_file()
        self._save_list_elems = pc.config.SAVE_LIST_ELEMS
        self.save_list = pc.config.SAVE_LIST
        self._save_list_grains = pc.config.SAVE_LIST_GRAINS
        self.cloudy_version = None
        
    def set_save_str(self, save = 'save'):
        """
        This determine if "save" (default) or "punch" is used in the input file
        Parameter:
            - save:    "save" (default) or "punch". If another value is sent, "save" is used.
        """
        if save not in ['save', 'punch']:
            self.log_.warn('save_str must be "save" or "punch". Set to "save"', calling = self.calling)
            self.save_str = 'save'
        else:
            self.save_str = save
        
    def set_radius(self, r_in=None, r_out=None):
        """
        param:
            r_in [float] (log cm)
        optional:
            r_out [float] (log cm)
        """
        if r_in is None:
            self._radius = None
            return None
        if r_out is None:
            self._radius = 'radius = {0:.3f}'.format(r_in)
        else:
            self._radius = 'radius = {0:.3f} {1:.3f}'.format(r_in, r_out)

    def set_BB(self, Teff=None, lumi_unit=None, lumi_value=None):
        """
        Add a Black Body as SED.
        Parameters:
            - Teff: Effective temeprature, in K.
            - lumi_unit:    a Cloudy unit for the luminosity (e.g 'q(H)', 'total luminosity', 'logU')
            - lumi_value:    the value of the luminosity
        """
        self.set_star(SED = 'Blackbody',  SED_params = Teff, lumi_unit = lumi_unit, lumi_value=lumi_value)
        
    def set_star(self, SED = None, SED_params = None, lumi_unit=None, lumi_value=None):
        """
        Add a table to the SED.
        Parameters:
            - SED:    The SED description, like "table Rauch"
            - SED_params:    parameter(s) for the SED. May be a list or a tuple, of strings or floats
                                or a simple string with everything in it.
        """
        if SED is None:
            self._SEDs = []
        else:
            params_str = '{0}'
            if type(SED_params) is type([]) or type(SED_params) is type(()):
                for i, SED_param in enumerate(SED_params):
                    if type(SED_param) is type(''):
                        params_str += ' {{1[{0}]}}'.format(i)
                    else:
                        params_str += ' {{1[{0}]:f}}'.format(i)
            elif type(SED_params) is type(''):
                params_str += ' {1}'
            else:
                params_str += ' {1:f}'
            shape = params_str.format(SED, SED_params)
            lumi = '{0} = {1:.3f}'.format(lumi_unit, lumi_value)
            self._SEDs.append((shape, lumi))
        
    def set_cste_density(self, dens = None, ff = None):
        """
        Set the density of the model to a constant value
        Parameters:
            - dens:    the density (in log(cm-3))
            - ff:    filling factor (unused if None, default value)
        """
        if dens is None:
            self._density = None
            self._filling_factor = None
            return None
        self._density = 'hden = {0:.3f}'.format(dens)
        if ff is not None:
            if type(ff) == type(()) or type(ff) == type([]):
                self._filling_factor = 'filling factor = {0[0]:f} {0[1]:f}'.format(ff)
            else:
                self._filling_factor = 'filling factor = {0:f}'.format(ff)
        else:
            self._filling_factor = 'filling factor = 1.0'
        
    def set_dlaw(self, dlaw_params, ff = None):
        """
        Define the user-define density law.
        Parameters:
            - dlaw_params may beof type: 1.4, '1.4, 5.6, 7e45' or (1, 2, 4.5)
            - ff: filling factor
        """
        if type(dlaw_params) != type(()) and type(dlaw_params) != type([]):
            dlaw_params = [dlaw_params]
        self._density = 'dlaw ' + ' , '.join([str(dlaw_param) for dlaw_param in dlaw_params])
        if ff is not None:
            if type(ff) == type(()) or type(ff) == type([]):
                self._filling_factor = 'filling factor = {0[0]:f} {0[1]:f}'.format(ff)
            else:
                self._filling_factor = 'filling factor = {0:f}'.format(ff)
        else:
            self._filling_factor = 'filling factor = 1.0'

    def set_fudge(self, fudge_params = None):
        """
        Define a user-defined fudge parameter.
        
        Parameter:
            - fudge_params: may be: 1.4, '1.4, 5.6, 7e45' or (1, 2, 4.5)
        """
        if fudge_params is None:
            self._fudge = None
            return None
        elif type(fudge_params) != type(()) and type(fudge_params) != type([]):
            fudge_params = [fudge_params]
        self._fudge = 'fudge factors ' + ' , '.join([str(fudge_param) for fudge_param in fudge_params])

    def set_sphere(self, sphere = True):
        """
        Set the sphere parameter if True, unset it otherwise. 
        """
        if sphere:
            self._input['sphere'] = 'sphere'
        else:
            if 'sphere' in self._input:
                del self._input['sphere']
            
    def set_iterate(self, n_iter = None, to_convergence = False):
        """
        Set the iterate parameter.
        Parameter:
            - n_iter: If None, set the iterate parameter to "iterate" in the Cloudy input file,
                if ==0, unset the iterate (nothing will be printed), otherwise set iterate to the
                value of n_iter.
            - to_convergence [False]: If True, iterate to convergence is printed out. 
                n_iter without effect then
        """
        if n_iter is None:
            self._input['iterate'] = 'iterate'
        elif n_iter == 0:
            if 'iterate' in self._input:
                del self._input['iterate']
        else:
            self._input['iterate'] = 'iterate {0:d}'.format(n_iter)
        if to_convergence:
            self._input['iterate'] = 'iterate to convergence'

    def set_grains(self, grains = None):
        """
        Append grains to the list.
        Parameter:
            - grains:    if None, reset the grains list, otherwise append the value of the parameter to the list.
        """
        if grains is None:
            self._grains = []
        else:
            if type(grains) == type(()) or type(grains) == type([]):
                for grain in grains:
                    self._grains.append(grain)
            else:
                self._grains.append(grains)
    
    def set_stop(self, stop_criter = None):
        """
        Append a stopping criterium to the list.
        Parameters:
            - stop:    if None, the list is reset, otherwise the value of the parameter is append to the list
                may be a list or a tuple of criteria.
        """
        if stop_criter is None:
            self._stop = []
        else:
            if type(stop_criter) == type(()) or type(stop_criter) == type([]): 
                for criter in stop_criter:
                    self._stop.append(criter)
            else:
                self._stop.append(stop_criter)
    
    def read_emis_file(self, emis_file, N_char=12):
        """
        Define the name of the file containing the labels for the list of emissivities to output
            in the .emis file
        """
        self._emis_tab = []
        try:
            with open(emis_file, 'r') as f:
                self._emis_tab = [row[0:N_char] for row in f]
        except:
            pc.log_.warn('File {0} for emis lines not accesible'.format(emis_file))
            
    def set_emis_tab(self, emis_tab_str = None):
        """
        Accept a list of line labels that will be used as:
        
        save last lines emissivity ".emis"
            *** enumeration of the elements of the list ***
        end of lines

        """
        if emis_tab_str is None:
            self._emis_tab = []
        self._emis_tab = emis_tab_str
            
    def import_file(self, file_ = None):
        """
        Import a file that will be append to the input file.
        """
        if file_ is None:
            self._imported = []
            return None
        try:
            with open(file_) as f:
                self._imported = f.readlines()
        except:
            pc.log_.warn('File {0} for not accesible'.format(file_))
            
    def set_line_file(self, line_file = None, absolute=False):
        """
        Set a file name containing a list of lines.
        Is used in the input file as: 
        save last linelist ".lin" "***line_file***"
        """
        ##
        # @todo verify existence of the file
        self.line_file_absolute = absolute
        if line_file is None:
            self._line_file = None
            return None
        self._line_file = line_file

    def set_theta_phi(self, theta = None, phi = None):
        """
        Set the values of the theta and phi angles for the 3D models
        """
        if theta is None and phi is None:
            if 'theta' in self._input:
                del self._input['theta']
            if 'phi' in self._input:
                del self._input['phi'] 
            return None
        if theta is not None:
            self._input['theta'] = 'c C3D theta = {0:.2f}'.format(theta)
        if phi is not None:
            self._input['phi'] = 'c C3D phi = {0:.2f}'.format(phi)

    ## define the abundances
    def set_abund(self, predef = None, elem = None, value = None, nograins = True, 
                  ab_dict = None, metals=None, metalsgrains=None):
        """
        Defines the abundances.
        Parameters:
            - predef : one of the Cloudy predefined abundances (e.g. "ism", "hii region")
            - elem and value: used to set one abundance, e.g, elem = 'O', value = -4.5
            - nograins: Boolean value
            - ab_dict: dictionnary of elem and values.
            - metals:    value by which all the metals are multiplied
        """
        if predef is None and elem is None and ab_dict is None:
            self._abund = {}
            self._abund_predef = None
            self._nograins = True
            self._metals = None
            self._metalsgrains = None
            return None
        
        if ab_dict is not None:
            for sym in ab_dict:
                if sym in SYM2ELEM:
                    self._abund[SYM2ELEM[sym]] = ab_dict[sym]
                else:
                    self.log_.warn('unkown symbol : {0}'.format(sym), calling = self.calling)
        elif elem is not None:
            self._abund[SYM2ELEM[elem]] = value
        elif predef is not None:
            self._abund_predef = predef
        self._metals = metals
        self._metalsgrains = metalsgrains
        self._nograins = nograins
        
    def set_other(self, other_str = None):
        """
        Define any other command line to be added to the Cloudy input file
        Parameter:
            - other_str: if None, reset the list, otherwise, append its value to the list
        """
        if other_str is None:
            self._input = {}
            self._other_cnt = 0
            return None
        if type(other_str) is type(()) or type(other_str) is type([]):
            for o_str in other_str:
                self.set_other(o_str)
        else:        
            if other_str != '':
                self._other_cnt += 1
                self._input['other_{0:d}'.format(self._other_cnt)] = other_str
        
    def set_comment(self, comment = None):
        """
        Add special comment that will be added in the input file in the form of: C ** comment
         Parameter:
            - comment: if None, reset the list, otherwise, append its value to the list
        
        """
        if comment is None:
            self._comments = []
            return None
        if type(comment) is type(()) or type(comment) is type([]):
            for com in comment:
                self.set_comment(com)
        else:        
            self._comments.append('C ** {0}'.format(comment))    
    
    def set_C3D_comment(self, comment = None):
        """
        Add special comment that will be added in the input file in the form of: C3D comment
         Parameter:
            - comment: if None, reset the list, otherwise, append its value to the list
        
        """
        if comment is None:
            self._C3D = []
            return None
        if type(comment) is type(()) or type(comment) is type([]):
            for com in comment:
                self.set_C3D_comment(com)
        else:        
            self._C3D.append('C3D {0}'.format(comment))
            
    def set_distance(self, dist = None, unit='kpc', linear = True):
        """
        Set the distance to the object.
        Parameters:
            - dist = float
            - unit = ('kpc', 'Mpc', 'parsecs', 'cm')
            - linear = boolean
        """
        if dist is None:
            self._distance = None
            return None
        if unit not in ('kpc', 'Mpc', 'parsecs', 'cm'):
            self.log_.error('Unknown distance unit: {0}'.format(dist), calling = self.calling)
        if unit == 'kpc':
            dist_pc = dist * 1e3
        elif unit == 'Mpc':
            dist_pc = dist * 1e6
        elif unit == 'cm':
            dist_pc = dist / pc.CST.PC
        if linear:
            linear_str = 'linear'
        else:
            linear_str = ''
        self._distance = 'distance = {0} parsecs {1}'.format(dist_pc, linear_str)
        
    def set_heat_cooling(self, cextra = None, hextra = None):
        if cextra is None:
            self._cextra = None
        else:
            self._cextra = cextra
        if hextra is None:
            self._hextra = None
        else:
            self._hextra = hextra
        
    def print_input(self, to_file = True, verbose = False):
        """
        This is the method to print the input file.
        Parameters:
            - to_file: Boolean. If True (default), print to the file defined as model_name + '.in'
            - verbose: Boolean. If True (not default), print to the standart output
        """
        if to_file:
            file_name = self.model_name+'.in' 
            f = open(file_name,'w')
        
        def this_print(s, eol = True):
            if s is None:
                self.log_.warn('"None" parameter not printed', calling = self.calling)
            else:
                to_print = s.strip()
                if verbose:
                    print(to_print)
                if to_file:
                    if eol: to_print += '\n'
                    f.write(to_print)
            
        this_print('////////////////////////////////////')
        this_print('title {0}'.format(self.model_name.split('/')[-1]))
        this_print('////////////////////////////////////')
        this_print('set punch prefix "{0}"'.format(self.model_name.split('/')[-1]))
        for SED in self._SEDs:
                this_print(SED[0])
                this_print(SED[1]) 
        if self._radius is not None:
            this_print(self._radius)
        this_print(self._density)
        if self._filling_factor is not None:
            this_print(self._filling_factor)
        if self._abund_predef is not None:
            if self._nograins:
                grains = 'no grains'
            else:
                grains = ''
            this_print('abundances {0} {1}'.format(self._abund_predef, grains))
        for elem in self._abund:
            this_print('element abundance {0} {1:.3f}'.format(elem, self._abund[elem]))
        for grain in self._grains:
            this_print('grains {0}'.format(grain))
        if self._metals is not None:
            this_print('metals {0}'.format(self._metals))
        if self._metalsgrains is not None:
            this_print('metals grains {0}'.format(self._metalsgrains))
        if self._distance is not None:
            this_print(self._distance)
        if self._fudge is not None:
            this_print(self._fudge)
        for key in self._input:
            this_print(self._input[key])
        for row in self._imported:
            this_print(row)
        for stop in self._stop:
            this_print('stop {0}'.format(stop))
        if self._cextra is not None:
            if len(self._cextra) == 2:
                this_print('cextra {0[0]} temp to the {0[1]} power'.format(self._cextra))
            else:
                self.log_.error('cextra needs 2', calling = self.calling)
        if self._hextra is not None:
            if len(self._hextra) == 2:
                this_print('Hextra {0[0]} depth {0[1]}'.format(self._hextra))
            elif len(self._hextra) == 3:
                this_print('Hextra {0[0]} depth {0[1]}, thickness {0[2]}'.format(self._hextra))
            else:
                self.log_.error('Hextra needs 2 or 3 parameters', calling = self.calling)
        for C3D in self._C3D:
            this_print(C3D)
        for com in self._comments:
            this_print(com)
        if self._line_file is not None:
            if self.line_file_absolute:
                absolute = 'absolute'
            else:
                absolute = ''
            this_print('{0} last linelist ".lin" "{1}" {2}'.format(self.save_str, self._line_file, absolute))
        for ext in self.save_list:
            this_print('{0} last {1} "{2}"'.format(self.save_str, ext[0], ext[1]))
        if self._nograins == False or self._grains != []:
            for ext in self._save_list_grains:
                this_print('{0} last {1} "{2}"'.format(self.save_str, ext[0], ext[1]))
        for ext in self._save_list_elems:
            this_print('{0} last element {1} "{2}"'.format(self.save_str, ext[0], ext[1]))
        if self._emis_tab is not None:
            this_print('{0} last lines emissivity ".emis"'.format(self.save_str))
            for emis in self._emis_tab:
                this_print(emis)
            this_print('end of lines')
                               
        if to_file:
            self.log_.message('Input writen in {0}'.format(file_name), calling = self.calling)
            f.close()
            
    def run_cloudy(self, dir_ = None, n_proc = 1, use_make = False, model_name = None, precom=""):
        """
        Method to run cloudy.
        Parameters:
            - dir_:        Directory where the model input files are
            - n_proc:      number of CPUs to run (default=1)
            - use_make:    if True (default), make is used. Otherwise Cloudy is run on one single model, 
                assuming that model_name.in exists
            - model_name:  if None, the models of this object is run, 
                if not None, used by: make name="model_name" or cloudy < model_name.in
            - precom: a string to put before Cloudy (e.g. "\nice 10")
        """
        if model_name is None:
            model_name = self.model_name
        run_cloudy(dir_ = dir_, n_proc = n_proc, use_make = use_make, model_name = model_name, precom=precom,
                   cloudy_version=self.cloudy_version)
    
    def print_make_file(self, dir_ = None):
        """
        Call pc.print_make_file. 
        Parameter:
            dir_:    if None, extract the string before the last / in the model_name. 
                Otherwise, use the value
        """
        if dir_ is None:
            dir_ = '/'.join(self.model_name.split('/')[0:-1])
        print_make_file(dir_ = dir_)
        
def print_make_file(dir_ = None):
    """
    Create a Makefile in the dir_ directory, using pc.config.cloudy_exe as executable for cloudy
    """
    makefile = open('{0}/Makefile'.format(dir_), 'w')
    txt_exe = 'CLOUDY = {0}\n'.format(pc.config.cloudy_exe)
    txt = """
SRC = $(wildcard ${name}*.in)
OBJ = $(SRC:.in=.out)

# Usage: make -j N name='NAME'
# N is the number of processors
# optional: NAME is a generic name, all models named NAME*.in will be run
# C. Morisset

all: $(OBJ)

%.out: %.in
\t-$(CLOUDY) < $< > $@
# Notice the previous line has TAB in first column
"""
    makefile.write(txt_exe)
    makefile.write(txt)
    makefile.close()

## Function used to run Cloudy on input files.                
def run_cloudy(dir_ = None, n_proc = 1, use_make = True, model_name = None, precom="", cloudy_version=None):
    """
    Run a (set of ) cloudy model(s)
    
    Parameters:
        - dir_:        Directory where the model input files are
        - n_proc:      number of CPUs to run (default=1)
        - use_make:    if True (default), make is used. Otherwise Cloudy is run on one single model, 
            assuming that model_name.in exists
        - model_name:  if not None, used by: make name="model_name" or cloudy < model_name.in
            if None and use_make, make will run any pending model
        - precom: a string to put before Cloudy (e.g. "\nice 10")
        - cloudy_version: one of the keys of pc.config.cloudy_dict, pointing to the location of the executable,
            e.g. '10.00' or '13.03'. If set to None (default), then pc.config.cloudy.exe is used
    """
    if dir_ is None:
        dir_ = '/'.join(model_name.split('/')[0:-1])
    if dir_ == '':
        dir_ = './'
    cloudy_exe = pc.config.cloudy_exe
    if cloudy_version is not None:
        if cloudy_version in pc.config.cloudy_dict:
            cloudy_exe = pc.config.cloudy_dict[cloudy_version]
    if use_make:
        to_run = 'cd {0} ; make -j {1:d}'.format(dir_, n_proc)
        if model_name is not None:
            to_run += ' name="{0}"'.format(model_name.split('/')[-1])
        stdin = None
        stdout = subprocess.PIPE
    else:
        if model_name is None:
            pc.log_.error('Model name must be set', calling = 'run_cloudy')
        else:
            to_run = 'cd {0} ; {1} {2}'.format(dir_, precom, cloudy_exe)
            stdin = open('{0}/{1}.in'.format(dir_, model_name.split('/')[-1]), 'r')
            stdout = open('{0}/{1}.out'.format(dir_, model_name.split('/')[-1]), 'w')   
    pc.log_.message('running: {0}'.format(to_run), calling = 'run_cloudy')
    proc = subprocess.Popen(to_run, shell=True, stdout=stdout, stdin = stdin)
    proc.communicate()
    if not use_make:
        stdin.close()
        stdout.close()
    pc.log_.message('ending: {0}'.format(to_run), calling = 'run_cloudy')

