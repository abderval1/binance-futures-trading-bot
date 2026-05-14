from sqlalchemy.orm import Session
from typing import List, Optional
from . import models, schemas, auth


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name,
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: int, user_update: schemas.UserUpdate):
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    for field, value in user_update.model_dump(exclude_unset=True).items():
        setattr(db_user, field, value)
    db.commit()
    db.refresh(db_user)
    return db_user


# ========== API Keys ==========
def get_api_keys(db: Session, user_id: int):
    return db.query(models.APIKey).filter(models.APIKey.user_id == user_id).all()


def get_api_key(db: Session, api_key_id: int):
    return db.query(models.APIKey).filter(models.APIKey.id == api_key_id).first()


def create_api_key(db: Session, api_key: schemas.APIKeyCreate, user_id: int):
    from .utils.encryption import encrypt_api_key
    encrypted_api, nonce = encrypt_api_key(api_key.api_key, api_key.secret_key)

    db_key = models.APIKey(
        user_id=user_id,
        label=api_key.label,
        encrypted_api_key=encrypted_api,
        encrypted_secret_key=nonce,
        testnet=api_key.testnet,
        leverage=api_key.leverage,
        margin_type=api_key.margin_type,
        permissions={"trade": True, "withdraw": False}
    )
    db.add(db_key)
    db.commit()
    db.refresh(db_key)
    return db_key


def get_max_api_keys(role: models.UserRole) -> int:
    limits = {
        models.UserRole.SUBSCRIBER: 2,
        models.UserRole.TRADER: 5,
        models.UserRole.ADMIN: 50
    }
    return limits.get(role, 2)


# ========== Trades ==========
def get_trades(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Trade).filter(
        models.Trade.user_id == user_id
    ).order_by(models.Trade.executed_at.desc()).offset(skip).limit(limit).all()


# ========== Positions ==========
def get_positions(db: Session, api_key_id: Optional[int] = None):
    query = db.query(models.Position)
    if api_key_id:
        query = query.filter(models.Position.api_key_id == api_key_id)
    return query.all()
