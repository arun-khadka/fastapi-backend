# from psycopg2.extras import RealDictCursor
# from fastapi.params import Body
# from random import randrange
# from typing import Optional
# import psycopg2
# import time

from fastapi import FastAPI
from .routers import post, user
from .database import engine
from .import models

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

@app.get("/")
def hello():
    return "Hello!"

app.include_router(post.router)
app.include_router(user.router)



# my_posts = [{"title": "test title 99", "content": "test content 99", "id": 1}]

# for database connection

# while True:
#     try:
#         conn = psycopg2.connect(
#             host="localhost",
#             database="fastapi",
#             user="postgres",
#             password="postgres",
#             cursor_factory=RealDictCursor,
#         )
#         cursor = conn.cursor()
#         print("Database connected successfully!")
#         break
#     except Exception as error:
#         print("Failed connection!")
#         print("Error:", error)
#         time.sleep(2)


# def find_post(id):
#     for p in my_posts:
#         if p["id"] == id:
#             return p


# def find_index_post(id):
#     for i, p in enumerate(my_posts):
#         if p["id"] == id:
#             return i




