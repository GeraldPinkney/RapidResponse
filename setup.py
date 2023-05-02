"""A setuptools based setup module.
See:
https://packaging.python.org/guides/distributing-packages-using-setuptools/
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / "README.md").read_text(encoding="utf-8")

# Arguments marked as "Required" below must be included for upload to PyPI.
# Fields marked as "Optional" may be commented out.

setup(
    name="RapidPy",
    version="0.0.4",
    description="A sample Python project",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/GeraldPinkney/RapidResponse",
    author="GP", # Heraldo Industries
    packages=find_packages(include=['RapidResponse']),  # Required
    python_requires=">=3.7, <4",
    install_requires=["requests"],  #  "csv", "logging", "os". all the other stuff is from standard lib
    include_package_data=True,
    package_data={  # Optional
        "": ["data/*.tab"], # includes all csv files (i.e. those data model ones)
        "RapidResponse.data": ["*.tab"], # this would only pick up that stuff in DM dir
    },
    test_suite='tests',
)