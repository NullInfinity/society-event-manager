"""The setup module for socman."""

import codecs
import os
import setuptools

FILEPATH = os.path.abspath(os.path.dirname(__file__))
with codecs.open(os.path.join(FILEPATH, 'README.md'), encoding='utf-8') as f:
    LONG_DESCRIPTION = f.read()

setuptools.setup(
    name='socman',
    version='0.1.0-dev',
    description='A Python library for society and membership management',
    long_description=LONG_DESCRIPTION,
    url='https://github.com/NullInfinity/socman/',
    author='Alex Thorne',
    author_email='alex@alexthorne.net',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Indended Audience :: Developers',
        'Topic :: Office/Business',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        ],
    keywords='society group membership',
    py_modules=['socman'],
    )
