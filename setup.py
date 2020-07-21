import sys
from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))


if sys.version_info < (3, 4):
    sys.exit('Sorry, Python < 3.4 is not supported')

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
      name='enedis-api',
      version='0.0.1',
      description='Get your consumption data from your Enedis account (www.enedis.fr)',
      long_description=long_description,
      author='HACF-FR (Quentin POLLET)',
      author_email='polletquentin74@me.com',
      url='https://github.com/hacf-fr/enedis-api',
      package_data={'': ['LICENSE']},
      include_package_data=True,
      packages=find_packages(),
      entry_points={
          'console_scripts': [
              'enedis-api = enedis.__main__:main'
          ]
      },
      license='Apache 2.0',
      install_requires=['python-dateutil', 'requests', 'simplejson', 'requests_oauthlib', 'oauthlib'],
      classifiers=[
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
      ]
)
