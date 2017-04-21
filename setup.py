#!/usr/bin/env python

# This file is public domain via CC0:
# <https://creativecommons.org/publicdomain/zero/1.0/>

import sys

from setuptools import setup, find_packages

import versioneer

setup(
 name="ezpyi",
 version=versioneer.get_version(),
 description="A wrapper for PyInstaller that simplifies its usage.",
 url="https://code.s.zeid.me/ezpyi",
 author="Scott Zeid",
 author_email="support+ezpyi@s.zeid.me",
 classifiers=[
  "Development Status :: 3 - Alpha",
  "Environment :: Console",
  "Natural Language :: English",
  "Programming Language :: Python :: 2",
  "Programming Language :: Python :: 2 :: Only",
  "Topic :: Software Development :: Libraries :: Python Modules",
 ],
 packages=find_packages(),
 install_requires=[],
 entry_points={
  "console_scripts": [
   "ezpyi=ezpyi.__main__:main",
   "ezpyi%d=ezpyi.__main__:main" % sys.version_info.major,
   "ezpyi%d.%d=ezpyi.__main__:main" % (sys.version_info.major, sys.version_info.minor),
  ]
 },
 cmdclass=versioneer.get_cmdclass(),
)
