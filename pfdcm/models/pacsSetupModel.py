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

from    db                  import pfdb
import  pudb

class PACSsetupCore(BaseModel):
    """The PACS service model"""
    aet             : str   = "CHIPS"
    aet_listener    : str   = "CHIPS"
    aec             : str   = "ORTHANC"
    serverIP        : str   = "192.168.1.189"
    serverPort      : str   = "4242"
    reallyEfficient : bool  = False

class time(BaseModel):
    """A simple model that has a time string field"""
    time            : str

class PACSdbReturnModel(BaseModel):
    """
    A full model that is returned from a call to the DB
    """
    info            : PACSsetupCore
    time_created    : time
    time_modified   : time
    message         : str

class PACSdbPutModel(BaseModel):
    """
    Model that illustrates what to PUT to the DB
    """
    info            : PACSsetupCore
    # WIP -- need to figure out how to be more pydantic, but for now... moving on
    # info            : dict = Field(
    #     pfdb.PACSsetupCore,
    #     title           = 'Data specific to one single PACS service',
    #     description     = """
    #     This field contains all the necessary information to communicate
    #     with a remote PACS service. This includes the IP adderss and port
    #     as well as the relevant remote and local AETitles.
    #     """
    # )

# Some "helper" classes
class ValueStr(BaseModel):
    value:              str         = ""
