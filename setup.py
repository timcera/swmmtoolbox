from setuptools import setup
import os
import sys
import shutil

pkg_name = "swmmtoolbox"

version = open("VERSION").readline().strip()

if sys.argv[-1] == "publish":
    os.system("python setup.py sdist")

    # The following block of code is to set the timestamp on files to
    # 'now', otherwise ChromeOS/google drive sets to 1970-01-01 and then
    # no one can install it because zip doesn't support dates before
    # 1980.
    os.chdir("dist")
    os.system("tar xvzf {pkg_name}-{version}.tar.gz".format(**locals()))
    os.system("find {pkg_name}-{version}* -exec touch {{}} \\;".format(**locals()))
    os.system(
        "tar czf {pkg_name}-{version}.tar.gz {pkg_name}-{version}".format(**locals())
    )
    shutil.rmtree("{pkg_name}-{version}".format(**locals()))
    os.chdir("..")

    os.system("twine upload dist/{pkg_name}-{version}.tar.gz".format(**locals()))
    sys.exit()

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, "README.rst")).read()

install_requires = [
    # List your project dependencies here.
    # For more details, see:
    # http://packages.python.org/distribute/setuptools.html#declaring-dependencies
    "tstoolbox >= 1.12.12.9",
    "sphinx >= 1.3",
    "future",
]

setup(
    name="swmmtoolbox",
    version=version,
    description="The swmmtoolbox extracts data from the Storm Water Management Model 5 binary output file.",
    long_description=README,
    classifiers=[
        # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
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
    python_requires=">=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*,!=3.4.*",
)
