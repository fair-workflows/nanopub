#!/usr/bin/env python

import codecs
import os.path

from setuptools import setup


def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), 'r') as fp:
        return fp.read()


def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith('__version__'):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")


setup(
    name='nanopub',
    version=get_version('nanopub/_version.py'),
    description='Python client for Nanopub',
    long_description=open("README.md", "r").read(),
    long_description_content_type='text/markdown',
    author='Robin Richardson, Djura Smits, Sven van den Burg',
    author_email='r.richardson@esciencecenter.nl',
    url='https://github.com/fair-workflows/nanopub/',
    install_requires=open("requirements.txt", "r").readlines(),
    packages=['nanopub'],
    data_files=[
        ('lib', ['lib/nanopub-1.32-jar-with-dependencies.jar']),
        ('bin', ['bin/nanopub-java',
                 'bin/nanopub-java.bat'])
    ],
    include_package_data=True,
    entry_points={
        'console_scripts': ['setup_profile=nanopub.setup_profile:main'],
    },
    extras_require={
        'dev': open('requirements-dev.txt', 'r').readlines()
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent"
    ],
    python_requires='>=3.6'
)
