from setuptools import setup, find_packages

setup(
    name='holophonor',
    install_requires='pluggy>=0.3,<1.0',
    entry_points={'console_scripts': ['holophonor=holophonor.main:main']},
    packages=find_packages(),
)