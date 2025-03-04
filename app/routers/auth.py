from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from .. import models, utils, oauth2, database
from sqlalchemy.orm import Session

router = APIRouter(tags=["Authentication"])


@router.post("/login")
def user_login(
    user_credentials: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(database.get_db),
):

    # Get user by email (which is stored in 'username' due to OAuth2 standard)
    user = (
        db.query(models.User)
        .filter(models.User.email.ilike(user_credentials.username))
        .first()
    )

    print("User found in DB:", user)

    # Check if user exists
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Invalid Credentials!",
        )

    # Verify password
    password_valid = utils.verify(user_credentials.password, user.password)
    print("Password valid:", password_valid)

    if not password_valid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials!"
        )

    # Create JWT access token
    access_token = oauth2.create_access_token(data={"user_id": str(user.id)})
    print("Generated access token:", access_token)

    return {"access_token": access_token, "token_type": "bearer"}
