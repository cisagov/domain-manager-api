"""
This is the setup module for the example project.

Based on:

- https://packaging.python.org/distributing/
- https://github.com/pypa/sampleproject/blob/master/setup.py
- https://blog.ionelmc.ro/2014/05/25/python-packaging/#the-structure
"""

# Standard Python Libraries
import codecs
from glob import glob
from os.path import abspath, basename, dirname, join, splitext

# Third-Party Libraries
from setuptools import find_packages, setup


def readme():
    """Read in and return the contents of the project's README.md file."""
    with open("README.md", encoding="utf-8") as f:
        return f.read()


# Below two methods were pulled from:
# https://packaging.python.org/guides/single-sourcing-package-version/
def read(rel_path):
    """Open a file for reading from a given relative path."""
    here = abspath(dirname(__file__))
    with codecs.open(join(here, rel_path), "r") as fp:
        return fp.read()


def get_version(version_file):
    """Extract a version number from the given file path."""
    for line in read(version_file).splitlines():
        if line.startswith("__version__"):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    raise RuntimeError("Unable to find version string.")


setup(
    name="example",
    # Versions should comply with PEP440
    version=get_version("src/_version.py"),
    description="Example Python library",
    long_description=readme(),
    long_description_content_type="text/markdown",
    # Landing page for CISA's cybersecurity mission
    url="https://www.cisa.gov/cybersecurity",
    # Additional URLs for this project per
    # https://packaging.python.org/guides/distributing-packages-using-setuptools/#project-urls
    project_urls={
        "Source": "https://github.com/cisagov/skeleton-python-library",
        "Tracker": "https://github.com/cisagov/skeleton-python-library/issues",
    },
    # Author details
    author="Cybersecurity and Infrastructure Security Agency",
    author_email="github@cisa.dhs.gov",
    license="License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication",
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 3 - Alpha",
        # Indicate who your project is intended for
        "Intended Audience :: Developers",
        # Pick your license as you wish (should match "license" above)
        "License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication",
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.6",
    # What does your project relate to?
    keywords="skeleton",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    package_data={"example": ["data/*.txt"]},
    py_modules=[splitext(basename(path))[0] for path in glob("src/*.py")],
    include_package_data=True,
    install_requires=[
        "2captcha-python>=1.0.3",
        "appdirs>=1.4.4",
        "appnope>=0.1.0",
        "attrs>=20.3.0",
        "backcall>=0.2.0",
        "bcrypt>=3.2.0",
        "beautifulsoup4>=4.9.1",
        "boto3>=1.14.39",
        "botocore>=1.17.63",
        "certifi>=2020.12.5",
        "cffi>=1.14.4",
        "cfgv>=3.2.0",
        "chardet>=3.0.4",
        "click>=7.1.2",
        "cognitojwt>=1.2.2",
        "cryptography>=3.3.2",
        "decorator>=4.4.2",
        "distlib>=0.3.1",
        "dnspython>=2.1.0",
        "docutils>=0.15.2",
        "ecdsa>=0.14.1",
        "Faker>=5.8.0",
        "filelock>=3.0.12",
        "Flask>=1.1.2",
        "Flask-Cors>=3.0.9",
        "gunicorn>=20.0.4",
        "identify>=1.5.5",
        "idna>=2.10",
        "iniconfig>=1.1.1",
        "ipdb>=0.13.4",
        "ipython>=7.18.1",
        "ipython-genutils>=0.2.0",
        "itsdangerous>=1.1.0",
        "jedi>=0.17.2",
        "Jinja2>=2.11.3",
        "jmespath>=0.10.0",
        "MarkupSafe>=1.1.1",
        "marshmallow>=3.7.1",
        "mccabe>=0.6.1",
        "mongomock>=3.22.0",
        "mypy-extensions>=0.4.3",
        "nodeenv>=1.5.0",
        "packaging>=20.9",
        "paramiko>=2.7.2",
        "parso>=0.7.1",
        "pathspec>=0.8.0",
        "pexpect>=4.8.0",
        "pickleshare>=0.7.5",
        "pluggy>=0.13.1",
        "prompt-toolkit>=3.0.8",
        "ptyprocess>=0.6.0",
        "py>=1.10.0",
        "pyasn1>=0.4.8",
        "pycodestyle>=2.6.0",
        "pycparser>=2.20",
        "pyflakes>=2.2.0",
        "Pygments>=2.7.4",
        "pymongo>=3.11.1",
        "PyNaCl>=1.4.0",
        "pyparsing>=2.4.7",
        "python-dateutil>=2.8.1",
        "python-dotenv>=0.14.0",
        "python-jose>=3.2.0",
        "PyYAML>=5.4",
        "regex>=2020.10.11",
        "requests>=2.24.0",
        "rsa>=4.7",
        "s3transfer>=0.3.4",
        "selenium>=3.141.0",
        "sentinels>=1.0.0",
        "six>=1.15.0",
        "soupsieve>=2.1",
        "sshtunnel>=0.3.1",
        "text-unidecode>=1.3",
        "toml>=0.10.1",
        "traitlets>=5.0.5",
        "TwoCaptcha>=0.0.1",
        "typed-ast>=1.4.1",
        "typing-extensions>=3.7.4.3",
        "undetected-chromedriver>=2.1.2",
        "urllib3>=1.25.11",
        "validators>=0.18.2",
        "wcwidth>=0.2.5",
        "Werkzeug>=1.0.1",
    ],
    extras_require={
        "test": [
            "black",
            "coverage",
            "flake8",
            "moto",
            "pre-commit",
            "pytest",
            "pytest-cov",
            "pytest-dockerc",
            "pytest-dotenv",
            "pytest-env",
            "pytest-mock",
            "pytest-pythonpath",
        ]
    },
    # Conveniently allows one to run the CLI tool as `example`
    entry_points={"console_scripts": ["example = example.example:main"]},
)
