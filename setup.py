import os
from setuptools import setup, find_packages
from distutils.util import convert_path

try:
    # pip >=20
    from pip._internal.network.session import PipSession
    from pip._internal.req import parse_requirements
except ImportError:
    try:
        # 10.0.0 <= pip <= 19.3.1
        from pip._internal.download import PipSession
        from pip._internal.req import parse_requirements
    except ImportError:
        # pip <= 9.0.3
        from pip.download import PipSession
        from pip.req import parse_requirements

here = os.path.abspath(os.path.dirname(__file__))

TWCC_CONFIG = {}
ver_path = convert_path('twccli/version.py')
with open(ver_path) as ver_file:
    exec(ver_file.read(), TWCC_CONFIG)


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

try:
    # for pip >= 10
    from pip._internal.req import parse_requirements
except ImportError:
    # for pip <= 9.0.3
    from pip.req import parse_requirements

def load_requirements(fname):
    reqs = parse_requirements(fname, session="test")
    return [str(ir.req) for ir in reqs]

reqs = [
        'netaddr',
        'pytz',
        'boto3==1.11.17',
        'botocore==1.14.17',
        'certifi==2019.11.28',
        'chardet==3.0.4',
        'Click==7.0',
        'colorclass==2.2.0',
        'docutils==0.15.2',
        'idna==2.8',
        'jmespath==0.9.4',
        'prompt-toolkit',
        'Pygments==2.5.2',
        'python-dateutil==2.8.1',
        'PyYAML==5.3',
        'regex==2020.1.8',
        'requests==2.22.0',
        's3transfer==0.3.3',
        'six==1.14.0',
        'termcolor==1.1.0',
        'terminaltables==3.1.0',
        'tqdm==4.42.1',
        'urllib3==1.25.8',
        'wcwidth==0.1.8']

long_desc = open("README.md", 'r').read()
print(long_desc)
setup(
    name='TWCC-CLI',
    author="TWCC SREr",
    author_email="isupport@narlabs.org.tw",
    description="TWCC-CLI is a toolkit for operating TWCC resources.",
    long_description=long_desc,
    version=TWCC_CONFIG['__version__'],
    py_modules=['twccli'],
    packages=find_packages(),
    install_requires= reqs,
    include_package_data=True,
    license="Apache License 2.0",
    url="https://github.com/TW-NCHC/TWCC-CLI",
    entry_points='''
        [console_scripts]
        twccli=twccli.twccli:cli
    ''',
    package_data={
        "twccli": ["yaml/*yaml", "commands/*py"],
        "":["requirements.txt"],
    },
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.7',
    ],
    zip_safe=True,
)
