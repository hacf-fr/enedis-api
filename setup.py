import sys
from setuptools import setup, find_packages
from codecs import open
from os import path

REPO_URL = "https://github.com/hacf-fr/enedis-api"
VERSION = "0.0.1"

if sys.version_info < (3, 6):
    sys.exit("Sorry, Python < 3.6 is not supported")

with open("requirements.txt") as f:
    required = f.read().splitlines()

with open("README.rst", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="enedis-api",
    version=VERSION,
    url=REPO_URL,
    download_url=REPO_URL + "/tarball/" + VERSION,
    description="Get your consumption data from your Enedis account (www.enedis.fr)",
    long_description=long_description,
    author="HACF-FR (Quentin POLLET)",
    author_email="polletquentin74@me.com",
    package_data={"": ["LICENSE"]},
    include_package_data=True,
    packages=find_packages(),
    entry_points={"console_scripts": ["enedis-api = enedis.__main__:main"]},
    license="Apache 2.0",
    install_requires=required,
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License"
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
)
