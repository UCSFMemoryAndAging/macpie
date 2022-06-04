from setuptools import setup

# cli packages
mpsql = ["mysql-connector-python >= 8.0", "python-dotenv >= 0.20", "SQLAlchemy >= 1.3"]
mpfile = ["tabulate >= 0.8"]
cli = mpsql + mpfile

# misc packages
misc = ["matplotlib >= 3.5", "networkx >= 2.8"]

# all packages
all = cli + misc

setup(
    name="macpie",
    install_requires=[
        "click >= 8.0",
        "openpyxl >= 3.0",
        "pandas >= 1.3",
        "tablib >= 3.0",
        "XlsxWriter >= 3.0",
    ],
    extras_require={"mpsql": mpsql, "mpfile": mpfile, "cli": cli, "all": all},
)
