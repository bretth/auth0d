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

]

setup(
    name='django-auth0',
    version='0.1.0',
    description="Auth0 authentication backend for Django",
    long_description=readme + '\n\n' + history,
    author="Brett Haydon",
    author_email='brett@haydon.id.au',
    url='https://github.com/bretth/auth0d',
    packages=[
        'auth0d',
    ],
    package_dir={'auth0d':
                 'auth0d'},
    include_package_data=True,
    install_requires=requirements,
    license="ISCL",
    zip_safe=False,
    keywords='django-auth0',
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
