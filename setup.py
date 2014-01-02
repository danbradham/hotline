import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


setup(
    name='hotline',
    version=0.2,
    description="A customizable popup input field.",
    long_description=open('README.md').read(),
    author='Dan Bradham',
    author_email='danielbradham@gmail.com',
    url='http://www.danbradham.com',
    packages=['hotline'],
    package_data={'': ['LICENSE']},
    package_dir={'hotline': 'hotline'},
    include_package_data=True,
    license=open('LICENSE').read(),
    zip_safe=False)