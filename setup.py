import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


setup(
    name='twccli',
    version='0.2',
    py_modules=['twccli'],
    packages=find_packages(),
    license="Apache License 2.0",
    entry_points='''
        [console_scripts]
        twccli=twccli.examples.twccli:cli
    ''',
    package_data={
        "twccli": ["yaml/*yaml"],
    },
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.7',
    ],
)
