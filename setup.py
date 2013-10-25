from setuptools import setup
import sys, os

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
CHANGES = open(os.path.join(here, 'CHANGES.rst')).read()


version=open("VERSION").readline().strip()

install_requires = [
    # List your project dependencies here.
    # For more details, see:
    # http://packages.python.org/distribute/setuptools.html#declaring-dependencies
    'baker >= 1.3',
    'python-dateutil >= 2.1',
    'pandas >= 0.9.0',
    'tstoolbox >= 0.5',
    'construct >= 2.0.6',
]


setup(name='swmmtoolbox',
    version=version,
    description="The swmmtoolbox extracts data from the Storm Water Management Model 5 binary output file.",
    long_description=README + '\n\n' + CHANGES,
    classifiers=[
      # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    ],
    keywords='stormwater model water hydrology hydraulics',
    author='Tim Cera, P.E.',
    author_email='tim@cerazone.net',
    url='',
    license='BSD:3 clause',
    packages=['swmmtoolbox'],
    package_dir={'': '.'},
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    entry_points={
        'console_scripts':
            ['swmmtoolbox=swmmtoolbox:main']
    }
)
