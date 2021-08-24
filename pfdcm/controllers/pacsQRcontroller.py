str_description = """
    This module contains logic pertinent to the PACS setup "subsystem"
    of the `pfdcm` service.
"""

from    concurrent.futures  import  ProcessPoolExecutor, ThreadPoolExecutor, Future

from    fastapi             import  APIRouter, Query
from    fastapi.encoders    import  jsonable_encoder
from    fastapi.concurrency import  run_in_threadpool
from    pydantic            import  BaseModel, Field
from    typing              import  Optional, List, Dict

from    .jobController      import  jobber

import  subprocess
from    models              import  pacsQRmodel
import  logging
from    pflogf              import  FnndscLogFormatter
import  os
from    datetime            import  datetime

import  pudb
import  config
import  json
import  pypx

threadpool      = ThreadPoolExecutor()
processpool     = ProcessPoolExecutor()

def noop():
    """
    A dummy function that does nothing.
    """
    return {
        'status':   True
    }

def pypx_threadedDo(
        PACSobjName             : str,
        listenerObjName         : str,
        queryTerms              : pacsQRmodel.PACSqueryCore,
) -> Future:
    """asynchronous wrapper around pypx_do that runs the method using concurrent.futures

    Args:
        PACSobjName (str): the PACS object to use
        listenerObjName (str): the listener subsystem associated with the PACS object
        queryTerms (pacsQRmodel.PACSqueryCore): the query JSON object dispatched to pypx

    Returns:
        dict: simple dictionary reflecting the async call.
    """
    future      = threadpool.submit(pypx_do, PACSobjName, listenerObjName, queryTerms)
    # d_pypx_do   = await run_in_threadpool(
    #                     lambda: pypx_do(PACSobjName, listenerObjName, queryTerms)
    #             )
    return future

def pypx_findExec(
        PACSobjName             : str,
        listenerObjName         : str,
        queryTerms              : pacsQRmodel.PACSqueryCore,
        action                  : str   = "query"
) -> dict:
    """
    This method calls a CLI equivalent of the px-find module.
    """

    def pxfindArgs_prune(d_args):
        """
        Prune dictionary args that do not map to px-find CLI
        """
        for tag in [
            'PatientBirthDate',
            'PatientAge',
            'NumberOfSeriesRelatedInstances',
            'InstanceNumber',
            'SeriesDate',
            'json_response'
            ]:
            del d_args[tag]

    d_response  : dict  = {
        'status'    :   False,
        'message'   :   "No %s performed" % action,
        'exec'      :   {}
    }
    d_JSONargs      : dict  = {}
    str_JSONargs    : str   = ""
    str_pxfindexec  : str   = ""
    d_service       : dict  = {}
    d_queryTerms    : dict  = jsonable_encoder(queryTerms)
    d_queryTerms['json']    = d_queryTerms['json_response']
    if PACSobjName in config.dbAPI.PACSservice_listObjs():
        if listenerObjName in config.dbAPI.listenerService_listObjs():
            d_PACSservice   : dict          = config.dbAPI.PACSservice_info(
                                                PACSobjName
                                            )
            d_service                       = d_PACSservice['info']
            # this following is an impedence matching hack!
            # replace the `dblogbasepath` with `db` for the CLI call
            d_queryTerms['db']              = d_queryTerms['dblogbasepath']
            del d_queryTerms['dblogbasepath']
            pxfindArgs_prune(d_queryTerms)
            del d_service['aet_listener']
            d_JSONargs                      = {**d_service, **d_queryTerms}
            try:
                shell                       = jobber({'verbosity' : 1, 'noJobLogging': True})
                str_cliArgs                 = shell.dict2cli(d_JSONargs)
                # str_JSONargs                = shell.dict2JSONcli(d_JSONargs)
                str_pxfindexec              = 'px-find %s' % str_cliArgs
                d_response['exec']          = shell.job_runbg(str_pxfindexec)
                d_response['status']        = True
                d_response['message']       = 'CLI px-find spawned'
            except Exception as e:
                d_response['error']         = '%s' % e
        else:
            d_response['message']       = \
                "'%s' is not a configured listener service" % listenerObjName
    else:
        d_response['message']   = \
                "'%s' is not a configured PACS service" % PACSobjName
    # with open('/home/dicom/tmp/resp.json', 'a') as db:
    #     json.dump(d_response, db)
    return d_response


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
    with open('/home/dicom/tmp/resp.json', 'a') as db:
        json.dump(d_response, db)
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
