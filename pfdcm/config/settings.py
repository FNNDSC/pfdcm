from    pydantic            import BaseSettings
from    pathlib             import Path

class App(BaseSettings):
    baseDir:Path            = Path("/home/dicom/")

appsettings:App             = App()
