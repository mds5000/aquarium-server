from setuptools import setup, find_packages

setup(
    name="aquarium-server",
    packages=find_packages(),
    entry_points={
          'console_scripts': [
              'backend_server = backend.app:main'
          ]
    }
)