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

from    models              import  pacsSetupModel
from    controllers         import  pacsSetupController

from    datetime            import  datetime
import  config


#import  logging
from    pflogf              import  FnndscLogFormatter

# pfstorage local dependencies
import  pfmisc
from    pfmisc.C_snode      import  *
import  pfstate
from    pfstate             import  S

router          = APIRouter()
router.tags     = ['PACS setup services']

@router.post(
    '/PACSservice/port/',
    response_model  = pacsSetupModel.PACSdbReturnModel,
    summary         = '''
    POST a change to the listener `port` of the PACS `objToUpdate`''',
)
async def PACSobj_portUpdate(
        objToUpdate : pacsSetupModel.ValueStr,
        newPort     : pacsSetupModel.ValueStr
):
    """
    Update the `server_port` of a given __objToUpdate__. This method is
    more exemplar than actually useful.

    Parameters
    ----------
    - `objToUpdate`:    name of the internal PACS object to update
    - `newPort`:        port value string to re-assign in the internal object

    Return
    ------
    - updated model of the `objToUpdate`
    """
    return pacsSetupController.obj_portUpdate(objToUpdate, newPort)

@router.get(
    "/PACSservice/list/",
    response_model  = List,
    summary         = "GET the list of configured PACS services"
)
async def serviceList_get():
    """
    GET the list of configured PACS services
    """
    # pudb.set_trace()
    return pacsSetupController.internalObjects_getList()

@router.get(
    "/PACSservice/{PACSobjName}/",
    response_model  = pacsSetupModel.PACSdbReturnModel,
    summary         = "GET the information for a given PACS"
)
async def pacsSetup_get(
    PACSobjName: str
):
    """
    GET the setup info pertinent to a `pacsSetup`
    """
    return pacsSetupController.internalObject_get(PACSobjName)

@router.put(
    "/PACSservice/{PACSobjName}/",
    response_model  = pacsSetupModel.PACSdbReturnModel,
    summary         = "PUT information to a (possibly new) PACS object"
)
async def pacsSetup_put(
    PACSobjName     : str,
    PACSsetupData   : pacsSetupModel.PACSdbPutModel
):
    """
    PUT an entire object. If the object already exists, overwrite.
    If it does not exist, append to the space of available objects.

    Note that overwriting an existing object will replace ALL the
    `info` fields, thus leaving a default of `"string"` will literally
    put the text `string` for a specific field.

    Parameters
    ----------

    - `PACSobjName`     : internal name of (new) object
    - `PACSsetupData`   : new values for object internals

    """
    return pacsSetupController.service_update(PACSobjName, PACSsetupData)
