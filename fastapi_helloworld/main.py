from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
from .models import User as DBUser, ToDo as DBToDo
from .schemas import UserCreate, ToDoCreate, ToDo, User, Token
from .auth import authenticate_user, create_access_token, get_current_user, get_password_hash, ACCESS_TOKEN_EXPIRE_MINUTES
from .database import SessionLocal, engine, Base
from datetime import timedelta
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency for getting DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/users/", response_model=User)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(DBUser).filter(DBUser.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = get_password_hash(user.password)
    db_user = DBUser(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, username=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/todos/", response_model=ToDo)
def create_todo(todo: ToDoCreate, db: Session = Depends(get_db), current_user: DBUser = Depends(get_current_user)):
    db_todo = DBToDo(**todo.dict(), owner_id=current_user.id)
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

@app.get("/todos/", response_model=List[ToDo])
def read_todos(db: Session = Depends(get_db), current_user: DBUser = Depends(get_current_user)):
    todos = db.query(DBToDo).filter(DBToDo.owner_id == current_user.id).all()
    return todos

@app.put("/todos/{todo_id}", response_model=ToDo)
def update_todo(todo_id: int, todo: ToDoCreate, db: Session = Depends(get_db), current_user: DBUser = Depends(get_current_user)):
    db_todo = db.query(DBToDo).filter(DBToDo.id == todo_id, DBToDo.owner_id == current_user.id).first()
    if not db_todo:
        raise HTTPException(status_code=404, detail="ToDo not found")
    for var, value in vars(todo).items():
        setattr(db_todo, var, value) if value else None
    db.commit()
    db.refresh(db_todo)
    return db_todo

@app.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(todo_id: int, db: Session = Depends(get_db), current_user: DBUser = Depends(get_current_user)):
    db_todo = db.query(DBToDo).filter(DBToDo.id == todo_id, DBToDo.owner_id == current_user.id).first()
    if not db_todo:
        raise HTTPException(status_code=404, detail="ToDo not found")
    db.delete(db_todo)
    db.commit()
    return {"ok": True}
