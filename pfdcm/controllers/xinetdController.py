str_description = """
    This module contains logic that might be pertinent to
    the foobar model manipulation and slightly beyond scope
    of for example one simple routing method.
"""


from    fastapi             import APIRouter, Query
from    fastapi.encoders    import jsonable_encoder
from    pydantic            import BaseModel, Field
from    typing              import Optional, List, Dict

def noop():
    """
    A dummy function that does nothing.
    """
    return {
        'status':   True
    }

