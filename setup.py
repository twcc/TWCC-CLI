import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    return codecs.open(os.path.join(here, *parts), 'r').read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


install_requirements = [
    'click',
    'boto3',
    'botocore',
    's3transfer',
    'certifi==2019.11.28',
    'chardet==3.0.4',
    'Click==7.0',
    'colorclass==2.2.0',
    'docutils==0.15.2',
    'idna==2.8',
    'jmespath==0.9.4',
    'prompt-toolkit==1.0.14',
    'Pygments==2.5.2',
    'PyInquirer==1.0.3',
    'python-dateutil==2.7.1',
    'PyYAML==5.1.2',
    'regex==2019.11.1',
    'requests==2.22.0',
    'six==1.13.0',
    'termcolor==1.1.0',
    'terminaltables==3.1.0',
    'tqdm==4.40.0',
    'urllib3==1.25.7',
    'wcwidth==0.1.7',
]

setup(
    name='twccli',
    version='0.1',
    py_modules=['twccli'],
    install_requires=install_requirements,
    packages=find_packages(),
    license="Apache License 2.0",
    entry_points='''
        [console_scripts]
        twccli=twccli.examples.twccli:cli
    ''',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
)
