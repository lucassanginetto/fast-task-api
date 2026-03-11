from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def get_root():
    return {"message": "Server is running"}
