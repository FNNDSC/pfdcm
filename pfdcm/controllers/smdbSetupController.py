str_description = """
    This module contains logic pertinent to the smdb setup "subsystem"
    of the `pfdcm` service.
"""


from    fastapi             import  APIRouter, Query
from    fastapi.encoders    import  jsonable_encoder
from    pydantic            import  BaseModel, Field
from    typing              import  Optional, List, Dict

import  subprocess
from    models              import  smdbSetupModel
#import  logging
from    pflogf              import  FnndscLogFormatter
import  os
from    datetime            import  datetime
import  json

from    pypx                import  smdb
from    argparse            import  Namespace

import  pudb
import  config


def swiftData_update(
        o_data      : smdbSetupModel.SMDBswiftCore
    ) -> dict:
    """Create or update swift data for a new key

    Args:
        o_data (dict): the key and corresponding swift data

    Returns:
        dict: data and status
    """
    d_ret       : dict  = {}
    d_access    : dict  = {}
    j_data      : dict  = jsonable_encoder(o_data)
    j_data['swiftInfo']['storagetype'] = "swift"
    d_data      : dict  = {
        j_data['swiftKeyName']['value']  : j_data['swiftInfo']
    }
    SMDB                        = smdb.SMDB(
                                    Namespace(str_logDir = '/home/dicom/log')
                                )
    SMDB.args.str_actionArgs    = json.dumps(d_data)
    d_access                    = SMDB.service_keyAccess('storage')
    d_ret['status']             = d_access['status']
    d_ret['swiftKeyName']       = j_data['swiftKeyName']['value']
    d_ret['swiftInfo']          = d_access['storage'][d_ret['swiftKeyName']]
    return d_ret

def fsData_update(
        o_data      : smdbSetupModel.SMDBFsCore
    ) -> dict:
    """Create or update swift data for a new key

    Args:
        o_data (dict): the key and corresponding swift data

    Returns:
        dict: data and status
    """
    d_ret       : dict  = {}
    d_access    : dict  = {}
    j_data      : dict  = jsonable_encoder(o_data)
    j_data['fsInfo']['storagetype'] = "fs"
    d_data      : dict  = {
        j_data['fsKeyName']['value']  : j_data['fsInfo']
    }
    SMDB                        = smdb.SMDB(
                                    Namespace(str_logDir = '/home/dicom/log')
                                )
    SMDB.args.str_actionArgs    = json.dumps(d_data)
    d_access                    = SMDB.service_keyAccess('storage')
    d_ret['status']             = d_access['status']
    d_ret['fsKeyName']       = j_data['fsKeyName']['value']
    d_ret['fsInfo']          = d_access['storage'][d_ret['fsKeyName']]
    return d_ret

def cubeData_update(
        o_data      : smdbSetupModel.SMDBcubeCore
    ) -> dict:
    """Create or update CUBE data for a new key

    Args:
        o_data (dict): the key and corresponding CUBE data

    Returns:
        dict: data and status
    """
    d_ret       : dict  = {}
    d_access    : dict  = {}
    j_data      : dict  = jsonable_encoder(o_data)
    d_data      : dict  = {
        j_data['cubeKeyName']['value']  : j_data['cubeInfo']
    }
    SMDB                        = smdb.SMDB(
                                    Namespace(str_logDir = '/home/dicom/log')
                                )
    SMDB.args.str_actionArgs    = json.dumps(d_data)
    d_access                    = SMDB.service_keyAccess('CUBE')
    d_ret['status']             = d_access['status']
    d_ret['cubeKeyName']        = j_data['cubeKeyName']['value']
    d_ret['cubeInfo']           = d_access['CUBE'][d_ret['cubeKeyName']]
    return d_ret

def swiftObjects_getList() -> list:
    """
    Return a list of configured swift objects
    """
    SMDB        = smdb.SMDB(
                            Namespace(str_logDir = '/home/dicom/log')
                       )
    d_swift     = SMDB.service_keyAccess('storage')

    if d_swift['status']:
        return list(d_swift['storage'].keys())
    else:
        return []

def swiftObject_get(
    storageResource : str
    ) -> dict:
    """GET information on a given SMDB storage resource

    Args:
        storageResource (str): the name of SMDB storage resource

    Returns:
        dict: the key and correpsonding storage data
    """
    d_ret       : dict  = {
        'status'          : False,
        'storageKeyName'  : "",
        'storageInfo'     : dict
    }
    d_access    : dict  = {}
    SMDB                        = smdb.SMDB(
                                    Namespace(str_logDir = '/home/dicom/log')
                                )
    d_access                    = SMDB.service_keyAccess('storage')
    if storageResource in d_access['storage'].keys():
        d_ret['status']               = True
        d_ret['storageKeyName']       = storageResource
        d_ret['storageInfo']          = d_access['storage'][storageResource]
    return d_ret

def cubeObjects_getList() -> list:
    """
    Return a list of configured swift objects
    """
    SMDB        = smdb.SMDB(
                            Namespace(str_logDir = '/home/dicom/log')
                        )
    d_cube     = SMDB.service_keyAccess('CUBE')
    if d_cube['status']:
        return list(d_cube['CUBE'].keys())
    else:
        return []

def cubeObject_get(
    cubeResource : str
    ) -> dict:
    """GET information on a given SMDB CUBE resource

    Args:
        swiftResource (str): the name of SMDB CUBE resource

    Returns:
        dict: the key and correpsonding CUBE data
    """
    d_ret       : dict  = {
        'status'        : False,
        'cubeKeyName'   : "",
        'cubeInfo'      : {
            'url'       : '',
            'username'  : '',
            'password'  : ''
        }
    }
    d_access    : dict  = {}
    SMDB                        = smdb.SMDB(
                                    Namespace(str_logDir = '/home/dicom/log')
                                )
    d_access                    = SMDB.service_keyAccess('CUBE')
    if cubeResource in d_access['CUBE'].keys():
        d_ret['status']             = True
        d_ret['cubeKeyName']        = cubeResource
        d_ret['cubeInfo']           = d_access['CUBE'][cubeResource]
    return d_ret
