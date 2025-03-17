import core.config as config
from datetime import datetime
from sqlalchemy.orm import Session
from models.project import User


SMTP_SERVER = config.SMTP_SERVER
SMTP_PORT = config.SMTP_PORT
SENDER_EMAIL = config.SENDER_EMAIL
SENDER_PASSWORD = config.SENDER_PASSWORD

def user_register(db : Session, email : str, pw : str, name : str):
    new_user = User(
        email = email,
        pw = pw,
        name = name,
        role = 'user',
        group = 'newUser',
        status = 'active',
        register_at=datetime.utcnow()
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def user_login(db : Session, email : str, pw : str):
    user = db.query(User).filter(User.email == email, User.pw == pw).first()
    if user:
        return {
            "email": user.email,
            "name": user.name,
            "role": user.role
        }
    return None

def get_user_data(db : Session, email : str):
    return db.query(User).filter(User.email.ilike(email)).first()

def create_google_user(db : Session, email : str, name : str):
    new_user = User(
        email = email,
        pw = 'default_password',
        name = name,
        role = 'googleUser',
        group = 'newUser',
        status = 'active',
        register_at = datetime.utcnow()
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
