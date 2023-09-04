import os

from sqlmodel import SQLModel, Field, create_engine


class Item(SQLModel, table=True):
    id: int = Field(primary_key=True, default=None)
    name: str
    description: str = Field(default=None)
    price: float


class User(SQLModel, table=True):
    id: int = Field(primary_key=True, default=None)
    username: str
    email: str


##

from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import SQLModel, create_engine, Session

# import from .env file manually
from dotenv import load_dotenv

load_dotenv()
# Database URL Format: "postgresql://<USERNAME>:<PASSWORD>@<HOST>:<PORT>/<DATABASE_NAME>"
postgres_user = os.environ.get("POSTGRES_USER")
postgres_password = os.environ.get("POSTGRES_PASSWORD")
postgres_host = os.environ.get("POSTGRES_HOST")
postgres_port = os.environ.get("POSTGRES_PORT", 5432)
project_name = os.environ.get("PROJECT_NAME", "leaguesmanager_project_name_not_passed")
DATABASE_URL = f"postgresql://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{project_name}"
# DATABASE_URL = f"postgresql+pool://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{project_name}"

engine = create_engine(DATABASE_URL)


def get_session():
    with Session(engine) as session:
        yield session


def create_tables():
    SQLModel.metadata.create_all(engine)




def create_item(item: Item):
    with Session(engine) as session:
        session.add(item)
        session.commit()


def get_items():
    with Session(engine) as session:
        return session.query(Item).all()


if __name__ == "__main__":
    # Create tables (run once)
    create_tables()

    # Create a new item
    new_item = Item(name="Sample Item", description="This is a sample item.", price=19.99)
    create_item(new_item)

    # Retrieve items
    items = get_items()
    for item in items:
        print(item.name, item.price)

exit()

app = FastAPI()






if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)
