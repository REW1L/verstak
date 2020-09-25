#!/usr/bin/env python

from distutils.core import setup

setup(name='verstak',
      version='0.0.1',
      description='Application for transformation of docx to html',
      author='Ivan Danilov',
      url='https://github.com/REW1L/verstak',
      packages=['docx_parser'],
      scripts=['scripts/verstak']
     )
