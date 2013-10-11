#!/usr/bin/env python
# Standard library
from distutils.core import setup
# Project
import dashgen

with open('README.rst') as file:
    long_description = file.read()

setup(author="Timid Robot Zehta",
      author_email="tim@clockwork.net",
      classifiers=["Environment :: Console",
                   "License :: OSI Approved :: MIT License",],
      description="Interquartile Mean pure-Python module",
      download_url="https://github.com/ClockworkNet/graphite-dashgen/releases",
      license="MIT License",
      long_description=long_description,
      name="python-graphite-dashgen",
      py_modules=["dashgen"],
      url="https://github.com/ClockworkNet/graphite-dashgen",
      version=dashgen.VERSION,
      )
