from setuptools import setup, find_packages

setup(
    name='chipshover',
    version='0.1.2',
    url='https://github.com/newaetech/ChipSHOVER',
    author='NewAE Technology Inc.',
    author_email='coflynn@newae.com',
    description='XY(Z) Controller Interface for ChipShover.',
    packages=find_packages(),
    install_requires=['pyserial >= 3.4'],
)