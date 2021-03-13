str_description = """

    This route module is a dummy/demo foobar example.

    The main purpose is simply to show how to create a router
    and define some simple routes, using the appropriate data
    model and also a simple meaningless call to the a related
    controller module.

"""


from    fastapi             import APIRouter, Query
from    fastapi.encoders    import jsonable_encoder

from    models              import foobarModel
from    controllers         import foobarController

router      = APIRouter()
router.tags = ['foobar']

@router.post(
    "/items/name/",
    summary         = "POST an update to a name field"
)
def itemName_update(name: foobarModel.nameInObject):
    """
    POST an update to a name field. Using the **nameInObject**:

    - Update the **name** field of the **obj**
    """
    d_update = jsonable_encoder(name)
    foobarModel.d_items[d_update['obj']]['name'] = d_update['name']
    return name

@router.get(
    "/items_foobar/{item_id}",
    response_model  = foobarModel.Item,
    summary         = "GET an item_id"
)
async def item_get(item_id: str):
    """
    Get information about a specific **foobar** item, one of:

    - **foo** : the first object
    - **bar** : the second object
    - **baz** : a fun object
    """
    return foobarModel.d_items[item_id]

@router.put("/items_foobar/{item_id}",
    response_model  = foobarModel.Item,
    summary         = "PUT an item_id"
)
async def item_put(item_id: str, item: foobarModel.Item):
    """
    PUT an item_id. Fields that are omitted will use base model values:
    - **foo** : the first object
    - **bar** : the second object
    - **baz** : a fun object
    """
    update_item_encoded             = jsonable_encoder(item)

    # Change state here!
    foobarModel.d_items[item_id]    = update_item_encoded

    # Call a method in the controller module
    d_ret                           = foobarController.noop()

    return update_item_encoded
