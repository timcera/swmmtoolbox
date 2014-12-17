from setuptools import setup
import os
import sys

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    os.system('python setup.py upload_docs')
    sys.exit()

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()

version = open("VERSION").readline().strip()

install_requires = [
    # List your project dependencies here.
    # For more details, see:
    # http://packages.python.org/distribute/setuptools.html#declaring-dependencies
    'mando',
    'python-dateutil >= 2.1',
    'pandas >= 0.9.0',
    'tstoolbox >= 0.8',
]

setup(name='swmmtoolbox',
      version=version,
      description="The swmmtoolbox extracts data from the Storm Water Management Model 5 binary output file.",
      long_description=README,
      classifiers=[
          # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
          'Development Status :: 5 - Production/Stable',
          'Environment :: Console',
          'Intended Audience :: End Users/Desktop',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 3',
          'Topic :: Scientific/Engineering',
          'Topic :: Software Development :: Libraries :: Python Modules',
      ],
      keywords='stormwater model water hydrology hydraulics',
      author='Tim Cera, P.E.',
      author_email='tim@cerazone.net',
      url='',
      packages=['swmmtoolbox'],
      package_dir={'': '.'},
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      entry_points={
          'console_scripts':
              ['swmmtoolbox=swmmtoolbox.swmmtoolbox:main']
      }
      )
