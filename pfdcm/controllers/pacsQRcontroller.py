str_description = """
    This module contains logic pertinent to the PACS setup "subsystem"
    of the `pfdcm` service.
"""


from    fastapi             import  APIRouter, Query
from    fastapi.encoders    import  jsonable_encoder
from    pydantic            import  BaseModel, Field
from    typing              import  Optional, List, Dict

import  subprocess
from    models              import  pacsQRmodel
import  logging
from    pflogf              import  FnndscLogFormatter
import  os
from    datetime            import  datetime

import  pudb
import  config

import  pypx

def noop():
    """
    A dummy function that does nothing.
    """
    return {
        'status':   True
    }

def pypx_do(
        PACSobjName             : str,
        listenerObjName         : str,
        queryTerms              : pacsQRmodel.PACSqueryCore,
        action                  : str   = "query"
) -> dict:
    """
    Main dispatching method for interacting with pypx to effect some behaviour.

    All calls happen with a px-find, with behaviour specified in the `then`
    """
    d_response  : dict  = {
        'status'    :   False,
        'find'      :   {},
        'message'   :   "No %s performed" % action
    }
    d_service       : dict  = {}
    d_queryTerms    : dict  = jsonable_encoder(queryTerms)
    d_queryTerms['json']    = d_queryTerms['json_response']
    if PACSobjName in config.dbAPI.PACSservice_listObjs():
        if listenerObjName in config.dbAPI.listenerService_listObjs():
            d_PACSservice   : dict          = config.dbAPI.PACSservice_info(
                                                PACSobjName
                                            )
            d_service                       = d_PACSservice['info']
            d_response['pypx']              = pypx.find({**d_service, **d_queryTerms})
            if d_response['pypx']['status'] == 'success':
                d_response['status']        = True
                d_response['message']       = "pypx.then = '%s' was executed successfully" % \
                                                d_queryTerms['then']
        else:
            d_response['message']       = \
                "'%s' is not a configured listener service" % listenerObjName
    else:
        d_response['message']   = \
                "'%s' is not a configured PACS service" % PACSobjName
    return d_response

def QRS_do(
        PACSobjName             : str,
        listenerObjName         : str,
        queryTerms              : pacsQRmodel.PACSqueryCore,
        action                  : str   = "query"
) -> dict:
    """
    Main dispatching method for performing either a:

        * query
        * retrieve
        * status

    as explicitly defined by the "action".
    """
    d_response  : dict  = {
        'status'    :   False,
        'find'      :   {},
        'message'   :   "No %s performed" % action
    }
    d_service       : dict  = {}
    d_queryTerms    : dict  = jsonable_encoder(queryTerms)
    if PACSobjName in config.dbAPI.PACSservice_listObjs():
        if listenerObjName in config.dbAPI.listenerService_listObjs():
            d_listenerObj   : dict          = config.dbAPI.listenerService_info(
                                                listenerObjName
                                            )
            d_PACSservice   : dict          = config.dbAPI.PACSservice_info(
                                                PACSobjName
                                            )
            d_service                       = d_PACSservice['info']
            d_service['executable']         = d_listenerObj['dcmtk']['info']['findscu']
            if action == 'retrieve':
                d_queryTerms['retrieve']    = True
            d_response['find']              = pypx.find({**d_service, **d_queryTerms})
            if d_response['find']['status'] == 'success':
                d_response['status']        = True
                d_response['message']       = "'%s' was executed successfully" % action
        else:
            d_response['message']       = \
                "'%s' is not a configured listener service" % listenerObjName
    else:
        d_response['message']   = \
                "'%s' is not a configured PACS service" % PACSobjName
    return d_response

def query_do(
        PACSobjName             : str,
        listenerObjName         : str,
        query                   : pacsQRmodel.PACSqueryCore
) -> dict:
    d_response  : dict  = {
        'status'    :   False,
        'find'      :   {},
        'message'   :   "No query performed"
    }
    d_service   : dict  = {}
    d_query     : dict  = jsonable_encoder(query)
    if PACSobjName in config.dbAPI.PACSservice_listObjs():
        if listenerObjName in config.dbAPI.listenerService_listObjs():
            d_listenerObj   : dict      = config.dbAPI.listenerService_info(
                                            listenerObjName
                                        )
            d_PACSservice   : dict      = config.dbAPI.PACSservice_info(
                                            PACSobjName
                                        )
            d_service                   = d_PACSservice['info']
            d_service['executable']     = d_listenerObj['dcmtk']['info']['findscu']
            d_response['find']          = pypx.find({**d_service, **d_query})
    else:
        d_response['message']   = "'%s' is not a configured PACS service" % \
            PACSobjName
    return d_response
