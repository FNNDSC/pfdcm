import sys
# Make sure we are running python3.5+
if 10 * sys.version_info[0]  + sys.version_info[1] < 35:
    sys.exit("Sorry, only Python 3.5+ is supported.")

from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()

setup(
      name             =   'pfdcm',
      version          =   '2.0.2.6',
      description      =   'Path and File DICOM',
      long_description =   readme(),
      author           =   'Rudolph Pienaar',
      author_email     =   'rudolph.pienaar@gmail.com',
      url              =   'https://github.com/FNNDSC/pfcon',
      packages         =   ['pfdcm'],
      install_requires =   ['pydicom', 'pycurl', 'pyzmq', 'webob', 'pudb', 'psutil', 'pfmisc', 'pudb', 'pfstorage', 'pfstate', 'pypx'],
      test_suite       =   'nose.collector',
      tests_require    =   ['nose'],
      scripts          =   ['bin/pfdcm'],
      license          =   'MIT',
      zip_safe         =   False
     )
