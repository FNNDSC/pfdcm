from fastapi    import APIRouter, Query
from pydantic   import BaseModel, Field

router = APIRouter()


class PACS(BaseModel):
    """
    Not actually a DICOM, just some JSON.
    """
    a_cool_picture: str = Field(
        'example response',
        title       = 'A sentence about nothing much',
        description = 'A longer sentence about nothing much'
    )


@router.get(
    '/PACS/',
    summary         = 'Get info about a specific PACS config',
    response_model  = PACS,
    tags            = ["PACS"])
async def PACS_read(
        mrn: int = Query(
            ...,
            description = "Patient's medical record number",
            gt          = 0
        )
):
    """
    Fake meaningless response
    """
    return PACS(a_cool_picture=f'your MRN is: {mrn}. Goodbye!')
