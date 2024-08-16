#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re
import sys
from setuptools import setup, find_packages

__version__ = ''
with open('threads/__version__.py', 'r') as fd:
    reg = re.compile(r'__version__ = [\'"]([^\'"]*)[\'"]')
    for line in fd:
        m = reg.match(line)
        if m:
            __version__ = m.group(1)
            break




this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    readme = f.read()

setup(
    name='threads-sdk',
    version=__version__,
    description='Using Threads API more easily',
    url='https://github.com/louis70109/threads-sdk',
    author='NiJia Lin',
    author_email='louis70109@gmail.com',
    maintainer="NiJia Lin",
    maintainer_email="louis70109@gmail.com",
    long_description=readme,
    long_description_content_type="text/markdown",
    keywords='Threads SDK',
    license='MIT',
    packages=find_packages(exclude=['tests']),
    install_requires=["requests>=2.0"],
    python_requires='!=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*',
    project_urls={
        'Bug Reports': 'https://github.com/louis70109/lotify/issues',
        'Source': 'https://github.com/louis70109/threads-sdk',
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        'License :: OSI Approved :: MIT License',
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development"
    ]
)
