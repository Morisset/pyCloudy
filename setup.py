#!/usr/bin/env python

from distutils.core import setup
from pyCloudy.version import __version__

setup(name='pyCloudy',
      version=__version__,
      description='Tools to manage Astronomical Cloudy photoionization code',
      long_description=open('README').read(),
      author='Christophe Morisset IA-UNAM',
      author_email='chris.morisset@gmail.com',
      maintainer='Christophe Morisset IA-UNAM',
      maintainer_email='chris.morisset@gmail.com',
      url='https://sites.google.com/site/pycloudy/',
      download_url = 'https://github.com/Morisset/pyCloudy/releases/tag/{}'.format(__version__),
      packages=['pyCloudy','pyCloudy.c1d','pyCloudy.c3d','pyCloudy.utils', 'pyCloudy.db'],
      package_data={'pyCloudy.utils':['*txt']},
      classifiers=['Development Status :: 5 - Production/Stable',
                   'Intended Audience :: Science/Research',
                   'License :: Free for non-commercial use',
                   'Programming Language :: Python :: 2',
                   'Topic :: Scientific/Engineering :: Astronomy'
                   ],
      license='GPL',
      keywords="astronomy photoionization cloudy"
     )
