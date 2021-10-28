import re

from setuptools import setup

with open("src/macpie/__init__.py", encoding="utf8") as f:
    version = re.search(r'__version__ = "(.*?)"', f.read()).group(1)

setup(
    name="macpie",
    version=version,
    install_requires=[
        "click >= 8.0.3",
        "mysql-connector-python >= 8.0.26",
        "openpyxl >= 3.0",
        "pandas >= 1.2",
        "tablib >= 3.0",
    ],
    extras_require={"dotenv": ["python-dotenv"]},
)
