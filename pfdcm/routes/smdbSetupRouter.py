str_description = """
    This route module handles logic pertaining to associating
    routes to actual logic in the controller module. For the
    most part, this module mostly has route method defintions
    and UI swagger for documentation.

    In most methods, the actual logic is simply a call out
    to the real method in the controller module that performs
    the application logic as well as any surface contact with
    the DB module/service.
"""


from    fastapi             import  APIRouter, Query
from    fastapi.encoders    import  jsonable_encoder
from    typing              import  List, Dict

from    models              import  smdbSetupModel
from    controllers         import  smdbSetupController

from    datetime            import  datetime
import  config


import  logging
from    pflogf              import  FnndscLogFormatter

# pfstorage local dependencies
import  pfmisc
from    pfmisc.C_snode      import  *
import  pfstate
from    pfstate             import  S

import  pudb

router          = APIRouter()
router.tags     = ['SMDB setup services']

@router.post(
    '/SMDB/swift/',
    response_model  = smdbSetupModel.SMDBswiftReturnModel,
    summary         = '''
    POST an update to a swift resource in the pypx SMDB object''',
)
async def SMDBobj_swiftUpdate(
        swiftData   : smdbSetupModel.SMDBswiftConfig
):
    """
    Update a swift resource within the SMDB module.

    Parameters
    ----------
    - `swiftData`:      an object with a name that defines a swift resource

    Return
    ------
    - updated `swiftData`
    """
    return smdbSetupController.swiftData_update(swiftData)

@router.post(
    '/SMDB/CUBE/',
    response_model  = smdbSetupModel.SMDBcubeReturnModel,
    summary         = '''
    POST an update to a CUBE resource in the pypx SMDB object''',
)
async def SMDBobj_cubeUpdate(
        cubeData   : smdbSetupModel.SMDBcubeConfig
):
    """
    Update a CUBE resource within the SMDB module.

    Parameters
    ----------
    - `swiftData`:      an object with a name that defines a CUBE resource

    Return
    ------
    - updated `CUBEdata`
    """
    return smdbSetupController.cubeData_update(cubeData)

@router.get(
    "/SMDB/swift/list/",
    response_model  = List,
    summary         = "GET the list of configured SMDB swift services"
)
async def swiftList_get():
    """
    GET the list of configured SMDB swift services
    """
    return smdbSetupController.swiftObjects_getList()

@router.get(
    "/SMDB/CUBE/list/",
    response_model  = List,
    summary         = "GET the list of configured SMDB CUBE services"
)
async def cubeList_get():
    """
    GET the list of configured SMDB CUBE services
    """
    return smdbSetupController.cubeObjects_getList()

@router.get(
    "/SMDB/swift/{swiftResource}/",
    response_model  = smdbSetupModel.SMDBswiftReturnModel,
    summary         = "GET detail on a specific swift resource"
)
async def swiftResource_get(
    swiftResource : str
):
    """
    GET detail info on a given SMDB swift resource
    """
    return smdbSetupController.swiftObject_get(swiftResource)

@router.get(
    "/SMDB/CUBE/{cubeResource}/",
    response_model  = smdbSetupModel.SMDBcubeReturnModel,
    summary         = "GET detail on a specific CUBE resource"
)
async def cubeResource_get(
    cubeResource : str
):
    """
    GET detail info on a given SMDB CUBE resource
    """
    return smdbSetupController.cubeObject_get(cubeResource)

