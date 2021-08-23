str_description = """

    The data models/schemas for the PACS QR collection.

"""

from    pydantic            import BaseModel, Field
from    typing              import Optional, List, Dict
from    datetime            import datetime

from    db                  import pfdb
import  pudb

class PACSqueryCore(BaseModel):
    """The PACS Query model"""
    AccessionNumber                     : str   = ""
    PatientID                           : str   = ""
    PatientName                         : str   = ""
    PatientBirthDate                    : str   = ""
    PatientAge                          : str   = ""
    PatientSex                          : str   = ""
    StudyDate                           : str   = ""
    StudyDescription                    : str   = ""
    StudyInstanceUID                    : str   = ""
    Modality                            : str   = ""
    ModalitiesInStudy                   : str   = ""
    PerformedStationAETitle             : str   = ""
    NumberOfSeriesRelatedInstances      : str   = ""
    InstanceNumber                      : str   = ""
    SeriesDate                          : str   = ""
    SeriesDescription                   : str   = ""
    SeriesInstanceUID                   : str   = ""
    ProtocolName                        : str   = ""
    AcquisitionProtocolDescription      : str   = ""
    AcquisitionProtocolName             : str   = ""
    withFeedBack                        : bool  = False
    then                                : str   = ""
    thenArgs                            : str   = ""
    dblogbasepath                       : str   = "/home/dicom/log"
    json_response                       : bool  = True

class PACSasync(BaseModel):
    """A model returned when an async PACS directive is indicated"""
    directiveType                       : str   = "async"
    response                            : dict
    timestamp                           : str

class time(BaseModel):
    """A simple model that has a time string field"""
    time            : str

class PACSqueyReturnModel(BaseModel):
    """
    A full model that is returned from a query call
    """
    response        : str

# Some "helper" classes
class ValueStr(BaseModel):
    value           : str = ""