#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'auth0plus',
    'auth0-python',
]

setup(
    name='auth0db',
    version='0.1.0',
    description="Auth0 authentication backend for Django",
    long_description=readme + '\n\n' + history,
    author="Brett Haydon",
    author_email='brett@haydon.id.au',
    url='https://github.com/bretth/auth0db',
    packages=[
        'auth0db',
    ],
    package_dir={'auth0db':
                 'auth0db'},
    include_package_data=True,
    install_requires=requirements,
    license="ISCL",
    zip_safe=False,
    keywords='auth0db',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ]
)
