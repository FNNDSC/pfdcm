from fastapi    import APIRouter, Query
from pydantic   import BaseModel, Field

router = APIRouter()


class Dicom(BaseModel):
    """
    Not actually a DICOM, just some JSON.
    """
    a_cool_picture: str = Field(
        'example response',
        title       = 'A sentence about nothing much',
        description = 'A longer sentence about nothing much'
    )


@router.get(
    '/dicom/',
    summary         = 'Get dicom images for a patient.',
    response_model  = Dicom,
    tags            = ["dicom"])

async def read_dicom(
        mrn: int = Query(
            ...,
            description = "Patient's medical record number",
            gt          = 0
        )
):
    """
    Fake meaningless response
    """
    return Dicom(a_cool_picture=f'your MRN is: {mrn}. Goodbye!')
