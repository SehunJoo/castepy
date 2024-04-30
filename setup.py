from setuptools import setup, find_packages

setup(
    name='castepy',
    version='0.0.1',
    packages=find_packages(),
    install_requires=[
        'ase',
        'matplotlib',
        'numpy',
        'pandas'
    ],
    author='Se Hun Joo',
    author_email='shjoo.lab@gmail.com',
    description='Python package for CASTEP'
)

