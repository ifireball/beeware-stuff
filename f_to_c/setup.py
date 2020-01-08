#!/usr/bin/env python
import io
import re
from setuptools import setup, find_packages
import sys

with io.open('./f_to_c/__init__.py', encoding='utf8') as version_file:
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file.read(), re.M)
    if version_match:
        version = version_match.group(1)
    else:
        raise RuntimeError("Unable to find version string.")


with io.open('README.rst', encoding='utf8') as readme:
    long_description = readme.read()


setup(
    name='f_to_c',
    version=version,
    description='Convert temepratures from Fahrenheit to Celsius',
    long_description=long_description,
    author='Jane Developer',
    author_email='jane@example.com',
    license='BSD license',
    packages=find_packages(
        exclude=[
            'docs', 'tests',
            'windows', 'macOS', 'linux',
            'iOS', 'android',
            'django'
        ]
    ),
    classifiers=[
        'Development Status :: 1 - Planning',
        'License :: OSI Approved :: BSD license',
    ],
    install_requires=[
    ],
    options={
        'app': {
            'formal_name': 'Fahrenheit to Celsius',
            'bundle': 'com.example'
        },

        # Desktop/laptop deployments
        'macos': {
            'app_requires': [
                'toga-cocoa==0.3.0.dev15',
            ]
        },
        'linux': {
            'app_requires': [
                'toga-gtk==0.3.0.dev15',
            ]
        },
        'windows': {
            'app_requires': [
                'toga-winforms==0.3.0.dev15',
            ]
        },

        # Mobile deployments
        'ios': {
            'app_requires': [
                'toga-ios==0.3.0.dev15',
            ]
        },
        'android': {
            'app_requires': [
                'toga-android==0.3.0.dev15',
            ]
        },

        # Web deployments
        'django': {
            'app_requires': [
                'toga-django==0.3.0.dev15',
            ]
        },
    }
)
