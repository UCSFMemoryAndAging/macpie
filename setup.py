from setuptools import setup

setup(
    name="macpie",
    install_requires=[
        "click >= 8.0.3",
        "mysql-connector-python >= 8.0.26",
        "openpyxl >= 3.0",
        "pandas >= 1.2",
        "tablib >= 3.0",
    ],
    extras_require={"dotenv": ["python-dotenv"]},
)
