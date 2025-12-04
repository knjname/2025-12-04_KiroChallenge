from fastapi import FastAPI

app = FastAPI()

def main() -> None:
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
