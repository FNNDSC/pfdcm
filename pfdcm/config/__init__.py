from fastapi    import APIRouter, Query
from pydantic   import BaseModel, Field

from    datetime            import datetime

import  logging
from    pflogf              import      FnndscLogFormatter

# pfstorage local dependencies
import  pfmisc
from    pfmisc.C_snode      import  *
import  pfstate
from    pfstate             import  S

class Xinetd(S):
    """
    A derived 'pfstate' class that keeps some state information relevant
    to some data module. In this case, information pertinent to the
    xinetd setup in this container.

    See https://github.com/FNNDSC/pfstate for more information.
    """

    def __init__(self, *args, **kwargs):
        """
        An object to hold some generic/global-ish system state, in C_snode
        trees.
        """
        self.state_create(
        {
            'timestamp':            {
                'now':              '%s' % datetime.now()
            },
            'xinetd': {
                'servicePort':      '10402',
                'tmpDir':           '/dicom/tmp',
                'logDir':           '/dicom/log',
                'dataDir':          '/dicom/data',
                'file':             '/etc/xinetd.d/dicomlistener',
                'patient_mapDir':   '/dicom/log/patient_map',
                'study_mapDir':     '/dicom/log/study_map',
                'series_mapDir':    '/dicom/log/series_map'
            },
        },
        *args, **kwargs)

Xinetd_obj          = Xinetd(
        name        = 'xinetd internals',
        desc        = 'information relevant to the creation and behaviour of the xinetd service'
)
