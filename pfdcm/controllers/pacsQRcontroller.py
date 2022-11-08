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
import  asyncio
import  subprocess
from    models              import  pacsQRmodel
import  logging
from    pflogf              import  FnndscLogFormatter
import  os
from    datetime            import  datetime

import  pudb
from    pudb.remote         import set_trace
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

async def thread_pypxDo_async(PACSobjName, listenerObjName, queryTerms):
    task    = asyncio.create_task(pypx_do(PACSobjName, listenerObjName, queryTerms))
    await task

def thread_pypxDo(PACSobjName, listenerObjName, queryTerms):
    asyncio.run(thread_pypxDo_async(PACSobjName, listenerObjName, queryTerms))

async def pypx_threadedDo(
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
    loop = asyncio.get_running_loop()
    future = loop.run_in_executor(threadpool, thread_pypxDo, PACSobjName, listenerObjName, queryTerms)
    return future

async def pypx_multiprocessDo(
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
            try:
                del d_args[tag]
            except:
                pass

    def args_prune():
        """Prune args -- removes any args not relevant to the CLI px-find
        """
        # global d_queryTerms, d_service
        # this following is an impedence matching hack!
        # replace the `dblogbasepath` with `db` for the CLI call
        d_queryTerms['db']              = d_queryTerms['dblogbasepath']
        del d_queryTerms['dblogbasepath']
        pxfindArgs_prune(d_queryTerms)
        try:
            del d_service['aet_listener']
        except:
            pass

    def shell_exec(d_JSONargs: dict) -> dict:
        """Run the specific PACS operation from a CLI call

        Args:
            d_JSONargs (dict): JSON representation of the CLI

        Returns:
            dict: response from CLI (stdout, stderr, returncode)
        """
        # global d_response
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
        return d_response

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
            args_prune()
            d_JSONargs                      = {**d_service, **d_queryTerms}
            d_response                      = shell_exec(d_JSONargs)
        else:
            d_response['message']       = \
                "'%s' is not a configured listener service" % listenerObjName
    else:
        d_response['message']   = \
                "'%s' is not a configured PACS service" % PACSobjName
    # with open('/home/dicom/tmp/resp.json', 'a') as db:
    #     json.dump(d_response, db)
    return d_response

async def pypx_do(
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
        'status'        :   False,
        'find'          :   {},
        'message'       :   "No %s performed" % action,
        'PACSdirective' :   queryTerms
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
            d_response['pypx']              = await pypx.find({**d_service, **d_queryTerms})
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
    # with open('/home/dicom/tmp/resp.json', 'a') as db:
    #     json.dump(d_response, db)
    return d_response

