from setuptools import setup

# cli packages
mpsql_cli = ["mysql-connector-python >= 8.0", "SQLAlchemy >= 1.3"]
all_cli = mpsql_cli

# misc packages
misc = ["matplotlib >= 3.5", "networkx >= 2.8"]

# all packages
all = all_cli + misc

setup(
    name="macpie",
    install_requires=[
        "pandas >= 1.3, < 2.0.0",
        "click >= 8.0",
        "openpyxl >= 3.0",
        "XlsxWriter >= 3.0",
        "python-dotenv >= 0.20",
        "tablib >= 3.0",
        "tabulate >= 0.8",
        "packaging",
    ],
    extras_require={"mpsql": mpsql_cli, "all_cli": all_cli, "all": all},
)
