str_description = """
    The main module for the service handler/system.

    This essentially creates the fastAPI app and adds
    route handlers.
"""

from    fastapi             import FastAPI
from    base.router         import helloRouter_create
from    routes.dicom        import router   as dicom_router
from    routes.xinetdRouter import router   as xinetd_router
from    routes.pacs         import router   as pacs_router
from    routes.foobarRouter import router   as foobar_router
from    os                  import path

import  pfstate
from    pfstate         import  S

with open(path.join(path.dirname(path.abspath(__file__)), 'ABOUT')) as f:
    str_about       = f.read()

with open(path.join(path.dirname(path.abspath(__file__)), 'VERSION')) as f:
    str_version     = f.read().strip()



app = FastAPI(
    title   = 'pfdcm',
    version = str_version
)

hello_router = helloRouter_create(
    name    = 'pfdcm_hello',
    version = str_version,
    about   = str_about
)

app.include_router( foobar_router,
                    prefix  = '/api/v1')

app.include_router( hello_router,
                    prefix='/api/v1')

app.include_router( dicom_router,
                    prefix='/api/v1')

app.include_router( xinetd_router,
                    prefix='/api/v1')

app.include_router( pacs_router,
                    prefix='/api/v1')
