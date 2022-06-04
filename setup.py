from setuptools import setup

dotenv = ["python-dotenv"]
mpsql = ["mysql-connector-python >= 8.0", "SQLAlchemy >= 1.3"]
mpfile = ["tabulate >= 0.8"]
cli = dotenv + mpsql + mpfile
all = cli

setup(
    name="macpie",
    install_requires=[
        "click >= 8.0",
        "openpyxl >= 3.0",
        "pandas >= 1.3",
        "tablib >= 3.0",
        "XlsxWriter >= 3.0",
    ],
    extras_require={"dotenv": dotenv, "mpsql": mpsql, "mpfile": mpfile, "cli": cli, "all": all},
)
