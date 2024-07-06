import databases
import sqlalchemy

from datetime import datetime
from typing import List

from fastapi import FastAPI
from pydantic import BaseModel, Field

DATABASE_URL = "sqlite:///my_database.db"

database = databases.Database(DATABASE_URL)

metadata = sqlalchemy.MetaData()

users = sqlalchemy.Table( "users", metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("first_name", sqlalchemy.String(32)),
    sqlalchemy.Column("last_name", sqlalchemy.String(32)),
    sqlalchemy.Column("email", sqlalchemy.String(128)),
    sqlalchemy.Column("password", sqlalchemy.String(32)),
)

items = sqlalchemy.Table( "items", metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String(32)),
    sqlalchemy.Column("desription", sqlalchemy.String(256)),
    sqlalchemy.Column("price", sqlalchemy.Float),
)

orders = sqlalchemy.Table( "orders", metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("user_id", sqlalchemy.ForeignKey(users.c.id)),
    sqlalchemy.Column("item_id", sqlalchemy.ForeignKey(items.c.id)),
    sqlalchemy.Column("order_date", sqlalchemy.DateTime),
    sqlalchemy.Column("status", sqlalchemy.String(32)),
)

engine = sqlalchemy.create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
metadata.create_all(engine)

app = FastAPI()

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# Модель для пользователей
class UserIn(BaseModel):
    first_name: str = Field(max_lenght = 32)
    last_name: str = Field(max_lenght = 32)
    email: str = Field(max_length = 128)
    password: str = Field(max_lenght = 32)

class User(BaseModel):
    id: int
    first_name: str = Field(max_lenght = 32)
    last_name: str = Field(max_lenght = 32)
    email: str = Field(max_length = 128)
    password: str = Field(max_lenght = 32)


# Модель для товаров
class ItemIn(BaseModel):
    name: str = Field(max_length = 32)
    description: str = Field(max_length = 128)
    price: float

class Item(BaseModel):
    id: int
    name: str = Field(max_lenght = 32)
    description: str = Field(max_length = 256)
    price: float

# Модель для заказов
class OrderIn(BaseModel):
    user_id: int
    item_id: int
    order_date: datetime
    status: str

class Order(BaseModel):
    id: int
    user_id: int
    item_id: int
    order_date: datetime
    status: str

@app.get("/fake_users/{count}")
async def create_fake_users(count: int):
    for i in range(count):
        query = users.insert().values(first_name = f"user{i}", last_name = f"test{i}", email = f"test{i}@mail.ru", password = "123qwerty")
        await database.execute(query)

@app.get("/users/", response_model=List[User])
async def read_users():
    query = users.select()
    return await database.fetch_all(query)

@app.get("/users/{user_id}", response_model=User)
async def read_user(user_id: int):
    query = users.select().where(users.c.id == user_id)
    return await database.fetch_one(query)

@app.post("/users/", response_model=User)
async def create_user(user: UserIn):
    query = users.insert().values(first_name = user.first_name, last_name = user.last_name, email = user.email, password = user.password)
    last_id = await database.execute(query)
    return {"id": last_id, **user.dict()}

@app.put("/users/{user_id}", response_model=User)
async def update_user(user_id: int, new_user: UserIn):
    query = users.update().where(users.c.id == user_id).values(**new_user.dict())
    await database.execute(query)
    return {"id": user_id, **new_user.dict()}

@app.delete("/users/{user_id}")
async def delete_user(user_id: int):
    query = users.delete().where(users.c.id == user_id)
    await database.execute(query)
    return {"message": "User deleted"}

@app.get("/items/", response_model=List[Item])
async def read_items():
    query = items.select()
    return await database.fetch_all(query)

@app.get("/items/{item_id}", response_model=Item)
async def read_item(item_id: int):
    query = items.select().where(items.c.id == item_id)
    return await database.fetch_one(query)

@app.post("/items/", response_model=Item)
async def create_item(item: ItemIn):
    query = items.insert().values(name = item.name, description = item.description, price = item.price)
    last_id = await database.execute(query)
    return {"id": last_id, **item.dict()}

@app.put("/items/{item_id}", response_model=Item)
async def update_item(item_id: int, new_item: ItemIn):
    query = items.update().where(items.c.id == item_id).values(**new_item.dict())
    await database.execute(query)
    return {"id": item_id, **new_item.dict()}

@app.delete("/items/{item_id}")
async def delete_item(item_id: int):
    query = items.delete().where(items.c.id == item_id)
    await database.execute(query)
    return {"message": "Item deleted"}

@app.get("/orders/", response_model=List[Order])
async def read_orders(user_id = None, item_id = None):
    if user_id and item_id:
        query = orders.select().where(orders.c.user_id == user_id and orders.c.item_id == item_id)
    elif user_id:
        query = orders.select().where(orders.c.user_id == user_id)
    elif item_id:
        query = orders.select().where(orders.c.item_id == item_id)
    else:
        query = orders.select()
    return await database.fetch_all(query)

@app.get("/orders/{order_id}", response_model=Order)
async def read_order(order_id: int):
    query = orders.select().where(orders.c.id == order_id)
    return await database.fetch_one(query)

@app.post("/orders/", response_model=Order)
async def create_order(order: OrderIn):
    query = orders.insert().values(user_id = order.user_id, item_id = order.item_id, status = order.status, order_date = datetime.now)
    last_id = await database.execute(query)
    return {"id": last_id, **order.dict()}

@app.put("/orders/{order_id}", response_model=Order)
async def update_order(order_id: int, new_order: OrderIn):
    query = orders.update().where(orders.c.id == orders).values(**new_order.dict())
    await database.execute(query)
    return {"id": order_id, **new_order.dict()}