"""
Copyright 2020 Lightbend Inc.
Licensed under the Apache License, Version 2.0.
"""

from setuptools import setup, find_packages

# Load version in cloudstate package.
exec(open('cloudstate/version.py').read())
version = __version__
name = 'cloudstate'

print(f'package name: {name}, version: {version}', flush=True)

setup(name=name,
      version=version,
      url='https://github.com/cloudstateio/python-support',
      license='Apache 2.0',
      description='Cloudstate Python Support Library',
      packages=find_packages(exclude=['tests', 'shoppingcart']),
      long_description=open('Description.md', 'r').read(),
      long_description_content_type='text/markdown',
      zip_safe=False)
