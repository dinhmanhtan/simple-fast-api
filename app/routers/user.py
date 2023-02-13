from fastapi import Response, status, HTTPException, Depends, APIRouter
from app.database import get_db
from sqlalchemy.orm import Session
from app import schemas
import app.utils as utils
from app import models

router = APIRouter(prefix="/users", tags=["User"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    user = user.dict()
    user["password"] = utils.hash(user["password"])

    new_user = models.User(**user)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user
