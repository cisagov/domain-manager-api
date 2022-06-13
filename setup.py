"""
This is the setup module for the Domain Manager API project.

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
    name="domain-manager-api",
    # Versions should comply with PEP440
    version=get_version("src/api/_version.py"),
    description="Domain Manager API Flask Python library",
    long_description=readme(),
    long_description_content_type="text/markdown",
    # Landing page for CISA's cybersecurity mission
    url="https://www.cisa.gov/cybersecurity",
    # Additional URLs for this project per
    # https://packaging.python.org/guides/distributing-packages-using-setuptools/#project-urls
    project_urls={
        "Source": "https://github.com/cisagov/domain-manager-api",
        "Tracker": "https://github.com/cisagov/domain-manager-api/issues",
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
    keywords="domains",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    py_modules=[splitext(basename(path))[0] for path in glob("src/*.py")],
    include_package_data=True,
    install_requires=[
        "APScheduler==3.9.1",
        "boto3==1.21.20",
        "cognitojwt==1.4.1",
        "dnspython==2.2.1",
        "Faker==13.13.0",
        "Flask==2.0.3",
        "Flask-Cors==3.0.10",
        "gunicorn>=20.0.4",
        "marshmallow>=3.13.0",
        "mongomock==4.0.0",
        "pymongo>=3.11.1",
        "requests>=2.24.0",
        "validators>=0.18.2",
    ],
    extras_require={
        "test": [
            "black",
            "coverage",
            # coveralls 1.11.0 added a service number for calls from
            # GitHub Actions. This caused a regression which resulted in a 422
            # response from the coveralls API with the message:
            # Unprocessable Entity for url: https://coveralls.io/api/v1/jobs
            # 1.11.1 fixed this issue, but to ensure expected behavior we'll pin
            # to never grab the regression version.
            "coveralls != 1.11.0",
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
    entry_points={"console_scripts": ["dm-api=api.main"]},
)
