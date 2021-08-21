import pathlib

try:
    import dotenv
except ImportError:
    dotenv = None

if dotenv:
    home_path = pathlib.Path.home()
    dotenv.load_dotenv(home_path / ".macpieenv")
