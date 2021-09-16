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


from    fastapi             import  APIRouter, Query, HTTPException, BackgroundTasks
from    fastapi.encoders    import  jsonable_encoder
from    typing              import  List, Dict

from    models              import  pacsQRmodel
from    controllers         import  pacsQRcontroller

from    datetime            import datetime, timezone
import  pudb

router          = APIRouter()
router.tags     = ['PACS QR services']

@router.post(
    '/PACS/thread/pypx/',
    response_model  = pacsQRmodel.PACSasync,
    summary         = '''
    Use this API route for RETRIEVE, PUSH, REGISTER operations and any others
    that might be possibly "long lived". The actual processing is dispatched
    to a separate thread so that the client receives a return immediately.
    Clients should use a STATUS request on the same payload to determine
    realtime status of the operation.
    '''
)
async def PACS_serviceThreaded(
        PACSservice         : pacsQRmodel.ValueStr,
        listenerService     : pacsQRmodel.ValueStr,
        PACSdirective       : pacsQRmodel.PACSqueryCore
):
    """
    POST a `PACSdirective` to the `PACSservice`, and capture return comms
    using the `listenerService`. The actual retrieve call is submitted using
    the python `concurrent.futures` module so that the client receives an
    immediate return.

    This API endpoint is provided so that clients can call a `pfdcm` operation
    and not block the fast API single event queue on a long-lived/long-compute
    call.

    Use a POST to the `sync/pypx` endpoint, typically with a `status`
    directive, to get information on the actual operation.

    Parameters
    ----------
    - `PACSservice`:        name of the internal PACS service to query
    - `listenerService`:    name of the listener service to use locally
    - `PACSdirective`:      the directive object

    Return
    ------
    - PACSasync object
    """

    # --> historical legacy for possible reference
    # background_tasks.add_task(  pacsQRcontroller.pypx_asyncDo,
    #                             PACSservice.value,
    #                             listenerService.value,
    #                             PACSdirective
    #                         )
    future = pacsQRcontroller.pypx_threadedDo(
                                PACSservice.value,
                                listenerService.value,
                                PACSdirective
                            )
    return {
            "directiveType"         : "threaded",
            "response"              : {
                'future.done'   : future.done(),
                'note'          : 'POST the same payload with a "status" verb to track.'
            },
            "timestamp"             : '%s' % datetime.now(timezone.utc).astimezone().isoformat(),
            "PACSdirective"         : PACSdirective
    }

# @router.post(
#     '/PACS/exec/pypx/',
#     response_model  = pacsQRmodel.PACSasync,
#     summary         = '''
#     POST a directive to the `PACSservice` using subsystem `listenerService`.
#     NOTE that this spawns a shell script process -- the call will be returned
#     immediately with an appropriate JSON reponse. To detemine status on this
#     job, POST the same payload to the `sync/pypx` endpoint with a `status`
#     `then` verb in the contents body.
#     '''
# )
# async def PACS_retrieveExec(
#         PACSservice         : pacsQRmodel.ValueStr,
#         listenerService     : pacsQRmodel.ValueStr,
#         PACSdirective       : pacsQRmodel.PACSqueryCore
# ):
#     """
#     POST a retrieve to the `PACSservice`. The actual retrieve call is a
#     a shell background process, and thus returns immediately.

#     Use a POST to the `pypx` endpoint, typically with a `status` directive,
#     to get data on the actual operation.

#     Parameters
#     ----------
#     - `PACSservice`:        name of the internal PACS service to query
#     - `listenerService`:    name of the listener service to use locally
#     - `PACSdirective`:      the directive object

#     Return
#     ------
#     - PACSasync object
#     """
#     d_exec  : dict  = {}
#     d_exec  = pacsQRcontroller.pypx_multiprocessDo(
#                                 PACSservice.value,
#                                 listenerService.value,
#                                 PACSdirective
#                             )
#     return {
#             "directiveType"         : "shell",
#             "response"              : d_exec,
#             "timestamp"             : '%s' % datetime.now(timezone.utc).astimezone().isoformat()
#     }

# @router.post(
#     '/PACS/query/',
#     # response_model  = pacsQRmodel.PACSqueyReturnModel,
#     summary         = '''
#     POST a query to a `PACSservice`. This is a synonym for the `pypx`
#     endpoint and kept currently only for historical reference.
#     '''
# )
# async def PACS_query(
#         PACSservice         : pacsQRmodel.ValueStr,
#         listenerService     : pacsQRmodel.ValueStr,
#         PACSquery           : pacsQRmodel.PACSqueryCore
# ):
#     """
#     POST a query to the `PACSservice`. This is a synonym for the `pypx`
#     endpoint and kept currently only for historical reference.

#     Parameters
#     ----------
#     - `PACSservice`:        name of the internal PACS service to query
#     - `listenerService`:    name of the listener service to use locally
#     - `PACSquery`:          the query object

#     Return
#     ------
#     - PACSqueryReturnModel
#     """
#     return pacsQRcontroller.pypx_do(
#             PACSservice.value,
#             listenerService.value,
#             PACSquery
#     )

@router.post(
    '/PACS/sync/pypx/',
    # response_model  = pacsQRmodel.PACSqueyReturnModel,
    summary         = '''
    Use this API route for STATUS operations and any others that block but
    which are "short lived". Since this is a synchronous operation, the call
    will only return on successful completion of the remote directive.
    '''
)
async def PACS_pypx(
        PACSservice         : pacsQRmodel.ValueStr,
        listenerService     : pacsQRmodel.ValueStr,
        PACSdirective       : pacsQRmodel.PACSqueryCore
):
    """
    POST a retrieve to the `PACSservice`, and capture return communication
    using the `listenerService`. The client will only receive a return
    payload when the PACSdirective has completed its remote execution.

    Parameters
    ----------
    - `PACSservice`:        name of the internal PACS service to query
    - `listenerService`:    name of the listener service to use locally
    - `PACSdirective`:      the pypx directive object

    Return
    ------
    - PACSqueryReturnModel
    """
    return pacsQRcontroller.pypx_do(
            PACSservice.value,
            listenerService.value,
            PACSdirective
    )

