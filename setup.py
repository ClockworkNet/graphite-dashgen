#!/usr/bin/env python
try:
    # Third-party
    from setuptools import setup
except ImportError:
    # Standard library
    from distutils.core import setup

with open("README.rst") as file:
    long_description = file.read()

setup(author="Timid Robot Zehta",
      author_email="tim@clockwork.net",
      classifiers=["Environment :: Console",
                   "Intended Audience :: System Administrators",
                   "License :: OSI Approved :: MIT License",
                   "Topic :: System :: Monitoring",
                   "Topic :: Utilities"],
      description=("Graphite-dashgen automates the creation of Graphite "
                   "dashboards"),
      download_url="https://github.com/ClockworkNet/graphite-dashgen/releases",
      install_requires=["PyYAML"],
      license="MIT License",
      long_description=long_description,
      name="python-graphite-dashgen",
      py_modules=["dashgen"],
      url="https://github.com/ClockworkNet/graphite-dashgen",
      version="0.1.1",
      )
