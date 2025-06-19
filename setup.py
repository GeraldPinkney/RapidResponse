"""
See:
https://github.com/GeraldPinkney/RapidResponse
"""

from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / "RapidResponse/docs/README.md").read_text(encoding="utf-8")


setup(
    name="RapidResponse",
    version="1.0.15",
    description="RapidResponse library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/GeraldPinkney/RapidResponse",
    author="Heraldo Industries",  # Heraldo Industries
    packages=find_packages(),  # Required include=['RapidResponse']
    #package_dir={"": "."},
    python_requires=">=3.10, <4",
    install_requires=["requests>=2.31.0", "httpx", "setuptools>=70"],
    # "csv", "logging", "os". all the other stuff is from standard lib
    include_package_data=True,
    package_data={  # Optional
        "": ["data/*.tab", "data/*.wwb", "docs/*.md"], # includes all tab files (i.e. those data model ones), and the wbb for data model bootstrapping
    },
    test_suite='tests',
)