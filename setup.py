import re

from setuptools import setup

with open("src/macpie/__init__.py", encoding="utf8") as f:
    version = re.search(r'__version__ = "(.*?)"', f.read()).group(1)

setup(
    name="macpie",
    version=version,
    install_requires=[
        "click>=7.1.2",
        "networkx>=2.5",
        "openpyxl>=3.0.5",
        "pandas>=1.1.2",
    ],
    extras_require={
        "dev": [
            "coverage",
            "pytest",
            "sphinx"
            "tox",
        ]
    },
)
