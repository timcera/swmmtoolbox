#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

from setuptools import setup

# temporarily redirect config directory to prevent matplotlib importing
# testing that for writeable directory which results in sandbox error in
# certain easy_install versions
os.environ["MPLCONFIGDIR"] = "."

pkg_name = "swmmtoolbox"

version = open("VERSION").readline().strip()

if sys.argv[-1] == "publish":
    os.system("python setup.py sdist")
    os.system("twine upload dist/{pkg_name}-{version}.tar.gz".format(**locals()))
    sys.exit()

README = open("README.rst").read()

install_requires = [
    # List your project dependencies here.
    # For more details, see:
    # http://packages.python.org/distribute/setuptools.html#declaring-dependencies
    "tstoolbox >= 102, < 103",
    "sphinx >= 1.3",
    "future",
]

setup(
    name=pkg_name,
    version=version,
    description="The swmmtoolbox extracts data from the Storm Water Management Model 5 binary output file.",
    long_description=README,
    classifiers=[
        # Get strings from
        # http://pypi.python.org/pypi?%3Aaction=list_classifiers
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Developers",
        "Environment :: Console",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="stormwater model water hydrology hydraulics",
    author="Tim Cera, P.E.",
    author_email="tim@cerazone.net",
    url="http://timcera.bitbucket.io/swmmtoolbox/docsrc/index.html",
    packages=["swmmtoolbox"],
    package_dir={"": "."},
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    entry_points={"console_scripts": ["swmmtoolbox=swmmtoolbox.swmmtoolbox:main"]},
    python_requires=">=3.7.1",
)
