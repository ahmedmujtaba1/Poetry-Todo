from fastapi import FastAPI,HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select
from contextlib import asynccontextmanager
from hero_api.settings import *
from hero_api.modals import *

@asynccontextmanager
async def lifespan(app):
    create_db_and_tables()

connect_args = {"check_same_thread": False}
app : FastAPI = FastAPI(lifespan=lifespan, connect_args=connect_args)

engine = create_engine(sqlite_url, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def hash_password(password: str) -> str:
    # Use something like passlib here
    return f"not really hashed {password} hehehe"

@app.get("/")
def root():
    return {"message": "Hello World"}


@app.post("/heroes/", response_model=HeroRead)
def create_hero(hero: HeroCreate):
    hashed_password = hash_password(hero.password)
    with Session(engine) as session:
        extra_data = {"hashed_password": hashed_password}
        db_hero = Hero.model_validate(hero, update=extra_data)
        session.add(db_hero)
        session.commit()
        session.refresh(db_hero)
        return db_hero


@app.get("/heroes/", response_model=list[HeroRead])
def read_heroes(offset: int = 0, limit: int = Query(default=100, le=100)):
    with Session(engine) as session:
        heroes = session.exec(select(Hero).offset(offset).limit(limit)).all()
        return heroes


@app.get("/heroes/{hero_id}", response_model=HeroRead)
def read_hero(hero_id: int):
    with Session(engine) as session:
        hero = session.get(Hero, hero_id)
        if not hero:
            raise HTTPException(status_code=404, detail="Hero not found")
        return hero


@app.patch("/heroes/{hero_id}", response_model=HeroRead)
def update_hero(hero_id: int, hero: HeroUpdate):
    with Session(engine) as session:
        db_hero = session.get(Hero, hero_id)
        if not db_hero:
            raise HTTPException(status_code=404, detail="Hero not found")
        hero_data = hero.model_dump(exclude_unset=True)
        extra_data = {}
        if "password" in hero_data:
            password = hero_data["password"]
            hashed_password = hash_password(password)
            extra_data["hashed_password"] = hashed_password
        db_hero.sqlmodel_update(hero_data, update=extra_data)
        session.add(db_hero)
        session.commit()
        session.refresh(db_hero)
        return db_hero