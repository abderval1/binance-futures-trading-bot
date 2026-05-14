from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from .. import crud, schemas, auth
from ..database import get_db

router = APIRouter(prefix="/api-keys", tags=["api-keys"])


@router.post("/", response_model=schemas.APIKeyResponse)
def create_api_key(
    api_key: schemas.APIKeyCreate,
    current_user: schemas.UserResponse = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    # Check subscription limits
    user_keys = db.query(crud.models.APIKey).filter(
        crud.models.APIKey.user_id == current_user.id
    ).count()
    max_keys = crud.get_max_api_keys(current_user.role)
    if user_keys >= max_keys:
        raise HTTPException(
            status_code=403,
            detail=f"Maximum number of API keys ({max_keys}) reached for your plan"
        )

    db_api_key = crud.create_api_key(db=db, api_key=api_key, user_id=current_user.id)
    return db_api_key


@router.get("/", response_model=List[schemas.APIKeyResponse])
def list_api_keys(
    current_user: schemas.UserResponse = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    keys = crud.get_api_keys(db, user_id=current_user.id)
    # Return masked keys (last 4 chars only)
    response = []
    for key in keys:
        key_dict = schemas.APIKeyResponse.model_validate(key).model_dump()
        key_dict["label"] = key.label
        key_dict["api_key"] = None
        key_dict["secret_key"] = None
        response.append(key_dict)
    return response


@router.delete("/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_api_key(
    key_id: int,
    current_user: schemas.UserResponse = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    key = db.query(crud.models.APIKey).filter(
        crud.models.APIKey.id == key_id,
        crud.models.APIKey.user_id == current_user.id
    ).first()
    if not key:
        raise HTTPException(status_code=404, detail="API key not found")
    db.delete(key)
    db.commit()
    return None
