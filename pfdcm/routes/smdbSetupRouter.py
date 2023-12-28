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


# import  logging
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
    response_model  = dict,
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
    '/SMDB/FS/',
    response_model  = smdbSetupModel.SMDBFsReturnModel,
    summary         = '''
    POST an update to a FS storage resource in the pypx SMDB object''',
)
async def SMDBobj_fsUpdate(
        fsData   : smdbSetupModel.SMDBFsConfig
):
    """
    Update a FS storage resource within the SMDB module.

    Parameters
    ----------
    - `FSData`:      an object with a name that defines a swift resource

    Return
    ------
    - updated `FSData`
    """
    return smdbSetupController.fsData_update(fsData)

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
    "/SMDB/storage/list/",
    response_model  = List,
    summary         = "GET the list of configured SMDB storage services"
)
async def storageList_get():
    """
    GET the list of configured SMDB storage services
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
    "/SMDB/storage/{storageResource}/",
    response_model  = dict,
    summary         = "GET detail on a specific storage resource"
)
async def storageResource_get(
    storageResource : str
):
    """
    GET detail info on a given SMDB storage resource
    """
    return smdbSetupController.swiftObject_get(storageResource)

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

