from sqlalchemy.orm import Session
from models.project import User

# 회원 가입
def create_user(db: Session, user_id: str, password: str, email: str, role: str):
    new_user = User(
        id=user_id,
        pw=password,
        email=email,
        role=role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def update_user(db: Session, id: str, new_id : str, new_pw: str, new_email: str):
    try:
        user = db.query(User).filter(User.id == id).one()

        if new_id:
            user.id = new_id
        if new_pw:
            user.pw = new_pw
        if new_email:
            user.email = new_email
        db.commit()
        return {"message" : "User Updated Successfully."}
    except Exception as e:
        db.rollback()
        return {"error" : str(e)}

def delete_user(db: Session, id: str):
    user = db.query(User).filter(User.id == id).first()
    if user:
        db.delete(user)
        db.commit()
        return True
    return False