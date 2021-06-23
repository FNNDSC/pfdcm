str_description = """

    The data model for the xinetd collection.

    Object instances are declared in the config module and here we create
    models of those object instances. So, the config module would declare
    say a state object, and here we create a model off that state object
    by calling specific member methods on those state objects.

"""

from    pydantic            import BaseModel, Field
from    typing              import Optional, List, Dict
from    datetime            import datetime

import  config
import  pudb

class time(BaseModel):
    """A simple model that has a time string field"""
    time            : str

class ListenerHandlerStatus(BaseModel):
    status          : bool

# A model for the listener system initialization
class ListenerInit(BaseModel):
    """
    This is returned when a listener subsystem is initialized
    """
    status          : bool
    ListenerInit    : str
    message         : str

# A model for the xinetd data
class XinetdCore(BaseModel):
    """
    The core data model
    """
    servicePort     : str
    tmpDir          : str
    logDir          : str
    dataDir         : str
    listener        : str
    patient_mapDir  : str
    study_mapDir    : str
    series_mapDir   : str

class XinetdDBReturnModel(BaseModel):
    info            : XinetdCore
    time_created    : time
    time_modified   : time
    message         : str

class XinetdDBPutModel(BaseModel):
    info            : XinetdCore

# A model for the dcmtk data
class DcmtkCore(BaseModel):
    storescu        : str
    storescp        : str
    findscu         : str
    movescu         : str
    echoscu         : str
    receiver        : str

class DcmtkDBReturnModel(BaseModel):
    info            : DcmtkCore
    time_created    : time
    time_modified   : time
    message         : str

class DcmtkDBPutModel(BaseModel):
    info            : DcmtkCore

class listenerDBreturnModel(BaseModel):
    """
    A full model that is returned from a call to the DB
    """
    xinetd          : XinetdDBReturnModel
    dcmtk           : DcmtkDBReturnModel

class listenerDBputXinetdModel(BaseModel):
    """
    Model that illustrates what to PUT to the DB
    """
    info            : XinetdCore

class listenerDBputDcmtkModel(BaseModel):
    """
    Model that illustrates what to PUT to the DB
    """
    info            : DcmtkCore

# Some "helper" classes
class ValueStr(BaseModel):
    value:              str         = ""
