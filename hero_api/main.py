from fastapi import FastAPI

app : FastAPI = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello World"}

