from fastapi import FastAPI


app = FastAPI(title="TaskLab API", version="0.1.0")


@app.get("/health", tags=["Infraestrutura"])
def health() -> dict[str, str]:
    return {"status": "ok"}
