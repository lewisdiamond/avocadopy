from setuptools import setup, find_packages

requires = [
    'requests',
    'six',
]

setup(name='avocadopy',
      version='0.0',
      description='ArangoDB client',
      author='Lewis Diamond',
      author_email='',
      url='',
      keywords='arangodb',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      test_suite="avocadopy.tests",
      )
