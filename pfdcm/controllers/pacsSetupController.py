str_description = """
    This module contains logic pertinent to the PACS setup "subsystem"
    of the `pfdcm` service.
"""


from    fastapi             import  APIRouter, Query
from    fastapi.encoders    import  jsonable_encoder
from    pydantic            import  BaseModel, Field
from    typing              import  Optional, List, Dict

import  subprocess
from    models              import  pacsSetupModel
import  logging
from    pflogf              import  FnndscLogFormatter
import  os
from    datetime            import  datetime

import  pudb
import  config

def noop():
    """
    A dummy function that does nothing.
    """
    return {
        'status':   True
    }

def internalObjects_getList() -> list:
    """
    Return a list of internal object names
    """
    return list(config.dbAPI.PACSservice_listObjs())

def internalObject_get(objName : str) -> dict:
    """
    Return a dictionary representation of a single PACS object
    """
    return dict(config.dbAPI.PACSservice_info(objName))

def obj_portUpdate(
        objName                 : pacsSetupModel.ValueStr,
        newPort                 : pacsSetupModel.ValueStr
) -> dict:
    return dict(config.dbAPI.PACSservice_portUpdate(objName.value, newPort.value))

def service_update(
        objName                 : str,
        data                    : pacsSetupModel.PACSdbPutModel
) -> dict:
    """
    Create (or update) a PACS object
    """
    d_data          : dict  = jsonable_encoder(data.info)
    return dict(config.dbAPI.PACSservice_initObj(objName, d_data))

