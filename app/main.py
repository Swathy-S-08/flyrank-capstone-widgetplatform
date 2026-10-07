from fastapi import FastAPI

app = FastAPI(title="Widget Platform")


@app.get("/health")
def health():
    return {"status": "ok"}
