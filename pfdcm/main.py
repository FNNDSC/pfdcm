str_description = """
"""

from fastapi        import FastAPI
from base.router    import helloRouter_create
from routes.dicom   import router as dicom_router
from os             import path

with open(path.join(path.dirname(path.abspath(__file__)), 'ABOUT')) as f:
    str_about       = f.read()

with open(path.join(path.dirname(path.abspath(__file__)), 'VERSION')) as f:
    str_version     = f.read().strip()

# __version__ = '1.0.0'


hello_router = helloRouter_create(
    name    = 'pfdcm_hello',
    version = str_version,
    about   = str_about
)

app = FastAPI(
    title   = 'pfdcm',
    version = str_version
)

app.include_router(hello_router,
                   prefix='/api/v1')

app.include_router(dicom_router,
                   prefix='/api/v1')
