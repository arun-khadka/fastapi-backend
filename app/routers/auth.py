from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from .. import models, schemas, utils
from .. import database


router = APIRouter(tags=["Authentication"])


@router.post("/login")
def user_login(
    user_credentials: schemas.UserLogin, db: Session = Depends(database.get_db)
):
    user = (
        db.query(models.User)
        .filter(models.User.email == user_credentials.email)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Invalid Credentials!"
        )

    if not utils.verify(user_credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Invalid Credentials!"
        )

#create a token

    return {"message": "Logged In"}