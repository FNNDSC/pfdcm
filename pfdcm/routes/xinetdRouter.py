str_description = """
    This route module handles logic pertaining to service
    infrastructure creation/instantiation.
"""


from    fastapi             import APIRouter, Query
from    fastapi.encoders    import jsonable_encoder

from    models              import xinetdModel, foobarModel
from    controllers         import xinetdController

import  logging
from    pflogf              import      FnndscLogFormatter

# pfstorage local dependencies
import  pfmisc
from    pfmisc.C_snode      import  *
import  pfstate
from    pfstate             import  S

router          = APIRouter()
router.tags     = ['xinetd']

@router.post(
    '/xinetd/timestamps/',
    response_model          = xinetdModel.XinetdModel,
    summary                 = 'Update the timestamp',
    response_description    = "An updated timestamp"
)
async def xinetd_timestampUpdate(target:   xinetdModel.updateTimestamp):
    """
    Update the timestamp field on the target object:

    - **xinetdObjToTouch**: the object to update
    """
    str_now         : str = datetime.now()
    # pudb.set_trace()
    # xinetdModel.d_xinetd[target.xinetdObjToTouch]["touch_timestamp"]   = str_now
    return xinetdModel.d_xinetd['default']

# # @router.post(
# #     '/xinetd/servicePort/',
# #     summary         = 'Set the local listener port',
# #     response_model  = Xinetd,
# # )
# # async def xinetd_portPOST(port : Item):
# #     Xinetd_obj.T.touch('/xinetd/servicePort', port.name)

@router.get(
    "/xinetd/{xinet_id}",
    response_model  = xinetdModel.XinetdModel,
    summary         = "GET an xinet_id"
)
async def xinetd_get(xinet_id: str):
    """
    GET an xinet_id -- one of:
    - **default**
    - **test**
    - **dev**
    """
    return xinetdModel.d_xinetd[xinet_id]

@router.put("/xinetd/{xinetd_id}",
    response_model  = xinetdModel.XinetdModel,
    summary         = "PUT an item_id"
)
async def item_put(xinetd_id: str, item: xinetdModel.XinetdModel):
    """
    PUT an item_id. Fields that are omitted will use base model values:
    - **foo** : the first object
    - **bar** : the second object
    - **baz** : a fun object
    """
    update_item_encoded             = jsonable_encoder(item)

    # Change state here!
    xinetdModel.d_xinetd[xinetd_id] = update_item_encoded

    # Call a method in the controller module
    d_ret                           = xinetdController.noop()

    return update_item_encoded


# @router.get(
#     '/xinetd/',
#     summary         = 'Get information pertinent to the internal xinetd service',
#     response_model  = xinetdModel.XinetdModel,
#     tags            = ["xinet"]
# )
# async def xinetd_info():
#     """
#     Return information pertinent to the XinetdModel
#     """
#     pudb.set_trace()
#     return xinetdModel.d_xinetd["default"]

# @router.get(
#     '/xinetd/servicePort',
#     summary         = 'Get information about the service port',
#     response_model  = Xinetd,
#     tags            = ["servicePort"]
# )
# async def xinetd_servicePortInfo():
#     """
#     Fake meaningless response
#     """
#     return {'servicePort':  Xinetd_obj.T.cat('/xinetd/servicePort')}
