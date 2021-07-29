str_description = """

    The data model for the smdb module.

    The smdb module is the "Simple Map Data Base" of the pypx
    subsystem. Various pypx modules/tools use the smdb to record
    state (what scans have been received, pushed, registered)
    etc.

"""

from    pydantic            import BaseModel, Field
from    typing              import Optional, List, Dict
from    datetime            import datetime

from    db                  import pfdb
from    pypx                import smdb
import  pudb

# Some "helper" classes
class ValueStr(BaseModel):
    value:              str         = ""

class SMDBswiftCore(BaseModel):
    """The SMDB swift service model"""
    ip              : str
    port            : str
    login           : str

class SMDBswiftConfig(BaseModel):
    """The SMDB swift key config model"""
    swiftKeyName    : ValueStr
    swiftInfo       : SMDBswiftCore

class SMDBcubeCore(BaseModel):
    """The SMDB cube service model"""
    url             : str
    username        : str
    password        : str

class SMDBcubeConfig(BaseModel):
    """The SMDB cube key config model"""
    cubeKeyName     : ValueStr
    cubeInfo        : SMDBcubeCore


class time(BaseModel):
    """A simple model that has a time string field"""
    time            : str

class SMDBswiftReturnModel(BaseModel):
    """
    A full model that is returned from a call to the DB
    """
    status          : bool  = False
    swiftKeyName    : str
    swiftInfo       : SMDBswiftCore

class SMDBcubeReturnModel(BaseModel):
    """
    A full model that is returned from a call to the DB
    """
    status          : bool  = False
    cubeKeyName     : str
    cubeInfo        : SMDBcubeCore

