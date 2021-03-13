str_description = """
    A simple dummy test model -- used for exploratory and
    conceptual purposes.
"""


from    fastapi             import APIRouter, Query
from    fastapi.encoders    import jsonable_encoder
from    pydantic            import BaseModel, Field
from    typing              import Optional, List, Dict

# The actual 'foobar' data model
class Item(BaseModel):
    name:           Optional[str]   = None
    description:    Optional[str]   = None
    price:          Optional[float] = None
    tax:            float           = 10.5
    tags:           List[str]       = []

class nameInObject(BaseModel):
    obj:    str             = 'foo'
    name:   Optional[str]   = ""

# and a dictionary of data items using this model...
d_items = {
    "foo": {
                "name":         "Foo",
                "price":        50.2
            },
    "bar": {
                "name":         "Bar",
                "description":  "The bartenders",
                "price":        62,
                "tax":          20.2
            },
    "baz": {
                "name":         "Baz",
                "description":  None,
                "price":        50.2,
                "tax":          10.5,
                "tags":         []
            },
}

