#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='verstak',
      version='0.0.14',
      description='Application for transformation of docx to html',
      author='Ivan Danilov',
      url='https://github.com/REW1L/verstak',
      packages=find_packages(),
      install_requires=['python-docx'],
      scripts=['scripts/verstak'],
      package_data={'': ['*.ini']})
