import numpy as np
import pyCloudy as pc
from pyCloudy.utils.misc import execution_path
if pc.config.INSTALLED['plt']:
    import matplotlib.pyplot as plt

class RedCorr(object):
    """
    Reddening correction
    RC = RedCorr()
    
    """

    def __init__(self, E_BV = 0., R_V = 3.1, law = 'No correction', cHbeta = None, 
                 user_function = None):
        """
        Reddening correction tool.
        params:
            - E_BV [float] : differential extinction between bands B and V
            - R_V = AV/E_BV
            - law [str] : one of the defined laws (available with RedCorr.getLaws()) 
            - cHbeta : logarithmic extinction a Hbeta (prevalence on E_BV)
            - user_function X(wave, param): A user-defined function that accept 2 parameters : wavelength(s) in Angstrom 
            and an optional parameter and return X(lambda) = A(lambda)/E_BV = R.A(lambda)/AV. 
            The correction is : 10**(0.4*E_bv*X)
        example:
            RC = RedCorr(E_BV = 1.)
            RC.plot(laws = 'all')
        """
        
        self.log_ = pc.log_ 
        self.calling = 'RedCorr'
        self._laws_dict = {} # dictionnary pointing to a reddening function depending on the key
        self._laws_dict['No correction'] = self._zeros
        self._laws_dict['CCM 89'] = self._CCM89
        self._laws_dict['S 79 H 83'] = self._SH
        self._laws_dict['GCC 09'] = self._GCC09
        self._laws_dict['GCC 09 Revised'] = self._GCC09R
        self._laws_dict['K 76'] = self._K76
        self._laws_dict['Gal SM 79'] = self._Gal_SM79
        self._laws_dict['LMC G 03'] = self._LMC_Gordon03

        self.user_function = user_function
        self.user_params = None

        self.R_V = R_V
        if cHbeta is not None:
            self.cHbeta = cHbeta
        else:
            self.E_BV = E_BV
        self.law = law     
            
    def cHbetaFromEBV(self, ebv):
        return np.asarray((-0.61 + (0.61 ** 2 + 4 * 0.024 * ebv) ** 0.5) / (2 * 0.024))
    
    def EBVFromCHbeta(self, cHbeta):
        return np.asarray(0.61 * cHbeta + 0.024 * cHbeta ** 2.)
    
    def getLaws(self):
        return list(self._laws_dict.keys())
                         
    def printLaws(self):
        for law in list(self._laws_dict.keys()):
            try:
                doc = self._laws_dict[law].__doc__
            except:
                doc = ''
            print("'{0}': {1}".format(law,doc))

    def _get_e_bv(self):
        return self.__E_BV
    def _get_r_v(self):
        return self.__R_V
    def _get_law(self):
        return self.__law
    def _get_cHbeta(self):
        return self.__cHbeta
    def _get_uf(self):
        return self.__user_function
    def _set_e_bv(self, value):
        self.__E_BV = np.asarray(value)
        self.__cHbeta = self.cHbetaFromEBV(self.__E_BV)
    def _set_r_v(self, value):       
        self.__R_V = np.asarray(value)
    def _set_law(self, value):
        if value not in list(self._laws_dict.keys()):
            self.log_.error('Unknown extinction law reference: {0}'.format(value), calling = self.calling)
            self.__law = None
            self.X = None
        else:
            self.__law = value
            self.X = self._laws_dict[self.law]
    def _set_cHbeta(self, value):
        self.__cHbeta = np.asarray(value)
        self.__E_BV = self.EBVFromCHbeta(self.__cHbeta)
    def _set_uf(self, value):
        self.__user_function = value
        if value is None:
            if 'user' in self._laws_dict:
                del self._laws_dict['user']
        else:
            def _uf2(wave):
                """
                This transform the user function with 2 parameters in a function of one single parameter
                """
                return np.asarray(self.__user_function(wave, self.user_params))
            self._laws_dict['user'] = _uf2
        
    E_BV = property(_get_e_bv, _set_e_bv, None, None)
    R_V = property(_get_r_v, _set_r_v, None, None)
    law = property(_get_law, _set_law, None, None)
    cHbeta = property(_get_cHbeta, _set_cHbeta, None, None)
    user_function = property(_get_uf, _set_uf, None, None)
        
    
    def getCorr(self, wave): 
        """
        
        """
        if self.law is None:
            self.log_.warn('No extinction law defined.', calling = self.calling)
            return None
        if self._laws_dict[self.law] is None:
            self.log_.warn('No user defined extinction law.', calling = self.calling)
            return None
        else:
            X = self.X(wave)
            return np.squeeze(10. ** (0.4 * np.outer(X, self.E_BV).reshape(X.shape+self.E_BV.shape)))
    
    def getCorrHb(self, wave):            
        Hb = np.ones_like(wave)*4861.
        return self.getCorr(wave) / self.getCorr(Hb)

    def getCorr2(self, wave1, wave2):            
        return self.getCorr(wave1) / self.getCorr(wave2)
    
    def setCorr(self, obs_over_theo, wave1, wave2):
        COR = RedCorr(E_BV= -2.5, R_V=self.R_V, law=self.law, user_function = self.user_function)
        f1 = np.log10(COR.getCorr(wave1))
        f2 = np.log10(COR.getCorr(wave2))
        if f1 != f2:
            self.E_BV = 2.5 * np.log10(obs_over_theo) / (f1 - f2)
        else:
            self.E_BV = 0.
                    
    def _CCM89(self, wave):
        """
        Cardelli 1989
        param:
            wave [flt] (angstrom) wavelength. May be an array
        """
        x = 1e4 / np.asarray([wave]) # inv microns
        a = np.zeros_like(x)
        b = np.zeros_like(x)
        
        tt = (x > 0.3) & (x <= 1.1)
        a[tt] = 0.574 * x[tt] ** 1.61 
        b[tt] = -0.527 * x[tt] ** 1.61
    
        tt = (x > 1.1) & (x <= 3.3)
        yg = x[tt] - 1.82
        a[tt] = (1. + 0.17699 * yg - 0.50447 * yg ** 2. - 0.02427 * yg ** 3. + 0.72085 * yg ** 4. + 
                 0.01979 * yg ** 5. - 0.7753 * yg ** 6. + 0.32999 * yg ** 7.)
        b[tt] = (0. + 1.41338 * yg + 2.28305 * yg ** 2. + 1.07233 * yg ** 3. - 5.38434 * yg ** 4. - 
                 0.622510 * yg ** 5. + 5.3026 * yg ** 6. - 2.09002 * yg ** 7.)
        
        tt = (x > 3.3) & (x <= 5.9)
        a[tt] = 1.752 - 0.316 * x[tt] - 0.104 / ((x[tt] - 4.67) ** 2. + 0.341)
        b[tt] = -3.090 + 1.825 * x[tt] + 1.206 / ((x[tt] - 4.62) ** 2 + 0.263)
        
        tt = (x > 5.9) & (x <= 8.0)
        a[tt] = (1.752 - 0.316 * x[tt] - 0.104 / ((x[tt] - 4.67) ** 2. + 0.341) - 
                 0.04473 * (x[tt] - 5.9) ** 2. - 0.009779 * (x[tt] - 5.9) ** 3.)
        b[tt] = (-3.090 + 1.825 * x[tt] + 1.206 / ((x[tt] - 4.62) ** 2. + 0.263) + 
                 0.2130 * (x[tt] - 5.9) ** 2. + 0.1207 * (x[tt] - 5.9) ** 3.)
        
        tt = (x > 8.0) & (x < 10.0)
        a[tt] = (-1.073 - 0.628 * (x[tt] - 8) + 0.137 * (x[tt] - 8) ** 2. - 
                 0.070 * (x[tt] - 8) ** 3.)
        b[tt] = (13.670 + 4.257 * (x[tt] - 8) - 0.420 * (x[tt] - 8) ** 2. + 
                 0.374 * (x[tt] - 8) ** 3.)
        
        Xx = self.R_V * a + b
        return np.squeeze(Xx)

    def _SH(self, wave):
        """
        Seaton (1979: MNRAS 187, 73) and 
        Howarth (1983, MNRAS 203, 301) Galactic law
        param:
            wave [float] (angstrom) wavelength. May be an array
        """
        x = 1e4 / np.asarray([wave]) # inv microns
        Xx = np.zeros_like(x)

        tt = (x > 0.3) & (x <= 1.1)
        Xx[tt] = self.R_V * (0.574 * x[tt] ** 1.61) - 0.527 * x[tt] ** 1.61

        tt = (x > 1.1) & (x <= 1.83)
        Xx[tt] = (self.R_V - 3.1) + ((1.86 - 0.48 * x[tt]) * x[tt] - 0.1) * x[tt]
        
        tt = (x > 1.83) & (x <= 2.75)
        Xx[tt] = self.R_V + 2.56 * (x[tt] - 1.83) - 0.993 * ((x[tt] - 1.83)**2)

        tt = (x > 2.75) & (x <= 3.65)
        Xx[tt] = (self.R_V - 3.1) + 1.46 + 1.048 * x[tt] + 1.01 / (((x[tt] - 4.6)**2) + 0.280)
        
        tt = (x > 3.65) & (x <= 7.14)
        Xx[tt] = (self.R_V - 3.1) + 2.19 + 0.848 * x[tt] + 1.01 / (((x[tt] - 4.6)**2) + 0.280)
        
        tt = (x > 7.14) 
        Xx[tt] = (self.R_V - 3.1) + 16.07 - 3.20 * x[tt] + 0.2975 * x[tt]**2
 
        return np.squeeze(Xx)
    
    def _GCC09(self, wave):
        """Generate an extinction function R.A(wave)/A(V) based on the Average 
           Galactic interstellar extinction function of Gordon, Cartledge & Clayton 
           (2009, ApJ, 705, 1320)
           !!! WARNING This law seems buggy...
        """
        x = 1e4 / np.asarray([wave]) # inv microns
        Xx = np.zeros_like(x)

        tt = (x > 0.3) & (x <= 1.1)
        Xx[tt] = (self.R_V * 0.574 - 0.527) * x[tt]**1.61
        
        tt = (x > 1.1) & (x <= 3.3)
        y = x[tt] - 1.82
        a = 1 + y*(0.17699 + y*(-0.50447 + y*(-0.02427 + y*(0.72085 + \
                y*(0.01979 + y*(-0.77530 + y*0.32999))))))
        b = y*(1.41338 + y*(2.28305 + y*(1.07233 + y*(-5.38434 + \
            y*(-0.62251 + y*(5.30260 - y*2.09002)))))) 
        Xx[tt] = self.R_V * a + b

        ##
        # @bug The coefficients are obviously not correct; 
        tt = (x > 3.3) & (x <= 5.9)
        a =  1.896 - 0.372*x[tt] - 0.0108 / ((x[tt] - 4.57)**2 + 0.0422)
        b = -3.503 + 2.057*x[tt] + 0.7180 / ((x[tt] - 4.59)**2 + 0.0530)
        Xx[tt] = self.R_V * a + b

        tt = (x > 5.9) & (x <= 11.0)
        a =  1.896 - 0.372*x[tt] - 0.0108 / ((x[tt] - 4.57)**2 + 0.0422)
        b = -3.503 + 2.057*x[tt] + 0.7180 / ((x[tt] - 4.59)**2 + 0.0530)
        y = x[tt] - 5.9
        a += -(0.110 + 0.0099 * y) * y**2
        b +=  (0.537 + 0.0530*y) * y**2
        Xx[tt] = self.R_V*a + b

        return np.squeeze(Xx)

    def _GCC09R(self, wave):
        """Generate an extinction function R.A(wave)/A(V) based on the Average 
           Galactic interstellar extinction function of Gordon, Cartledge & Clayton 
           (2009, ApJ, 705, 1320)
           Revised version
        """
        x = 1e4 / np.asarray([wave]) # inv microns
        Xx = np.zeros_like(x)

        tt = (x > 0.3) & (x <= 1.1)
        Xx[tt] = (self.R_V * 0.574 - 0.527) * x[tt]**1.61
        
        tt = (x > 1.1) & (x <= 3.3)
        y = x[tt] - 1.82
        a = 1 + y*(0.17699 + y*(-0.50447 + y*(-0.02427 + y*(0.72085 + \
                y*(0.01979 + y*(-0.77530 + y*0.32999))))))
        b = y*(1.41338 + y*(2.28305 + y*(1.07233 + y*(-5.38434 + \
            y*(-0.62251 + y*(5.30260 - y*2.09002)))))) 
        Xx[tt] = self.R_V * a + b

        ##
        # @bug The coefficients are obviously not correct; 
        # the substitutions explore the possibility of a typo in the UV-bump term
        tt = (x > 3.3) & (x <= 5.9)
#        a =  1.896 - 0.372*x[tt] - 0.0108 / ((x[tt] - 4.57)**2 + 0.0422)
#        b = -3.503 + 2.057*x[tt] + 0.7180 / ((x[tt] - 4.59)**2 + 0.0530)
        a =  1.896 - 0.372*x[tt] - 0.108 / ((x[tt] - 4.57)**2 + 0.0422)
        b = -3.503 + 2.057*x[tt] + 0.7180 / ((x[tt] - 4.59)**2 + 0.0530)
        Xx[tt] = self.R_V * a + b

        tt = (x > 5.9) & (x <= 11.0)
        a =  1.896 - 0.372*x[tt] - 0.108 / ((x[tt] - 4.57)**2 + 0.0422)
        b = -3.503 + 2.057*x[tt] + 0.7180 / ((x[tt] - 4.59)**2 + 0.0530)
        y = x[tt] - 5.9
        a += -(0.110 + 0.0099 * y) * y**2
        b +=  (0.537 + 0.0530*y) * y**2
        Xx[tt] = self.R_V * a + b

        return np.squeeze(Xx)

    def _K76(self, wave):
        """
        from Kaler (1976, ApJS, 31, 517).
        This function returns the correction relative to Hbeta, not usable for absolute correction.
        """
        
        w = np.asarray([wave]) # inv microns

        f_tab = np.loadtxt(execution_path('Gal_Kaler.txt'))
        f = np.interp(w, f_tab[:,0], f_tab[:,1])
        return np.squeeze(f * self.cHbeta / 0.4 / self.E_BV)

    def _Gal_SM79(self, wave):
        """
        from Savage & Mathis (1979, ARA&A, 17, 73)
        """
        
        x = 1e4 / np.asarray([wave]) # inv microns

        X_tab = np.loadtxt(execution_path('Gal_SM79.txt'))
        Xx = np.interp(x, X_tab[:,0], X_tab[:,1])
        return np.squeeze(Xx)
    
    def _LMC_Gordon03(self, wave):
        """
        Gordon et al. (2003, ApJ, 594,279)
        """
        
        x = 1e4 / np.asarray([wave]) # inv microns

        X_tab = np.loadtxt(execution_path('LMC_Gordon.txt'))
        Xx = self.R_V * np.interp(x, X_tab[:,0], X_tab[:,1])
        return np.squeeze(Xx)
    

    def _zeros(self, wave):
        """
        No Correction
        """
        return np.zeros_like(wave)
    
    def plot(self, w_inf = 1000., w_sup = 10000., laws = None, **kwargs):
        """
        plot extinction laws
        param:
            - w_inf [float] lower limit of plot
            - w_sup [float] upper limit of plot
            - laws [list of strings] list of extinction law labels. If set to 'all', all the laws are plotted
            - **kwargs arguments to plot
        """
        if not pc.config.INSTALLED['plt']:
            pc.log_.error('No plotting allowed', calling = self.calling)
        old_E_BV = self.E_BV
        old_law = self.law
        self.E_BV = 2.5
        w = np.linspace(w_inf, w_sup, 1000)
        if laws is None:
            laws = self.law
        elif laws == 'all':
            laws = self.getLaws()
        if type(laws) is str:
            laws = [laws]
        for law in laws:
            self.law = law
            plt.plot(w,np.log10(self.getCorrHb(w)), label = law, **kwargs)
        plt.legend()
        plt.xlabel('Wavelength (A)')
        plt.ylabel('X')
        self.law = old_law
        self.E_BV = old_E_BV

    
