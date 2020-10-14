from typing import Any

from fastapi import APIRouter, Depends
from pydantic.networks import EmailStr

from app import auth, schemas
from app.utils import send_test_email

router = APIRouter()


@router.post("/test-email/", response_model=schemas.Msg, status_code=201)
def test_email(
    email_to: EmailStr,
    current_user: schemas.User = Depends(auth.get_current_active_superuser),
) -> Any:
    """
    Test emails.
    """
    send_test_email(email_to=email_to)
    msg = schemas.Msg(msg="Test email sent")
    return msg
