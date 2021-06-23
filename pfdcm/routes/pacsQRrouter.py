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


from    fastapi             import  APIRouter, Query, HTTPException
from    fastapi.encoders    import  jsonable_encoder
from    typing              import  List, Dict

from    models              import  pacsQRmodel
from    controllers         import  pacsQRcontroller

import  pudb

router          = APIRouter()
router.tags     = ['PACS QR services']

@router.post(
    '/PACS/retrieve/',
    # response_model  = pacsQRmodel.PACSqueyReturnModel,
    summary         = '''
    POST a retrieve to the `PACSservice` using listener subsystem `listenerService`
    '''
)
async def PACS_retrieve(
        PACSservice         : pacsQRmodel.ValueStr,
        listenerService     : pacsQRmodel.ValueStr,
        PACSquery           : pacsQRmodel.PACSqueryCore
):
    """
    POST a retrieve to the `PACSservice`

    Parameters
    ----------
    - `PACSservice`:        name of the internal PACS service to query
    - `listenerService`:    name of the listener service to use locally
    - `PACSquery`:          the query object

    Return
    ------
    - PACSqueryReturnModel
    """
    return pacsQRcontroller.QRS_do(
            PACSservice.value,
            listenerService.value,
            PACSquery,
            'retrieve'
    )

@router.post(
    '/PACS/query/',
    # response_model  = pacsQRmodel.PACSqueyReturnModel,
    summary         = '''
    POST a query to a `PACSservice`
    '''
)
async def PACS_query(
        PACSservice         : pacsQRmodel.ValueStr,
        listenerService     : pacsQRmodel.ValueStr,
        PACSquery           : pacsQRmodel.PACSqueryCore
):
    """
    POST a query to the `PACSservice`

    Parameters
    ----------
    - `PACSservice`:        name of the internal PACS service to query
    - `listenerService`:    name of the listener service to use locally
    - `PACSquery`:          the query object

    Return
    ------
    - PACSqueryReturnModel
    """
    return pacsQRcontroller.QRS_do(
            PACSservice.value,
            listenerService.value,
            PACSquery
    )

