#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='tower-web',
      version='1.0.0',
      description='Browser-based GCS.',
      author='Hanno Blankenstein',
      author_email='hannoblankenstein@gmail.com',
      url='https://github.com/hblanken/tower-web.git',
      install_requires=[
          'Flask>=0.10.1',
          'requests>=2.5.1',
          'wheel>=0.24.0',
          'dronekit>=2.0.0,<=2.99999',
      ],
      package_data={
          'tower': [
              'static/images/*',
              'static/scripts/*',
              'templates/*',
          ],
      },
      entry_points={
          'console_scripts': [
              'galacsian = tower.__main__:main',
              'tower = tower.__main__:main',
          ]
      },
      packages=['tower'])
