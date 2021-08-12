import os
from setuptools import setup, find_packages
from distutils.util import convert_path
import sys
import subprocess
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

reqs = open(convert_path("requirements.txt"), 'r').readlines()

long_desc = open("README.md", 'r').read()
setup(
    name='TWCC-CLI',
    author="TWS TWCC-CLI Team",
    author_email="isupport@twcc.ai",
    description="TWCC-CLI is a toolkit for operating TWCC resources.",
    long_description=long_desc,
    long_description_content_type="text/markdown",
    version=TWCC_CONFIG['__version__'],
    py_modules=['twccli'],
    packages=find_packages(),
    install_requires= reqs,
    license="Apache License 2.0",
    url="https://github.com/TW-NCHC/TWCC-CLI",
    entry_points='''
        [console_scripts]
        twccli=twccli.twccli:cli
    ''',
    package_data={
        "twccli": ["yaml/*yaml", "commands/*py"],
    },
    include_package_data=True,
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    zip_safe=True,
)