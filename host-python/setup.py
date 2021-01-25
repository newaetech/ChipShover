from setuptools import setup, find_packages

# read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='chipshover',
    version='0.2.1',
    url='https://github.com/newaetech/ChipShover',
    author='NewAE Technology Inc.',
    author_email='coflynn@newae.com',
    description='XYZ Controller Interface for ChipShover.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    install_requires=['pyserial >= 3.4'],
    project_urls={
        'Documentation': 'https://chipshover.readthedocs.io',
        'Source': 'https://github.com/newaetech/chipshover',
        'Issue Tracker': 'https://github.com/newaetech/chipshover/issues',
    },
)
