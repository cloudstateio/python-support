from setuptools import setup, find_packages
 
setup(name='cloudstate',
      version='0.1.0',
      url='https://github.com/marcellanz/cloudstate_python-support',
      license='Apache 2.0',
      description='Cloudstate Python Support',
      packages=find_packages(exclude=['tests', 'shoppingcart']),
      long_description=open('README.md').read(),
      zip_safe=False)