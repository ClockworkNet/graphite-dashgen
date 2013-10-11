#!/usr/bin/env python
# Standard library
from distutils.core import setup

with open("README.rst") as file:
    long_description = file.read()

setup(author="Timid Robot Zehta",
      author_email="tim@clockwork.net",
      classifiers=["Environment :: Console",
                   "License :: OSI Approved :: MIT License",],
      description=("Graphite-dashgen automates the creation of Graphite "
                   "dashboards"),
      download_url="https://github.com/ClockworkNet/graphite-dashgen/releases",
      license="MIT License",
      long_description=long_description,
      name="python-graphite-dashgen",
      py_modules=["dashgen",],
      requires=["PyYAML",],
      url="https://github.com/ClockworkNet/graphite-dashgen",
      version="0.1.0",
      )
