# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import sys
import os
import re
import glob


version = re.findall('__version__ = "(.*)"',
                     open('metabot/__init__.py', 'r').read())[0]

packages = [
    "metabot",
    ]

CLASSIFIERS = """
Development Status :: 2 - Pre-Alpha
Environment :: Console
Intended Audience :: Science/Research
License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)
Programming Language :: Python
Topic :: Scientific/Engineering :: Neuroscience
"""
classifiers = CLASSIFIERS.split('\n')[1:-1]

# TODO: This is cumbersome and prone to omit something
demofiles = glob.glob(os.path.join("examples", "*", "*.py"))
demofiles += glob.glob(os.path.join("examples", "*", "*", "*.py"))
demofiles += glob.glob(os.path.join("examples", "*", "*", "*.xml*"))
demofiles += glob.glob(os.path.join("examples", "*", "*", "*", "*.geo"))
demofiles += glob.glob(os.path.join("examples", "*", "*", "*", "*.xml*"))

# Don't bother user with test files
[demofiles.remove(f) for f in demofiles if "test_" in f]

setup(name="simplepackage",
      version=version,
      author="Maaike van Swieten",
      author_email="mvanswieten@outlook.com",
      url="https://github.com/MaaikevS/metabot",
      description="A simple python package to convert metadata from a file to openMINDS conform JSON-LD files that can be uploaded to the EBRAINS Knowledge Graph.",
      long_description="--",
      classifiers=classifiers,
      license="GNU LGPL v3 or later",
      packages=packages,
      package_dir={"metabot": "metabot"},
      data_files=[(os.path.join("share", "metabot", os.path.dirname(f)), [f])
                  for f in demofiles],
    )