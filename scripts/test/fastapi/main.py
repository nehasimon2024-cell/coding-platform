from fastapi import FastAPI

app = FastAPI()

@app.get("/greet")
def greet(name: str = "Guest"):
    return {"message": f"Welcome, {name}!"}