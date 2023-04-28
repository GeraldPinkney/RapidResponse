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
    name="RapidResponse",
    version="2.0.0",
    description="A sample Python project",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/GeraldPinkney/RapidResponse",
    author="GP", # Heraldo Industries
    package_dir={"": "RapidResponse"},
    packages=find_packages(),  # Required
    python_requires=">=3.7, <4",
    install_requires=["requests"],  #  "csv", "logging", "os". all the other stuff is from standard lib
    package_data={  # Optional
        "": ["*.csv"], # includes all csv files (i.e. those data model ones)
        "RapidResponse.DataModel": ["*.csv"], # this would only pick up that stuff in DM dir
    },
)