str_description = """

    The data model for the xinetd collection

"""

from    pydantic            import BaseModel, Field
from    typing              import Optional, List, Dict
from    datetime            import datetime

from    config              import Xinetd_obj

# The actual model class
class XinetdModel(BaseModel):
    """
    """

    xinetd_info         : dict = Field(
        {
            'state':    'unintialized'
        },
        title           = 'Specific xinetd instance data',
        description     = 'A dictionary representation of an external "state" object'
    )

    touch_timestamp     : str = Field(
        'now',
        title       = 'The current timestamp this object was touched',
        description = 'Useful to track the persistency of data in the system'
    )

# Some "helper" classes
class Value(BaseModel):
    text:           str             = ""

class updateTimestamp(BaseModel):
    xinetdObjToTouch:   str         = ""

# and a dictionary of data for this model.
d_xinetd  = {
    "default": {
        "xinetd_info"       :   Xinetd_obj.as_dict(),
        "touch_timestamp"   :   "%s" % datetime.now()
    },
    "test": {
        "xinetd_info"       :   Xinetd_obj.as_dict(),
        "touch_timestamp"   :   "%s" % datetime.now()
    },
    "dev": {
        "xinetd_info"       :   Xinetd_obj.as_dict(),
        "touch_timestamp"   :   "%s" % datetime.now()
    },

}

