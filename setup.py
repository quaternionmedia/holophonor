from setuptools import setup, find_packages

setup(
    name='holophonor',
    install_requires=['pluggy >= 1.0, < 1.1', 'python-rtmidi >= 1.4.9, < 1.5'],
    entry_points={'console_scripts': ['holophonor=holophonor.main:main']},
    packages=find_packages(),
)
