from fastapi import FastAPI
# import psycopg2
# from psycopg2 import sql

app = FastAPI() 

@app.get("/") 
async def root():
     return {"message": "Hello World"}
