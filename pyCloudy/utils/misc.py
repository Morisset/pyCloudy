import numpy as np
import pickle
import os
import sys
import pyCloudy as pc 
from pyCloudy.utils.init import LIST_ALL_ELEM 
if pc.config.INSTALLED['Image']:
    from PIL import Image
if pc.config.INSTALLED['scipy']:
    from scipy import signal

def execution_path(filename):
    return os.path.join(os.path.dirname(sys._getframe(1).f_code.co_filename), filename)

## @include copyright.txt
def sextract(text, par1=None, par2=None): 
    """
    extract a substring from text (first parameter)
     
    If par1 is a string, the extraction starts after par1,
    else if it is an integer, it starts at position par1.
    If par 2 is a string, extraction stop at par2, 
    else if par2 is an integer, extraction stop after par2 characters.
    ex: sextract('test123','e','1')
    sextract('test123','st',4)
    """
    if np.size(text) == 1:
        if type(par1) is int:
            str1 = text[par1::]
        elif type(par1) is str:
            str1 = text.split(par1)
            if len(str1) == 1:
                return ''
            else:
                str1 = str1[-1]
        else:
            str1 = text
    
        if type(par2) is int:
            str2 = str1[0:par2]
        elif type(par2) is str:
            str2 = str1.split(par2)
            if len(str2) == 1:
                return ''
            else:
                str2 = str2[0]
        else:
            str2 = str1
        return str2
    else:
        res = []
        for subtext in text:
            res1 = sextract(subtext, par1=par1, par2=par2)
            if res1 != '':
                res.append(res1)
        return res
    
## @include copyright.txt
def half_gaussian(N=100, sigma=1.):

    x = np.arange(0, N)
    g = np.exp(-0.5 * (x / sigma) ** 2)
    return g / g.sum()

def gaussian(x, zeta_0 = None, sigma = None, FWHM = None):
    """
    Return the value of a gaussian function.
    param:
        x
        One of the following parameter must be given:
        zeta_0, sigma or FWHM
    """
    if sigma is not None:
        zeta_0 = np.sqrt(2.)*sigma
    elif FWHM is not None:
        zeta_0 = FWHM / (2*np.sqrt(np.log(2.)))
    elif zeta_0 is None:
        return None
    else:
        res = 1. /zeta_0 / np.sqrt(np.pi) * np.exp(-((x/zeta_0)**2))
        return res

def gauss_kern(size, sizey=None):
    """ Returns a normalized 2D gauss kernel array for convolutions """
    size = int(size)
    if not sizey:
        sizey = size
    else:
        sizey = int(sizey)
    x, y = np.mgrid[-size:size+1, -sizey:sizey+1]
    g = np.exp(-(x**2/float(size)+y**2/float(sizey)))
    return g / g.sum()

def blur_image(im, n, ny=None) :
    """ blurs the image by convolving with a gaussian kernel of typical
        size n. The optional keyword argument ny allows for a different
        size in the y direction.
    """
    g = gauss_kern(n, sizey=ny)
    improc = signal.convolve(im, g, mode='valid')
    return(improc)

def Hb_prof(x, zeta_0):
    """
    The Hbeta profile is sum of 2 blocks of lines (actually 3 + 4 lines)
    """
    res1 = .41 /zeta_0 / np.sqrt(np.pi) * np.exp(-(((x-2.7)/zeta_0)**2))
    res2 = .59 /zeta_0 / np.sqrt(np.pi) * np.exp(-(((x+2.0)/zeta_0)**2))
    return res1 + res2

## @include copyright.txt
def convol(y, kernel): 
    
    N = np.size(kernel)
    res = y * kernel[0]
    for i in range(N - 1):
        y_shift = np.zeros_like(y)
        y_shift[:-i - 1] = y[i + 1:]
        res = res + y_shift * kernel[i + 1]
        y_shift = np.zeros_like(y)
        y_shift[i + 1:] = y[:-i - 1]
        res = res + y_shift * kernel[i + 1]
    res = res / 2.
    return res

        
## @include copyright.txt
def save(file_, *args, **kwargs):
    """
    Save the value of some data in a file.
    Usage: save('misdatos.pypic','a',b=b)
    """
    f = open(file_, "wb")
    dico = kwargs
    for name in args:
        dico[name] = eval(name)
    pickle.dump(dico, f, protocol=2)
    f.close
    
## @include copyright.txt
def restore(file_):
    """
    Read data saved with save function.
    Usage: datos = restore('misdatos.pypic')
    """
    f = open(file_, "rb")
    result = pickle.load(f)
    f.close
    return result

## @include copyright.txt
def convert_label(str_):
    """
    converts a line in format Cloudy to a line in format pyCloudy
    ex: 
    convert_label('C  2  1335') is C__2__1335A
    convert_label('Ne 3 15.55m') is NE_3_1555M
    """
    try:
        a = str_.strip().replace(' ', '_').replace('.', '').upper()
        if a[-1].isdigit():
            a += 'A'
    except:
        a = None
    return a

## @include copyright.txt
def dist_point_line(P, P0, P1):
    """ computing the distance between point x,y and line (x0,y0)->(x1,y1)
    """
    dx = P1[0]-P0[0]
    dy = P0[1]-P1[1]
    return abs(dx*(P0[1]-P[1])+dy*(P0[0]-P[0]))/np.sqrt(dx**2.+dy**2.)

## @include copyright.txt
def points_right_of_line(x, y, P0, P1):
    """Return True if the point (x,y) is right to the line P0-P1"""
    res = np.zeros_like(x, dtype = bool)
    #(y - y0) (x1 - x0) - (x - x0) (y1 - y0)
    tt = (y - P0[1]) * (P1[0] - P0[0]) - (x - P0[0]) * (P1[1] - P0[1]) < 0
    if np.asarray(x).size == 1:
        return tt
    else:
        res[tt] = True
        return res

## @include copyright.txt
def points_left_of_line(x, y, P0, P1):
    """Return True if the point (x,y) is left to the line P0-P1"""
    res = np.zeros_like(x, dtype = bool)
    #(y - y0) (x1 - x0) - (x - x0) (y1 - y0)
    tt = (y - P1[1]) * (P0[0] - P1[0]) - (x - P1[0]) * (P0[1] - P1[1]) < 0
    if np.asarray(x).size == 1:
        return tt
    else:
        res[tt] = True
        return res

## @include copyright.txt
def points_inside_triangle(x, y, P0, P1, P2):
    """
    Determine if a point is in a triangle
    Adapted from http://paulbourke.net/geometry/insidepoly/
    param:
        x, y [float] coordinates of the test point
        P1, P2, P3 [list or tupple or array of 3 elements] coordinates of the triangle corners.
    return:
        [boolean] True if points (x,y) is/are inside a triangle P0-P1-P2.
    """
    sx = np.asarray(x).size
    sy = np.asarray(y).size
    assert  sx == sy, 'x and y must have the same size'
    res = np.zeros_like(x, dtype = bool)
    tt = ((points_right_of_line(x, y, P0, P1) & points_right_of_line(x, y, P1, P2) & points_right_of_line(x, y, P2, P0))|
            (points_left_of_line(x, y, P0, P1) & points_left_of_line(x, y, P1, P2) & points_left_of_line(x, y, P2, P0)))
    if sx == 1:
        return tt
    else:
        res[tt] = True
        return res
    
def int_to_roman(input_):
    """
    Convert an integer to Roman numerals.
    
    Examples:
    >>> int_to_roman(0)
    Traceback (most recent call last):
    ValueError: Argument must be between 1 and 3999
    
    >>> int_to_roman(-1)
    Traceback (most recent call last):
    ValueError: Argument must be between 1 and 3999
    
    >>> int_to_roman(1.5)
    Traceback (most recent call last):
    TypeError: expected integer, got <type 'float'>
    
    >>> print int_to_roman(2000)
    MM

    >>> print int_to_roman(1999)
    MCMXCIX

    """
    if type(input_) != type(1):
        raise TypeError("expected integer, got {0}".format(type(input_)))
    if not 0 < input_ < 4000:
        raise ValueError("Argument must be between 1 and 3999")   
    ints = (1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1)
    nums = ('M', 'CM', 'D', 'CD', 'C', 'XC', 'L', 'XL', 'X', 'IX', 'V', 'IV', 'I')
    result = ""
    for i in range(len(ints)):
        count = int(input_ / ints[i])
        result += nums[i] * count
        input_ -= ints[i] * count
    return result

def roman_to_int(input_):
    """
    Convert a roman numeral to an integer.
    
    >>> r = range(1, 4000)
    >>> nums = [int_to_roman(i) for i in r]
    >>> ints = [roman_to_int(n) for n in nums]
    >>> print r == ints
    1
    
    >>> roman_to_int('VVVIV')
    Traceback (most recent call last):
     ...
    ValueError: input is not a valid roman numeral: VVVIV

    >>> roman_to_int(1)
    Traceback (most recent call last):
     ...
    TypeError: expected string, got <type 'int'>

    >>> roman_to_int('a')
    Traceback (most recent call last):
     ...
    ValueError: input is not a valid roman numeral: A

    >>> roman_to_int('IL')
    Traceback (most recent call last):
     ...
    ValueError: input is not a valid roman numeral: IL

    """   
    if type(input_) != type(""):
        raise TypeError("expected string, got {0}".format(type(input_)))
    input_ = input_.upper()
    nums = ['M', 'D', 'C', 'L', 'X', 'V', 'I']
    ints = [1000, 500, 100, 50, 10, 5, 1]
    places = []
    for c in input_:
        if not c in nums:
            raise ValueError("input is not a valid roman numeral: {0}".format(input_))
    for i in range(len(input_)):
        c = input_[i]
        value = ints[nums.index(c)]
        # If the next place holds a larger number, this value is negative.
        try:
            nextvalue = ints[nums.index(input_[i + 1])]
            if nextvalue > value:
                value *= -1
        except IndexError:
            # there is no next place.
            pass
        places.append(value)
    sum_ = 0
    for n in places: sum_ += n
    # Easiest test for validity...
    if int_to_roman(sum_) == input_:
        return sum_
    else:
        raise ValueError('input is not a valid roman numeral: {0}'.format(input_))
      
def get_elem_ion(label):
    """
    Split a Cloudy label into elem and ion
    """
    dictio = {}
    dictio['TOTL__4363A'] = ('O', 3)
    spl = label.split('_')
    list_upper = [elem.upper() for elem in LIST_ALL_ELEM]
    if spl[0] in list_upper:
        elem = spl[0]
        if spl[1] == '':
            ion = spl[2]
        else:
            ion = spl[1]
        if ion[-1] == 'R':
            ion = ion[:-1]
        if ion.isdigit():
            ion = int(ion)
        else:
            ion = int(roman_to_int(ion))
    else:
        if label in dictio:
            elem, ion = dictio[label]
        else:
            elem = None
            ion = None
    return (elem,ion)

def pyneb2cloudy(file_ = 'pyneb2cloudy.txt', with_ = False):
    """
    define a dictionary to translate pyneb labels, as used in observation files, into Cloudy label
    ex: 'N2_6583A': 'N  2  6584A'
    the with_ option transform the output into pyCloudy label:
    ex: 'Ne3_3869A': 'NE_3__3869A'
    """
    
    f = open(execution_path(file_), 'r')
    lines = f.readlines()
    f.close()
    dic = {}
    for line in lines:
        line_py = sextract(line, 0, ' ')
        if with_:
            line_cl = line[14:25].upper().replace(' ','_')
        else:
            line_cl = line[14:25]
        dic[line_py] = line_cl
    return dic

def cloudy2pyneb(file_ = 'pyneb2cloudy.txt'):
    """
    define a dictionary to translate cloudy labels into pyneb atom.lines
    """
    f = open(execution_path(file_), 'r')
    lines = f.readlines()
    f.close()
    dic = {}
    for line in lines:
        if line[0] != '#':
            line_py = sextract(line, 0, ' ')
            line_cl = line[14:25].upper().replace(' ','_').replace('.','')
            if line_cl != '_____ABSENT':
                dic[line_cl] = line_py.split('_')
    return dic

def convert2RGB(im_R, im_G, im_B):
    x_size = im_R.shape[0]
    y_size = im_R.shape[1]
    im3 = np.zeros((x_size, y_size, 3), dtype = np.uint8)
    im3[:,:,0] = im_R / np.max(im_R) * 255
    im3[:,:,1] = im_G / np.max(im_G) * 255
    im3[:,:,2] = im_B / np.max(im_B) * 255
    imRGB = Image.fromarray(im3)
    return imRGB

def make_mask(X, Y, ap_center, ap_size, seeing = None):
    mask = ((X > ap_center[0] - ap_size[0]/2.) & 
            (X <= ap_center[0] + ap_size[0]/2.) & 
            (Y > ap_center[1] - ap_size[1]/2.) & 
            (Y <= ap_center[1] + ap_size[1]/2.))
    if seeing is not None:
        if pc.config.INSTALLED['scipy']:
            # seeing is the FWHM of the gaussian function
            sigma = seeing / (2 * (2 * np.log(2))**0.5)
            kernel = np.exp( - (X**2 + Y**2) / (2*sigma**2) )
            kernel = kernel / kernel.sum()
            mask = signal.convolve2d(mask, kernel, mode='same')
        else:
            pc.log_.error('Scipy not installed, no seeing convolution')
    return mask

def revert_seterr(oldsettings):
    """
    This function revert the options of seterr to a value saved in oldsettings.
    
    Usage:
        oldsettings = np.seterr(all='ignore')
        to_return = (result - int_ratio) / int_ratio # this will not issue Warning messages
        revert_seterr(oldsettings)
    Parameter:
        oldsettings: result of np.seterr(all='ignore')
    """
    np.seterr(over = oldsettings['over'])
    np.seterr(divide = oldsettings['divide'])
    np.seterr(invalid = oldsettings['invalid'])
    np.seterr(under = oldsettings['under'])
     
def quiet_divide(a, b):
    """
    This function returns the division of a by b, without any waring in case of b beeing 0.
    """
    oldsettings = np.seterr(all='ignore')
    to_return = a / b # this will not issue Warning messages
    revert_seterr(oldsettings)
    return to_return

def quiet_log10(a):
    """
    This function returns the log10 of a, without any waring in case of b beeing 0.
    """
    oldsettings = np.seterr(all='ignore')
    to_return = np.log10(a) # this will not issue Warning messages
    revert_seterr(oldsettings)
    return to_return
     
class ImportFromFile(object):
    """
    Create an object with parameters as defined in the file_to_import (which is a python-style file)
    """
    def __init__(self, file_to_import):
        MM = {}
        exec(compile(open(file_to_import).read(), file_to_import, 'exec'), MM)
        for key in list(MM.keys()):
            vars(self)[key] = MM[key]

def fill_from_file(N, open_file, dtype = np.float64):
    """
    Read N elements from an already open file and put them to a numpy array.
    The elements don't need to be in rectangular form, e.g. the following 10 elements can be read:
    1 2 3 4
    2 3 4 5
    2 4
    """
    i = 0
    res = np.zeros(N, dtype = dtype)
    for line in iter(open_file):
        tab = line.split()
        for elem in tab:
            res[i] = dtype(elem)
            i += 1
            if i >= N:
                return(res)
    return(res)

def write_cols(tab, N, open_file):
    """
    Write an array into an already open file, using N columns
    """
    for i, elem in enumerate(tab):
        open_file.write('{0} '.format(elem))
        if i%N == (N-1):
            open_file.write('\n')

def read_atm_ascii(ascii_file):
    """
       20060612
   1
   1
   Teff
   1
   110396
   lambda
   1.00000000e+00
    F_lambda
    2.37160000e+20
       1.070E+05
      43.2662      43.3385      43.4109      43.4834      43.5561      43.6288      43.7017      43.7747      43.8479      43.9211
    """
    f = open(ascii_file, 'r')
    for i in np.arange(5):
        foo = f.readline()
    n = np.int(f.readline().split()[0])
    for i in np.arange(5):
        foo = f.readline()
    lam = []
    i = 0
    while (i < n):
        l = f.readline()
            
def convert_c13_c17(label):
    """
    Transform a label from c13 style into c17+ style
    """
    c13c17 = pc.config.c13c17
    if label in c13c17['c13']:
        return c13c17['c17'][c13c17['c13'] == label][0]
    else:
        return ''

def convert_c17_c13(label):
    """
    Transform a label from c17+ style into c13 style
    """
    c13c17 = pc.config.c13c17
    if label in c13c17['c17']:
        return c13c17['c13'][c13c17['c17'] == label][0]
    else:
        return ''

def correc_He1(tem=1e4, den=1e2, lambda_ = 5876, print_only_lambdas=False):
    """
    Compute the correction to the CA_B__5876A ,  CA_B__4471A , and CA_B__6678A line intensities.
    Using formula 3 and table 3 from Izotov et al. 2013, A&A 558, A57
    """
    d = np.genfromtxt(execution_path('Izotov2013_CR.txt'), delimiter='\t', dtype=None, names=True)
    if print_only_lambdas:
        print(np.unique(d['Wavelength']))
        return(None)
    try:
        d = d[d['Wavelength'] == lambda_]
    except:
        raise('Incorrect wavelength')
        return(None)
    t4 = np.array(tem)/1e4
    dens = np.array(den)
    if np.ndim(dens) == 0:
        dens = np.ones_like(t4) * dens
    CR = 0
    for i in range(8):
        dd = d[d['i'] == i+1]
        CR += dd['a_i'] * t4**dd['b_i'] * np.exp(dd['c_i']/t4)
    CR *= 1./(1. + 3552*t4**0.55/dens)
    mask = t4 < 0.50
    if type(mask) is bool or type(mask) is numpy.bool_:
        if mask:
            CR = correc_He1(5000, den, lambda_=lambda_) - 1
    else:
        if mask.sum() > 0:
            CR[mask] = correc_He1(np.ones_like(dens[mask])*5000.00, dens[mask], lambda_=lambda_) - 1
    mask = t4 > 2.50
    if type(mask) is bool or type(mask) is numpy.bool_:
        if mask:
            CR = correc_He1(25000, den, lambda_=lambda_) - 1
    else:
        if mask.sum() > 0:
            CR[mask] = correc_He1(np.ones_like(dens[mask])*25000.00, dens[mask], lambda_=lambda_) - 1
    return(1. + CR)
