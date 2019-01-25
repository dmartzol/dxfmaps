from setuptools import setup

setup(
	name='dxfmaps',
      version='0.1',
      description='Generates maps from shapefiles',
      url='http://github.com/dmartzol/dxfmaps',
      author='Daniel Martinez',
      author_email='danielmartinezolivas@gmail.com',
      license='MIT',
      packages=['dxfmaps'],
      install_requires=['pyshp', 'Shapely']
	)
