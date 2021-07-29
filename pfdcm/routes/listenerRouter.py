str_description = """
    This route module handles logic pertaining to service
    infrastructure creation/instantiation.
"""


from    fastapi             import  APIRouter, Query
from    fastapi.encoders    import  jsonable_encoder
from    typing              import  List, Dict

from    models              import  listenerModel
from    controllers         import  listenerController

from    datetime            import  datetime
import  config

import  logging
from    pflogf              import  FnndscLogFormatter

# pfstorage local dependencies
import  pfmisc
from    pfmisc.C_snode      import  *
import  pfstate
from    pfstate             import  S

router          = APIRouter()
router.tags     = ['listener subsystem services']

@router.get(
    "/listener/list/",
    response_model  = List,
    summary         = "GET the list of configured listener services"
)
async def serviceList_get():
    """
    GET the list of configured PACS services
    """
    return listenerController.internalObjects_getList()

@router.post(
    '/listener/initialize/',
    summary         = 'POST a signal to the listener `objToInitialize`, triggering a self initialization',
)
async def listener_initialize(
        objToInitialize : listenerModel.ValueStr
) -> dict:
    """
    Initialize the listener service for the object __objToInitialize__.

    Parameters
    ----------
    - `objToInitialize`:    name of the listener object to initialize

    Return
    ------
    - dictionary response from the initialization process

    NOTE: A return / response model is not specified since the return from the 
    call is variable.
    """
    return listenerController.obj_initialize(objToInitialize)

@router.get(
    "/listener/status/{listenerObjName}/",
    response_model  = listenerModel.ListenerHandlerStatus,
    summary         = "GET the listener subsystem status of a given listener object"
)
async def listenerStatus_get(listenerObjName: str):
    """
    GET the listener susystem information pertinent to a `listenerObjName`.
    This information indicates if the subsystem has been initialized and
    therefore if it is ready to accept incoming data.

    (for a list of valid `listenerObjName` GET the `serviceList`)
    """
    return listenerController.internalObject_getStatus(listenerObjName)


@router.get(
    "/listener/{listenerObjName}/",
    response_model  = listenerModel.listenerDBreturnModel,
    summary         = "GET information for a given listener object"
)
async def listener_get(listenerObjName: str):
    """
    GET the information pertinent to a `listenerObjName`

    (for a list of valid `listenerObjName` GET the `serviceList`)
    """
    return listenerController.internalObject_get(listenerObjName)

@router.put("/listener/{listenerObjName}/xinetd/",
    response_model  = listenerModel.XinetdDBReturnModel,
    summary         = "PUT an xinetd update"
)
async def item_putXinetd(
    listenerObjName : str,
    xinetdInfo      : listenerModel.XinetdDBPutModel
):
    """
    PUT an entire xinetd object. If the object already exists, overwrite.
    If it does not exist, append to the space of available objects.

    Note that overwriting an existing object will replace ALL the
    `info` fields, thus leaving a default of `"string"` will literally
    put the text `string` for a specific field.

    Parameters
    ----------

    - `listenerObjName` : internal name of (new) object
    - `xinetdInfo`      : new values for object internals

    """
    return listenerController.service_update(listenerObjName, 'xinetd', xinetdInfo)

@router.put("/listener/{listenerObjName}/dcmtk/",
    response_model  = listenerModel.DcmtkDBReturnModel,
    summary         = "PUT a dcmtk update"
)
async def item_putDcmtk(
    listenerObjName : str,
    dcmtkInfo       : listenerModel.DcmtkDBPutModel
):
    """
    PUT an entire dcmtk object. If the object already exists, overwrite.
    If it does not exist, append to the space of available objects.

    Note that overwriting an existing object will replace ALL the
    `info` fields, thus leaving a default of `"string"` will literally
    put the text `string` for a specific field.

    Parameters
    ----------

    - `listenerObjName` : internal name of (new) object
    - `dcmtkInfo`       : new values for object internals

    """
    return listenerController.service_update(listenerObjName, 'dcmtk', dcmtkInfo)
